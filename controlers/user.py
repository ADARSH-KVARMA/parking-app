from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from controlers.control import *
import time
from datetime import datetime


user_bp = Blueprint(
    "user",
    __name__,
    template_folder="../templates/user",
    url_prefix="/user",
)

@user_bp.before_request
def requre_user():
    if 'email' not in session or not is_user(session['email']):
        flash("😞😞 You need to Login as user 😞😞", "error")
        return redirect(url_for('login'))
    
@user_bp.route("/dashboard")
def user_dashboard():
    parking_lots = get_all_lots()
    spots = []  # spot contains the list of parking spots for each lot
    for lot in parking_lots:
        spots.append(get_spots_from_lot(lot[0]))

    return render_template('/user/dashboard.html', parking_lots=parking_lots, spots=spots)

@user_bp.route('/park', methods = ['GET', 'POST'])
def park():

    if request.method == 'GET':
        lot_id = request.args.get('lot_id')
        email = session['email']
        user_id = get_user_id(email)
        CPH  = request.args.get('cost_PH')
        current_time  = datetime.now() 

        # Check if the user has already reserved a parking spot
        if is_user_reserved_spot(email):
            flash("You have already reserved a parking spot. Please unpark before reserving another.", "error")
            return redirect(url_for('user.user_dashboard'))
        
        reserve_parking_spot(lot_id=lot_id, user_id=user_id, parking_time=current_time, cost_per_hour=float(CPH))


        return redirect(url_for('user.user_dashboard'))

@user_bp.route('/unpark', methods = ['GET', 'post'])
def unpark():
    if request.method == 'GET':
        lot_id = request.args.get('lot_id')
        email = session['email']
        user_id = get_user_id(email)
        leaving_time = datetime.now() 

        # Call the function to unpark the vehicle

        flass_message, _flash_type = unpark_vehicle(lot_id=lot_id, user_id=user_id, leaving_time=leaving_time)
        flash(flass_message, _flash_type)
        
        return redirect(url_for('user.user_dashboard'))
    
@user_bp.route('/parking')
def parking():
    email = session['email']
    parked = is_user_reserved_spot(email)
    


    if parked:
        lot_info = get_parking_lot_from_spot(parked[1])
        current_time  = datetime.now()
        start_datetime = datetime.strptime(parked[3], "%Y-%m-%d %H:%M:%S.%f")
        time_difference = current_time - start_datetime
        total_seconds = round(time_difference.total_seconds())
        tota_hr = total_seconds/3600
        total_cost = round(tota_hr*(parked[5]))
        
        parking_data = {
                'lot_name': lot_info[1],
                'lotid': lot_info[0],
                'spot_id': parked[1],
                'parking_time': parked[3],
                'cost_per_hr': parked[5],
                'total_cost': total_cost
            }
        return render_template('/user/parked.html', parking_data=parking_data)


    parking_data = {
                'spot_id': ''
            }
        
    return render_template('/user/parked.html', parking_data=parking_data)

@user_bp.route('/edit', methods=['GET', 'POST'])
def edit_user():
    if request.method == 'POST':
        email = session['email']
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        car_number = request.form.get('car_number')
        new_email = request.form.get('email')
        user_id = get_user_id(email)

        new_details = {
            'email': new_email,
            'full_name': full_name,
            'password': password,
            'user_id': user_id,
            'address': address,
            'pin_code': pin_code,
            'car_number': car_number
        }
        # Call the function to edit user details
        edit_user_details(user_id, new_details)

        flash("User details updated successfully!", "success")
        return redirect(url_for('user.user_dashboard'))

    # Fetch the current user details
    email = session['email']
    user_id = get_user_id(email)
    user_details = get_user_from_id(user_id)


    return render_template('/user/edit_user.html', user_details=user_details)

@user_bp.route('/summary')
def summary():
    email = session['email']
    user_id = get_user_id(email)

    user_summary = get_user_summary(user_id)
    if user_summary:
        return render_template('/user/summary.html', user_summary=user_summary)

