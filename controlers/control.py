# Here we will define the control functions for the application
# for example add parking lot, add admin, etc.

import sqlite3
from datetime import datetime

db_path = 'instance/parking.db'

def get_user(email):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()

    #if user is None, check admin table
    if user is None:
        c.execute('SELECT * FROM admin WHERE email = ?', (email,))
        user = c.fetchone()

    conn.close()
    return user

#function to check is email is in admin table
def is_admin(email):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM admin WHERE email = ?', (email,))
    admin = c.fetchone()
    conn.close()
    return admin is not None

def is_user(email):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user is not None

# Get Parking lot of Admin form email
def get_all_lots(email):

    # funtionc to get id of all parking lots form admin_parking_lots table with email id
    def get_parking_lots_ids(email):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT parking_lot_id FROM admin_parking_lots WHERE admin_email = ?', (email,))
        parking_lots = c.fetchall()
        conn.close()
        return parking_lots

    # function to get parking lots from id
    def get_parking_lots(id):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM parking_lot WHERE id = ?', (id,))
        parking_lots = c.fetchall()
        conn.close()
        return parking_lots
    
    list_lots_ids = get_parking_lots_ids(email)
    print(list_lots_ids)

    parking_lots = []
    for id in list_lots_ids:
        parking_lots.append(get_parking_lots(id[0]))
    
    return parking_lots





# ///// Change Database //////
def add_user(email, password, full_name=None, address=None, pin_code=None, car_number=None):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (email, password, full_name, address, pin_code, car_number)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, password, full_name, address, pin_code, car_number))
        conn.commit()
        print("User added successfully.")
    except sqlite3.IntegrityError:
        print("Error: User with this email already exists.")
    finally:
        conn.close()

def add_admin(email, password, full_name):
    conn = sqlite3.connect(db_path)
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

def add_parking_spot(lot_id: int, status='A'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO parking_spot (lot_id, status)
        VALUES (?, ?)
    ''', (lot_id, status))
    conn.commit()
    conn.close()

def delete_parking_spot(lot_id: int, db_path=db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute delete query
    cursor.execute("DELETE FROM parking_spot WHERE lot_id = ?", (lot_id,))
    conn.commit()

    # Check if any row was actually deleted
    if cursor.rowcount == 0:
        print(f"No parking spot found with ID {lot_id}.")
        return False

    return True

def reserve_parking_spot(lot_id, user_id, parking_time, cost_per_hour, db_path=db_path):
    ''' Reserve a parking spot for a user and update the status of the parking spot '''

    # get next available parking spot from the lot_id
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT id FROM parking_spot
        WHERE lot_id = ? AND status = 'A'
        LIMIT 1
    ''', (lot_id,))
    spot = c.fetchone()
    conn.close()

    if not spot:
        print("No available parking spots.")
        return

    spot_id = spot[0]

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO reserve_spot (spot_id, user_id, parking_time, cost_per_hour)
            VALUES (?, ?, ?, ?)
        ''', (spot_id, user_id, parking_time, cost_per_hour))
        
        # Update the status of the parking spot to 'R' (Reserved)
        c.execute('''
            UPDATE parking_spot
            SET status = 'O'
            WHERE id = ?
        ''', (spot_id,))
        
        conn.commit()
        print("Parking spot reserved successfully.")
    except sqlite3.IntegrityError:
        print("Error: Spot already reserved or invalid data.")
    finally:
        conn.close()

def unpark_vehicle(lot_id, user_id, leaving_time, db_path=db_path):
    ''' Unpark a vehicle and update the parking spot status '''
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        # Get the reserved spot for the user in the specified lot
        c.execute('''
            SELECT spot_id FROM reserve_spot
            WHERE user_id = ? AND spot_id IN (
                SELECT id FROM parking_spot WHERE lot_id = ?
            ) AND leaving_time IS NULL
        ''', (user_id, lot_id))

        reserved_spot = c.fetchone()
        if reserved_spot:
            spot_id = reserved_spot[0]
            c.execute('''
                UPDATE parking_spot
                SET status = 'A'
                WHERE id = ?
            ''', (spot_id,))
            c.execute('''
                UPDATE reserve_spot
                SET leaving_time = ?
                WHERE spot_id = ?
            ''', (leaving_time, spot_id))
            conn.commit()
            return ("Vehicle unparked successfully.", "success")
        else:
            return ("No reserved spot found.","error")
    except Exception as e:
        return f"Error: {e}"
    finally:
        conn.close()

def add_parking_lot(prime_location_name, price_per_hour, address, pin_code, max_spots, admin_email):
    ''' Add a parking lot and associate it with an admin, also create parking spots if max_spots is provided '''

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO parking_lot (prime_location_name, price_per_hour, address, pin_code, max_spots)
            VALUES (?, ?, ?, ?, ?)
        ''', (prime_location_name, price_per_hour, address, pin_code, max_spots))
        
        lot_id = c.lastrowid  # Get the last inserted row ID
        c.execute('''
            INSERT INTO admin_parking_lots (admin_email, parking_lot_id)
            VALUES (?, ?)
        ''', (admin_email, lot_id)) 
        
        if max_spots is not None:
            for _ in range(max_spots):
                c.execute('''
                    INSERT INTO parking_spot (lot_id, status)
                    VALUES (?, 'A')
                ''', (lot_id,))

        conn.commit()
        print("Parking lot added successfully.")
        return lot_id
    except sqlite3.IntegrityError:
        print("Error: Parking lot with this name already exists or admin does not exist.")
    finally:
        conn.close()

