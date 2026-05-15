from app import run
from services.best_practice_validator import validate_best_practices
from validators.syntax_validator import validate_syntax


def test_generated_sql_passes_pipeline():
    result = run("Show me the top 10 customers by revenue last quarter")
    assert result["passed"] is True
    assert "calculate_customer_revenue" in result["generated_sql"]
    assert "SELECT *" not in result["generated_sql"].upper()


def test_syntax_validator_accepts_simple_sql():
    result = validate_syntax("SELECT c.customer_id FROM customers AS c")
    assert result.passed is True


def test_best_practice_rejects_select_star():
    result = validate_best_practices("SELECT * FROM customers")
    assert result.passed is False
