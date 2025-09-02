#!/usr/bin/env python3
"""
Setup script for C-Suite Pathway Program Website
"""

import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db, User

def create_admin_user():
    """Create an admin user for initial setup"""
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(is_admin=True).first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        print("Creating admin user...")
        print("Please provide the following information:")
        
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if not all([first_name, last_name, email, password]):
            print("All fields are required!")
            return
        
        # Create admin user
        admin_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=generate_password_hash(password),
            is_verified=True,
            is_admin=True
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            print(f"\n✅ Admin user created successfully!")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print("\nYou can now log in with these credentials.")
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.session.rollback()

def check_email_config():
    """Check if email configuration is set up"""
    print("Email Configuration Check:")
    print("=" * 30)
    
    with app.app_context():
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')
        
        if mail_username == 'your-email@gmail.com':
            print("❌ Email configuration not set up!")
            print("\nTo enable email verification, please:")
            print("1. Edit app.py")
            print("2. Update MAIL_USERNAME and MAIL_PASSWORD")
            print("3. For Gmail, enable 2FA and generate an App Password")
        else:
            print("✅ Email configuration appears to be set up")
            print(f"Username: {mail_username}")

def main():
    """Main setup function"""
    print("C-Suite Pathway Program Setup")
    print("=" * 30)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
    
    # Check email configuration
    check_email_config()
    
    print("\nSetup Options:")
    print("1. Create admin user")
    print("2. Exit")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == '1':
        create_admin_user()
    elif choice == '2':
        print("Setup complete!")
    else:
        print("Invalid choice!")

if __name__ == '__main__':
    main()
