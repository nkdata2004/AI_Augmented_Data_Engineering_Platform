from providers.base import LLMProvider


class MockProvider(LLMProvider):
    """Deterministic provider for reproducible take-home demo without API keys."""

    def generate(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        if "top 10" in lower_prompt and "revenue" in lower_prompt:
            return """
WITH revenue_by_customer AS (
    SELECT
        c.customer_id AS customer_id,
        c.customer_name AS customer_name,
        calculate_customer_revenue(
            c.customer_id,
            DATE '2026-01-01',
            DATE '2026-03-31'
        ) AS revenue
    FROM customers AS c
)
SELECT
    r.customer_id,
    r.customer_name,
    r.revenue
FROM revenue_by_customer AS r
ORDER BY r.revenue DESC
LIMIT 10;
""".strip()
        return """
SELECT
    c.customer_id,
    c.customer_name,
    c.region
FROM customers AS c
LIMIT 10;
""".strip()
