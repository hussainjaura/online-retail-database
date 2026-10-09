# this file contains reusable database functions that can be shared across the gui:
# the database connection is passed in from main.py so we avoid opening multiple connections:

def register_functions(conn):
    # create a cursor from the connection provided by the gui:
    cur = conn.cursor()

    # this function calculates the total value of an order:
    # it multiplies quantity by unit price for each item in the order:
    def fn_order_total(order_id):
        # run a query to sum all order item values for the given order id:
        cur.execute("""
            SELECT COALESCE(SUM(quantity * unit_price), 0)
            FROM OrderItems
            WHERE order_id = ?
        """, (order_id,))
        
        # fetch the result returned by the database:
        row = cur.fetchone()
        
        # return the total amount or 0 if no rows were found:
        return row[0] if row else 0

    # this function calculates the current stock level of a product:
    # it combines base stock with any inventory adjustments:
    def fn_stock_level(product_id):
        # simple print used while testing to confirm function calls:
        print("for debugging: fn_stock_level called with:", product_id)
        
        # query base stock and add any inventory adjustments:
        cur.execute("""
            SELECT
                p.stock_qty + COALESCE((
                    SELECT SUM(adjustment)
                    FROM Inventory
                    WHERE product_id = p.product_id
                ), 0)
            FROM Products p
            WHERE p.product_id = ?
        """, (product_id,))
        
        # fetch the calculated stock value:
        row = cur.fetchone()
        
        # return the stock level or 0 if the product does not exist:
        return row[0] if row else 0

    # register both python functions so sqlite can call them inside sql queries:
    # these functions are now reusable across reports and views:
    conn.create_function("fn_order_total", 1, fn_order_total)
    conn.create_function("fn_stock_level", 1, fn_stock_level)
