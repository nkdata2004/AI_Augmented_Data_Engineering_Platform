-- Business purpose: create daily customer order summary for analytics.
CREATE TABLE mart.customer_order_summary AS
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS order_count,
    SUM(o.order_amount) AS total_order_amount,
    MAX(o.order_timestamp) AS latest_order_timestamp
FROM raw.customers c
JOIN raw.orders o
  ON c.customer_id = o.customer_id
WHERE o.order_status = 'COMPLETE'
GROUP BY c.customer_id, c.customer_name;
