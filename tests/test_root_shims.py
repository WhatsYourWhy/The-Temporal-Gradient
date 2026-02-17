import chronometric_vector
import chronos_engine
import entropic_decay
import salience_pipeline


def test_root_shims_export_canonical_symbols():
    assert hasattr(chronometric_vector, "ChronometricVector")
    assert hasattr(chronos_engine, "ClockRateModulator")
    assert hasattr(entropic_decay, "DecayEngine")
    assert hasattr(salience_pipeline, "SaliencePipeline")
