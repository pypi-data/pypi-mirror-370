from __future__ import annotations

import os
from typing import Dict, Optional

from .exceptions import InitializationError


def _parse_env_file(path: str) -> Dict[str, str]:
	if not os.path.exists(path):
		raise InitializationError(f"env 文件不存在: {path}")
	values: Dict[str, str] = {}
	with open(path, "r", encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith("#"):
				continue
			if "=" not in line:
				continue
			k, v = line.split("=", 1)
			values[k.strip()] = v.strip().strip('"').strip("'")
	return values


class MySQLConfig(Dict[str, str]):
	__slots__ = ()


class RedisConfig(Dict[str, str]):
	__slots__ = ()


class ConfigProvider:
	"""Reads configuration from env files without logging sensitive values."""

	def __init__(self, base_dir: Optional[str] = None) -> None:
		self.base_dir = base_dir or os.getcwd()

	def get_mysql_config(self, filename: str = "mysql.env") -> MySQLConfig:
		path = os.path.join(self.base_dir, filename)
		vals = _parse_env_file(path)
		required = ["MYSQL_HOST", "MYSQL_PORT", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"]
		missing = [k for k in required if not vals.get(k)]
		if missing:
			raise InitializationError(
				"mysql.env 缺少必要字段: " + ",".join(missing)
			)
		return MySQLConfig({
			"host": vals["MYSQL_HOST"],
			"port": vals["MYSQL_PORT"],
			"user": vals["MYSQL_USER"],
			"password": vals["MYSQL_PASSWORD"],
			"database": vals["MYSQL_DATABASE"],
		})

	def get_redis_config(self, filename: str = "mysql.env") -> Optional[RedisConfig]:
		# 默认与 mysql.env 同文件，若实际提供独立 redis.env，可在调用处传入
		path = os.path.join(self.base_dir, filename)
		if not os.path.exists(path):
			return None
		vals = _parse_env_file(path)
		keys = ["REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD"]
		if not any(vals.get(k) for k in keys):
			return None
		return RedisConfig({
			"host": vals.get("REDIS_HOST", ""),
			"port": vals.get("REDIS_PORT", ""),
			"password": vals.get("REDIS_PASSWORD", ""),
		})