def edit_parking_lot(lot_id : int, prime_location_name: str =None , price_per_hour: int =None, address: str =None, pin_code: str =None, max_spots: int =None):
    ''' Edit details of a parking lot with the given lot_id and new details ''' 

    conn = sqlite3.connect(db_path)
    print(f"going to update the parking lot : {lot_id}")
    c = conn.cursor()
    try:
        if prime_location_name:
            c.execute('''
                UPDATE parking_lot
                SET prime_location_name = ?
                WHERE id = ?
            ''', (prime_location_name, lot_id))
            print("prime location updated")
        
        if price_per_hour is not None:
            c.execute('''
                UPDATE parking_lot
                SET price_per_hour = ?
                WHERE id = ?
            ''', (price_per_hour, lot_id))
        
        if address:
            c.execute('''
                UPDATE parking_lot
                SET address = ?
                WHERE id = ?
            ''', (address, lot_id))
        
        if pin_code:
            c.execute('''
                UPDATE parking_lot
                SET pin_code = ?
                WHERE id = ?
            ''', (pin_code, lot_id))
        
        if max_spots is not None:
            if not is_lot_occupied(lot_id=lot_id):
                c.execute('''
                    UPDATE parking_lot
                    SET max_spots = ?
                    WHERE id = ?
                ''', (max_spots, lot_id))
                
            else:
                print("Canot change max spot")
                pass
                
        conn.commit()
            
        if max_spots and not is_lot_occupied(lot_id=lot_id):
            delete_parking_spot(lot_id=lot_id)
            for _ in range(int(max_spots)):
                add_parking_spot(lot_id=lot_id)
            
            

        
        print("Parking lot details updated successfully.")
    except sqlite3.Error as e:
        print("Error updating parking lot:", e)
    finally:
        conn.close() 

def delete_parking_lot(lot_id : int):
    if is_lot_occupied(lot_id=lot_id):
        return "Lot is courrently occupied! Cannot delete Lot"
    else:
        delete_parking_spot(lot_id=lot_id)
        conn = sqlite3.connect("instance/parking.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM parking_lot WHERE id = ?", (lot_id,))
        conn.commit()
    
        return "lot deleted succesfully"
    
def edit_admin_details(admin_id, new_details):
    ''' Edit the details of an admin with the given admin_id and new details '''
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        if 'email' in new_details:
            c.execute('''
                UPDATE admin
                SET email = ?
                WHERE id = ?
            ''', (new_details['email'], admin_id))
        
        if 'password' in new_details:
            c.execute('''
                UPDATE admin
                SET password = ?
                WHERE id = ?
            ''', (new_details['password'], admin_id))
        
        if 'full_name' in new_details:
            c.execute('''
                UPDATE admin
                SET full_name = ?
                WHERE id = ?
            ''', (new_details['full_name'], admin_id))
        
        conn.commit()
        print("Admin details updated successfully.")
    except sqlite3.Error as e:
        print("Error updating admin details:", e)
    finally:
        conn.close()

