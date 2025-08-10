from parking_db import *

# print parking_lots
def check_data():
    conn = sqlite3.connect('instance\parking.db')
    c = conn.cursor()

    # Check if all tables exist
    tables = ['users', 'admin', 'parking_lot', 'admin_parking_lots']
    for table in tables:
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not c.fetchone():
            print(f"Table {table} does not exist.")
            return False

    # Check if users table has at least one user
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        print("No users found in the users table.")
        return False

    # Check if admin table has at least one admin
    c.execute('SELECT COUNT(*) FROM admin')
    if c.fetchone()[0] == 0:
        print("No admins found in the admin table.")
        return False

    # Check if parking_lot table has at least one parking lot
    c.execute('SELECT COUNT(*) FROM parking_lot')
    if c.fetchone()[0] == 0:
        print("No parking lots found in the parking_lot table.")
        return False

    # Check if admin_parking_lots table has valid entries
    c.execute('SELECT COUNT(*) FROM admin_parking_lots')
    if c.fetchone()[0] == 0:
        print("No entries found in the admin_parking_lots table.")
        return False

    print("All data checks passed successfully.")
    return True

# print total lots available
def total_lots_available():
    conn = sqlite3.connect('instance\parking.db')
    c = conn.cursor()
    c.execute('SELECT * FROM parking_lot')
    total_lots = c.fetchone()
    conn.close()
    print("Total parking lots available:", total_lots)
    return total_lots

total_lots_available()

# print parking spots available
def parking_spots_available():
    conn = sqlite3.connect('instance\parking.db')
    c = conn.cursor()
    c.execute('SELECT * FROM parking_spot')
    available_spots = c.fetchone()
    conn.close()
    print("Available parking spots:", available_spots)
    return available_spots

parking_spots_available()