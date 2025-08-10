from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from controlers.control import *
from controlers.admin import admin_bp
from controlers.user import user_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(user_bp, url_prefix="/user")

@app.route('/')
def home():
    if 'email' in session:
        # Check if the user is an admin
        if is_admin(session['email']):
            return redirect(url_for('admin.admin_dashboard'))
        elif is_user(session['email']):
            flash("Welcome back, " + session['full_name'], "success")
            return redirect(url_for('user.user_dashboard'))
        else:
            return render_template('home.html', full_name=session['full_name'])
          
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user(request.form['email'])
        if not user:
            flash("User does not exist", "error")
            return redirect(url_for('login'))
        if user and user[2] == request.form['password']:
            
            session['email'] = user[1]
            session['full_name'] = user[3]
            return redirect(url_for('home'))
        flash("Invalid credentials", "error")
    return render_template('login.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect('tmp\parking.db')
            c = conn.cursor()
            c.execute("""
                    INSERT INTO users (email, password, full_name, address, pin_code, car_number)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, 
                (request.form['email'],
                 request.form['password'],
                 request.form['Full Name'],
                 request.form['Address'],
                 request.form['Pin Code'],
                 request.form['Car Number']))
            
            conn.commit()
            conn.close()
            flash("Account created! Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))





if __name__ == '__main__':
    app.run(debug=True)
