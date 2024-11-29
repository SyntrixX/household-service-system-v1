import logging
import traceback
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm, ProfessionalRegistrationForm
from models import db, User, Service
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
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
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            role=form.role.data,
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip=form.zip.data,
            country=form.country.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/register_professional', methods=['GET', 'POST'])
def register_professional():
    form = ProfessionalRegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, role='professional')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register_professional.html', form=form)

@app.route('/admin_home')
@login_required
def admin_home():
    return render_template('admin/admin_home.html')

@app.route('/professional_home')
@login_required
def professional_home():
    return render_template('professional/professional_home.html')

@app.route('/customer_home')
@login_required
def customer_home():
    return render_template('customer/customer_home.html')

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('Server Error: %s', (error))
    app.logger.error('Stack Trace: %s', traceback.format_exc())
    return "Internal Server Error", 500

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.ERROR)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5000, debug=True)