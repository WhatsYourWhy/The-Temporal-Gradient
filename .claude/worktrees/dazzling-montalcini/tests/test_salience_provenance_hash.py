from temporal_gradient.salience.provenance import compute_provenance_hash


def test_compute_provenance_hash_is_stable_across_calls() -> None:
    provenance = {
        "H_window_size": "3",
        "V_keyword_count": "5",
    }

    hash1 = compute_provenance_hash(provenance)
    hash2 = compute_provenance_hash(provenance)

    assert hash1 == hash2


def test_compute_provenance_hash_is_key_order_invariant() -> None:
    provenance1 = {
        "H_window_size": "3",
        "V_keyword_count": "5",
        "V_keyword_hits": "2",
    }
    provenance2 = {
        "V_keyword_hits": "2",
        "H_window_size": "3",
        "V_keyword_count": "5",
    }

    assert compute_provenance_hash(provenance1) == compute_provenance_hash(provenance2)


def test_compute_provenance_hash_changes_with_kind() -> None:
    provenance = {"H_window_size": "3", "V_keyword_count": "5"}

    default_hash = compute_provenance_hash(provenance)
    alternate_hash = compute_provenance_hash(provenance, kind="temporal_gradient.alt_provenance")

    assert default_hash != alternate_hash


def test_compute_provenance_hash_changes_with_role() -> None:
    provenance = {"H_window_size": "3", "V_keyword_count": "5"}

    default_hash = compute_provenance_hash(provenance)
    alternate_hash = compute_provenance_hash(provenance, role="H")

    assert default_hash != alternate_hash


def test_compute_provenance_hash_changes_with_provenance_version() -> None:
    provenance = {"H_window_size": "3", "V_keyword_count": "5"}

    v1_hash = compute_provenance_hash(provenance, provenance_version="1")
    v2_hash = compute_provenance_hash(provenance, provenance_version="2")

    assert v1_hash != v2_hash
