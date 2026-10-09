-- =====================================================================
-- Online Retail Store: sample data
-- Customers and Products come from the original flat file
-- (data/flat_file_online_store.xlsx). Orders are sample data so the
-- reports, views and triggers have something to show.
-- =====================================================================
PRAGMA foreign_keys = ON;

-- Suppliers ------------------------------------------------------------
INSERT INTO Suppliers (supplier_id, name, contact_name, phone, email, address) VALUES
  ('S2001', 'Stride Supplies Ltd',   'Helen Park', '01234 567890', 'helen@stride.co.uk',     '1 Supply Way, London'),
  ('S2002', 'Urban Apparel Inc',     'Mark Lewis', '01111 222333', 'mark@urbanapparel.com',  '5 Fashion St, Manchester'),
  ('S2003', 'SoundWave Electronics', 'Aisha Khan', '0222 333444',  'aisha@soundwave.com',    '9 Tech Park, Cambridge'),
  ('S2004', 'Harbor Goods',          'Tom Reed',   '0333 444555',  'tom@harborgoods.co.uk',  '12 Dockside, Liverpool'),
  ('S2005', 'Bright Homewares',      'Lucia Grey', '0444 555666',  'lucia@brighthome.co.uk', '7 Home Ln, Bristol');

-- Products (from flat file) -------------------------------------------
INSERT INTO Products (product_id, name, category, price_gbp, stock_qty, supplier_id, product_spec_xml) VALUES
  ('P1001', 'AeroFit Running Shoes', 'Footwear', 79.99, 120, 'S2001', '<spec><brand>AeroFit</brand><size_range>6-12</size_range><material>Mesh</material></spec>'),
  ('P1002', 'Nimbus Hoodie', 'Apparel', 49.5, 200, 'S2002', '<spec><brand>Nimbus</brand><sizes>S,M,L,XL</sizes><material>Cotton Blend</material></spec>'),
  ('P1003', 'Orbit Wireless Earbuds', 'Electronics', 129, 75, 'S2003', '<spec><brand>Orbit</brand><battery>24h</battery><connectivity>Bluetooth 5.2</connectivity></spec>'),
  ('P1004', 'Harbor Laptop Sleeve 13"', 'Accessories', 19.99, 150, 'S2004', '<spec><brand>Harbor</brand><fits>13-inch</fits><material>Neoprene</material></spec>'),
  ('P1005', 'Terra Backpack', 'Bags', 89, 60, 'S2002', '<spec><brand>Terra</brand><volume>25L</volume><water_resistant>true</water_resistant></spec>'),
  ('P1006', 'Lumina Desk Lamp', 'Home', 34.25, 85, 'S2005', '<spec><brand>Lumina</brand><lumens>800</lumens><adjustable>true</adjustable></spec>'),
  ('P1007', 'SkyTrail Hiking Boots', 'Footwear', 110, 95, 'S2001', '<spec><brand>SkyTrail</brand><size_range>7-13</size_range><material>Leather</material><waterproof>true</waterproof></spec>'),
  ('P1008', 'BreezeFlex T-Shirt', 'Apparel', 22.5, 320, 'S2002', '<spec><brand>BreezeFlex</brand><sizes>S,M,L,XL,XXL</sizes><material>Polyester</material></spec>'),
  ('P1009', 'PulseFit Smartwatch', 'Electronics', 199.99, 50, 'S2003', '<spec><brand>PulseFit</brand><battery>48h</battery><connectivity>Bluetooth 5.3</connectivity><water_resistant>5ATM</water_resistant></spec>');

-- Customers (from flat file) ------------------------------------------
-- Emails are stored reversed because the app reverses them on write and
-- on read (utils.encrypt_string / decrypt_string), so they display correctly.
INSERT INTO Customers (customer_id, first_name, last_name, email, phone, address, city, country, registration_date) VALUES
  ('C3001', 'Alice', 'Johnson', 'moc.elpmaxe@nosnhoj.ecila', '441234567890', '12 Green St', 'London', 'UK', '2024-01-12'),
  ('C3002', 'Mark', 'Hughes', 'moc.elpmaxe@sehguh.kram', '441987654321', '89 River Rd', 'Manchester', 'UK', '2024-01-18'),
  ('C3003', 'Sara', 'Lee', 'moc.elpmaxe@eel.aras', '353871234567', '45 Oak Ave', 'Dublin', 'Ireland', '2024-02-04'),
  ('C3004', 'James', 'Walker', 'moc.elpmaxe@reklaw.semaj', '447700900123', '7 King St', 'Birmingham', 'UK', '2024-02-16'),
  ('C3005', 'Emily', 'Brown', 'moc.elpmaxe@nworb.ylime', '447912345678', '22 Hilltop Dr', 'Leeds', 'UK', '2024-03-01'),
  ('C3006', 'Tom', 'Richards', 'moc.elpmaxe@sdrahcir.mot', '447811223344', '3 Lakeview Cres', 'Glasgow', 'UK', '2024-03-11'),
  ('C3007', 'Nina', 'Patel', 'moc.elpmaxe@letap.anin', '447900112233', '54 Meadow Ln', 'Bristol', 'UK', '2024-03-20'),
  ('C3008', 'David', 'Chen', 'moc.elpmaxe@nehc.divad', '447733998877', '101 Cherry Rd', 'Liverpool', 'UK', '2024-04-02'),
  ('C3009', 'Olivia', 'Adams', 'moc.elpmaxe@smada.aivilo', '447644556677', '8 Seaside Way', 'Brighton', 'UK', '2024-04-10');

-- Sample orders ---------------------------------------------------------
INSERT INTO Orders (order_id, customer_id, order_date, status, shipping_address) VALUES
  ('O4001', 'C3001', '2024-04-03 10:15:00', 'Delivered', '12 Green St, London'),
  ('O4002', 'C3002', '2024-04-11 14:02:00', 'Delivered', '89 River Rd, Manchester'),
  ('O4003', 'C3001', '2024-05-06 09:40:00', 'Shipped',   '12 Green St, London'),
  ('O4004', 'C3005', '2024-05-19 18:25:00', 'Pending',   '22 Hilltop Dr, Leeds'),
  ('O4005', 'C3007', '2024-06-02 11:11:00', 'Delivered', '54 Meadow Ln, Bristol'),
  ('O4006', 'C3002', '2024-06-21 16:45:00', 'Pending',   '89 River Rd, Manchester');

-- Each insert fires trg_orderitems_after_insert (stock goes down, Inventory row logged)
INSERT INTO OrderItems (order_id, product_id, quantity, unit_price) VALUES
  ('O4001', 'P1001', 1,  79.99),
  ('O4001', 'P1004', 2,  19.99),
  ('O4002', 'P1003', 1, 129.00),
  ('O4002', 'P1008', 3,  22.50),
  ('O4003', 'P1009', 1, 199.99),
  ('O4004', 'P1002', 2,  49.50),
  ('O4004', 'P1006', 1,  34.25),
  ('O4005', 'P1007', 1, 110.00),
  ('O4005', 'P1005', 1,  89.00),
  ('O4006', 'P1001', 2,  79.99);

-- Keep the stored order total in step with its lines
UPDATE Orders
SET total_amount = (SELECT COALESCE(SUM(line_total), 0)
                    FROM OrderItems oi WHERE oi.order_id = Orders.order_id);

-- Cancelling an order fires trg_order_cancel_restore_stock (stock goes back up)
UPDATE Orders SET status = 'Cancelled' WHERE order_id = 'O4006';
