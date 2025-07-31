from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db, Admin, ParkingLot, ParkingSpot, User, Reservation
from datetime import datetime

admin_bp = Blueprint('admin', __name__)



@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    total_users = User.query.count()
    active_reservations = Reservation.query.filter_by(status='Active').count()
    
    # Calculate total revenue from completed reservations
    total_revenue = db.session.query(db.func.sum(Reservation.total_cost)).filter(
        Reservation.status == 'Completed',
        Reservation.total_cost.isnot(None)
    ).scalar() or 0.0
    
    return render_template('admin_dashboard.html', 
                         total_lots=total_lots,
                         total_spots=total_spots,
                         occupied_spots=occupied_spots,
                         total_users=total_users,
                         active_reservations=active_reservations,
                         total_revenue=total_revenue)

@admin_bp.route('/admin/parking-lots')
def view_parking_lots():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lots = ParkingLot.query.all()
    selected_lots = request.args.get('selected', '').split(',') if request.args.get('selected') else []
    return render_template('admin_parking_lots.html', lots=lots, selected_lots=selected_lots)

@admin_bp.route('/admin/add-parking-lot', methods=['GET', 'POST'])
def add_parking_lot():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        location_name = request.form['location_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price_per_hour = float(request.form['price_per_hour'])
        max_spots = int(request.form['max_spots'])
        
        # Create parking lot
        parking_lot = ParkingLot(
            location_name=location_name,
            address=address,
            pin_code=pin_code,
            price_per_hour=price_per_hour,
            max_spots=max_spots,
            available_spots=max_spots
        )
        db.session.add(parking_lot)
        db.session.flush()  # Get the ID
        
        # Create parking spots
        for i in range(1, max_spots + 1):
            spot = ParkingSpot(
                spot_number=f"P{i:03d}",
                lot_id=parking_lot.id,
                status='A'
            )
            db.session.add(spot)
        
        db.session.commit()
        flash('Parking lot added successfully!', 'success')
        return redirect(url_for('admin.view_parking_lots'))
    
    return render_template('admin_add_lot.html')

@admin_bp.route('/admin/edit-parking-lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        lot.location_name = request.form['location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_hour = float(request.form['price_per_hour'])
        new_max_spots = int(request.form['max_spots'])
        
        # Handle spot modification
        current_spots = len(lot.spots)
        
        if new_max_spots > current_spots:
            # Add new spots
            for i in range(current_spots + 1, new_max_spots + 1):
                spot = ParkingSpot(
                    spot_number=f"P{i:03d}",
                    lot_id=lot.id,
                    status='A'
                )
                db.session.add(spot)
            
        elif new_max_spots < current_spots:
            # Remove excess spots (only if they're available)
            spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').offset(new_max_spots).all()
            for spot in spots_to_remove:
                db.session.delete(spot)
        
        lot.max_spots = new_max_spots
        # Fix available spots count properly
        _fix_lot_counts(lot)
        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin.view_parking_lots'))
    
    return render_template('admin_edit_lot.html', lot=lot)

def _fix_lot_counts(lot):
    """Fix available spots count for a parking lot"""
    total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    lot.max_spots = total_spots
    lot.available_spots = total_spots - occupied_spots
    if lot.available_spots < 0:
        lot.available_spots = 0



@admin_bp.route('/admin/delete-parking-lot/<int:lot_id>')
def delete_parking_lot(lot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if all spots in the parking lot are empty
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    
    if occupied_spots > 0:
        flash(f'Cannot delete parking lot "{lot.location_name}" - it has {occupied_spots} occupied spots. Please wait for all vehicles to be released first.', 'error')
        return redirect(url_for('admin.view_parking_lots'))
    
    # Delete all reservations (completed ones) for this lot first
    completed_reservations = Reservation.query.join(ParkingSpot).filter(
        ParkingSpot.lot_id == lot_id
    ).all()
    
    for reservation in completed_reservations:
        db.session.delete(reservation)
    
    # Delete all spots in this lot
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    for spot in spots:
        db.session.delete(spot)
    
    # Finally delete the lot
    lot_name = lot.location_name
    db.session.delete(lot)
    db.session.commit()
    
    flash(f'Parking lot "{lot_name}" deleted successfully!', 'success')
    return redirect(url_for('admin.view_parking_lots'))

@admin_bp.route('/admin/bulk-delete-parking-lots', methods=['POST'])
def bulk_delete_parking_lots():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot_ids = request.form.getlist('lot_ids')
    
    if not lot_ids:
        flash('No parking lots selected for deletion.', 'error')
        return redirect(url_for('admin.view_parking_lots'))
    
    deleted_count = 0
    failed_deletions = []
    
    for lot_id in lot_ids:
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            continue
            
        # Check if all spots in the parking lot are empty
        occupied_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
        
        if occupied_spots > 0:
            failed_deletions.append(f'"{lot.location_name}" ({occupied_spots} occupied spots)')
            continue
        
        # Delete all reservations (completed ones) for this lot first
        completed_reservations = Reservation.query.join(ParkingSpot).filter(
            ParkingSpot.lot_id == lot_id
        ).all()
        
        for reservation in completed_reservations:
            db.session.delete(reservation)
        
        # Delete all spots in this lot
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        for spot in spots:
            db.session.delete(spot)
        
        # Finally delete the lot
        db.session.delete(lot)
        deleted_count += 1
    
    db.session.commit()
    
    if deleted_count > 0:
        flash(f'{deleted_count} parking lot(s) deleted successfully!', 'success')
    
    if failed_deletions:
        flash(f'Could not delete: {", ".join(failed_deletions)} - all spots must be empty.', 'error')
    
    return redirect(url_for('admin.view_parking_lots'))

@admin_bp.route('/admin/select-all-lots')
def select_all_lots():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lots = ParkingLot.query.all()
    lot_ids = [str(lot.id) for lot in lots]
    return redirect(url_for('admin.view_parking_lots', selected=','.join(lot_ids)))

@admin_bp.route('/admin/clear-selection')
def clear_selection():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    return redirect(url_for('admin.view_parking_lots'))

@admin_bp.route('/admin/users')
def view_users():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/admin/parking-history')
def parking_history():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    # Get filter parameter
    status_filter = request.args.get('status', 'all')
    
    # Get all reservations with related data
    query = Reservation.query.join(ParkingSpot).join(ParkingLot).join(User)
    
    # Apply status filter
    if status_filter == 'Active':
        query = query.filter(Reservation.status == 'Active')
    elif status_filter == 'Completed':
        query = query.filter(Reservation.status == 'Completed')
    
    reservations = query.order_by(Reservation.created_at.desc()).all()
    
    # Calculate summary statistics
    total_reservations = len(reservations)
    active_reservations = len([r for r in reservations if r.status == 'Active'])
    completed_reservations = len([r for r in reservations if r.status == 'Completed'])
    total_revenue = sum([r.total_cost for r in reservations if r.total_cost])
    
    return render_template('admin_parking_history.html', 
                         reservations=reservations,
                         total_reservations=total_reservations,
                         active_reservations=active_reservations,
                         completed_reservations=completed_reservations,
                         total_revenue=total_revenue,
                         current_filter=status_filter)

@admin_bp.route('/admin/view-spots/<int:lot_id>')
def view_spots(lot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).order_by(ParkingSpot.spot_number).all()
    
    # Handle select all parameter
    select_all = request.args.get('select_all') == 'true'
    
    return render_template('admin_view_spots.html', lot=lot, spots=spots, select_all=select_all)

@admin_bp.route('/admin/edit-spot-form/<int:spot_id>')
def edit_spot_form(spot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    return render_template('admin_edit_spot.html', spot=spot)

@admin_bp.route('/admin/add-spot/<int:lot_id>', methods=['POST'])
def add_spot(lot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    spot_number = request.form['spot_number'].upper().strip()
    
    # Check if spot number already exists
    existing_spot = ParkingSpot.query.filter_by(lot_id=lot_id, spot_number=spot_number).first()
    if existing_spot:
        flash(f'Spot number {spot_number} already exists', 'error')
        return redirect(url_for('admin.view_spots', lot_id=lot_id))
    
    # Create new spot
    new_spot = ParkingSpot(
        spot_number=spot_number,
        lot_id=lot_id,
        status='A'
    )
    
    db.session.add(new_spot)
    lot.max_spots += 1
    # Recalculate available spots properly
    lot.available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').count() + 1
    db.session.commit()
    
    flash(f'Parking spot {spot_number} added successfully!', 'success')
    return redirect(url_for('admin.view_spots', lot_id=lot_id))

@admin_bp.route('/admin/edit-spot/<int:spot_id>', methods=['POST'])
def edit_spot(spot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    new_spot_number = request.form['spot_number'].upper()
    
    # Check if new spot number already exists (excluding current spot)
    existing_spot = ParkingSpot.query.filter(
        ParkingSpot.lot_id == spot.lot_id,
        ParkingSpot.spot_number == new_spot_number,
        ParkingSpot.id != spot_id
    ).first()
    
    if existing_spot:
        flash(f'Spot number {new_spot_number} already exists', 'error')
        return redirect(url_for('admin.view_spots', lot_id=spot.lot_id))
    
    old_number = spot.spot_number
    spot.spot_number = new_spot_number
    db.session.commit()
    
    flash(f'Spot {old_number} renamed to {new_spot_number} successfully!', 'success')
    return redirect(url_for('admin.view_spots', lot_id=spot.lot_id))

@admin_bp.route('/admin/delete-spot/<int:spot_id>')
def delete_spot(spot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    lot = spot.parking_lot
    
    # Check if spot is occupied
    if spot.status == 'O':
        flash(f'Cannot delete spot {spot.spot_number} - it is currently occupied', 'error')
        return redirect(url_for('admin.view_spots', lot_id=lot.id))
    
    # Delete all reservations for this spot first
    reservations = Reservation.query.filter_by(spot_id=spot_id).all()
    for reservation in reservations:
        db.session.delete(reservation)
    
    spot_number = spot.spot_number
    db.session.delete(spot)
    lot.max_spots -= 1
    # Recalculate available spots properly
    lot.available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count() - 1
    if lot.available_spots < 0:
        lot.available_spots = 0
    db.session.commit()
    
    flash(f'Parking spot {spot_number} deleted successfully!', 'success')
    return redirect(url_for('admin.view_spots', lot_id=lot.id))

@admin_bp.route('/admin/bulk-spot-action/<int:lot_id>', methods=['POST'])
def bulk_spot_action(lot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    action = request.form.get('action')
    spot_ids = request.form.getlist('spot_ids')
    
    if action == 'delete' and spot_ids:
        spots_to_delete = ParkingSpot.query.filter(ParkingSpot.id.in_(spot_ids)).all()
        
        # Check if any selected spots are occupied
        occupied_spots = [spot for spot in spots_to_delete if spot.status == 'O']
        if occupied_spots:
            occupied_numbers = [spot.spot_number for spot in occupied_spots]
            flash(f'Cannot delete occupied spots: {", ".join(occupied_numbers)}', 'error')
            return redirect(url_for('admin.view_spots', lot_id=lot_id))
        
        # Delete all selected available spots
        deleted_count = 0
        for spot in spots_to_delete:
            if spot.status == 'A':
                # Delete reservations for this spot first
                reservations = Reservation.query.filter_by(spot_id=spot.id).all()
                for reservation in reservations:
                    db.session.delete(reservation)
                db.session.delete(spot)
                deleted_count += 1
        
        lot.max_spots -= deleted_count
        # Recalculate available spots properly
        remaining_spots = ParkingSpot.query.filter_by(lot_id=lot_id).count() - deleted_count
        occupied_spots_count = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
        lot.available_spots = remaining_spots - occupied_spots_count
        if lot.available_spots < 0:
            lot.available_spots = 0
        
        db.session.commit()
        
        flash(f'{deleted_count} parking spots deleted successfully!', 'success')
    
    return redirect(url_for('admin.view_spots', lot_id=lot_id))

@admin_bp.route('/admin/confirm-delete-parking-lot/<int:lot_id>')
def confirm_delete_parking_lot(lot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)
    return render_template('admin_confirm_delete_lot.html', lot=lot)

@admin_bp.route('/admin/confirm-delete-spot/<int:spot_id>')
def confirm_delete_spot(spot_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    spot = ParkingSpot.query.get_or_404(spot_id)
    return render_template('admin_confirm_delete_spot.html', spot=spot)

@admin_bp.route('/admin/confirm-bulk-delete-lots')
def confirm_bulk_delete_lots():
    if 'admin_id' not in session:
        return redirect(url_for('main.login'))
    
    lot_ids = request.args.get('lot_ids', '').split(',')
    lots = ParkingLot.query.filter(ParkingLot.id.in_(lot_ids)).all()
    return render_template('admin_confirm_bulk_delete_lots.html', lots=lots)

