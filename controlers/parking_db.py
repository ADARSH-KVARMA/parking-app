import sqlite3

def create_tables():
    conn = sqlite3.connect('instance/parking.db')
    c = conn.cursor()

    # 1. Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            address TEXT,
            pin_code TEXT,
            car_number TEXT
        )
    ''')

    # 2. Admin Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT
        )
    ''')

    # 3. Parking Lot Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS parking_lot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prime_location_name TEXT,
            price_per_hour INTEGER,
            address TEXT,
            pin_code TEXT,
            max_spots INTEGER
        )
    ''')

    # 4. Parking Spot Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS parking_spot(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER,
            status TEXT CHECK(status IN ('O', 'A')) DEFAULT 'A',
            FOREIGN KEY (lot_id) REFERENCES parking_lot(id)
        )
    ''')

    # 5. Reserve Parking Spot Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reserve_spot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER,
            user_id INTEGER,
            parking_time TIMESTAMP,
            leaving_time TIMESTAMP,
            cost_per_hour REAL,
            FOREIGN KEY (spot_id) REFERENCES parking_spot(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 6. Admin - Parking Lot Mapping Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_email TEXT,
            parking_lot_id INTEGER,
            FOREIGN KEY (admin_email) REFERENCES admin(email),
            FOREIGN KEY (parking_lot_id) REFERENCES parking_lot(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("All tables created successfully.")


def add_admin(email, password, full_name):
    conn = sqlite3.connect('instance/parking.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO admin (email, password, full_name)
            VALUES (?, ?, ?)
        ''', (email, password, full_name))
        conn.commit()
        print("Admin added successfully.")
    except sqlite3.IntegrityError:
        print("Error: Admin with this email already exists.")
    finally:
        conn.close()

create_tables()
add_admin(email="admin2@example.com", password="123", full_name="The Adarsh")
