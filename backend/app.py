import os
from flask import Flask, send_from_directory, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db, User, Pet, Clinic, Donation
from routes import auth_bp, pet_bp, clinic_bp, donation_bp
from routes.admin_routes import admin_bp

# Get frontend path
FRONTEND_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
ADMIN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'admin')

def create_app():
    app = Flask(__name__, static_folder=FRONTEND_PATH, static_url_path='')
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(pet_bp, url_prefix='/api/pets')
    app.register_blueprint(clinic_bp, url_prefix='/api/clinics')
    app.register_blueprint(donation_bp, url_prefix='/api/donations')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Serve uploaded files - MUST be before serve_frontend
    @app.route('/static/uploads/<filename>')
    def uploaded_file(filename):
        upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
        return send_from_directory(upload_folder, filename)
    
    # Health check
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Pet Tashkent API is running'}
    
    # Serve frontend
    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_PATH, 'index.html')
    
    # Serve admin panel - dedicated routes
    @app.route('/admin/')
    @app.route('/admin')
    def serve_admin():
        return send_from_directory(ADMIN_PATH, 'index.html')
    
    @app.route('/admin/<path:filename>')
    def serve_admin_file(filename):
        file_path = os.path.join(ADMIN_PATH, filename)
        if os.path.exists(file_path):
            return send_from_directory(ADMIN_PATH, filename)
        return send_from_directory(ADMIN_PATH, 'index.html')
    
    @app.route('/<path:filename>')
    def serve_frontend(filename):
        # Handle static/uploads specially
        if filename.startswith('static/uploads/'):
            upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
            upload_filename = filename.replace('static/uploads/', '')
            return send_from_directory(upload_folder, upload_filename)
        
        # Check if file exists in frontend
        file_path = os.path.join(FRONTEND_PATH, filename)
        if os.path.exists(file_path):
            return send_from_directory(FRONTEND_PATH, filename)
        
        # For SPA routing, return index.html
        if '.' not in filename:
            return send_from_directory(FRONTEND_PATH, 'index.html')
        
        return {'error': 'Not found'}, 404
    
    # Create tables and seed admin user
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@pettashkent.uz').first()
        if not admin:
            admin = User(
                full_name='Admin',
                email='admin@pettashkent.uz',
                phone='+998901234567',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Add sample clinics
            sample_clinics = [
                Clinic(
                    name='Tashkent Veterinary Clinic',
                    address='Amir Temur ko\'chasi, 100',
                    lat=41.3111,
                    lng=69.2797,
                    phone='+998712345678',
                    working_hours='09:00 - 18:00',
                    services='Diagnostika, Jarrohlik, Vaksinatsiya'
                ),
                Clinic(
                    name='Pet Care Center',
                    address='Navoiy ko\'chasi, 55',
                    lat=41.3167,
                    lng=69.2833,
                    phone='+998712345679',
                    working_hours='24/7',
                    services='Shoshilinch yordam, Diagnostika, Parvarish'
                ),
                Clinic(
                    name='Zoo Veterinar',
                    address='Chilonzor, 12-mavze',
                    lat=41.2856,
                    lng=69.2044,
                    phone='+998712345680',
                    working_hours='08:00 - 20:00',
                    services='Vaksinatsiya, Diagnostika, Laboratoriya'
                )
            ]
            
            for clinic in sample_clinics:
                db.session.add(clinic)
            
            db.session.commit()
            print("Admin user and sample data created!")
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
