import math

from salience_pipeline import KeywordImperativeValue, RollingJaccardNovelty, SaliencePipeline


def test_salience_pipeline_bounds_and_product():
    novelty = RollingJaccardNovelty(window_size=3)
    value = KeywordImperativeValue(keywords=["must"], base_value=0.2, hit_value=0.3, max_value=1.0)
    pipeline = SaliencePipeline(novelty, value)

    first = pipeline.evaluate("We must always test our pipeline.")
    second = pipeline.evaluate("We must always test our pipeline.")

    for result in (first, second):
        assert 0.0 <= result.novelty <= 1.0
        assert 0.0 <= result.value <= 1.0
        assert 0.0 <= result.psi <= 1.0
        assert math.isclose(result.psi, result.novelty * result.value, rel_tol=1e-9)
