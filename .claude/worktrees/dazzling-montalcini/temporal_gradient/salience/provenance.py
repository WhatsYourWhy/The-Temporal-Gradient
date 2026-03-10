from __future__ import annotations

import hashlib
import json
from typing import Mapping


def compute_provenance_hash(
    provenance: Mapping[str, str],
    *,
    kind: str = "temporal_gradient.salience_provenance",
    provenance_version: str = "1",
    role: str = "pipeline",
) -> str:
    preimage = {
        "kind": kind,
        "provenance_version": provenance_version,
        "role": role,
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
