from __future__ import annotations

import hashlib
import secrets
from typing import Tuple


def generate_key(prefix: str, entropy_bytes: int = 24) -> str:
	body = secrets.token_urlsafe(entropy_bytes)
	return f"{prefix}-{body}"


def hash_key(plain_key: str) -> str:
	# Stable, fast hash; no plaintext persisted
	return hashlib.sha256(plain_key.encode("utf-8")).hexdigest()


def parse_rate_limit(value: str) -> Tuple[int, str]:
	"""Parse rate string like '100/minute' -> (100, 'minute')."""
	parts = value.split("/")
	if len(parts) != 2:
		raise ValueError("invalid rate format")
	count = int(parts[0])
	unit = parts[1].strip().lower()
	return count, unit
