from temporal_gradient.policies import ComputeBudgetPolicy, ComputeCooldownPolicy, allows_compute
from temporal_gradient.policies.compute_budget import ComputeBudgetPolicy as BudgetFromShim
from temporal_gradient.policies.compute_cooldown import ComputeCooldownPolicy as CanonicalCooldownPolicy


def test_compute_cooldown_policy_enforces_cooldown():
    policy = ComputeCooldownPolicy(cooldown_tau=2.0)
    assert not policy.allows_compute(elapsed_tau=1.0)
    assert policy.allows_compute(elapsed_tau=2.0)
    assert allows_compute(elapsed_tau=3.0, cooldown_tau=2.0)


def test_compute_budget_shim_aliases_canonical_policy():
    assert ComputeBudgetPolicy is ComputeCooldownPolicy
    assert BudgetFromShim is CanonicalCooldownPolicy
