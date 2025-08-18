from __future__ import annotations

from typing import Optional

from urllib.parse import quote_plus
from sqlalchemy import create_engine

from .config_provider import ConfigProvider
from .exceptions import InitializationError
from .schema import create_all


def build_mysql_url(cfg: dict) -> str:
	host = cfg["host"]
	port = cfg["port"]
	user = cfg["user"]
	password = cfg["password"]
	database = cfg["database"]
	user_enc = quote_plus(user)
	pass_enc = quote_plus(password)
	db_enc = quote_plus(database)
	return f"mysql+mysqlconnector://{user_enc}:{pass_enc}@{host}:{port}/{db_enc}"


def init_db(base_dir: Optional[str] = None) -> None:
	provider = ConfigProvider(base_dir)
	mysql_cfg = provider.get_mysql_config()
	try:
		url = build_mysql_url(mysql_cfg)
	except KeyError as e:
		raise InitializationError(f"MySQL 配置缺失字段: {e}") from e

	engine = create_engine(url, pool_pre_ping=True)
	create_all(engine)
