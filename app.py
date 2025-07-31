from flask import Flask
from models.database import db, Admin
from controllers.main_controller import main_bp
from controllers.user_controller import user_bp
from controllers.admin_controller import admin_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'parking-system-secret-key-2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_system.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    # Create tables and default admin
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.filter_by(email='admin@parking.com').first():
            admin = Admin(email='admin@parking.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5600)