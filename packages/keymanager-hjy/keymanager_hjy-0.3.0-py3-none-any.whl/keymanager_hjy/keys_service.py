from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, select, update, and_
from sqlalchemy.engine import Engine

from .schema import (
	keymaster_keys,
	keymaster_tags,
	keymaster_key_tag_map,
	keymaster_scopes,
	keymaster_key_scope_map,
)
from .settings_service import SettingsService
from .utils import generate_key, hash_key


class KeysService:
	def __init__(self, engine: Engine, settings: SettingsService) -> None:
		self._engine = engine
		self._settings = settings

	def create(
		self,
		description: str,
		rate_limit: Optional[str] = None,
		expires_at: Optional[str] = None,
		tags: Optional[List[str]] = None,
		scopes: Optional[List[str]] = None,
	) -> Dict[str, Any]:
		prefix = self._settings.key_prefix()
		plain = generate_key(prefix)
		hashed = hash_key(plain)
		with self._engine.begin() as conn:
			result = conn.execute(
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

			# tags
			for tag in (tags or []):
				row = conn.execute(select(keymaster_tags.c.id).where(keymaster_tags.c.name == tag)).fetchone()
				if row is None:
					row_ins = conn.execute(insert(keymaster_tags).values(name=tag))
					tag_id = row_ins.inserted_primary_key[0]
				else:
					tag_id = row[0]
				# insert mapping if not exists
				exists = conn.execute(
					select(keymaster_key_tag_map.c.key_id).where(
						and_(
							keymaster_key_tag_map.c.key_id == key_id,
							keymaster_key_tag_map.c.tag_id == tag_id,
						)
					)
				).fetchone()
				if exists is None:
					conn.execute(insert(keymaster_key_tag_map).values(key_id=key_id, tag_id=tag_id))

			# scopes
			for scope in (scopes or []):
				row = conn.execute(select(keymaster_scopes.c.id).where(keymaster_scopes.c.name == scope)).fetchone()
				if row is None:
					row_ins = conn.execute(insert(keymaster_scopes).values(name=scope))
					scope_id = row_ins.inserted_primary_key[0]
				else:
					scope_id = row[0]
				# insert mapping if not exists
				exists = conn.execute(
					select(keymaster_key_scope_map.c.key_id).where(
						and_(
							keymaster_key_scope_map.c.key_id == key_id,
							keymaster_key_scope_map.c.scope_id == scope_id,
						)
					)
				).fetchone()
				if exists is None:
					conn.execute(insert(keymaster_key_scope_map).values(key_id=key_id, scope_id=scope_id))

		return {"key": plain, "id": key_id}

	def deactivate(self, key_id: int) -> None:
		with self._engine.begin() as conn:
			conn.execute(update(keymaster_keys).where(keymaster_keys.c.id == key_id).values(is_active=False))

	def rotate(self, key_id: int, transition_period_hours: int = 24) -> Dict[str, Any]:
		"""Create a new key inheriting properties and set old key to expire after transition period."""
		with self._engine.begin() as conn:
			row = conn.execute(
				select(
					keymaster_keys.c.description,
					keymaster_keys.c.rate_limit,
					keymaster_keys.c.key_prefix,
				)
				.where(keymaster_keys.c.id == key_id)
			).fetchone()
			if row is None:
				raise ValueError("key not found")
			description, rate_limit, prefix = row

			# collect tags
			tag_rows = conn.execute(
				select(keymaster_tags.c.name)
				.select_from(keymaster_key_tag_map.join(keymaster_tags, keymaster_key_tag_map.c.tag_id == keymaster_tags.c.id))
				.where(keymaster_key_tag_map.c.key_id == key_id)
			).fetchall()
			tags = [r[0] for r in tag_rows]
			# collect scopes
			scope_rows = conn.execute(
				select(keymaster_scopes.c.name)
				.select_from(keymaster_key_scope_map.join(keymaster_scopes, keymaster_key_scope_map.c.scope_id == keymaster_scopes.c.id))
				.where(keymaster_key_scope_map.c.key_id == key_id)
			).fetchall()
			scopes = [r[0] for r in scope_rows]

		# create new key with same attributes
		new_info = self.create(description=description or "rotated", rate_limit=rate_limit, tags=tags, scopes=scopes)
		# set old key expires_at to now + transition
		exp_at = datetime.now(timezone.utc) + timedelta(hours=transition_period_hours)
		with self._engine.begin() as conn2:
			conn2.execute(update(keymaster_keys).where(keymaster_keys.c.id == key_id).values(expires_at=exp_at))
		return new_info
