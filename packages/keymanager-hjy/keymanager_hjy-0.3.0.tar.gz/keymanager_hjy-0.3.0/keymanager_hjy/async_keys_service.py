from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, select, update, and_
from sqlalchemy.ext.asyncio import AsyncEngine

from .schema import (
    keymaster_keys,
    keymaster_tags,
    keymaster_key_tag_map,
    keymaster_scopes,
    keymaster_key_scope_map,
)
from .async_settings_service import AsyncSettingsService
from .utils import generate_key, hash_key


class AsyncKeysService:
    def __init__(self, engine: AsyncEngine, settings: AsyncSettingsService) -> None:
        self._engine = engine
        self._settings = settings

    async def create(
        self,
        description: str,
        rate_limit: Optional[str] = None,
        expires_at: Optional[str] = None,
        tags: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        prefix = await self._settings.key_prefix()
        plain = generate_key(prefix)
        hashed = hash_key(plain)
        
        async with self._engine.begin() as conn:
            result = await conn.execute(
                insert(keymaster_keys).values(
                    hashed_key=hashed,
                    key_prefix=prefix,
                    description=description,
                    rate_limit=rate_limit,
                    expires_at=expires_at,
                    is_active=True,
                )
            )
            key_id = result.inserted_primary_key[0]

            # Handle tags
            for tag in (tags or []):
                # Check if tag exists
                tag_result = await conn.execute(
                    select(keymaster_tags.c.id).where(keymaster_tags.c.name == tag)
                )
                tag_row = tag_result.fetchone()
                
                if tag_row is None:
                    # Create new tag
                    tag_insert = await conn.execute(
                        insert(keymaster_tags).values(name=tag)
                    )
                    tag_id = tag_insert.inserted_primary_key[0]
                else:
                    tag_id = tag_row[0]
                
                # Check if mapping exists
                mapping_result = await conn.execute(
                    select(keymaster_key_tag_map.c.key_id).where(
                        and_(
                            keymaster_key_tag_map.c.key_id == key_id,
                            keymaster_key_tag_map.c.tag_id == tag_id,
                        )
                    )
                )
                if mapping_result.fetchone() is None:
                    await conn.execute(
                        insert(keymaster_key_tag_map).values(key_id=key_id, tag_id=tag_id)
                    )

            # Handle scopes
            for scope in (scopes or []):
                # Check if scope exists
                scope_result = await conn.execute(
                    select(keymaster_scopes.c.id).where(keymaster_scopes.c.name == scope)
                )
                scope_row = scope_result.fetchone()
                
                if scope_row is None:
                    # Create new scope
                    scope_insert = await conn.execute(
                        insert(keymaster_scopes).values(name=scope)
                    )
                    scope_id = scope_insert.inserted_primary_key[0]
                else:
                    scope_id = scope_row[0]
                
                # Check if mapping exists
                mapping_result = await conn.execute(
                    select(keymaster_key_scope_map.c.key_id).where(
                        and_(
                            keymaster_key_scope_map.c.key_id == key_id,
                            keymaster_key_scope_map.c.scope_id == scope_id,
                        )
                    )
                )
                if mapping_result.fetchone() is None:
                    await conn.execute(
                        insert(keymaster_key_scope_map).values(key_id=key_id, scope_id=scope_id)
                    )

        return {"key": plain, "id": key_id}

    async def deactivate(self, key_id: int) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(
                update(keymaster_keys)
                .where(keymaster_keys.c.id == key_id)
                .values(is_active=False)
            )

    async def rotate(self, key_id: int, transition_period_hours: int = 24) -> Dict[str, Any]:
        """Create a new key inheriting properties and set old key to expire after transition period."""
        async with self._engine.begin() as conn:
            # Get existing key properties
            result = await conn.execute(
                select(
                    keymaster_keys.c.description,
                    keymaster_keys.c.rate_limit,
                    keymaster_keys.c.key_prefix,
                )
                .where(keymaster_keys.c.id == key_id)
            )
            row = result.fetchone()
            if row is None:
                raise ValueError("key not found")
            description, rate_limit, prefix = row

            # Collect tags
            tag_result = await conn.execute(
                select(keymaster_tags.c.name)
                .select_from(
                    keymaster_key_tag_map.join(
                        keymaster_tags, keymaster_key_tag_map.c.tag_id == keymaster_tags.c.id
                    )
                )
                .where(keymaster_key_tag_map.c.key_id == key_id)
            )
            tag_rows = tag_result.fetchall()
            tags = [r[0] for r in tag_rows]
            
            # Collect scopes
            scope_result = await conn.execute(
                select(keymaster_scopes.c.name)
                .select_from(
                    keymaster_key_scope_map.join(
                        keymaster_scopes, keymaster_key_scope_map.c.scope_id == keymaster_scopes.c.id
                    )
                )
                .where(keymaster_key_scope_map.c.key_id == key_id)
            )
            scope_rows = scope_result.fetchall()
            scopes = [r[0] for r in scope_rows]

        # Create new key with same attributes
        new_info = await self.create(
            description=description or "rotated", 
            rate_limit=rate_limit, 
            tags=tags, 
            scopes=scopes
        )
        
        # Set old key expires_at to now + transition
        exp_at = datetime.now(timezone.utc) + timedelta(hours=transition_period_hours)
        async with self._engine.begin() as conn:
            await conn.execute(
                update(keymaster_keys)
                .where(keymaster_keys.c.id == key_id)
                .values(expires_at=exp_at)
            )
        
        return new_info
