# PoC Validation Report

Validated `anomaly_poc.py` and `docs_knob_validation_checklist.md` against requested goals.

- Deterministic seeding is wired via `random.seed(cfg.policies.deterministic_seed)`.
- Flat config sections are loaded from `tg.load_config` and accessed as `cfg.salience`, `cfg.clock`, `cfg.memory`, `cfg.policies`.
- `validate_packet_schema(packet, salience_mode=cfg.clock.salience_mode)` call matches signature.
- Packet annotations are added **after** schema validation.
- Summary currently omits `total_swept_forgotten`, `total_swept_survivors`, `sweep_points`, and `vault_size`.
- Checklist currently references `memories_alive` / `memories_forgotten` instead of aggregate sweep metrics.
- Recent PoC-related commits appear limited to PoC/docs/tests files.
