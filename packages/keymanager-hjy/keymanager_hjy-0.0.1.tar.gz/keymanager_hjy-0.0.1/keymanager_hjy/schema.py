from __future__ import annotations

from sqlalchemy import (
	MetaData,
	Table,
	Column,
	Integer,
	BigInteger,
	String,
	Text,
	Boolean,
	DateTime,
	ForeignKey,
	UniqueConstraint,
	Index,
	func,
)


metadata = MetaData()


keymaster_settings = Table(
	"keymaster_settings",
	metadata,
	Column("key", String(128), primary_key=True),
	Column("value", Text, nullable=False),
	Column("description", Text, nullable=True),
)


keymaster_keys = Table(
	"keymaster_keys",
	metadata,
	Column("id", Integer, primary_key=True, autoincrement=True),
	Column("hashed_key", String(180), nullable=False),
	Column("key_prefix", String(64), nullable=False),
	Column("description", Text, nullable=True),
	Column("rate_limit", String(64), nullable=True),
	Column("is_active", Boolean, nullable=False, server_default="1"),
	Column("expires_at", DateTime, nullable=True),
	Column("created_at", DateTime, nullable=False, server_default=func.now()),
	Column("updated_at", DateTime, nullable=False, server_default=func.now(), onupdate=func.now()),
	UniqueConstraint("hashed_key", name="uq_keymaster_keys_hashed_key"),
	Index("ix_keymaster_keys_hashed_key", "hashed_key"),
)


keymaster_logs = Table(
	"keymaster_logs",
	metadata,
	Column("id", BigInteger, primary_key=True, autoincrement=True),
	Column("key_id", Integer, ForeignKey("keymaster_keys.id"), nullable=True, index=True),
	Column("timestamp", DateTime, nullable=False, server_default=func.now(), index=True),
	Column("request_id", String(64), nullable=True, index=True),
	Column("source_ip", String(64), nullable=True),
	Column("request_method", String(16), nullable=True),
	Column("request_path", String(255), nullable=True),
	Column("was_success", Boolean, nullable=False, server_default="0"),
	Column("error_reason", String(128), nullable=True),
)


keymaster_tags = Table(
	"keymaster_tags",
	metadata,
	Column("id", Integer, primary_key=True, autoincrement=True),
	Column("name", String(64), nullable=False, unique=True),
)


keymaster_key_tag_map = Table(
	"keymaster_key_tag_map",
	metadata,
	Column("key_id", Integer, ForeignKey("keymaster_keys.id"), nullable=False),
	Column("tag_id", Integer, ForeignKey("keymaster_tags.id"), nullable=False),
	UniqueConstraint("key_id", "tag_id", name="uq_key_tag_pair"),
)


keymaster_scopes = Table(
	"keymaster_scopes",
	metadata,
	Column("id", Integer, primary_key=True, autoincrement=True),
	Column("name", String(64), nullable=False, unique=True),
	Column("description", Text, nullable=True),
)


keymaster_key_scope_map = Table(
	"keymaster_key_scope_map",
	metadata,
	Column("key_id", Integer, ForeignKey("keymaster_keys.id"), nullable=False),
	Column("scope_id", Integer, ForeignKey("keymaster_scopes.id"), nullable=False),
	UniqueConstraint("key_id", "scope_id", name="uq_key_scope_pair"),
)


def create_all(engine) -> None:  # type: ignore[no-untyped-def]
	"""Create all keymaster tables idempotently."""
	metadata.create_all(engine)
