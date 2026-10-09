-- =====================================================================
-- Online Retail Store: business queries
-- Each query answers a question the business actually asks.
-- =====================================================================

-- 1. JOIN across 3 tables
-- "Show every order with the customer's name and how many items it had."
SELECT
    o.order_id,
    o.order_date,
    c.first_name || ' ' || c.last_name AS customer_name,
    SUM(oi.quantity)                   AS total_items
FROM Orders o
JOIN Customers  c  ON c.customer_id = o.customer_id
JOIN OrderItems oi ON oi.order_id   = o.order_id
GROUP BY o.order_id;


-- 2. GROUP BY with HAVING
-- "Who are our repeat customers (more than one order)?"
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(o.order_id)                  AS total_orders
FROM Customers c
JOIN Orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id
HAVING COUNT(o.order_id) > 1;


-- 3. Date + aggregate functions
-- "What is our revenue per month?"
SELECT
    strftime('%Y-%m', order_date)  AS order_month,
    COUNT(order_id)                AS total_orders,
    ROUND(SUM(total_amount), 2)    AS total_revenue
FROM Orders
WHERE status <> 'Cancelled'
GROUP BY order_month
ORDER BY order_month;


-- 4. Customer spending report (used by the Reports window in the app)
-- "Which customers have spent the most?"
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    SUM(oi.quantity * oi.unit_price)   AS total_spent
FROM Customers c
JOIN Orders     o  ON c.customer_id = o.customer_id
JOIN OrderItems oi ON o.order_id    = oi.order_id
GROUP BY c.customer_id
HAVING total_spent > 0
ORDER BY total_spent DESC;


-- 5. Views
SELECT * FROM vw_customer_order_summary ORDER BY total_spent DESC;
SELECT * FROM vw_top_selling_products;


-- 6. Low stock report (the app runs this with the custom fn_stock_level()
--    function; plain-SQL version shown here)
SELECT product_id, name, stock_qty
FROM Products
WHERE stock_qty < 20
ORDER BY stock_qty;


-- 7. Optimisation: check that the JOIN uses the index
EXPLAIN QUERY PLAN
SELECT o.order_id, SUM(oi.quantity)
FROM Orders o
JOIN OrderItems oi ON oi.order_id = o.order_id
GROUP BY o.order_id;
