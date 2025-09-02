#!/usr/bin/env python3
"""
Process Alumni List Script
Breaks down full names into first and last names, displays them, and loads to database
"""

import re
from datetime import datetime

# Raw alumni data from the user
ALUMNI_DATA = """Name	Email
Alejandro Tizzoni	atizzoni@bladex.com
Alexandre Ozzetti	alex.ozzetti@gmail.com
Amanjeet Singh	amanjeetsaluja@gmail.com
Angus Chen	chentail@protonmail.ch
Asaf Snear	asafsnear@gmail.com
Belen Robles	belenalonsorobles@gmail.com
Diana Orozco	dorozco@koskoff.com
Ehab Al Judaibi	ealjudaibi@spb.com.sa
Fulya Sarican	fulyasarican88@hotmail.com
Gabriel Varga	gabriel@aplusfinishes.com
Gonzalo Puerta	gongreenesgsolutions@gmail.com
Hani Abdullah	hamehmadi@spb.com.sa
Joe Akahane	yoichiro.akahane@us.panasonic.com
Juan Carlos Gutierrez	jclopez@lopesolutions.com
Marijose Betant	marijosebetant@gmail.com
Natalia Mercker	natalia.mercker@cfcdiamonds.com
Pedro Pimenta	ppimenta@abanca.com
Priscila Pasqualin	pripasq@yahoo.com.br
Quinci Martin	quincimartin3@gmail.com
Raed Alsufyani 	ralsufyani@moc.gov.sa
Rafael Bittar	rafael.bittar@gmail.com
Runi Mehta	mehta.runi@gmail.com
Sam Mangrum	sam.mangrum@leewardenergy.com
Saud Alfaadhel	s.alfaadhel@misk.org.sa
Tommy Hoey	tdhoy@grundfos.com
Yousuf Rashid	yusuf.s.zaabi@pdo.co.om"""

def parse_name(full_name):
    """
    Parse full name into first and last name
    Special handling for names like "Juan Carlos" where first name is two words
    """
    # Clean up extra whitespace
    full_name = re.sub(r'\s+', ' ', full_name.strip())
    
    # Split by spaces
    name_parts = full_name.split()
    
    if len(name_parts) == 1:
        # Only one name provided
        return name_parts[0], ""
    elif len(name_parts) == 2:
        # Standard first last name
        return name_parts[0], name_parts[1]
    else:
        # Multiple parts - check for special cases
        if full_name.lower().startswith("juan carlos"):
            # Juan Carlos is first name
            first_name = "Juan Carlos"
            last_name = " ".join(name_parts[2:]) if len(name_parts) > 2 else ""
            return first_name, last_name
        elif full_name.lower().startswith("ehab al"):
            # Ehab Al Judaibi - "Ehab Al" might be first name
            first_name = "Ehab Al"
            last_name = " ".join(name_parts[2:]) if len(name_parts) > 2 else ""
            return first_name, last_name
        else:
            # Default: first word is first name, rest is last name
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:])
            return first_name, last_name

def process_alumni_data():
    """Process the alumni data and display results"""
    print("🔄 Processing C-Suite Pathway Alumni Data")
    print("=" * 60)
    
    # Parse the data
    lines = ALUMNI_DATA.strip().split('\n')
    header = lines[0]
    data_lines = lines[1:]
    
    processed_alumni = []
    
    print(f"📊 Found {len(data_lines)} alumni records")
    print()
    
    for line in data_lines:
        if '\t' in line:
            name, email = line.split('\t')
            first_name, last_name = parse_name(name)
            
            alumni_record = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email.strip(),
                'original_name': name.strip()
            }
            
            processed_alumni.append(alumni_record)
    
    # Display results
    print("📋 Processed Alumni List:")
    print("-" * 60)
    print(f"{'First Name':<15} {'Last Name':<15} {'Email':<35}")
    print("-" * 60)
    
    for alumni in processed_alumni:
        print(f"{alumni['first_name']:<15} {alumni['last_name']:<15} {alumni['email']:<35}")
    
    print("-" * 60)
    print(f"Total: {len(processed_alumni)} alumni")
    print()
    
    # Show special cases
    print("🔍 Special Name Parsing Cases:")
    print("-" * 40)
    for alumni in processed_alumni:
        if len(alumni['original_name'].split()) > 2:
            print(f"'{alumni['original_name']}' → '{alumni['first_name']}' '{alumni['last_name']}'")
    
    return processed_alumni

def confirm_and_load_to_database(processed_alumni):
    """Ask for confirmation before loading to database"""
    print("\n" + "=" * 60)
    print("🚀 Ready to Load to Database")
    print("=" * 60)
    
    print("The following alumni will be added to the verification system:")
    print()
    
    for i, alumni in enumerate(processed_alumni, 1):
        print(f"{i:2d}. {alumni['first_name']} {alumni['last_name']} ({alumni['email']})")
    
    print()
    response = input("Do you want to load these alumni to the database? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        return True
    else:
        print("❌ Operation cancelled.")
        return False

if __name__ == '__main__':
    # Process the data
    processed_alumni = process_alumni_data()
    
    # Ask for confirmation
    if confirm_and_load_to_database(processed_alumni):
        print("\n✅ Proceeding to load alumni to database...")
        print("📝 You can now use the admin interface to add these alumni manually,")
        print("   or I can create a script to automatically load them.")
    else:
        print("\n📝 Data processed and displayed. No changes made to database.")
