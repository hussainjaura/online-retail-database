# import tkinter for building the product management window:
import tkinter as tk
# import filedialog for selecting image files and messagebox for alerts:
from tkinter import filedialog, messagebox
# import ttk for displaying product data in a table:
from tkinter import ttk
# import elementtree for handling xml validation and parsing:
import xml.etree.ElementTree as ET
# import pillow for displaying image on the frontend:
from PIL import Image, ImageTk
import io


# import helper function used to convert images into binary format:
from utils import load_image_as_blob


# this function opens the product management window:
# it receives the main window, database connection, and cursor:
def open_product_window(root, conn, cur):
    # create a new top-level window for managing products:
    product_win = tk.Toplevel(root)
    product_win.title("Product Management")
    product_win.geometry("900x600")
    product_win.configure(bg="#ffffff")

    # heading label displayed at the top of the window:
    tk.Label(
        product_win,
        text="Product Management",
        font=("Arial", 18, "bold"),
        bg="#ffffff"
    ).pack(pady=10)

    # frame used to hold all product input fields:
    form_frame = tk.Frame(product_win, bg="#ffffff")
    form_frame.pack(pady=10)

    # product id input field:
    tk.Label(form_frame, text="Product ID:", bg="#ffffff").grid(row=0, column=0, pady=5)
    entry_pid = tk.Entry(form_frame, width=30)
    entry_pid.grid(row=0, column=1, pady=5)

    # product name input field:
    tk.Label(form_frame, text="Name:", bg="#ffffff").grid(row=1, column=0, pady=5)
    entry_name = tk.Entry(form_frame, width=30)
    entry_name.grid(row=1, column=1, pady=5)

    # product category input field:
    tk.Label(form_frame, text="Category:", bg="#ffffff").grid(row=2, column=0, pady=5)
    entry_category = tk.Entry(form_frame, width=30)
    entry_category.grid(row=2, column=1, pady=5)

    # product price input field:
    tk.Label(form_frame, text="Price (£):", bg="#ffffff").grid(row=3, column=0, pady=5)
    entry_price = tk.Entry(form_frame, width=30)
    entry_price.grid(row=3, column=1, pady=5)

    # product stock quantity input field:
    tk.Label(form_frame, text="Stock Qty:", bg="#ffffff").grid(row=4, column=0, pady=5)
    entry_stock = tk.Entry(form_frame, width=30)
    entry_stock.grid(row=4, column=1, pady=5)

    # supplier id input field:
    tk.Label(form_frame, text="Supplier ID:", bg="#ffffff").grid(row=5, column=0, pady=5)
    entry_supplier = tk.Entry(form_frame, width=30)
    entry_supplier.grid(row=5, column=1, pady=5)

    # xml specification text area:
    tk.Label(form_frame, text="Product Spec (XML):", bg="#ffffff").grid(row=6, column=0, pady=5, sticky="n")
    xml_text = tk.Text(form_frame, width=40, height=6)
    xml_text.grid(row=6, column=1, pady=5)

    # refresh the product table using the latest database values:
    def refresh_table():
        # clear existing rows from the table:
        for row in table.get_children():
            table.delete(row)

        # fetch product records from the database:
        cur.execute("""
            SELECT product_id, name, category, price_gbp, stock_qty, supplier_id
            FROM Products
        """)

        # insert each product into the table:
        for row in cur.fetchall():
            table.insert("", "end", values=row)

    # variable used to store selected image as binary data:
    selected_image_blob = None

    # open file dialog to select an image for the product:
    def choose_image():
        nonlocal selected_image_blob
        filepath = filedialog.askopenfilename(
            title="Choose Product Image",
            filetypes=[("Image files", "*.jpg *.png *.jpeg *.gif *.bmp")]
        )
        if filepath:
            selected_image_blob = load_image_as_blob(filepath)
            messagebox.showinfo("Image Loaded", "Image selected successfully!")


        # display the stored product image from the database:
    def view_product_image():
        pid = entry_pid.get().strip()

        # Here I have ensured that the product id is provided:
        if not pid:
            messagebox.showerror("Error", "Enter Product ID first.")
            return

        # fetching image blob from the database:
        cur.execute(
            "SELECT image_blob FROM Products WHERE product_id = ?",
            (pid,)
        )
        row = cur.fetchone()

        # checking if an image exists for the product:
        if not row or not row[0]:
            messagebox.showinfo("Info", "No image found for this product.")
            return

        # converting binary data back into an image:
        image_data = row[0]
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((300, 300))

        # created a new window to display the image:
        img_win = tk.Toplevel(product_win)
        img_win.title("Product Image")

        photo = ImageTk.PhotoImage(image)

        # kept it safe here so the image doesnt get mixed up:
        img_label = tk.Label(img_win, image=photo)
        img_label.image = photo
        img_label.pack(padx=10, pady=10)


    # add a new product into the database:
    def add_product():
        pid = entry_pid.get().strip()
        name = entry_name.get().strip()
        category = entry_category.get().strip()
        price = entry_price.get().strip()
        stock = entry_stock.get().strip()
        supplier = entry_supplier.get().strip()

        # build xml using relational values from the form:
        spec_xml = f"""
        <spec>
            <name>{name}</name>
            <category>{category}</category>
            <price>{price}</price>
            <stock>{stock}</stock>
            <supplier>{supplier}</supplier>
        </spec>
        """.strip()

        # basic validation to ensure required fields are filled:
        if not pid or not name or not price or not stock or not supplier:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        # ensure price value is numeric:
        if not price.replace(".", "", 1).isdigit():
            messagebox.showerror("Error", "Price must be numeric.")
            return

        # ensure stock value is a whole number:
        if not stock.isdigit():
            messagebox.showerror("Error", "Stock must be a whole number.")
            return

        try:
            # insert the new product record into the database:
            cur.execute("""
                INSERT INTO Products
                (product_id, name, category, price_gbp, stock_qty, supplier_id, image_blob, product_spec_xml)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (pid, name, category, float(price), int(stock), supplier, selected_image_blob, spec_xml))
            conn.commit()
            messagebox.showinfo("Success", "Product added successfully.")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # update an existing product record:
    def update_product():
        pid = entry_pid.get().strip()
        price = entry_price.get().strip()
        stock = entry_stock.get().strip()

        # ensure product id is provided before updating:
        if not pid:
            messagebox.showerror("Error", "Product ID is required.")
            return

        cur.execute("""
            UPDATE Products
            SET price_gbp = ?, stock_qty = ?
            WHERE product_id = ?
        """, (float(price), int(stock), pid))
        conn.commit()
        messagebox.showinfo("Success", "Product updated.")
        refresh_table()

    # delete a product from the database:
    def delete_product():
        pid = entry_pid.get().strip()
        if not pid:
            messagebox.showerror("Error", "Enter Product ID to delete.")
            return

        cur.execute("DELETE FROM Products WHERE product_id = ?", (pid,))
        conn.commit()
        messagebox.showinfo("Deleted", "Product removed.")
        refresh_table()

    # load xml specification for the selected product:
    def load_spec_for_product():
        pid = entry_pid.get().strip()
        if not pid:
            messagebox.showerror("Error", "Enter Product ID first.")
            return

        cur.execute("SELECT product_spec_xml FROM Products WHERE product_id = ?", (pid,))
        row = cur.fetchone()
        if row and row[0]:
            xml_text.delete("1.0", tk.END)
            xml_text.insert(tk.END, row[0])
        else:
            messagebox.showinfo("Info", "No XML found for this product.")

    # save updated xml specification back to the database:
    def save_spec_for_product():
        pid = entry_pid.get().strip()
        xml_string = xml_text.get("1.0", tk.END).strip()

        # ensure product id and xml content are provided:
        if not pid or not xml_string:
            messagebox.showerror("Error", "Product ID and XML are required.")
            return

        # validate that the xml is well formed before saving:
        try:
            ET.fromstring(xml_string)
        except Exception as e:
            messagebox.showerror("Invalid XML", str(e))
            return

        cur.execute("""
            UPDATE Products
            SET product_spec_xml = ?
            WHERE product_id = ?
        """, (xml_string, pid))
        conn.commit()
        messagebox.showinfo("Success", "XML specification saved.")

    # frame that holds product action buttons:
    btn_frame = tk.Frame(product_win, bg="#ffffff")
    btn_frame.pack(pady=10)

    # buttons for product actions:
    tk.Button(btn_frame, text="Add Product", width=15, command=add_product).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Update Product", width=15, command=update_product).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Delete Product", width=15, command=delete_product).grid(row=0, column=2, padx=10)
    tk.Button(form_frame, text="Choose Image", width=20, command=choose_image).grid(row=7, column=1, pady=5)
    tk.Button(btn_frame, text="Load XML Spec", width=15, command=load_spec_for_product).grid(row=1, column=0, padx=10)
    tk.Button(btn_frame, text="Save XML Spec", width=15, command=save_spec_for_product).grid(row=1, column=1, padx=10)
    tk.Button(btn_frame, text="View Product Image", width=18, command=view_product_image).grid(row=1, column=2, padx=10)


    # table used to display product records:
    table = ttk.Treeview(product_win, columns=("pid", "name", "cat", "price", "stock", "sup"), show="headings")
    table.pack(fill="both", expand=True, pady=20)

    # table column headings:
    table.heading("pid", text="Product ID")
    table.heading("name", text="Name")
    table.heading("cat", text="Category")
    table.heading("price", text="Price (£)")
    table.heading("stock", text="Stock")
    table.heading("sup", text="Supplier ID")

    # load product data when the window opens:
    refresh_table()
