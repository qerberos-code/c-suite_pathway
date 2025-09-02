#!/usr/bin/env python3
"""
Load Alumni to Database Script
Automatically loads the processed alumni data into the database
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Alumni, UserMessage

# Processed alumni data from the previous script
ALUMNI_DATA = [
    {'first_name': 'Alejandro', 'last_name': 'Tizzoni', 'email': 'atizzoni@bladex.com'},
    {'first_name': 'Alexandre', 'last_name': 'Ozzetti', 'email': 'alex.ozzetti@gmail.com'},
    {'first_name': 'Amanjeet', 'last_name': 'Singh', 'email': 'amanjeetsaluja@gmail.com'},
    {'first_name': 'Angus', 'last_name': 'Chen', 'email': 'chentail@protonmail.ch'},
    {'first_name': 'Asaf', 'last_name': 'Snear', 'email': 'asafsnear@gmail.com'},
    {'first_name': 'Belen', 'last_name': 'Robles', 'email': 'belenalonsorobles@gmail.com'},
    {'first_name': 'Diana', 'last_name': 'Orozco', 'email': 'dorozco@koskoff.com'},
    {'first_name': 'Ehab Al', 'last_name': 'Judaibi', 'email': 'ealjudaibi@spb.com.sa'},
    {'first_name': 'Fulya', 'last_name': 'Sarican', 'email': 'fulyasarican88@hotmail.com'},
    {'first_name': 'Gabriel', 'last_name': 'Varga', 'email': 'gabriel@aplusfinishes.com'},
    {'first_name': 'Gonzalo', 'last_name': 'Puerta', 'email': 'gongreenesgsolutions@gmail.com'},
    {'first_name': 'Hani', 'last_name': 'Abdullah', 'email': 'hamehmadi@spb.com.sa'},
    {'first_name': 'Joe', 'last_name': 'Akahane', 'email': 'yoichiro.akahane@us.panasonic.com'},
    {'first_name': 'Juan Carlos', 'last_name': 'Gutierrez', 'email': 'jclopez@lopesolutions.com'},
    {'first_name': 'Marijose', 'last_name': 'Betant', 'email': 'marijosebetant@gmail.com'},
    {'first_name': 'Natalia', 'last_name': 'Mercker', 'email': 'natalia.mercker@cfcdiamonds.com'},
    {'first_name': 'Pedro', 'last_name': 'Pimenta', 'email': 'ppimenta@abanca.com'},
    {'first_name': 'Priscila', 'last_name': 'Pasqualin', 'email': 'pripasq@yahoo.com.br'},
    {'first_name': 'Quinci', 'last_name': 'Martin', 'email': 'quincimartin3@gmail.com'},
    {'first_name': 'Raed', 'last_name': 'Alsufyani', 'email': 'ralsufyani@moc.gov.sa'},
    {'first_name': 'Rafael', 'last_name': 'Bittar', 'email': 'rafael.bittar@gmail.com'},
    {'first_name': 'Runi', 'last_name': 'Mehta', 'email': 'mehta.runi@gmail.com'},
    {'first_name': 'Sam', 'last_name': 'Mangrum', 'email': 'sam.mangrum@leewardenergy.com'},
    {'first_name': 'Saud', 'last_name': 'Alfaadhel', 'email': 's.alfaadhel@misk.org.sa'},
    {'first_name': 'Tommy', 'last_name': 'Hoey', 'email': 'tdhoy@grundfos.com'},
    {'first_name': 'Yousuf', 'last_name': 'Rashid', 'email': 'yusuf.s.zaabi@pdo.co.om'}
]

def load_alumni_to_database():
    """Load all alumni data into the database"""
    
    with app.app_context():
        print("🔄 Loading C-Suite Pathway Alumni to Database")
        print("=" * 60)
        
        # Create tables if they don't exist
        db.create_all()
        
        success_count = 0
        error_count = 0
        duplicate_count = 0
        
        for i, alumni_data in enumerate(ALUMNI_DATA, 1):
            try:
                # Check if alumni already exists
                existing_alumni = Alumni.query.filter_by(email=alumni_data['email']).first()
                
                if existing_alumni:
                    print(f"⚠️  {i:2d}. {alumni_data['first_name']} {alumni_data['last_name']} - Already exists")
                    duplicate_count += 1
                    continue
                
                # Create new alumni record
                new_alumni = Alumni(
                    first_name=alumni_data['first_name'],
                    last_name=alumni_data['last_name'],
                    email=alumni_data['email'].lower(),
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                
                db.session.add(new_alumni)
                db.session.commit()
                
                print(f"✅ {i:2d}. {alumni_data['first_name']} {alumni_data['last_name']} - Added successfully")
                success_count += 1
                
            except Exception as e:
                print(f"❌ {i:2d}. {alumni_data['first_name']} {alumni_data['last_name']} - Error: {str(e)}")
                error_count += 1
                db.session.rollback()
        
        print("\n" + "=" * 60)
        print("📊 Loading Summary:")
        print(f"✅ Successfully added: {success_count}")
        print(f"⚠️  Duplicates found: {duplicate_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📋 Total processed: {len(ALUMNI_DATA)}")
        
        if success_count > 0:
            print(f"\n🎉 {success_count} new alumni added to the verification system!")
            print("🔐 These alumni can now register on the website.")
        
        # Show total alumni count
        total_alumni = Alumni.query.filter_by(is_active=True).count()
        print(f"\n📈 Total active alumni in database: {total_alumni}")

if __name__ == '__main__':
    load_alumni_to_database()
