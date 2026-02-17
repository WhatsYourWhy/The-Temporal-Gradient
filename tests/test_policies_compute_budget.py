from temporal_gradient.policies.compute_budget import ComputeBudgetPolicy, allows_compute


def test_compute_budget_policy_enforces_cooldown():
    policy = ComputeBudgetPolicy(cooldown_tau=2.0)
    assert not policy.allows_compute(elapsed_tau=1.0)
    assert policy.allows_compute(elapsed_tau=2.0)
    assert allows_compute(elapsed_tau=3.0, cooldown_tau=2.0)