def edit_user_details(user_id, new_details):
    ''' Edit the details of a user with the given user_id and new details '''

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        if 'email' in new_details:
            print('Updating email...',user_id)
            print("new mail:",new_details['email'])
            c.execute('''
                UPDATE users
                SET email = ?
                WHERE id = ?
            ''', (new_details['email'], user_id))
        
        if 'password' in new_details:
            print('Upadating Pass..')
            c.execute('''
                UPDATE users
                SET password = ?
                WHERE id = ?
            ''', (new_details['password'], user_id))
        
        if 'full_name' in new_details:
            c.execute('''
                UPDATE users
                SET full_name = ?
                WHERE id = ?
            ''', (new_details['full_name'], user_id))
        
        if 'address' in new_details:
            c.execute('''
                UPDATE users
                SET address = ?
                WHERE id = ?
            ''', (new_details['address'], user_id))
        
        if 'pin_code' in new_details:
            c.execute('''
                UPDATE users
                SET pin_code = ?
                WHERE id = ?
            ''', (new_details['pin_code'], user_id))

        if 'car_number' in new_details:
            c.execute('''
                UPDATE users
                SET car_number = ?
                WHERE id = ?
            ''', (new_details['car_number'], user_id))
        
        conn.commit()
        print("User details updated successfully.")
    except sqlite3.Error as e:
        print("Error updating user details:", e)
    finally:
        conn.close()



