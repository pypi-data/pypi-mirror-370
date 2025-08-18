from __future__ import annotations

from typing import Any, Optional

import redis
from sqlalchemy import create_engine

from .config_provider import ConfigProvider
from .db_init import build_mysql_url, init_db
from .settings_service import SettingsService, ensure_default_settings
from .keys_service import KeysService
from .auth_service import AuthService


class _KeysAPI:
	"""Facade to KeysService."""

	def __init__(self, master: "KeyMaster") -> None:
		self._m = master

	def create(self, *args: Any, **kwargs: Any) -> Any:
		return self._m._keys_service().create(*args, **kwargs)

	def deactivate(self, key_id: int) -> None:
		self._m._keys_service().deactivate(key_id)

	def rotate(self, key_id: int, transition_period_hours: int = 24) -> Any:
		return self._m._keys_service().rotate(key_id=key_id, transition_period_hours=transition_period_hours)


class _AuthAPI:
	"""Auth facade to AuthService."""

	def __init__(self, master: "KeyMaster") -> None:
		self._m = master

	def validate_key(self, key_string: str, request_id: Optional[str] = None, required_scope: Optional[str] = None, *, source_ip: Optional[str] = None, request_method: Optional[str] = None, request_path: Optional[str] = None) -> None:
		return self._m._auth_service().validate_key(key_string, request_id=request_id, required_scope=required_scope, source_ip=source_ip, request_method=request_method, request_path=request_path)


class KeyMaster:
	"""Main orchestrator."""

	def __init__(self, base_dir: Optional[str] = None) -> None:
		self._base_dir = base_dir
		self.keys = _KeysAPI(self)
		self.auth = _AuthAPI(self)
		self._engine = None
		self._settings = None
		self._keys = None
		self._auth = None
		self._redis: Optional[redis.Redis] = None

	def _ensure_engine(self):
		if self._engine is None:
			provider = ConfigProvider(self._base_dir)
			mysql_cfg = provider.get_mysql_config()
			url = build_mysql_url(mysql_cfg)
			self._engine = create_engine(url, pool_pre_ping=True)
			# ensure schema and defaults
			init_db(self._base_dir)
			ensure_default_settings(self._engine)
		return self._engine

	def _ensure_redis(self) -> Optional[redis.Redis]:
		if self._redis is None:
			provider = ConfigProvider(self._base_dir)
			redis_cfg = provider.get_redis_config()
			if redis_cfg:
				self._redis = redis.Redis(
					host=redis_cfg["host"],
					port=int(redis_cfg["port"]),
					password=redis_cfg["password"],
					decode_responses=True,
				)
		return self._redis

	def _settings_service(self) -> SettingsService:
		if self._settings is None:
			self._settings = SettingsService(self._ensure_engine())
		return self._settings

	def _keys_service(self) -> KeysService:
		if self._keys is None:
			self._keys = KeysService(self._ensure_engine(), self._settings_service())
		return self._keys

	def _auth_service(self) -> AuthService:
		if self._auth is None:
			self._auth = AuthService(self._ensure_engine(), self._settings_service(), self._ensure_redis())
		return self._auth


def _build_master() -> KeyMaster:
	return KeyMaster()


master: KeyMaster = _build_master()
