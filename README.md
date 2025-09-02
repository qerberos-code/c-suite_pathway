# C-Suite Pathway Program Website

A modern, interactive website for the C-Suite Pathway Program participants, jointly delivered by IESE Business School and NYU Stern School of Business.

## Features

### 🔐 Authentication & Registration
- Simple sign-in with email and password
- User registration with first name, last name, and email
- Email verification system with secure tokens
- Password hashing for security

### 📱 Dashboard
- Welcome page with personalized greeting
- Admin messages section for official communications
- Classmate messages for peer-to-peer communication
- Quick actions for common tasks
- Upcoming events overview

### 💬 Messaging System
- Admin messages (for class presidents, vice presidents, administrators)
- Classmate messages for peer communication
- Real-time message preview
- Character counter for messages

### 📅 Calendar & Events
- Event creation and management
- Date and time validation
- Location tracking
- Upcoming events display

### ❓ FAQ System
- Searchable FAQ section
- Accordion-style display
- Add new FAQs functionality

### 📚 Resources (Coming Soon)
- File upload functionality planned for next version
- Document sharing capabilities

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Email**: Flask-Mail with SMTP

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd csuite
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Configure Email Settings
Edit `app.py` and update the email configuration:
```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

**Note**: For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password instead of your regular password

### Step 6: Add School Logos
✅ **Both logos have been automatically downloaded from the official websites:**
- IESE Business School logo (SVG format)
- NYU Stern School of Business logo (PNG format)

### Step 7: Run the Application
```bash
python app.py
```

The website will be available at `http://localhost:5000`

## Database Setup

The database will be automatically created when you first run the application. The SQLite database file (`csuite.db`) will be created in the project root directory.

## Usage

### First Time Setup
1. Visit `http://localhost:5000`
2. Click "Register" to create an account
3. Check your email for verification link
4. Click the verification link to activate your account
5. Sign in with your credentials

### Creating Admin Users
To create an admin user, you can modify the database directly or add this code temporarily to `app.py`:

```python
# Add this after db.create_all() in the main block
with app.app_context():
    # Create an admin user
    admin_user = User(
        first_name='Admin',
        last_name='User',
        email='admin@example.com',
        password_hash=generate_password_hash('password123'),
        is_verified=True,
        is_admin=True
    )
    db.session.add(admin_user)
    db.session.commit()
```

### Features Overview

#### Dashboard
- View recent admin and classmate messages
- See upcoming events
- Access quick actions

#### Messages
- Post new messages (admin or classmate)
- View all messages in chronological order
- Real-time preview while typing

#### Calendar
- Add new events with date, time, and location
- View all scheduled events
- Automatic date validation

#### FAQ
- Search through existing FAQs
- Add new questions and answers
- Accordion-style display for easy navigation

## Security Features

- Password hashing using Werkzeug
- Email verification with secure tokens
- CSRF protection (Flask-WTF)
- Session management with Flask-Login
- Input validation and sanitization

## Customization

### Styling
- Modify `static/css/style.css` for custom styling
- Update color variables in CSS `:root` section
- Add custom animations and transitions

### Functionality
- Add new routes in `app.py`
- Create new database models as needed
- Extend JavaScript functionality in `static/js/script.js`

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
For production deployment, consider:
1. Using a production WSGI server (Gunicorn, uWSGI)
2. Setting up a proper database (PostgreSQL, MySQL)
3. Configuring environment variables
4. Setting up SSL certificates
5. Using a reverse proxy (Nginx)

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and internal use by the C-Suite Pathway Program participants.

## Support

For technical support or questions about the website functionality, please contact the development team.

## Changelog

### Version 1.0.0
- Initial release
- User authentication and registration
- Dashboard with messages and events
- FAQ system
- Responsive design
- Email verification system

### Planned Features
- File upload functionality for resources
- Photo gallery
- Advanced search capabilities
- Push notifications
- Mobile app version
