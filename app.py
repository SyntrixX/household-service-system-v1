import logging
import traceback
from logging.handlers import RotatingFileHandler

from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy

from forms import LoginForm, ProfessionalRegistrationForm, CustomerRegistrationForm
from models import Service, User, ServiceRemark, Professional, Booking, db
# Remove the import for the API blueprint
# from views import api  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)  # ensure the SQLAlchemy instance is properly initialized with the Flask app

migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)

# Remove the API blueprint registration
# app.register_blueprint(api)  

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    return Professional.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if (form.validate_on_submit()):
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_home'))
            elif user.role == 'professional':
                return redirect(url_for('professional_home'))
            elif user.role == 'customer':
                return redirect(url_for('customer_home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = CustomerRegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists!', 'error')
            return render_template('register.html', form=form)

        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip=form.zip.data,
            country=form.country.data,
            role='customer'
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Registration error: {str(e)}\n{traceback.format_exc()}')
            flash('An error occurred during registration.', 'error')
            
    return render_template('register.html', form=form)

@app.route('/register_professional', methods=['GET', 'POST'])
def register_professional():
    form = ProfessionalRegistrationForm()
    if form.validate_on_submit():
        if Professional.query.filter_by(email=form.email.data).first():
            flash('Email already exists!', 'error')
            return render_template('register_professional.html', form=form)

        professional = Professional(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip=form.zip.data,
            country=form.country.data,
            profession=form.profession.data,  # ensure profession field is handled
            role='professional'
        )
        professional.set_password(form.password.data)
        
        try:
            db.session.add(professional)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Registration error: {str(e)}\n{traceback.format_exc()}')
            flash('An error occurred during registration.', 'error')
            
    return render_template('register_professional.html', form=form)

@app.route('/admin_home')
@login_required
def admin_home():
    professionals = Professional.query.all()
    return render_template('admin/admin_home.html', professionals=professionals)

@app.route('/professional_home')
@login_required
def professional_home():
    return render_template('professional/professional_home.html')

@app.route('/customer_home')
@login_required
def customer_home():
    return render_template('customer/customer_home.html')

@app.route('/customer_summary', methods=['GET'])
@login_required
def customer_summary():
    requested_count = Booking.query.filter_by(customer_id=current_user.id).count()
    closed_count = Booking.query.join(Service).filter(Booking.customer_id == current_user.id, Service.status == 'completed').count()
    assigned_count = Booking.query.join(Service).filter(Booking.customer_id == current_user.id, Service.status == 'accepted').count()
    
    return render_template('customer/customer_summary.html', requested_count=requested_count, closed_count=closed_count, assigned_count=assigned_count)

@app.route('/search_service', methods=['GET', 'POST'])
@login_required
@csrf.exempt  # Disable CSRF protection for this route
def search_service():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        # Add logic to handle search query
        pass
    return render_template('customer/search_service.html')

@app.route('/service_remarks', methods=['GET', 'POST'])
@login_required
def service_remarks():
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        remark = request.form.get('remark')
        customer_id = current_user.id
        service_remark = ServiceRemark(service_id=service_id, customer_id=customer_id, remark=remark)  # Remove rating
        db.session.add(service_remark)
        db.session.commit()
        flash('Remark added successfully!', 'success')
    return render_template('customer/service_remarks.html')

@app.route('/profile', methods=['GET'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    return render_template('customer/profile.html', user=user)

@app.route('/professional_profile', methods=['GET'])
@login_required
def professional_profile():
    professional = Professional.query.filter_by(email=current_user.email).first()
    return render_template('professional/professional_profile.html', professional=professional)

@app.route('/professional_search_service', methods=['GET', 'POST'])
@login_required
def professional_search_service():
    if request.method == 'POST':
        pass
    return render_template('professional/professional_search_service.html')

@app.route('/professional_summary', methods=['GET'])
@login_required
def professional_summary():
    return render_template('professional/professional_summary.html')

@app.route('/admin_summary')
@login_required
def admin_summary():
    num_customers = User.query.filter_by(role='customer').count()
    num_professionals = Professional.query.count()
    overall_rating = 0  
    service_requests = 0 
    return render_template('admin/admin_summary.html', num_customers=num_customers, num_professionals=num_professionals, overall_rating=overall_rating, service_requests=service_requests)

@app.route('/search_service_request')
@login_required
def search_service_request():
    return render_template('admin/search_service_request.html')

@app.route('/get_professionals', methods=['GET'])
def get_professionals():
    professionals = Professional.query.all()
    professional_list = [{
        'id': pro.id,
        'name': pro.name,
        'profession': pro.profession,
        'experience': pro.experience,
        'phone': pro.phone,
        'image': 'https://via.placeholder.com/150',  # Placeholder image URL
        'description': 'Description for ' + pro.profession
    } for pro in professionals]
    return jsonify(professional_list)

@app.route('/book_service/<int:professional_id>', methods=['POST'])
@login_required
def book_service(professional_id):
    professional = Professional.query.get(professional_id)
    if not professional:
        return jsonify({'error': 'Professional not found'}), 404

    # Simulate booking logic
    service = Service(
        name=professional.profession,
        description=f'Service booked with {professional.name}',
        category=professional.profession,
        location=professional.city,
        professional_id=professional.id,
        customer_id=current_user.id,
        status='Booked',
        rating=0,
        price=100  # Example price
    )
    db.session.add(service)
    db.session.commit()

    return jsonify({
        'id': service.id,
        'name': professional.name,
        'profession': professional.profession,
        'phone': professional.phone
    })

@app.route('/accept_service/<int:service_id>', methods=['POST'])
@login_required
def accept_service(service_id):
    service = Service.query.get(service_id)
    if service and service.professional_id == current_user.id:
        service.status = 'accepted'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/reject_service/<int:service_id>', methods=['POST'])
@login_required
def reject_service(service_id):
    service = Service.query.get(service_id)
    if service and service.professional_id == current_user.id:
        service.status = 'rejected'
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/get_service_history', methods=['GET'])
@login_required
def get_service_history():
    services = Service.query.filter_by(customer_id=current_user.id).all()
    service_list = [{
        'id': service.id,
        'name': service.name,
        'professional_name': service.user.name,
        'phone': service.user.phone,
        'status': service.status
    } for service in services]
    return jsonify(service_list)

@app.route('/get_closed_services', methods=['GET'])
@login_required
def get_closed_services():
    services = Service.query.filter_by(professional_id=current_user.id, status='completed').all()
    service_list = [{
        'id': service.id,
        'name': service.user.name,
        'phone': service.user.phone,
        'location': service.location,
        'date': service.bookings[0].service.date if service.bookings else 'N/A',
        'rating': service.rating
    } for service in services]
    return jsonify(service_list)

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('Server Error: %s', (error))
    app.logger.error('Stack Trace: %s', traceback.format_exc())
    return "Internal Server Error", 500

with app.app_context():
    db.create_all()

import views  

if __name__ == '__main__':
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000, debug=True)