-- =====================================================================
-- Online Retail Store: database schema (SQLite)
-- 6 tables, 2 triggers, 2 views, 2 indexes
-- Run with: python scripts/rebuild_db.py
-- =====================================================================

-- SQLite does NOT enforce foreign keys unless this is switched on
-- (per connection), so it is the first line of the schema.
PRAGMA foreign_keys = ON;

DROP VIEW    IF EXISTS vw_customer_order_summary;
DROP VIEW    IF EXISTS vw_top_selling_products;
DROP TRIGGER IF EXISTS trg_orderitems_after_insert;
DROP TRIGGER IF EXISTS trg_order_cancel_restore_stock;
DROP TABLE   IF EXISTS Inventory;
DROP TABLE   IF EXISTS OrderItems;
DROP TABLE   IF EXISTS Orders;
DROP TABLE   IF EXISTS Products;
DROP TABLE   IF EXISTS Suppliers;
DROP TABLE   IF EXISTS Customers;

-- ---------------------------------------------------------------------
-- Customers: one row per registered customer
-- ---------------------------------------------------------------------
CREATE TABLE Customers (
    customer_id       TEXT PRIMARY KEY,           -- e.g. C3001
    first_name        TEXT NOT NULL,
    last_name         TEXT NOT NULL,
    email             TEXT NOT NULL,              -- stored obfuscated by the app (see utils.py)
    phone             TEXT,
    address           TEXT,
    city              TEXT,
    country           TEXT,
    registration_date TEXT                        -- ISO-8601 date (YYYY-MM-DD)
);

-- ---------------------------------------------------------------------
-- Suppliers: who supplies each product
-- ---------------------------------------------------------------------
CREATE TABLE Suppliers (
    supplier_id   TEXT PRIMARY KEY,               -- e.g. S2001
    name          TEXT NOT NULL,
    contact_name  TEXT,
    phone         TEXT,
    email         TEXT,
    address       TEXT
);

-- ---------------------------------------------------------------------
-- Products: catalogue, with flexible specs as XML and an optional image
-- ---------------------------------------------------------------------
CREATE TABLE Products (
    product_id        TEXT PRIMARY KEY,           -- e.g. P1001
    name              TEXT NOT NULL,
    category          TEXT,
    price_gbp         REAL NOT NULL CHECK (price_gbp >= 0),
    stock_qty         INTEGER NOT NULL CHECK (stock_qty >= 0),
    supplier_id       TEXT NOT NULL,
    product_spec_xml  TEXT,                       -- attributes that vary by product type
    image_blob        BLOB,                       -- product photo as raw bytes

    -- every product must come from a real supplier;
    -- a supplier that still has products cannot be deleted
    FOREIGN KEY (supplier_id)
        REFERENCES Suppliers(supplier_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- Orders: one row per order (header)
-- ---------------------------------------------------------------------
CREATE TABLE Orders (
    order_id         TEXT PRIMARY KEY,            -- e.g. O4001
    customer_id      TEXT NOT NULL,
    order_date       TEXT DEFAULT (datetime('now')),
    status           TEXT NOT NULL DEFAULT 'Pending',
    shipping_address TEXT,
    total_amount     REAL NOT NULL DEFAULT 0,

    -- every order belongs to a real customer;
    -- deleting a customer deletes their orders
    FOREIGN KEY (customer_id)
        REFERENCES Customers(customer_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- OrderItems: the lines of an order (resolves Orders <-> Products M:N)
-- ---------------------------------------------------------------------
CREATE TABLE OrderItems (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id      TEXT NOT NULL,
    product_id    TEXT NOT NULL,
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    unit_price    REAL NOT NULL CHECK (unit_price >= 0),  -- price at time of sale

    -- derived column, always consistent with quantity * unit_price
    line_total    REAL GENERATED ALWAYS AS (quantity * unit_price) VIRTUAL,

    FOREIGN KEY (order_id)
        REFERENCES Orders(order_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    -- products that appear in past orders cannot be deleted,
    -- which protects sales history
    FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------
-- Inventory: audit log of every stock movement
-- ---------------------------------------------------------------------
CREATE TABLE Inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id   TEXT NOT NULL,
    location     TEXT,
    adjustment   INTEGER NOT NULL,                -- +in / -out
    reason       TEXT,
    adjusted_by  TEXT,
    adjusted_at  TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Indexes on the foreign-key columns used in JOINs
-- ---------------------------------------------------------------------
CREATE INDEX idx_orderitems_order   ON OrderItems(order_id);
CREATE INDEX idx_orderitems_product ON OrderItems(product_id);

-- ---------------------------------------------------------------------
-- Trigger 1: when an item is ordered, reduce stock and log the movement
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_orderitems_after_insert
AFTER INSERT ON OrderItems
BEGIN
    UPDATE Products
    SET stock_qty = stock_qty - NEW.quantity
    WHERE product_id = NEW.product_id;

    INSERT INTO Inventory (product_id, location, adjustment, reason, adjusted_by)
    VALUES (NEW.product_id, 'Online Store', -NEW.quantity,
            'Order ' || NEW.order_id, 'system');
END;

-- ---------------------------------------------------------------------
-- Trigger 2: when an order is cancelled, put the stock back and log it
-- ---------------------------------------------------------------------
CREATE TRIGGER trg_order_cancel_restore_stock
AFTER UPDATE OF status ON Orders
WHEN NEW.status = 'Cancelled' AND OLD.status <> 'Cancelled'
BEGIN
    UPDATE Products
    SET stock_qty = stock_qty + (
        SELECT COALESCE(SUM(quantity), 0)
        FROM OrderItems oi
        WHERE oi.order_id = NEW.order_id
          AND oi.product_id = Products.product_id
    )
    WHERE product_id IN (
        SELECT product_id FROM OrderItems WHERE order_id = NEW.order_id
    );

    INSERT INTO Inventory (product_id, location, adjustment, reason, adjusted_by)
    SELECT oi.product_id, 'Online Store', oi.quantity,
           'Order ' || NEW.order_id || ' cancelled', 'system'
    FROM OrderItems oi
    WHERE oi.order_id = NEW.order_id;
END;

-- ---------------------------------------------------------------------
-- View 1: one summary row per customer
-- ---------------------------------------------------------------------
CREATE VIEW vw_customer_order_summary AS
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(DISTINCT o.order_id)         AS total_orders,
    COALESCE(SUM(o.total_amount), 0)   AS total_spent,
    MAX(o.order_date)                  AS last_order_date
FROM Customers c
LEFT JOIN Orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id;

-- ---------------------------------------------------------------------
-- View 2: best-selling products by quantity, with revenue
-- ---------------------------------------------------------------------
CREATE VIEW vw_top_selling_products AS
SELECT
    p.product_id,
    p.name,
    SUM(oi.quantity)                 AS total_quantity_sold,
    SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM Products p
JOIN OrderItems oi ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_quantity_sold DESC;
