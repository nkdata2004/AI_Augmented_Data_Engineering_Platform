-- Auto-generated dbt model draft. Review before production.
-- Migration decision: keep SQL business logic in dbt; orchestration moves to Prefect.
{{ config(materialized='table') }}

SELECT
    c.customer_id AS customer_id,
    c.customer_name AS customer_name,
    COUNT(o.order_id) AS order_count -- HUMAN REVIEW: inferred aggregate/expression,
    SUM(o.order_amount) AS total_order_amount -- HUMAN REVIEW: inferred aggregate/expression,
    MAX(o.order_timestamp) AS latest_order_timestamp -- HUMAN REVIEW: inferred aggregate/expression
FROM {{ source('raw', 'customers') }} c
JOIN {{ source('raw', 'orders') }} o ON c.customer_id = o.customer_id
WHERE o.order_status = 'COMPLETE' -- Preserved business filter from legacy SQL
GROUP BY c.customer_id, c.customer_name
