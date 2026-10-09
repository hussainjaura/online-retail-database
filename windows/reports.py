# import tkinter for building the reports window interface:
import tkinter as tk
# import ttk for displaying report results in a table format:
from tkinter import ttk
# import elementtree for working with xml data stored in the database:
import xml.etree.ElementTree as ET


# this function opens the reports and views window:
# it receives the main window and database cursor:
def open_reports_window(root, cur):
    # create a new top-level window for reports:
    reports_win = tk.Toplevel(root)
    reports_win.title("Reports & Views")
    reports_win.geometry("900x600")
    reports_win.configure(bg="#ffffff")

    # heading shown at the top of the reports window:
    tk.Label(
        reports_win,
        text="Reports Window",
        font=("Arial", 18, "bold"),
        bg="#ffffff"
    ).pack(pady=10)

    # table used to display all report results:
    table = ttk.Treeview(reports_win, show="headings")
    table.pack(fill="both", expand=True, pady=20)

    # helper function to reset table columns and clear old data:
    def set_table_columns(columns):
        table.delete(*table.get_children())
        table["columns"] = columns
        for col in columns:
            table.heading(col, text=col)

    # report that calculates how much each customer has spent:
    def report_customer_spending():
        query = """
            SELECT 
                c.customer_id,
                c.first_name || ' ' || c.last_name AS customer_name,
                SUM(oi.quantity * oi.unit_price) AS total_spent
            FROM Customers c
            JOIN Orders o ON c.customer_id = o.customer_id
            JOIN OrderItems oi ON o.order_id = oi.order_id
            GROUP BY c.customer_id
            HAVING total_spent > 0
            ORDER BY total_spent DESC;
        """

        # set table headings for the customer spending report:
        set_table_columns(["Customer ID", "Name", "Total Spent (£)"])

        # execute the query and insert each result into the table:
        for row in cur.execute(query).fetchall():
            table.insert("", "end", values=row)

    # report that shows products with low stock levels:
    def report_low_stock():
        query = """
            SELECT 
                product_id,
                name,
                fn_stock_level(product_id) AS stock_level
            FROM Products
            WHERE fn_stock_level(product_id) < 20;
        """

        # set table headings for the low stock report:
        set_table_columns(["Product ID", "Name", "Stock Level"])

        # execute the query and insert results into the table:
        for row in cur.execute(query).fetchall():
            table.insert("", "end", values=row)

    # report that displays xml specifications stored for products:
    def report_xml_specs():
        query = """
            SELECT product_id, name, product_spec_xml
            FROM Products
            WHERE product_spec_xml IS NOT NULL;
        """

        # set table headings for the xml specification report:
        set_table_columns(["Product ID", "Name", "XML Spec"])

        # fetch and display xml data from the database:
        for row in cur.execute(query).fetchall():
            table.insert("", "end", values=row)

    # frame that holds the report action buttons:
    btn_frame = tk.Frame(reports_win, bg="#ffffff")
    btn_frame.pack(pady=10)

    # button to run the customer spending report:
    tk.Button(
        btn_frame,
        text="Customer Spending Report",
        width=25,
        command=report_customer_spending
    ).grid(row=0, column=0, padx=10)

    # button to run the low stock report:
    tk.Button(
        btn_frame,
        text="Low Stock Report",
        width=20,
        command=report_low_stock
    ).grid(row=0, column=1, padx=10)

    # button to show xml specifications stored for products:
    tk.Button(
        btn_frame,
        text="Show XML Product Specs",
        width=25,
        command=report_xml_specs
    ).grid(row=0, column=2, padx=10)


# this function prints xml product data to the console for testing purposes:
def show_product_specs_report(cur):
    # fetch product id, name, and xml specification from the database:
    cur.execute("SELECT product_id, name, product_spec_xml FROM Products")
    rows = cur.fetchall()

    # loop through each product and extract data from the xml:
    for pid, name, spec_xml in rows:
        try:
            root = ET.fromstring(spec_xml)
            price_tag = root.find("price")
            xml_price = price_tag.text if price_tag is not None else "N/A"
        except Exception:
            xml_price = "N/A"

        # print extracted xml data to the console:
        print(f"{pid} - {name} | XML price: {xml_price}")
