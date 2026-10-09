# import sqlite so the app can connect to the database:
import sqlite3
# import messagebox to show database error messages in the gui:
from tkinter import messagebox

# import the function that registers reusable sqlite functions:
from function import register_functions


# this function connects the application to the sqlite database:
# it returns the connection if successful or none if it fails:
def connect_db():
    # try to open a connection to the database file:
    try:
        return sqlite3.connect("database/online_retail.db")
    # if something goes wrong show an error message:
    except Exception as e:
        messagebox.showerror(
            "database error",
            f"there was a problem connecting to the database: {e}"
        )
        return None


# create a shared database connection for the whole application:
conn = connect_db()
# create a cursor only if the connection was successful:
cur = conn.cursor() if conn else None
# register custom sqlite functions so they can be used in sql queries:
if conn:
    register_functions(conn)
