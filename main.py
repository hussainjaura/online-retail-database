# import tkinter to create the main gui window:
import tkinter as tk

# import the shared database connection and cursor:
from db import conn, cur
# import the customer window function:
from windows.customer import open_customer_window
# import the product window function:
from windows.product import open_product_window
# import the reports window function:
from windows.reports import open_reports_window


# create the main tkinter window:
root = tk.Tk()
# set the window title shown at the top:
root.title("Online Retail Store")
# set the window size:
root.geometry("900x600")
# set the background colour of the main window:
root.configure(bg="#f1f1f1")

# main title label displayed at the top of the gui:
title_label = tk.Label(
    root,
    text="Online Retail Store",
    font=("Arial", 20, "bold"),
    bg="#f1f1f1"
)
title_label.pack(pady=20)

# short message confirming the gui loaded successfully:
placeholder = tk.Label(
    root,
    text="Welcome to our Online Retail Store. Feel free to have a look around!",
    font=("Arial", 14),
    bg="#f1f1f1"
)
placeholder.pack(pady=10)


# button used to open the product management window:
btn_product = tk.Button(
    root,
    text="Manage Products",
    font=("Arial", 14),
    width=20,
    command=lambda: open_product_window(root, conn, cur)
)
btn_product.pack(pady=10)

# button used to open the customer management window:
btn_customer = tk.Button(
    root,
    text="Manage Customers",
    font=("Arial", 14),
    width=20,
    command=lambda: open_customer_window(root, conn, cur)
)
btn_customer.pack(pady=10)

# button used to open the reports window:
btn_reports = tk.Button(
    root,
    text="Reports",
    font=("Arial", 14),
    width=20,
    command=lambda: open_reports_window(root, cur)
)
btn_reports.pack(pady=10)

# button used to close the application:
btn_exit = tk.Button(
    root,
    text="Exit",
    font=("Arial", 14),
    width=20,
    command=root.quit,
    fg="red"
)
btn_exit.pack(pady=10)

# start the tkinter event loop:
root.mainloop()
