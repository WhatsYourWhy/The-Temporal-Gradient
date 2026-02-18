from __future__ import annotations

import tempfile
from anomaly_poc import run_poc


BASE_CONFIG = """salience:
  window_size: 5
  keywords:
    - must
    - never
    - critical
    - always
    - don't
    - stop
    - urgent
  base_value: 0.1
  hit_value: 0.2
  max_value: 1.0

clock:
  base_dilation_factor: 1.0
  min_clock_rate: 0.05
  salience_mode: canonical
  legacy_density_scale: 100.0

memory:
  half_life: 20.0
  prune_threshold: 0.2
  encode_threshold: {encode_threshold}
  initial_strength_max: 1.2
  decay_lambda: {decay_lambda}
  s_max: {s_max}

policies:
  deterministic_seed: 1337
  event_wall_delta: 1.0
  cooldown_tau: {cooldown_tau}
  calibration_post_sweep_wall_delta: {sweep_every}
"""


def _write_cfg(*, cooldown_tau: float, encode_threshold: float, s_max: float, decay_lambda: float, sweep_every: float) -> str:
    tmp = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False)
    tmp.write(
        BASE_CONFIG.format(
            cooldown_tau=cooldown_tau,
            encode_threshold=encode_threshold,
            s_max=s_max,
            decay_lambda=decay_lambda,
            sweep_every=sweep_every,
        )
    )
    tmp.flush()
    tmp.close()
    return tmp.name


def test_run_poc_is_deterministic_for_same_config():
    cfg = _write_cfg(cooldown_tau=0.0, encode_threshold=0.0, s_max=1.5, decay_lambda=0.05, sweep_every=5.0)

    first = run_poc(config_path=cfg, n_events=25)
    second = run_poc(config_path=cfg, n_events=25)

    assert first["seed"] == 1337
    assert first["tau_final"] == second["tau_final"]
    assert first["encoded_count"] == second["encoded_count"]
    assert first["write_log"] == second["write_log"]


def test_run_poc_knobs_change_observable_outputs():
    no_cooldown = _write_cfg(cooldown_tau=0.0, encode_threshold=0.0, s_max=1.5, decay_lambda=0.05, sweep_every=5.0)
    with_cooldown = _write_cfg(cooldown_tau=10.0, encode_threshold=0.0, s_max=1.5, decay_lambda=0.05, sweep_every=5.0)
    small_cap = _write_cfg(cooldown_tau=0.0, encode_threshold=0.0, s_max=0.05, decay_lambda=0.05, sweep_every=5.0)
    low_decay = _write_cfg(cooldown_tau=0.0, encode_threshold=0.0, s_max=1.5, decay_lambda=0.05, sweep_every=100.0)
    high_decay = _write_cfg(cooldown_tau=0.0, encode_threshold=0.0, s_max=1.5, decay_lambda=0.5, sweep_every=100.0)

    baseline = run_poc(config_path=no_cooldown, n_events=50)
    cooldown = run_poc(config_path=with_cooldown, n_events=50)
    capped = run_poc(config_path=small_cap, n_events=50)
    low = run_poc(config_path=low_decay, n_events=50)
    high = run_poc(config_path=high_decay, n_events=50)

    assert len(cooldown["write_log"]) < len(baseline["write_log"])
    assert max(item["strength"] for item in capped["write_log"]) <= 0.05
    assert high["total_swept_forgotten"] >= low["total_swept_forgotten"]
