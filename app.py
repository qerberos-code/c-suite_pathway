from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Production: Use PostgreSQL from Render
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Development: Use SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///csuite.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verification_token = db.Column(db.String(100), unique=True)

class Alumni(db.Model):
    """Table to store verified C-Suite Pathway alumni information"""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    graduation_year = db.Column(db.Integer)
    company = db.Column(db.String(100))
    position = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Alumni verification - List of approved alumni emails
# In production, this could be stored in environment variables or a separate table
ALUMNI_EMAILS = {
    # C-Suite Pathway Alumni Emails
    'atizzoni@bladex.com',
    'alex.ozzetti@gmail.com',
    'amanjeetsaluja@gmail.com',
    'chentail@protonmail.ch',
    'asafsnear@gmail.com',
    'belenalonsorobles@gmail.com',
    'dorozco@koskoff.com',
    'ealjudaibi@spb.com.sa',
    'fulyasarican88@hotmail.com',
    'gabriel@aplusfinishes.com',
    'gongreenesgsolutions@gmail.com',
    'hamehmadi@spb.com.sa',
    'yoichiro.akahane@us.panasonic.com',
    'jclopez@lopesolutions.com',
    'marijosebetant@gmail.com',
    'natalia.mercker@cfcdiamonds.com',
    'ppimenta@abanca.com',
    'pripasq@yahoo.com.br',
    'quincimartin3@gmail.com',
    'ralsufyani@moc.gov.sa',
    'rafael.bittar@gmail.com',
    'mehta.runi@gmail.com',
    'sam.mangrum@leewardenergy.com',
    's.alfaadhel@misk.org.sa',
    'tdhoy@grundfos.com',
    'yusuf.s.zaabi@pdo.co.om'
}

def is_alumni_email(email):
    """Check if email belongs to a verified C-Suite Pathway alumni"""
    # First check the hardcoded list
    if email.lower() in {email.lower() for email in ALUMNI_EMAILS}:
        return True
    
    # Then check the Alumni table
    alumni = Alumni.query.filter_by(email=email.lower(), is_active=True).first()
    return alumni is not None

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_type = db.Column(db.String(20), default='classmate')  # admin, classmate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('User', backref='messages')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if user.is_verified:
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Please verify your email before logging in.')
        else:
            flash('Invalid email or password.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.')
            return render_template('register.html')
        
        # Check if email is in the approved alumni list
        if not is_alumni_email(email):
            flash('This email address is not recognized as a C-Suite Pathway alumni email. Please contact the administrator if you believe this is an error.')
            return render_template('register.html')
        
        # Create verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            verification_token=verification_token
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send verification email
        send_verification_email(new_user)
        
        flash('Registration successful! Please check your email to verify your account.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        flash('Email verified successfully! You can now log in.')
    else:
        flash('Invalid verification token.')
    
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    admin_messages = Message.query.filter_by(message_type='admin').order_by(Message.created_at.desc()).limit(5).all()
    classmate_messages = Message.query.filter_by(message_type='classmate').order_by(Message.created_at.desc()).limit(10).all()
    upcoming_events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date).limit(5).all()
    
    return render_template('dashboard.html', 
                         admin_messages=admin_messages,
                         classmate_messages=classmate_messages,
                         upcoming_events=upcoming_events)

@app.route('/messages')
@login_required
def messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template('messages.html', messages=messages)

@app.route('/add_message', methods=['GET', 'POST'])
@login_required
def add_message():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        message_type = 'admin' if current_user.is_admin else 'classmate'
        
        new_message = Message(
            title=title,
            content=content,
            author_id=current_user.id,
            message_type=message_type
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        flash('Message posted successfully!')
        return redirect(url_for('messages'))
    
    return render_template('add_message.html')

@app.route('/calendar')
@login_required
def calendar():
    events = Event.query.order_by(Event.date).all()
    return render_template('calendar.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date']
        location = request.form['location']
        
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        new_event = Event(
            title=title,
            description=description,
            date=date,
            location=location,
            created_by=current_user.id
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        flash('Event added successfully!')
        return redirect(url_for('calendar'))
    
    return render_template('add_event.html')

@app.route('/resources')
@login_required
def resources():
    resources = Resource.query.order_by(Resource.created_at.desc()).all()
    return render_template('resources.html', resources=resources)

@app.route('/faq')
@login_required
def faq():
    faqs = FAQ.query.order_by(FAQ.created_at.desc()).all()
    return render_template('faq.html', faqs=faqs)

@app.route('/add_faq', methods=['GET', 'POST'])
@login_required
def add_faq():
    if request.method == 'POST':
        question = request.form['question']
        answer = request.form['answer']
        
        new_faq = FAQ(
            question=question,
            answer=answer,
            created_by=current_user.id
        )
        
        db.session.add(new_faq)
        db.session.commit()
        
        flash('FAQ added successfully!')
        return redirect(url_for('faq'))
    
    return render_template('add_faq.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin routes for managing alumni
@app.route('/admin/alumni')
@login_required
def admin_alumni():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('dashboard'))
    
    alumni_list = Alumni.query.filter_by(is_active=True).order_by(Alumni.last_name).all()
    return render_template('admin_alumni.html', alumni_list=alumni_list)

@app.route('/admin/add_alumni', methods=['GET', 'POST'])
@login_required
def add_alumni():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        graduation_year = request.form.get('graduation_year')
        company = request.form.get('company')
        position = request.form.get('position')
        
        # Check if alumni already exists
        existing_alumni = Alumni.query.filter_by(email=email).first()
        if existing_alumni:
            flash('Alumni with this email already exists.')
            return render_template('add_alumni.html')
        
        new_alumni = Alumni(
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            graduation_year=int(graduation_year) if graduation_year else None,
            company=company,
            position=position
        )
        
        db.session.add(new_alumni)
        db.session.commit()
        
        flash(f'Alumni {first_name} {last_name} added successfully!')
        return redirect(url_for('admin_alumni'))
    
    return render_template('add_alumni.html')

def send_verification_email(user):
    msg = Message(
        'Verify Your C-Suite Pathway Account',
        sender=app.config['MAIL_USERNAME'],
        recipients=[user.email]
    )
    
    verification_url = url_for('verify_email', token=user.verification_token, _external=True)
    
    msg.html = f'''
    <h2>Welcome to C-Suite Pathway Program!</h2>
    <p>Hi {user.first_name},</p>
    <p>Thank you for registering for the C-Suite Pathway Program. Please click the button below to verify your email address:</p>
    <a href="{verification_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
    <p>{verification_url}</p>
    <p>Best regards,<br>C-Suite Pathway Team</p>
    '''
    
    mail.send(msg)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
