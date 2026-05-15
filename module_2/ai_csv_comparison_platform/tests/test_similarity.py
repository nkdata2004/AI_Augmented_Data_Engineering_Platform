from csv_compare.similarity import combined_similarity, levenshtein_distance, normalize_column


def test_levenshtein_distance():
    assert levenshtein_distance("kitten", "sitting") == 3


def test_abbreviation_normalization():
    assert "customer" in normalize_column("cust_id")
    assert "identifier" in normalize_column("cust_id")


def test_column_similarity_customer_id():
    score = combined_similarity("cust_id", "CustomerID")
    assert score.confidence >= 0.70
    assert score.embedding > 0.0
