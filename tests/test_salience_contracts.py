from temporal_gradient.contracts.salience import SalienceEvaluationRequest
from temporal_gradient.salience.pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline


def test_salience_pipeline_matches_contract_shape():
    req = SalienceEvaluationRequest(text="CRITICAL: never stop")
    pipeline = SaliencePipeline(RollingJaccardNovelty(), KeywordImperativeValue())
    result = pipeline.evaluate(req.text)
    assert 0.0 <= result.novelty <= 1.0
    assert 0.0 <= result.value <= 1.0
    assert 0.0 <= result.psi <= 1.0
    assert "H_tokens" in result.diagnostics
    assert "H_window_size" in result.provenance
    assert "V_keyword_count" in result.provenance
