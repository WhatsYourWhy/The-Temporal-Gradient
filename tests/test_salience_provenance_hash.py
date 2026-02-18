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