# ///// Get Info from Database //////
def is_lot_occupied(lot_id, db_path=db_path):
    """
    Checks if any parking spot in the given lot_id is occupied.

    Parameters:
        lot_id (int): The ID of the parking lot to check.
        db_path (str): Path to the SQLite database file. Default is 'parking.db'.

    Returns:
        bool: True if any spot is occupied, False if all are available or none found.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute query to check if any spot is occupied
        cursor.execute("""
            SELECT 1 FROM parking_spot
            WHERE lot_id = ? AND status = 'O'
            LIMIT 1;
        """, (lot_id,))
        
        result = cursor.fetchone()
        return result is not None

    except sqlite3.Error as e:
        print("Database error:", e)
        return False

    finally:
        if conn:
            conn.close()

def get_admin_dashboard_data(admin_email):
    ''' Get all parking lots associated with the admin and their details '''

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('''
            SELECT pl.id, pl.prime_location_name, pl.price_per_hour, pl.address, pl.pin_code, pl.max_spots,
                   SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) AS available_spots,
                   SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) AS reserved_spots
            FROM parking_lot pl
            LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
            JOIN admin_parking_lots apl ON pl.id = apl.parking_lot_id
            WHERE apl.admin_email = ?
            GROUP BY pl.id
        ''', (admin_email,))
        
        parking_lots = c.fetchall()

        
        return (parking_lots)
    except sqlite3.Error as e:
        print("Error fetching admin dashboard data:", e)
    finally:
        conn.close()

def get_spots_from_lot(lot_id):
    ''' Get all parking spots for a specific parking lot '''

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('''
            SELECT id, status FROM parking_spot WHERE lot_id = ?
        ''', (lot_id,))
        
        spots = c.fetchall()
        return spots
    except sqlite3.Error as e:
        print("Error fetching parking spots:", e)
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT full_name,email,address,pin_code,car_number FROM users')
    users = c.fetchall()
    conn.close()
    
    return users

def get_summary_for_admin(admin_email):
    lots = get_admin_dashboard_data(admin_email)

    return lots

def get_all_lots():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('''
            SELECT pl.id, pl.prime_location_name, pl.price_per_hour, pl.address, pl.pin_code, pl.max_spots,
                   SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) AS available_spots,
                   SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) AS reserved_spots
            FROM parking_lot pl
            LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
            JOIN admin_parking_lots apl ON pl.id = apl.parking_lot_id
            GROUP BY pl.id
        ''',)
        
        parking_lots = c.fetchall()

        
        return (parking_lots)
    except sqlite3.Error as e:
        print("Error fetching admin dashboard data:", e)
    finally:
        conn.close()

def get_user_id(email):
    ''' Get user ID from email '''
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    user_id = c.fetchone()
    conn.close()

    return user_id[0] if user_id else None

def get_parked_spot_info(spot_id):
    ''' Get parked spot information '''
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM reserve_spot WHERE spot_id = ? AND leaving_time IS NULL', (spot_id,))
    spot_info = c.fetchone()
    conn.close()
    return spot_info

def get_user_from_id(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def is_user_reserved_spot(email):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM reserve_spot rs
        JOIN users u ON rs.user_id = u.id
        WHERE u.email = ? AND rs.leaving_time IS NULL
    ''', (email,))
    
    result = c.fetchone()
    conn.close()
    
    return result if result is not None else False

def calculate_time_difference(start_datetime, end_datetime):
    start_datetime = str(start_datetime)
    start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S.%f")

    time_difference = end_datetime - start_datetime
    total_seconds = round(time_difference.total_seconds())

    seconds = total_seconds

    minutes_total = total_seconds // 60
    minutes = minutes_total

    hours_total = minutes_total // 60
    hours = hours_total

    days_total = hours_total // 24
    days = days_total
    
    weeks = days_total // 7

    return (weeks, days, hours, minutes, seconds)

def summary_lot(lot_id):
    ''' Get the summary data of parking lot in the format of a dictionary :
        {
        
            "id": <lot_id>,✅
            "name": <lot_name>,✅
            "total_spots": <total_spots>,✅
            "available_spots": <available_spots>,✅
            "reserved_spots": <reserved_spots>,✅
            "location": <location>,✅
            "price_per_hour": <price_per_hour>,✅
            "last_week_trafic": [list of cars parked in lask week],✅
            "currently_parked_users": [list of users id whos car is currently in parking lot],✅
            "Total_earning": {"last_week": ---, "last_month": ---, "last_year": ---}✅
        }
    '''
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
            SELECT * FROM parking_lot WHERE id = ?
        ''', (int(lot_id), ))   
    lot = c.fetchone()
   
    id = lot[0]
    name = lot[1]
    PPH  = lot[2]
    location =lot[3]
    total_spots = lot[5]

    c.execute('''SELECT SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) AS available_spots,
                   SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) AS reserved_spots
              FROM parking_spot ps
              WHERE lot_id = ?
        ''', (lot_id, )
    )
    available_spots, reserved_spots = c.fetchone()

    c.execute('''SELECT id, status FROM parking_spot WHERE lot_id=?
    ''', (lot_id, )
    )
    spots = c.fetchall()
    days = [0,0,0,0,0,0,0,0]
    Total_earning = {"last_week": 0, "last_month": 0, "last_year": 0}
    users = []
    for spot in spots:
        c.execute('''SELECT cost_per_hour, parking_time, leaving_time 
                    FROM reserve_spot 
                    WHERE spot_id=?''',
                 (spot[0],))
        
        spot_datails = c.fetchall()
        time_now = datetime.now()
        days_list = []
        
        for details in spot_datails:
            d = calculate_time_difference(details[1], time_now)
            if details[2] is not None and d[1] < 8:
                Total_earning["last_week"] += int(details[0])*d[2]
            if details[2] is not None and d[1] < 31:
                Total_earning["last_month"] += int(details[0])*d[2]
            if details[2] is not None and d[1] < 366:
                Total_earning["last_year"] += int(details[0])*d[2]

            days_list.append(d[1])

        
        if spot[1] == 'O':
            c.execute('''SELECT user_id
                    FROM reserve_spot 
                    WHERE spot_id=?''',
                 (spot[0],))
            
            user_id = c.fetchone()
            users.append(get_user_from_id(user_id[0])[3])

        for day in days_list:
            if day < 8:
                days[day] +=1

    last_week_trafic = days
    

    return {
            "id": id,
            "name": name,
            "total_spots": total_spots,
            "available_spots": available_spots,
            "reserved_spots": reserved_spots,
            "location": location,
            "price_per_hour": PPH,
            "last_week_trafic": last_week_trafic,
            "currently_parked_users": users, 
            "Total_earning": Total_earning
        }

def get_parking_lot_from_spot(spot_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT pl.* FROM parking_lot pl
        JOIN parking_spot ps ON pl.id = ps.lot_id
        WHERE ps.id = ?
    ''', (spot_id,))
    
    lot = c.fetchone()
    conn.close()
    
    return lot if lot else None

def get_user_summary(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT 
            users.id AS user_id,
            users.full_name,
            users.car_number,
            reserve_spot.spot_id,
            reserve_spot.parking_time,
            reserve_spot.leaving_time,
            reserve_spot.cost_per_hour
        FROM users
        JOIN reserve_spot ON users.id = reserve_spot.user_id
        WHERE users.id = ?;

    ''', (user_id,))

    usery_summary = c.fetchall()
    conn.close()

    return usery_summary if usery_summary else None

def get_all_user_summary():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        SELECT 
            users.id AS user_id,
            users.full_name,
            users.car_number,
            reserve_spot.spot_id,
            reserve_spot.parking_time,
            reserve_spot.leaving_time,
            reserve_spot.cost_per_hour
        FROM users
        JOIN reserve_spot ON users.id = reserve_spot.user_id
        ORDER BY reserve_spot.parking_time DESC;
    ''')

    users_summary = c.fetchall()
    conn.close()
    return users_summary if users_summary else None