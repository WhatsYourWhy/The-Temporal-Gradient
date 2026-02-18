from __future__ import annotations

import hashlib
import json
from typing import Mapping


def compute_provenance_hash(provenance: Mapping[str, str], *, version: str = "1") -> str:
    preimage = {
        "provenance_version": version,
        "provenance": dict(provenance),
    }
    payload = json.dumps(
        preimage,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return digest
