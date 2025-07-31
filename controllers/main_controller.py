from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from models.database import db, Admin, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not email or not password:
                flash('Please provide both email and password', 'error')
                return render_template('login.html')
            
            # First try to find admin by email
            admin = Admin.query.filter_by(email=email).first()
            if admin and admin.check_password(password):
                session['admin_id'] = admin.id
                session['is_admin'] = True
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin.admin_dashboard'))
            
            # If not admin, try to find user by email
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_name'] = user.full_name
                flash('Login successful!', 'success')
                return redirect(url_for('user.dashboard'))
            
            # If neither admin nor user found, show error
            flash('Invalid email or password', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        address = request.form['address']
        pin_code = request.form['pin_code']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            address=address,
            pin_code=pin_code
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.index'))