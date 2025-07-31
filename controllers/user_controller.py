from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime

user_bp = Blueprint('user', __name__)



@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    active_reservation = Reservation.query.filter_by(user_id=user_id, status='Active').first()
    recent_reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).limit(5).all()
    
    return render_template('user_dashboard.html', 
                         active_reservation=active_reservation,
                         recent_reservations=recent_reservations)

@user_bp.route('/book-parking')
def book_parking():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    lots = ParkingLot.query.filter(ParkingLot.available_spots > 0).all()
    return render_template('book_parking.html', lots=lots)

@user_bp.route('/book-spot/<int:lot_id>', methods=['GET', 'POST'])
def book_spot(lot_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    
    # Check if user already has an active reservation
    active_reservation = Reservation.query.filter_by(user_id=user_id, status='Active').first()
    if active_reservation:
        flash('You already have an active parking reservation', 'error')
        return redirect(url_for('user.dashboard'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number'].upper().strip()
        
        # Check if vehicle number already has an active reservation
        existing_vehicle_reservation = Reservation.query.filter_by(vehicle_number=vehicle_number, status='Active').first()
        if existing_vehicle_reservation:
            flash(f'Vehicle {vehicle_number} is already parked. Only one active booking per vehicle allowed.', 'error')
            return render_template('book_spot.html', lot=lot)
        
        # Find available spot
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not available_spot:
            flash('No available spots in this parking lot', 'error')
            return redirect(url_for('user.book_parking'))
        
        # Create reservation
        reservation = Reservation(
            user_id=user_id,
            spot_id=available_spot.id,
            vehicle_number=vehicle_number,
            status='Active'
        )
        
        # Update spot status and recalculate available spots
        available_spot.status = 'O'
        lot.available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').count() - 1
        if lot.available_spots < 0:
            lot.available_spots = 0
        
        db.session.add(reservation)
        db.session.commit()
        
        flash(f'Parking spot {available_spot.spot_number} booked successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('book_spot.html', lot=lot)

@user_bp.route('/release-parking/<int:reservation_id>')
def release_parking(reservation_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id, status='Active').first()
    
    if not reservation:
        flash('Reservation not found', 'error')
        return redirect(url_for('user.dashboard'))
    
    # Calculate cost
    duration_hours = (datetime.utcnow() - reservation.start_time).total_seconds() / 3600
    if duration_hours < 1:
        duration_hours = 1  # Minimum 1 hour charge
    
    lot = reservation.parking_spot.parking_lot
    total_cost = duration_hours * lot.price_per_hour
    
    # Update reservation
    reservation.end_time = datetime.utcnow()
    reservation.total_cost = round(total_cost, 2)
    reservation.status = 'Completed'
    
    # Update spot and recalculate available spots properly
    reservation.parking_spot.status = 'A'
    lot.available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count() + 1
    if lot.available_spots > lot.max_spots:
        lot.available_spots = lot.max_spots
    
    db.session.commit()
    
    flash(f'Parking released successfully! Total cost: ₹{reservation.total_cost}', 'success')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/booking-history')
def booking_history():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
    
    return render_template('booking_history.html', reservations=reservations)

