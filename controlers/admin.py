from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from controlers.control import *
from flask import jsonify

admin_bp = Blueprint(
    "admin",
    __name__,
    template_folder="../templates/admin",
    url_prefix="/admin",
)

@admin_bp.before_request
def require_admin():
    if 'email' not in session or not is_admin(session['email']):
        flash("😞😞 You need to Login as Admin 😞😞", "error")
        return redirect(url_for('login'))

@admin_bp.route("/dashboard")
def admin_dashboard():
    email = session['email']
    parking_lots = get_admin_dashboard_data(email)

    spots = []  # spot contains the list of parking spots for each lot
    for lot in parking_lots:
        spots.append(get_spots_from_lot(lot[0]))

    return render_template('admin/dashboard.html', parking_lots=parking_lots, spots=spots)

@admin_bp.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if request.method == 'POST':
        location_name = request.form['location_name']
        price_per_hour = float(request.form['price_per_hour'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        num_spots = int(request.form['num_spots'])

        # add new lot using control function add_parking_lot
        add_parking_lot(
            prime_location_name = location_name, 
            price_per_hour = price_per_hour, 
            address = address, 
            pin_code = pin_code, 
            max_spots = num_spots, 
            admin_email = session['email']
            )


        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_parking_lot.html')

@admin_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if request.method == 'POST':
        prime_location_name = request.form.get('prime_location_name')
        price_per_hour = request.form.get('price_per_hour')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        max_spots = request.form.get('max_spots')

        edit_parking_lot(
            lot_id=lot_id,
            prime_location_name=prime_location_name,
            price_per_hour=price_per_hour,
            address=address,
            pin_code=pin_code,
            max_spots=max_spots
        )
        
        return redirect(url_for('admin.admin_dashboard'))

    # Fetch the current details of the parking lot
    conn = sqlite3.connect('tmp/parking.db')
    c = conn.cursor()
    c.execute('SELECT * FROM parking_lot WHERE id = ?', (lot_id,))
    lot_details = c.fetchone()
    conn.close()
    return render_template('admin/edit_parking_lot.html', lot=lot_details)

@admin_bp.route('/delete/<int:lot_id>')
def delete(lot_id):
    flash(delete_parking_lot(lot_id=lot_id))
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/users')
def users():
    user_data = get_all_users()
    
    return render_template('/admin/users.html', user_data =user_data)

@admin_bp.route('/summary/<int:lot_id>')
def summary(lot_id):
    data = summary_lot(lot_id)
    return render_template('/admin/summary.html', parking_lot_data = data)

@admin_bp.route('/spot_info/<int:spotID>')
def spot_info(spotID):
    spot_data = get_parked_spot_info(spotID)
    user_parked_data = get_user_from_id(user_id=spot_data[2])
    

    return jsonify(
        {
            "name": user_parked_data[3],
            "vehicle": user_parked_data[6],
            "contact": user_parked_data[4],
            "time_in": spot_data[3]
        }
    )

@admin_bp.route('/edit', methods=['GET', 'POST'])
def edit_admin():
    if request.method == 'POST':
        new_details = {
            'name': request.form['name'],
            'email': request.form['email'],
            'contact': request.form['contact']
        }
        edit_admin_details(session['email'], new_details)
        flash("Admin details updated successfully!")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/edit_admin.html')

@admin_bp.route('/user_summary')
def user_summary():
    user_summary = get_all_user_summary()
    if user_summary:
        return render_template('/admin/all_user_summary.html', user_summary=user_summary)
