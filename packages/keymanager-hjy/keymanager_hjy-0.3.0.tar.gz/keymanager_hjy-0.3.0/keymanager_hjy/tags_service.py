from __future__ import annotations

from typing import List, Dict, Any

from sqlalchemy import select, insert, update, delete
from sqlalchemy.engine import Engine

from .schema import keymaster_tags, keymaster_key_tag_map, keymaster_keys


class TagService:
	def __init__(self, engine: Engine) -> None:
		self._engine = engine

	def create(self, name: str) -> int:
		with self._engine.begin() as conn:
			row = conn.execute(select(keymaster_tags.c.id).where(keymaster_tags.c.name == name)).fetchone()
			if row is not None:
				return int(row[0])
			res = conn.execute(insert(keymaster_tags).values(name=name))
			return int(res.inserted_primary_key[0])

	def rename(self, old: str, new: str) -> None:
		with self._engine.begin() as conn:
			conn.execute(update(keymaster_tags).where(keymaster_tags.c.name == old).set({"name": new}))

	def delete(self, name: str) -> None:
		with self._engine.begin() as conn:
			row = conn.execute(select(keymaster_tags.c.id).where(keymaster_tags.c.name == name)).fetchone()
			if row is None:
				return
			tag_id = int(row[0])
			conn.execute(delete(keymaster_key_tag_map).where(keymaster_key_tag_map.c.tag_id == tag_id))
			conn.execute(delete(keymaster_tags).where(keymaster_tags.c.id == tag_id))

	def list(self) -> List[Dict[str, Any]]:
		with self._engine.begin() as conn:
			rows = conn.execute(select(keymaster_tags.c.id, keymaster_tags.c.name)).fetchall()
			return [{"id": int(r[0]), "name": r[1]} for r in rows]

	def add_to_key(self, key_id: int, tag_name: str) -> None:
		with self._engine.begin() as conn:
			row = conn.execute(select(keymaster_tags.c.id).where(keymaster_tags.c.name == tag_name)).fetchone()
			if row is None:
				res = conn.execute(insert(keymaster_tags).values(name=tag_name))
				tag_id = int(res.inserted_primary_key[0])
			else:
				tag_id = int(row[0])
			conn.execute(insert(keymaster_key_tag_map).prefix_with("OR IGNORE").values(key_id=key_id, tag_id=tag_id))

	def remove_from_key(self, key_id: int, tag_name: str) -> None:
		with self._engine.begin() as conn:
			row = conn.execute(select(keymaster_tags.c.id).where(keymaster_tags.c.name == tag_name)).fetchone()
			if row is None:
				return
			tag_id = int(row[0])
			conn.execute(delete(keymaster_key_tag_map).where((keymaster_key_tag_map.c.key_id == key_id) & (keymaster_key_tag_map.c.tag_id == tag_id)))

	def update_by_tag(self, tag_name: str, *, is_active: bool | None = None, rate_limit: str | None = None) -> int:
		"""Bulk update keys with a tag. Returns affected row count (best-effort)."""
		with self._engine.begin() as conn:
			row = conn.execute(select(keymaster_tags.c.id).where(keymaster_tags.c.name == tag_name)).fetchone()
			if row is None:
				return 0
			tag_id = int(row[0])
			q = select(keymaster_key_tag_map.c.key_id).where(keymaster_key_tag_map.c.tag_id == tag_id)
			key_ids = [int(r[0]) for r in conn.execute(q).fetchall()]
			if not key_ids:
				return 0
			values: dict[str, Any] = {}
			if is_active is not None:
				values["is_active"] = is_active
			if rate_limit is not None:
				values["rate_limit"] = rate_limit
			if not values:
				return 0
			res = conn.execute(update(keymaster_keys).where(keymaster_keys.c.id.in_(key_ids)).values(**values))
			return res.rowcount or 0
