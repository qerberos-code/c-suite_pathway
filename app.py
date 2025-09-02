from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import secrets
import uuid
from werkzeug.utils import secure_filename

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

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager()

# Make helper functions available in templates
@app.context_processor
def utility_processor():
    return {
        'get_file_icon': get_file_icon,
        'format_file_size': format_file_size
    }
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

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_icon(file_type):
    """Get appropriate icon for file type"""
    icons = {
        'pdf': 'fas fa-file-pdf',
        'doc': 'fas fa-file-word',
        'docx': 'fas fa-file-word',
        'ppt': 'fas fa-file-powerpoint',
        'pptx': 'fas fa-file-powerpoint',
        'xls': 'fas fa-file-excel',
        'xlsx': 'fas fa-file-excel',
        'txt': 'fas fa-file-alt',
        'jpg': 'fas fa-file-image',
        'jpeg': 'fas fa-file-image',
        'png': 'fas fa-file-image',
        'gif': 'fas fa-file-image'
    }
    return icons.get(file_type.lower(), 'fas fa-file')

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def verify_alumni_registration(first_name, last_name, email):
    """Verify that the registration matches a verified C-Suite Pathway alumni"""
    # Check the Alumni table for exact match
    alumni = Alumni.query.filter_by(
        email=email.lower(), 
        is_active=True
    ).first()
    
    if not alumni:
        return False, "Email not found in alumni database"
    
    # Check if names match (case-insensitive)
    if (alumni.first_name.lower() != first_name.lower() or 
        alumni.last_name.lower() != last_name.lower()):
        return False, f"Name does not match alumni record. Expected: {alumni.first_name} {alumni.last_name}"
    
    return True, "Verification successful"

class UserMessage(db.Model):
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
    file_name = db.Column(db.String(200))
    file_size = db.Column(db.Integer)  # Size in bytes
    file_type = db.Column(db.String(50))  # MIME type
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploader = db.relationship('User', backref='uploaded_resources')

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
            if existing_user.is_verified:
                flash('This email is already registered and verified. Please sign in instead.')
            else:
                flash('This email is already registered but not verified. Please check your email for verification link.')
            return render_template('register.html')
        
        # Verify that the registration matches a verified alumni
        is_verified, message = verify_alumni_registration(first_name, last_name, email)
        if not is_verified:
            flash(f'Alumni verification failed: {message}. Please check your information and try again.')
            return render_template('register.html')
        
        try:
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
            email_sent = send_verification_email(new_user)
            
            if email_sent:
                flash('Registration successful! Please check your email to verify your account.')
            else:
                flash('Registration successful! Your account has been auto-verified for development.')
            
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}. Please try again.')
            return render_template('register.html')
    
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
    admin_messages = UserMessage.query.filter_by(message_type='admin').order_by(UserMessage.created_at.desc()).limit(5).all()
    classmate_messages = UserMessage.query.filter_by(message_type='classmate').order_by(UserMessage.created_at.desc()).limit(10).all()
    upcoming_events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date).limit(5).all()
    
    return render_template('dashboard.html', 
                         admin_messages=admin_messages,
                         classmate_messages=classmate_messages,
                         upcoming_events=upcoming_events)

@app.route('/messages')
@login_required
def messages():
    messages = UserMessage.query.order_by(UserMessage.created_at.desc()).all()
    return render_template('messages.html', messages=messages)

@app.route('/add_message', methods=['GET', 'POST'])
@login_required
def add_message():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        message_type = 'admin' if current_user.is_admin else 'classmate'
        
        new_message = UserMessage(
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
    try:
        resources = Resource.query.order_by(Resource.created_at.desc()).all()
        return render_template('resources.html', resources=resources)
    except Exception as e:
        # If there's a database schema issue, show empty resources
        print(f"Database error in resources: {str(e)}")
        flash('Resources temporarily unavailable. Please try again later.')
        return render_template('resources.html', resources=[])

@app.route('/add_resource', methods=['GET', 'POST'])
@login_required
def add_resource():
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            
            # Check if file was uploaded
            if 'file' not in request.files:
                flash('No file selected.')
                return render_template('add_resource.html')
            
            file = request.files['file']
            
            if file.filename == '':
                flash('No file selected.')
                return render_template('add_resource.html')
            
            if file and allowed_file(file.filename):
                # Create upload directory if it doesn't exist
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Generate unique filename
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Save file
                file.save(file_path)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Create resource record
                new_resource = Resource(
                    title=title,
                    description=description,
                    file_path=unique_filename,
                    file_name=file.filename,
                    file_size=file_size,
                    file_type=file_extension,
                    uploaded_by=current_user.id
                )
                
                db.session.add(new_resource)
                db.session.commit()
                
                flash('Resource uploaded successfully!')
                return redirect(url_for('resources'))
            else:
                flash('File type not allowed. Please upload a valid file.')
                return render_template('add_resource.html')
        except Exception as e:
            print(f"Error uploading resource: {str(e)}")
            flash('Error uploading resource. Please try again.')
            return render_template('add_resource.html')
    
    return render_template('add_resource.html')

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    """Download a file from the uploads folder"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        flash('File not found.')
        return redirect(url_for('resources'))

@app.route('/delete_resource/<int:resource_id>', methods=['POST'])
@login_required
def delete_resource(resource_id):
    """Delete a resource"""
    resource = Resource.query.get_or_404(resource_id)
    
    # Only allow deletion by uploader or admin
    if resource.uploaded_by != current_user.id and not current_user.is_admin:
        flash('You can only delete your own resources.')
        return redirect(url_for('resources'))
    
    try:
        # Delete file from filesystem
        if resource.file_path:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], resource.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Delete from database
        db.session.delete(resource)
        db.session.commit()
        
        flash('Resource deleted successfully!')
    except Exception as e:
        flash(f'Error deleting resource: {str(e)}')
    
    return redirect(url_for('resources'))

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

@app.route('/debug/users')
def debug_users():
    """Debug route to see current users (remove in production)"""
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'verified': user.is_verified,
            'admin': user.is_admin,
            'created': user.created_at
        })
    return {'users': result, 'count': len(result)}

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
    try:
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
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        # For development, we'll auto-verify the user if email fails
        if app.config.get('MAIL_USERNAME') == 'your-email@gmail.com':
            user.is_verified = True
            user.verification_token = None
            db.session.commit()
            return False
        return False

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
