# import tkinter for building the customer management window:
import tkinter as tk
# import messagebox for showing error and success messages:
from tkinter import messagebox
# import ttk for displaying customer data in a table:
from tkinter import ttk

# import encryption and decryption helpers from utils file:
from utils import decrypt_string, encrypt_string


# this function opens the customer management window:
# it receives the main window, database connection, and cursor:
def open_customer_window(root, conn, cur):
    # create a new top-level window for customer management:
    customer_win = tk.Toplevel(root)
    customer_win.title("Customer Management")
    customer_win.geometry("900x600")
    customer_win.configure(bg="#ffffff")

    # heading label displayed at the top of the window:
    tk.Label(
        customer_win,
        text="Customer Management",
        font=("Arial", 18, "bold"),
        bg="#ffffff"
    ).pack(pady=10)

    # frame used to hold all input fields:
    form_frame = tk.Frame(customer_win, bg="#ffffff")
    form_frame.pack(pady=10)

    # customer id input field:
    tk.Label(form_frame, text="Customer ID:", bg="#ffffff").grid(row=0, column=0, pady=5)
    entry_cid = tk.Entry(form_frame, width=30)
    entry_cid.grid(row=0, column=1, pady=5)

    # first name input field:
    tk.Label(form_frame, text="First Name:", bg="#ffffff").grid(row=1, column=0, pady=5)
    entry_fname = tk.Entry(form_frame, width=30)
    entry_fname.grid(row=1, column=1, pady=5)

    # last name input field:
    tk.Label(form_frame, text="Last Name:", bg="#ffffff").grid(row=2, column=0, pady=5)
    entry_lname = tk.Entry(form_frame, width=30)
    entry_lname.grid(row=2, column=1, pady=5)

    # email input field:
    tk.Label(form_frame, text="Email:", bg="#ffffff").grid(row=3, column=0, pady=5)
    entry_email = tk.Entry(form_frame, width=30)
    entry_email.grid(row=3, column=1, pady=5)

    # this function reloads the customer table from the database:
    def refresh_table():
        # clear existing rows from the table:
        for row in table.get_children():
            table.delete(row)

        # fetch all customer records from the database:
        cur.execute("""
            SELECT customer_id, first_name, last_name, email
            FROM Customers
        """)

        # decrypt email before displaying it in the table:
        for row in cur.fetchall():
            decrypted_email = decrypt_string(row[3]) if row[3] else ""
            table.insert("", "end", values=(row[0], row[1], row[2], decrypted_email))

    # this function adds a new customer to the database:
    def add_customer():
        cid = entry_cid.get().strip()
        fname = entry_fname.get().strip()
        lname = entry_lname.get().strip()
        email = entry_email.get().strip()

        # basic validation to ensure all fields are filled:
        if not cid or not fname or not lname or not email:
            messagebox.showerror("Error", "All fields are required.")
            return

        # simple check to ensure email format looks valid:
        if "@" not in email:
            messagebox.showerror("Error", "Invalid email format.")
            return

        # encrypt email before storing it in the database:
        encrypted_email = encrypt_string(email)

        try:
            # insert the new customer record into the database:
            cur.execute("""
                INSERT INTO Customers (customer_id, first_name, last_name, email)
                VALUES (?, ?, ?, ?)
            """, (cid, fname, lname, encrypted_email))
            conn.commit()
            messagebox.showinfo("Success", "Customer added successfully.")
            refresh_table()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # this function updates an existing customer's email:
    def update_customer():
        cid = entry_cid.get().strip()
        email = entry_email.get().strip()

        # ensure customer id is provided before updating:
        if not cid:
            messagebox.showerror("Error", "Customer ID is required.")
            return

        # encrypt updated email before saving:
        encrypted_email = encrypt_string(email)

        cur.execute("""
            UPDATE Customers
            SET email = ?
            WHERE customer_id = ?
        """, (encrypted_email, cid))
        conn.commit()
        messagebox.showinfo("Success", "Customer updated.")
        refresh_table()

    # this function removes a customer from the database:
    def delete_customer():
        cid = entry_cid.get().strip()

        # ensure customer id is entered before deleting:
        if not cid:
            messagebox.showerror("Error", "Enter Customer ID to delete.")
            return

        cur.execute("DELETE FROM Customers WHERE customer_id = ?", (cid,))
        conn.commit()
        messagebox.showinfo("Deleted", "Customer was removed.")
        refresh_table()

    # frame that holds action buttons:
    btn_frame = tk.Frame(customer_win, bg="#ffffff")
    btn_frame.pack(pady=10)

    # buttons for customer actions:
    tk.Button(btn_frame, text="Add Customer", width=15, command=add_customer).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Update Email", width=15, command=update_customer).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Delete Customer", width=15, command=delete_customer).grid(row=0, column=2, padx=10)

    # table used to display customer records:
    table = ttk.Treeview(customer_win, columns=("cid", "fname", "lname", "email"), show="headings")
    table.pack(fill="both", expand=True, pady=20)

    # table column headings:
    table.heading("cid", text="Customer ID")
    table.heading("fname", text="First Name")
    table.heading("lname", text="Last Name")
    table.heading("email", text="Email (Decrypted)")

    # load customer data when the window opens:
    refresh_table()
