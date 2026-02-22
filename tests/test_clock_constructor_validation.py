import textwrap

import pytest

from temporal_gradient.clock.chronos import ClockRateModulator
from temporal_gradient.config_loader import ConfigValidationError, load_config


def _write(tmp_path, body: str):
    path = tmp_path / "tg.yaml"
    path.write_text(textwrap.dedent(body))
    return path


@pytest.mark.parametrize(
    "kwargs, expected_error",
    [
        ({"min_clock_rate": -0.1}, "clock.min_clock_rate must be > 0.0"),
        ({"base_dilation_factor": 0.0}, "clock.base_dilation_factor must be > 0.0"),
        ({"legacy_density_scale": 0.0}, "clock.legacy_density_scale must be > 0.0"),
        (
            {"min_clock_rate": 0.9, "max_clock_rate": 0.5},
            "clock.min_clock_rate must be <= clock.max_clock_rate",
        ),
    ],
)
def test_direct_constructor_rejects_invalid_clock_bounds(kwargs, expected_error):
    with pytest.raises(ValueError, match=expected_error):
        ClockRateModulator(**kwargs)


def test_constructor_error_matches_config_path_for_negative_min_clock_rate(tmp_path):
    config_path = _write(
        tmp_path,
        """
        salience: {}
        clock:
          min_clock_rate: -0.1
        memory: {}
        policies: {}
        """,
    )

    with pytest.raises(ConfigValidationError) as config_exc:
        load_config(config_path)
    with pytest.raises(ValueError) as constructor_exc:
        ClockRateModulator(min_clock_rate=-0.1)

    assert str(constructor_exc.value) == str(config_exc.value)


def test_constructor_error_matches_config_path_for_non_positive_base_dilation(tmp_path):
    config_path = _write(
        tmp_path,
        """
        salience: {}
        clock:
          base_dilation_factor: 0.0
        memory: {}
        policies: {}
        """,
    )

    with pytest.raises(ConfigValidationError) as config_exc:
        load_config(config_path)
    with pytest.raises(ValueError) as constructor_exc:
        ClockRateModulator(base_dilation_factor=0.0)

    assert str(constructor_exc.value) == str(config_exc.value)
