-- =====================================================================
-- Online Retail Store: database tests
-- Run against a freshly seeded database (python scripts/rebuild_db.py).
-- Each SELECT shows what to expect in its comment.
-- =====================================================================
PRAGMA foreign_keys = ON;

-- TEST 1A: Trigger "reduce stock + log inventory" ---------------------
SELECT stock_qty FROM Products WHERE product_id = 'P1003';     -- expect 74

INSERT INTO Orders (order_id, customer_id, status) VALUES ('T9001', 'C3004', 'Pending');
INSERT INTO OrderItems (order_id, product_id, quantity, unit_price)
VALUES ('T9001', 'P1003', 4, 129.00);

SELECT stock_qty FROM Products WHERE product_id = 'P1003';     -- expect 70 (down by 4)
SELECT product_id, adjustment, reason FROM Inventory
WHERE reason = 'Order T9001';                                  -- expect P1003 | -4

-- TEST 1B: Trigger "restore stock on cancel" ---------------------------
UPDATE Orders SET status = 'Cancelled' WHERE order_id = 'T9001';

SELECT stock_qty FROM Products WHERE product_id = 'P1003';     -- expect 74 (back up)
SELECT product_id, adjustment, reason FROM Inventory
WHERE reason = 'Order T9001 cancelled';                        -- expect P1003 | 4

-- TEST 2: Views ---------------------------------------------------------
SELECT * FROM vw_customer_order_summary WHERE customer_id = 'C3001';
-- expect 2 orders, total_spent ~319.96 (REAL floating point: see README, Next steps)
SELECT * FROM vw_top_selling_products LIMIT 3;
-- expect P1003 first with 5 sold: the view still counts lines from cancelled
-- orders (T9001, O4006). Known limitation, see README.

-- TEST 3: Constraints (each statement below should FAIL) ----------------
-- CHECK (quantity > 0)
INSERT INTO OrderItems (order_id, product_id, quantity, unit_price)
VALUES ('O4001', 'P1001', -1, 79.99);
-- CHECK (price_gbp >= 0)
INSERT INTO Products (product_id, name, price_gbp, stock_qty, supplier_id)
VALUES ('PX1', 'Bad price', -5, 10, 'S2001');
-- FOREIGN KEY: supplier does not exist
INSERT INTO Products (product_id, name, price_gbp, stock_qty, supplier_id)
VALUES ('PX2', 'No supplier', 5, 10, 'S9999');
-- ON DELETE RESTRICT: product appears in past orders
DELETE FROM Products WHERE product_id = 'P1001';

-- TEST 4: Index is used --------------------------------------------------
EXPLAIN QUERY PLAN
SELECT * FROM OrderItems WHERE order_id = 'O4001';
-- expect: SEARCH OrderItems USING INDEX idx_orderitems_order (order_id=?)
