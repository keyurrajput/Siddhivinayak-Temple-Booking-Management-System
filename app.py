#app.py
import streamlit as st
import mysql.connector
import traceback
from datetime import datetime, timedelta
import time
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64

# Set page configuration
st.set_page_config(
    page_title="Siddhivinayak Temple",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #F97316;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #7E22CE;
        margin-bottom: 1rem;
        border-bottom: 2px solid #FFEDD5;
        padding-bottom: 0.5rem;
    }
    .card {
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #F97316;
    }
    .card-gold {
        border-left: 4px solid #FBBF24;
        background: linear-gradient(135deg, white, #FFFBEB);
    }
    .card-purple {
        border-left: 4px solid #7E22CE;
        background: linear-gradient(135deg, white, #F3E8FF);
    }
    .success-msg {
        color: white;
        background: linear-gradient(135deg, #10B981, #34D399);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid #FFEDD5;
        color: #64748B;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
def get_database_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="keyur123",
            database="temple_db"
        )
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Format currency
def format_currency(amount):
    if amount == 0:
        return "Free"
    return f"₹{amount:,.2f}"

# Sidebar
def create_sidebar():
    try:
        with st.sidebar:
            st.title("Siddhivinayak Temple")
            st.markdown("*Shree Siddhivinayak Ganapati Mandir*")
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### Navigation")
            menu = st.radio(
                label="Navigation Menu",
                options=["Home", "Book Darshan", "Make Donation", "Virtual Puja", "Order Prasadam", "View Bookings", "Admin Dashboard"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Temple timings
            st.markdown("### Temple Timings")
            st.markdown("**Morning**: 5:30 AM - 12:00 PM")
            st.markdown("**Evening**: 4:00 PM - 9:30 PM")
            
            # Get festivals if possible
            conn = get_database_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute("SELECT * FROM Temples LIMIT 1")
                    temple = cursor.fetchone()
                    
                    if temple:
                        # Get festivals
                        cursor.execute("""
                        SELECT FestivalName, StartDate, EndDate FROM Festivals 
                        WHERE TempleID = %s AND EndDate >= CURDATE() 
                        ORDER BY StartDate LIMIT 3
                        """, (temple['TempleID'],))
                        
                        festivals = cursor.fetchall()
                        
                        if festivals:
                            st.markdown("### Upcoming Festivals")
                            for festival in festivals:
                                st.markdown(f"**{festival['FestivalName']}**: {festival['StartDate']} to {festival['EndDate']}")
                
                except Exception as e:
                    # Just skip festivals if there's an error
                    pass
                
                finally:
                    cursor.close()
                    conn.close()
            
            st.markdown("---")
            st.info("📞 Helpline: +91-22-24373626\n\n📧 Email: info@siddhivinayak.org")
        
        return menu
    except Exception as e:
        st.error(f"Error creating sidebar: {e}")
        return "Home"  # Default to home on error

# Home page
def show_home_page():
    try:
        st.markdown('<h1 class="main-header">Welcome to Siddhivinayak Temple</h1>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### About Shree Siddhivinayak Ganapati Mandir")
            
            st.markdown("""
            The Shree Siddhivinayak Ganapati Mandir is a Hindu temple dedicated to Lord Shri Ganesh. It is located in Prabhadevi, Mumbai, Maharashtra, India. It was originally built in 1801 and has since become one of the most visited temples in Mumbai.
            
            The temple has a small mandap (hall) with the shrine for Siddhi Vinayak ("Ganesh who grants your wish"). The wooden doors to the sanctum are carved with images of the Ashtavinayak (the eight manifestations of Ganesh in Maharashtra). The inner roof of the sanctum is plated with gold.
            
            Siddhivinayak is well known as "Navasacha Ganapati" or "Navasala Pavanara Ganapati" (Marathi: नवसाला पावणारा गणपती) among devotees.
            """)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('<h2 class="sub-header">Our Services</h2>', unsafe_allow_html=True)
            
            service_col1, service_col2 = st.columns(2)
            
            with service_col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### Book Darshan")
                st.markdown("Schedule your visit to the temple for darshan. Choose from various types of darshan based on your preferences and convenience.")
                if st.button("Book Darshan Now", key="home_book"):
                    st.session_state.menu = "Book Darshan"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown('<div class="card card-purple">', unsafe_allow_html=True)
                st.markdown("### Virtual Puja Services")
                st.markdown("Can't visit in person? Participate in a virtual puja performed by temple priests on your behalf.")
                if st.button("Book Virtual Puja", key="home_puja"):
                    st.session_state.menu = "Virtual Puja"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            
            with service_col2:
                st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
                st.markdown("### Make Donation")
                st.markdown("Contribute to the temple's various initiatives and activities. Your donations help us maintain and improve the temple facilities.")
                if st.button("Make Donation Now", key="home_donate"):
                    st.session_state.menu = "Make Donation"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### Order Prasadam")
                st.markdown("Have the divine prasadam from Siddhivinayak delivered to your doorstep. Experience the divine blessing at your home.")
                if st.button("Order Prasadam", key="home_prasadam"):
                    st.session_state.menu = "Order Prasadam"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Temple Highlights")
            st.markdown("- **Founded**: 1801")
            st.markdown("- **Main Deity**: Lord Ganesha")
            st.markdown("- **Architecture**: Traditional Maharashtrian")
            st.markdown("- **Daily Visitors**: ~25,000")
            st.markdown("- **Special Day**: Tuesday (Busiest)")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Today's Aarti Schedule")
            st.markdown("**Morning Aarti**: 5:30 AM")
            st.markdown("**Afternoon Aarti**: 12:00 PM")
            st.markdown("**Evening Aarti**: 7:00 PM")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Important Guidelines")
            st.markdown("1. Mobile phones must be switched off")
            st.markdown("2. Photography is strictly prohibited")
            st.markdown("3. Dress modestly and appropriately")
            st.markdown("4. Maintain silence inside the temple")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Location
        st.markdown('<h2 class="sub-header">Location</h2>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### How to Reach")
            st.markdown("""
            **Address**: SK Bole Marg, Prabhadevi, Mumbai, Maharashtra 400028
            
            **By Train**: Nearest railway stations are Dadar (Western & Central Line) and Prabhadevi (Western Line)
            
            **By Bus**: BEST Bus routes 1, 2, 3, 5, 6, and 7 stop near the temple
            
            **By Car**: The temple is located in Prabhadevi, central Mumbai. Parking facilities are available nearby.
            """)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Map Location")
            st.markdown("Siddhivinayak Temple, SK Bole Marg, Prabhadevi, Mumbai")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown('<div class="footer">', unsafe_allow_html=True)
        st.markdown("© 2025 Siddhivinayak Temple Trust. All Rights Reserved.")
        st.markdown("Prabhadevi, Mumbai, Maharashtra 400028, India")
        st.markdown("</div>", unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error in home page: {e}")
        st.write(traceback.format_exc())

# Book Darshan page
def show_book_darshan_page():
    try:
        st.markdown('<h1 class="main-header">Book Darshan</h1>', unsafe_allow_html=True)
        
        conn = get_database_connection()
        if not conn:
            st.error("Could not connect to database. Please try again later.")
            return
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get temples
            cursor.execute("SELECT * FROM Temples WHERE IsActive = TRUE")
            temples = cursor.fetchall()
            
            if not temples:
                st.error("No temples available in the system")
                return
            
            # Temple selection
            temple_names = [temple['TempleName'] for temple in temples]
            selected_temple = st.selectbox("Select Temple", temple_names)
            selected_temple_id = next((temple['TempleID'] for temple in temples if temple['TempleName'] == selected_temple), None)
            
            if not selected_temple_id:
                st.error("Temple information not available")
                return
            
            # Select date
            selected_date = st.date_input("Select Date", datetime.now())
            
            # Get darshan types
            cursor.execute("""
            SELECT * FROM DarshanTypes 
            WHERE TempleID = %s
            """, (selected_temple_id,))
            
            darshan_types = cursor.fetchall()
            
            if not darshan_types:
                st.warning("No darshan types available")
                return
            
            st.markdown('<h2 class="sub-header">Available Darshan Types</h2>', unsafe_allow_html=True)
            
            for darshan in darshan_types:
                class_type = "card-gold" if "VIP" in darshan['DarshanName'] or "Aarti" in darshan['DarshanName'] else "card-purple"
                st.markdown(f'<div class="card {class_type}">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {darshan['DarshanName']}")
                    if darshan['Description']:
                        st.markdown(f"**Description**: {darshan['Description']}")
                    st.markdown(f"**Duration**: {darshan['Duration']} minutes")
                    
                    price_text = "Free" if darshan['StandardPrice'] == 0 else f"₹{darshan['StandardPrice']:.2f} per person"
                    st.markdown(f"**Price**: {price_text}")
                
                with col2:
                    # Get available schedules for this darshan type
                    cursor.execute("""
                    SELECT ScheduleID, ScheduleDate, StartTime, EndTime, RemainingSlots
                    FROM DarshanSchedules
                    WHERE TempleID = %s AND DarshanTypeID = %s 
                      AND ScheduleDate = %s AND IsCancelled = FALSE
                      AND RemainingSlots > 0
                    ORDER BY StartTime
                    """, (selected_temple_id, darshan['DarshanTypeID'], selected_date.strftime('%Y-%m-%d')))
                    
                    schedules = cursor.fetchall()
                    
                    if schedules:
                        schedule_options = [f"{schedule['StartTime']} - {schedule['EndTime']} ({schedule['RemainingSlots']} slots)" 
                                         for schedule in schedules]
                        
                        selected_slot = st.selectbox(
                            f"Select Time Slot",
                            schedule_options,
                            key=f"slot_{darshan['DarshanTypeID']}"
                        )
                        
                        selected_idx = schedule_options.index(selected_slot)
                        selected_schedule = schedules[selected_idx]
                        
                        if st.button("Book Now", key=f"book_{darshan['DarshanTypeID']}"):
                            st.session_state.selected_darshan = darshan
                            st.session_state.selected_schedule = selected_schedule
                            st.session_state.booking_step = "visitor_details"
                    else:
                        st.info("No slots available for this date")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Visitor details
            if 'booking_step' in st.session_state and st.session_state.booking_step == "visitor_details":
                st.markdown('<h2 class="sub-header">Visitor Details</h2>', unsafe_allow_html=True)
                
                darshan = st.session_state.selected_darshan
                schedule = st.session_state.selected_schedule
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Selected Darshan")
                    st.markdown(f"**Type**: {darshan['DarshanName']}")
                    st.markdown(f"**Date**: {schedule['ScheduleDate']}")
                    st.markdown(f"**Time**: {schedule['StartTime']} - {schedule['EndTime']}")
                    st.markdown(f"**Price**: {format_currency(darshan['StandardPrice'])}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Enter Mobile Number")
                    st.markdown("We'll check if you're already registered with us.")
                    phone = st.text_input("Mobile Number", placeholder="10-digit number")
                    
                    if st.button("Check") and phone:
                        cursor.execute("SELECT * FROM Visitors WHERE MobileNumber = %s", (phone,))
                        visitor = cursor.fetchone()
                        if visitor is not None:
                            st.session_state.existing_visitor = visitor
                            st.success(f"Welcome back, {visitor['FirstName']} {visitor['LastName']}!")
                        else:
                            st.warning("Mobile number not found. Please register.")
                            st.session_state.new_visitor = True
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Existing visitor
                if 'existing_visitor' in st.session_state:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Booking Details")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        num_people = st.number_input("Number of People", min_value=1, max_value=10, value=1)
                        special_req = st.text_area("Special Requirements (if any)")
                    
                    with col2:
                        # Calculate total
                        total = num_people * darshan['StandardPrice']
                        
                        st.markdown("### Payment Summary")
                        st.markdown(f"**Price per person**: ₹{darshan['StandardPrice']:.2f}")
                        st.markdown(f"**Number of people**: {num_people}")
                        st.markdown(f"**Total Amount**: ₹{total:.2f}")
                        
                        payment_method = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Net Banking"])
                    
                    if st.button("Proceed to Payment"):
                        with st.spinner("Processing payment..."):
                            time.sleep(2)
                        
                        st.success("Booking successful!")
                        st.session_state.booking_completed = True
                        st.session_state.booking_details = {
                            'darshan_name': darshan['DarshanName'],
                            'date': schedule['ScheduleDate'],
                            'time': f"{schedule['StartTime']} - {schedule['EndTime']}",
                            'num_people': num_people,
                            'total': total,
                            'visitor_name': f"{st.session_state.existing_visitor['FirstName']} {st.session_state.existing_visitor['LastName']}"
                        }
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # New visitor
                elif 'new_visitor' in st.session_state:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Register as New Visitor")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        first_name = st.text_input("First Name")
                        last_name = st.text_input("Last Name")
                        mobile = phone  # Already entered
                        email = st.text_input("Email")
                    
                    with col2:
                        address = st.text_area("Address")
                        city = st.text_input("City")
                        state = st.text_input("State")
                        pincode = st.text_input("PIN Code")
                    
                    if st.button("Register & Continue"):
                        try:
                            # Insert new visitor
                            cursor.execute("""
                            INSERT INTO Visitors (FirstName, LastName, MobileNumber, EmailAddress,
                            Address, City, State, PINCode, LastVisit)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
                            """, (
                                first_name, last_name, mobile, email, address,
                                city, state, pincode
                            ))
                            
                            conn.commit()
                            st.success(f"Registration successful! Welcome, {first_name} {last_name}")
                            
                            # Get the new visitor ID
                            cursor.execute("SELECT LAST_INSERT_ID() as id")
                            result = cursor.fetchone()
                            visitor_id = result['id']
                            
                            # Update session state
                            st.session_state.existing_visitor = {
                                'VisitorID': visitor_id,
                                'FirstName': first_name,
                                'LastName': last_name
                            }
                            
                            # Clean up
                            del st.session_state.new_visitor
                            st.rerun()
                            
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Registration failed: {e}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Booking confirmation
            if 'booking_completed' in st.session_state:
                st.markdown('<div class="success-msg">', unsafe_allow_html=True)
                st.markdown("## 🙏 Booking Confirmed!")
                st.markdown("Your darshan has been successfully booked.")
                st.markdown("</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Booking Details")
                    details = st.session_state.booking_details
                    st.markdown(f"**Booking ID**: BK-{random.randint(10000, 99999)}")
                    st.markdown(f"**Name**: {details['visitor_name']}")
                    st.markdown(f"**Temple**: {selected_temple}")
                    st.markdown(f"**Darshan Type**: {details['darshan_name']}")
                    st.markdown(f"**Date**: {details['date']}")
                    st.markdown(f"**Time**: {details['time']}")
                    st.markdown(f"**Number of People**: {details['num_people']}")
                    st.markdown(f"**Amount Paid**: ₹{details['total']:.2f}")
                    
                    st.markdown("""
                    ### Important Instructions
                    1. Please arrive at least 30 minutes before your scheduled time
                    2. Bring a valid ID proof for verification
                    3. Mobile phones and cameras are not allowed inside the temple
                    4. Follow dress code: Traditional Indian attire preferred
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
                    st.markdown("### Entry Pass")
                    st.markdown("Your booking is confirmed. Show this booking confirmation at the temple entrance.")
                    st.markdown("*This serves as your entry pass. Please save it or take a screenshot.*")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Done"):
                    # Clean up session state
                    for key in ['booking_step', 'selected_darshan', 'selected_schedule', 
                               'existing_visitor', 'new_visitor', 'booking_completed', 
                               'booking_details']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        st.error(f"Error in Book Darshan page: {e}")
        st.write(traceback.format_exc())

# Make Donation page
def show_donation_page():
    try:
        st.markdown('<h1 class="main-header">Make Donation</h1>', unsafe_allow_html=True)
        
        conn = get_database_connection()
        if not conn:
            st.error("Could not connect to database. Please try again later.")
            return
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get temples
            cursor.execute("SELECT * FROM Temples WHERE IsActive = TRUE")
            temples = cursor.fetchall()
            
            if not temples:
                st.error("No temples available in the system")
                return
            
            # Temple selection
            temple_names = [temple['TempleName'] for temple in temples]
            selected_temple = st.selectbox("Select Temple", temple_names)
            selected_temple_id = next((temple['TempleID'] for temple in temples if temple['TempleName'] == selected_temple), None)
            
            if not selected_temple_id:
                st.error("Temple information not available")
                return
            
            # Get donation types
            cursor.execute("""
            SELECT * FROM DonationTypes
            WHERE TempleID = %s AND IsActive = TRUE
            ORDER BY DisplayOrder
            """, (selected_temple_id,))
            
            donation_types = cursor.fetchall()
            
            if not donation_types:
                st.error("No donation types available")
                return
            
            st.markdown('<h2 class="sub-header">Select Donation Type</h2>', unsafe_allow_html=True)
            
            # Pre-select donation type if coming from home page
            default_idx = 0
            if 'donation_type' in st.session_state:
                for idx, d_type in enumerate(donation_types):
                    if d_type['TypeName'] == st.session_state.donation_type:
                        default_idx = idx
                        # Clear the session state
                        del st.session_state.donation_type
                        break
            
            selected_type = st.selectbox("Donation Purpose", 
                                       [d_type['TypeName'] for d_type in donation_types],
                                       index=default_idx)
            
            selected_type_id = next((d_type['DonationTypeID'] for d_type in donation_types 
                                   if d_type['TypeName'] == selected_type), None)
            min_amount = next((d_type['MinimumAmount'] for d_type in donation_types 
                             if d_type['TypeName'] == selected_type), 0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"### {selected_type}")
                st.markdown(f"Minimum donation amount: ₹{min_amount:.2f}")
                
                custom_amount = st.number_input("Enter Amount (₹)", 
                                             min_value=float(min_amount), 
                                             value=float(min_amount),
                                             step=100.0)
                
                is_anonymous = st.checkbox("Make Anonymous Donation")
                st.markdown("</div>", unsafe_allow_html=True)
                
                if is_anonymous:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Anonymous Donor Details")
                    donor_name = st.text_input("Donor Name (Optional)")
                    donor_phone = st.text_input("Donor Phone (Optional)")
                    donor_email = st.text_input("Donor Email (Optional)")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Donor Details")
                    st.markdown("We'll check if you're already registered with us.")
                    phone = st.text_input("Mobile Number", placeholder="10-digit number")
                    
                    if st.button("Check") and phone:
                        cursor.execute("SELECT * FROM Visitors WHERE MobileNumber = %s", (phone,))
                        visitor = cursor.fetchone()
                        if visitor is not None:
                            st.session_state.existing_donor = visitor
                            st.success(f"Welcome back, {visitor['FirstName']} {visitor['LastName']}!")
                        else:
                            st.warning("Mobile number not found. Please register.")
                            st.session_state.new_donor = True
                            st.session_state.donor_phone = phone
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### About this Donation")
                description = next((d_type['Description'] for d_type in donation_types 
                                  if d_type['TypeName'] == selected_type), "")
                if description:
                    st.markdown(description)
                else:
                    st.markdown(f"Your contribution to {selected_type} will help support the temple's activities.")
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### Payment Method")
                payment_method = st.selectbox("Select Payment Method", 
                                           ["UPI", "Credit Card", "Debit Card", "Net Banking"])
                
                st.markdown("### Total Amount")
                st.markdown(f"**Total**: ₹{custom_amount:.2f}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Process donation based on visitor type
                if 'existing_donor' in st.session_state:
                    if st.button("Proceed to Payment", key="donation_payment"):
                        with st.spinner("Processing payment..."):
                            time.sleep(2)
                        
                        # Store donation details for confirmation
                        st.session_state.donation_completed = True
                        st.session_state.donation_details = {
                            'receipt_number': f"DON-{selected_temple_id}-{random.randint(1000, 9999)}-{datetime.now().strftime('%y%m%d')}",
                            'donor_name': f"{st.session_state.existing_donor['FirstName']} {st.session_state.existing_donor['LastName']}",
                            'donation_type': selected_type,
                            'amount': custom_amount,
                            'date': datetime.now().strftime('%d-%m-%Y %H:%M')
                        }
                
                elif is_anonymous and st.button("Proceed to Payment", key="anonymous_donation"):
                    with st.spinner("Processing payment..."):
                        time.sleep(2)
                    
                    # Store donation details for confirmation
                    st.session_state.donation_completed = True
                    st.session_state.donation_details = {
                        'receipt_number': f"DON-{selected_temple_id}-{random.randint(1000, 9999)}-{datetime.now().strftime('%y%m%d')}",
                        'donor_name': donor_name if donor_name else "Anonymous Donor",
                        'donation_type': selected_type,
                        'amount': custom_amount,
                        'date': datetime.now().strftime('%d-%m-%Y %H:%M')
                    }
            
            # New donor registration
            if 'new_donor' in st.session_state and 'new_donor_registered' not in st.session_state:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown("### Register as New Donor")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    first_name = st.text_input("First Name")
                    last_name = st.text_input("Last Name")
                    email = st.text_input("Email")
                    mobile = st.session_state.donor_phone  # Already entered
                
                with col2:
                    address = st.text_area("Address")
                    city = st.text_input("City")
                    state = st.text_input("State")
                    pincode = st.text_input("PIN Code")
                
                if st.button("Register & Continue"):
                    try:
                        # Insert new visitor
                        cursor.execute("""
                        INSERT INTO Visitors (FirstName, LastName, MobileNumber, EmailAddress,
                        Address, City, State, PINCode, LastVisit)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
                        """, (
                            first_name, last_name, mobile, email, address,
                            city, state, pincode
                        ))
                        
                        conn.commit()
                        st.success(f"Registration successful! Welcome, {first_name} {last_name}")
                        
                        # Get the new visitor ID
                        cursor.execute("SELECT LAST_INSERT_ID() as id")
                        result = cursor.fetchone()
                        visitor_id = result['id']
                        
                        # Update session state
                        st.session_state.existing_donor = {
                            'VisitorID': visitor_id,
                            'FirstName': first_name,
                            'LastName': last_name
                        }
                        
                        # Clean up
                        del st.session_state.new_donor
                        st.session_state.new_donor_registered = True
                        st.rerun()
                        
                    except Exception as e:
                        conn.rollback()
                        st.error(f"Registration failed: {e}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Donation Confirmation
            if 'donation_completed' in st.session_state:
                st.markdown('<div class="success-msg">', unsafe_allow_html=True)
                st.markdown("## 🙏 Donation Successful!")
                st.markdown("Thank you for your generous contribution.")
                st.markdown("</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Donation Receipt")
                    details = st.session_state.donation_details
                    st.markdown(f"**Receipt Number**: {details['receipt_number']}")
                    st.markdown(f"**Donor Name**: {details['donor_name']}")
                    st.markdown(f"**Donation Type**: {details['donation_type']}")
                    st.markdown(f"**Amount**: ₹{details['amount']:.2f}")
                    st.markdown(f"**Date**: {details['date']}")
                    
                    st.markdown("""
                    ### Tax Benefits
                    Donations to temples are eligible for tax exemption under Section 80G of the Income Tax Act.
                    Please keep this receipt safe for your tax records.
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
                    st.markdown("### Divine Blessings")
                    st.markdown("""
                    Thank you for your generous donation to Siddhivinayak Temple.
                    
                    May Lord Ganesha bless you with health, wealth, and prosperity.
                    Your contribution will help us continue the sacred traditions and
                    maintain the divine sanctity of the temple.
                    
                    🙏 Om Gam Ganapataye Namaha 🙏
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Done"):
                    # Clean up session state
                    for key in ['donation_completed', 'donation_details', 'existing_donor',
                              'new_donor', 'new_donor_registered']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        st.error(f"Error in Make Donation page: {e}")
        st.write(traceback.format_exc())

# Virtual Puja page
def show_virtual_puja_page():
    try:
        st.markdown('<h1 class="main-header">Book Virtual Puja</h1>', unsafe_allow_html=True)
        
        conn = get_database_connection()
        if not conn:
            st.error("Could not connect to database. Please try again later.")
            return
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get temples
            cursor.execute("SELECT * FROM Temples WHERE IsActive = TRUE")
            temples = cursor.fetchall()
            
            if not temples:
                st.error("No temples available in the system")
                return
            
            # Temple selection
            temple_names = [temple['TempleName'] for temple in temples]
            selected_temple = st.selectbox("Select Temple", temple_names)
            selected_temple_id = next((temple['TempleID'] for temple in temples if temple['TempleName'] == selected_temple), None)
            
            if not selected_temple_id:
                st.error("Temple information not available")
                return
            
            # Get puja types
            cursor.execute("""
            SELECT * FROM PujaTypes
            WHERE TempleID = %s AND IsActive = TRUE
            """, (selected_temple_id,))
            
            puja_types = cursor.fetchall()
            
            if not puja_types:
                st.error("No puja types available")
                return
            
            st.markdown('<h2 class="sub-header">Available Puja Types</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            current_col = col1
            
            for i, puja in enumerate(puja_types):
                # Switch columns
                current_col = col1 if i % 2 == 0 else col2
                
                with current_col:
                    st.markdown('<div class="card card-purple">', unsafe_allow_html=True)
                    st.markdown(f"### {puja['PujaName']}")
                    if puja['Description']:
                        st.markdown(f"**Description**: {puja['Description']}")
                    st.markdown(f"**Duration**: {puja['Duration']} minutes")
                    st.markdown(f"**Price**: ₹{puja['Price']:.2f}")
                    
                    if st.button(f"Book {puja['PujaName']}", key=f"puja_{puja['PujaTypeID']}"):
                        st.session_state.selected_puja = puja
                        st.session_state.puja_step = "details"
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Puja booking details
            if 'puja_step' in st.session_state and st.session_state.puja_step == "details":
                st.markdown('<h2 class="sub-header">Puja Booking Details</h2>', unsafe_allow_html=True)
                
                puja = st.session_state.selected_puja
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Selected Puja")
                    st.markdown(f"**Type**: {puja['PujaName']}")
                    if puja['Description']:
                        st.markdown(f"**Description**: {puja['Description']}")
                    st.markdown(f"**Duration**: {puja['Duration']} minutes")
                    st.markdown(f"**Price**: ₹{puja['Price']:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Schedule Puja")
                    
                    # Date selection
                    min_date = datetime.now() + timedelta(days=1)
                    max_date = datetime.now() + timedelta(days=30)
                    selected_date = st.date_input("Select Date", min_date, min_value=min_date, max_value=max_date)
                    
                    # Time selection
                    time_options = ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", 
                                  "16:00", "17:00", "18:00", "19:00"]
                    selected_time = st.selectbox("Select Time", time_options)
                    
                    devotee_message = st.text_area("Your Message for the Priests")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Enter Mobile Number")
                    st.markdown("We'll check if you're already registered with us.")
                    phone = st.text_input("Mobile Number", placeholder="10-digit number")
                    
                    if st.button("Check") and phone:
                        cursor.execute("SELECT * FROM Visitors WHERE MobileNumber = %s", (phone,))
                        visitor = cursor.fetchone()
                        if visitor is not None:
                            st.session_state.existing_puja_visitor = visitor
                            st.success(f"Welcome back, {visitor['FirstName']} {visitor['LastName']}!")
                        else:
                            st.warning("Mobile number not found. Please register.")
                            st.session_state.new_puja_visitor = True
                            st.session_state.puja_visitor_phone = phone
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if 'existing_puja_visitor' in st.session_state:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown("### Payment Details")
                        
                        st.markdown(f"**Total Amount**: ₹{puja['Price']:.2f}")
                        payment_method = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Net Banking"])
                        
                        if st.button("Book Puja"):
                            with st.spinner("Processing payment..."):
                                time.sleep(2)
                            
                            st.success("Virtual Puja booked successfully!")
                            st.session_state.puja_completed = True
                            st.session_state.puja_details = {
                                'receipt_number': f"PUJA-{random.randint(10000, 99999)}",
                                'puja_name': puja['PujaName'],
                                'date': selected_date.strftime('%Y-%m-%d'),
                                'time': selected_time,
                                'visitor_name': f"{st.session_state.existing_puja_visitor['FirstName']} {st.session_state.existing_puja_visitor['LastName']}",
                                'price': puja['Price'],
                                'devotee_message': devotee_message if devotee_message else "For the wellbeing of my family"
                            }
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    elif 'new_puja_visitor' in st.session_state:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown("### Register as New Visitor")
                        
                        first_name = st.text_input("First Name")
                        last_name = st.text_input("Last Name")
                        email = st.text_input("Email")
                        address = st.text_input("Address")
                        
                        if st.button("Register & Continue"):
                            try:
                                # Insert new visitor (simplified)
                                cursor.execute("""
                                INSERT INTO Visitors (FirstName, LastName, MobileNumber, EmailAddress,
                                Address, LastVisit)
                                VALUES (%s, %s, %s, %s, %s, CURDATE())
                                """, (
                                    first_name, last_name, st.session_state.puja_visitor_phone, 
                                    email, address
                                ))
                                
                                conn.commit()
                                st.success(f"Registration successful! Welcome, {first_name} {last_name}")
                                
                                # Get the new visitor ID
                                cursor.execute("SELECT LAST_INSERT_ID() as id")
                                result = cursor.fetchone()
                                visitor_id = result['id']
                                
                                # Update session state
                                st.session_state.existing_puja_visitor = {
                                    'VisitorID': visitor_id,
                                    'FirstName': first_name,
                                    'LastName': last_name
                                }
                                
                                # Clean up
                                del st.session_state.new_puja_visitor
                                st.rerun()
                                
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Registration failed: {e}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            
            # Puja confirmation
            if 'puja_completed' in st.session_state:
                st.markdown('<div class="success-msg">', unsafe_allow_html=True)
                st.markdown("## 🙏 Virtual Puja Booked!")
                st.markdown("Your virtual puja has been successfully scheduled.")
                st.markdown("</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Puja Details")
                    details = st.session_state.puja_details
                    st.markdown(f"**Puja Type**: {details['puja_name']}")
                    st.markdown(f"**Name**: {details['visitor_name']}")
                    st.markdown(f"**Temple**: {selected_temple}")
                    st.markdown(f"**Date**: {details['date']}")
                    st.markdown(f"**Time**: {details['time']}")
                    st.markdown(f"**Receipt Number**: {details['receipt_number']}")
                    st.markdown(f"**Your Message**: \"{details['devotee_message']}\"")
                    
                    st.markdown("""
                    ### What Happens Next
                    1. Our priests will perform the puja at the scheduled time
                    2. You will receive a video recording of the puja via email
                    3. Prasadam from the puja will be sent to your registered address
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
                    st.markdown("### Important Information")
                    st.markdown("""
                    - The recording will be available within 24 hours after the puja
                    - You can share this recording with your family members
                    - For any assistance, please contact our helpline
                    - Thank you for your devotion and trust in Siddhivinayak Temple
                    """)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Done"):
                    # Clean up session state
                    for key in ['puja_step', 'selected_puja', 'existing_puja_visitor', 
                               'puja_completed', 'puja_details']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        st.error(f"Error in Virtual Puja page: {e}")
        st.write(traceback.format_exc())

# Order Prasadam page  
def show_order_prasadam_page():
    try:
        st.markdown('<h1 class="main-header">Order Temple Prasadam</h1>', unsafe_allow_html=True)
        
        conn = get_database_connection()
        if not conn:
            st.error("Could not connect to database. Please try again later.")
            return
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Get temples
            cursor.execute("SELECT * FROM Temples WHERE IsActive = TRUE")
            temples = cursor.fetchall()
            
            if not temples:
                st.error("No temples available in the system")
                return
            
            # Temple selection
            temple_names = [temple['TempleName'] for temple in temples]
            selected_temple = st.selectbox("Select Temple", temple_names)
            selected_temple_id = next((temple['TempleID'] for temple in temples if temple['TempleName'] == selected_temple), None)
            
            if not selected_temple_id:
                st.error("Temple information not available")
                return
            
            # Get prasadam types
            cursor.execute("""
            SELECT * FROM PrasadamTypes
            WHERE TempleID = %s AND IsActive = TRUE
            """, (selected_temple_id,))
            
            prasadam_types = cursor.fetchall()
            
            if not prasadam_types:
                st.error("No prasadam types available")
                return
            
            st.markdown('<h2 class="sub-header">Available Prasadam</h2>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            current_col = col1
            
            for i, prasadam in enumerate(prasadam_types):
                # Switch columns
                current_col = col1 if i % 2 == 0 else col2
                
                with current_col:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(f"### {prasadam['Name']}")
                    if prasadam['Description']:
                        st.markdown(f"{prasadam['Description']}")
                    st.markdown(f"**Price**: ₹{prasadam['Price']:.2f} per pack")
                    
                    if st.button(f"Order {prasadam['Name']}", key=f"prasadam_{prasadam['PrasadamTypeID']}"):
                        st.session_state.selected_prasadam = prasadam
                        st.session_state.prasadam_step = "details"
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Prasadam order details
            if 'prasadam_step' in st.session_state and st.session_state.prasadam_step == "details":
                st.markdown('<h2 class="sub-header">Order Details</h2>', unsafe_allow_html=True)
                
                prasadam = st.session_state.selected_prasadam
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Selected Prasadam")
                    st.markdown(f"**Type**: {prasadam['Name']}")
                    if prasadam['Description']:
                        st.markdown(f"**Description**: {prasadam['Description']}")
                    st.markdown(f"**Price**: ₹{prasadam['Price']:.2f} per pack")
                    
                    quantity = st.number_input("Quantity", min_value=1, max_value=20, value=1)
                    
                    subtotal = quantity * prasadam['Price']
                    shipping = 100.00
                    total = subtotal + shipping
                    
                    st.markdown("### Order Summary")
                    st.markdown(f"**Subtotal**: ₹{subtotal:.2f}")
                    st.markdown(f"**Shipping & Handling**: ₹{shipping:.2f}")
                    st.markdown(f"**Total**: ₹{total:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Enter Mobile Number")
                    st.markdown("We'll check if you're already registered with us.")
                    phone = st.text_input("Mobile Number", placeholder="10-digit number")
                    
                    if st.button("Check") and phone:
                        cursor.execute("SELECT * FROM Visitors WHERE MobileNumber = %s", (phone,))
                        visitor = cursor.fetchone()
                        if visitor is not None:
                            st.session_state.existing_prasadam_visitor = visitor
                            st.success(f"Welcome back, {visitor['FirstName']} {visitor['LastName']}!")
                        else:
                            st.warning("Mobile number not found. Please register.")
                            st.session_state.new_prasadam_visitor = True
                            st.session_state.prasadam_visitor_phone = phone
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if 'existing_prasadam_visitor' in st.session_state:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown("### Shipping Address")
                        
                        address_line1 = st.text_input("Address Line 1")
                        address_line2 = st.text_input("Address Line 2")
                        city = st.text_input("City")
                        state = st.selectbox("State", ["Maharashtra", "Gujarat", "Karnataka", 
                                                    "Tamil Nadu", "Andhra Pradesh", "Delhi", "Other"])
                        pincode = st.text_input("PIN Code")
                        
                        full_address = f"{address_line1}, {address_line2}, {city}, {state} - {pincode}"
                        
                        payment_method = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Net Banking"])
                        
                        if st.button("Place Order"):
                            with st.spinner("Processing payment..."):
                                time.sleep(2)
                            
                            st.success("Order placed successfully!")
                            
                            # Get estimated delivery
                            estimated_delivery = (datetime.now() + timedelta(days=7)).strftime('%d %b %Y')
                            
                            st.session_state.order_completed = True
                            st.session_state.order_details = {
                                'order_id': f"ORD-{random.randint(10000, 99999)}",
                                'tracking_number': f"TRACK-{random.randint(10000000, 99999999)}",
                                'prasadam_name': prasadam['Name'],
                                'quantity': quantity,
                                'total': total,
                                'shipping_address': full_address,
                                'visitor_name': f"{st.session_state.existing_prasadam_visitor['FirstName']} {st.session_state.existing_prasadam_visitor['LastName']}",
                                'estimated_delivery': estimated_delivery
                            }
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    elif 'new_prasadam_visitor' in st.session_state:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown("### Register as New Visitor")
                        
                        first_name = st.text_input("First Name")
                        last_name = st.text_input("Last Name")
                        email = st.text_input("Email")
                        address = st.text_input("Address")
                        
                        if st.button("Register & Continue"):
                            try:
                                # Insert new visitor (simplified)
                                cursor.execute("""
                                INSERT INTO Visitors (FirstName, LastName, MobileNumber, EmailAddress,
                                Address, LastVisit)
                                VALUES (%s, %s, %s, %s, %s, CURDATE())
                                """, (
                                    first_name, last_name, st.session_state.prasadam_visitor_phone, 
                                    email, address
                                ))
                                
                                conn.commit()
                                st.success(f"Registration successful! Welcome, {first_name} {last_name}")
                                
                                # Get the new visitor ID
                                cursor.execute("SELECT LAST_INSERT_ID() as id")
                                result = cursor.fetchone()
                                visitor_id = result['id']
                                
                                # Update session state
                                st.session_state.existing_prasadam_visitor = {
                                    'VisitorID': visitor_id,
                                    'FirstName': first_name,
                                    'LastName': last_name
                                }
                                
                                # Clean up
                                del st.session_state.new_prasadam_visitor
                                st.rerun()
                                
                            except Exception as e:
                                conn.rollback()
                                st.error(f"Registration failed: {e}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            
            # Order confirmation
            if 'order_completed' in st.session_state:
                st.markdown('<div class="success-msg">', unsafe_allow_html=True)
                st.markdown("## 🙏 Prasadam Order Placed!")
                st.markdown("Your order has been successfully placed and will be shipped soon.")
                st.markdown("</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("### Order Details")
                    details = st.session_state.order_details
                    st.markdown(f"**Order ID**: {details['order_id']}")
                    st.markdown(f"**Tracking Number**: {details['tracking_number']}")
                    st.markdown(f"**Customer**: {details['visitor_name']}")
                    st.markdown(f"**Prasadam**: {details['prasadam_name']}")
                    st.markdown(f"**Quantity**: {details['quantity']}")
                    st.markdown(f"**Total Amount**: ₹{details['total']:.2f}")
                    st.markdown(f"**Shipping Address**: {details['shipping_address']}")
                    st.markdown(f"**Estimated Delivery**: {details['estimated_delivery']}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
                    st.markdown("### Tracking Information")
                    st.markdown(f"Your order with tracking number **{details['tracking_number']}** has been confirmed.")
                    st.markdown("You will receive email notifications as your order progresses.")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("Done"):
                    # Clean up session state
                    for key in ['prasadam_step', 'selected_prasadam', 'existing_prasadam_visitor',
                               'order_completed', 'order_details']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        finally:
            cursor.close()
            conn.close()
    
    except Exception as e:
        st.error(f"Error in Order Prasadam page: {e}")
        st.write(traceback.format_exc())

# View Bookings page
def show_view_bookings_page():
    try:
        st.markdown('<h1 class="main-header">View Your Bookings & Donations</h1>', unsafe_allow_html=True)
        
        # Get visitor details
        st.markdown("### Enter your mobile number to view your bookings")
        phone = st.text_input("Mobile Number", placeholder="10-digit number")
        
        if st.button("Search") and phone:
            conn = get_database_connection()
            if not conn:
                st.error("Could not connect to database. Please try again later.")
                return
            
            cursor = conn.cursor(dictionary=True)
            
            try:
                cursor.execute("SELECT * FROM Visitors WHERE MobileNumber = %s", (phone,))
                visitor = cursor.fetchone()
                
                if visitor is not None:
                    st.success(f"Welcome, {visitor['FirstName']} {visitor['LastName']}!")
                    
                    # Tabs for bookings and donations
                    tabs = st.tabs(["Darshan Bookings", "Donation History"])
                    
                    with tabs[0]:
                        cursor.execute("""
                        SELECT b.BookingID, dt.DarshanName, ds.ScheduleDate, ds.StartTime, ds.EndTime, 
                               b.NumberOfPeople, b.TotalAmount, b.BookingStatus, t.TempleName
                        FROM DarshanBookings b
                        JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                        JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
                        JOIN Temples t ON ds.TempleID = t.TempleID
                        WHERE b.VisitorID = %s
                        ORDER BY ds.ScheduleDate DESC, ds.StartTime
                        """, (visitor['VisitorID'],))
                        
                        bookings = cursor.fetchall()
                        
                        if bookings:
                            st.markdown("### Your Darshan Bookings")
                            
                            for booking in bookings:
                                css_class = "card-gold" if "VIP" in booking["DarshanName"] or "Aarti" in booking["DarshanName"] else "card"
                                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                                
                                st.markdown(f"#### {booking['DarshanName']}")
                                st.markdown(f"**Temple**: {booking['TempleName']}")
                                st.markdown(f"**Date**: {booking['ScheduleDate']}")
                                st.markdown(f"**Time**: {booking['StartTime']} - {booking['EndTime']}")
                                st.markdown(f"**People**: {booking['NumberOfPeople']}")
                                st.markdown(f"**Amount**: ₹{booking['TotalAmount']:.2f}")
                                st.markdown(f"**Status**: {booking['BookingStatus']}")
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("You have no darshan bookings yet.")
                    
                    with tabs[1]:
                        cursor.execute("""
                        SELECT d.DonationID, dt.TypeName, d.DonationDate, d.Amount, d.PaymentMode, 
                               d.ReceiptNumber, t.TempleName
                        FROM Donations d
                        JOIN DonationTypes dt ON d.DonationTypeID = dt.DonationTypeID
                        JOIN Temples t ON d.TempleID = t.TempleID
                        WHERE d.VisitorID = %s
                        ORDER BY d.DonationDate DESC
                        """, (visitor['VisitorID'],))
                        
                        donations = cursor.fetchall()
                        
                        if donations:
                            st.markdown("### Your Donation History")
                            
                            for donation in donations:
                                st.markdown('<div class="card card-gold">', unsafe_allow_html=True)
                                
                                st.markdown(f"#### {donation['TypeName']} Donation")
                                st.markdown(f"**Temple**: {donation['TempleName']}")
                                st.markdown(f"**Date**: {donation['DonationDate']}")
                                st.markdown(f"**Receipt**: {donation['ReceiptNumber']}")
                                st.markdown(f"**Amount**: ₹{donation['Amount']:.2f}")
                                st.markdown(f"**Payment Mode**: {donation['PaymentMode']}")
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("You have no donation history yet.")
                
                else:
                    st.error("No visitor found with this mobile number. Please check and try again.")
            
            finally:
                cursor.close()
                conn.close()
    
    except Exception as e:
        st.error(f"Error in View Bookings page: {e}")
        st.write(traceback.format_exc())

# Admin Dashboard - simplified
# Admin Dashboard - enhanced with more SQL skills
def show_admin_dashboard():
    try:
        st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)
        
        # Simple login
        if 'admin_authenticated' not in st.session_state:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### Admin Login")
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                if username == "admin" and password == "admin123":
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        else:
            conn = get_database_connection()
            if not conn:
                st.error("Could not connect to database. Please try again later.")
                return
            
            cursor = conn.cursor(dictionary=True)
            
            try:
                # Get all temples
                cursor.execute("SELECT * FROM Temples WHERE IsActive = TRUE")
                temples = cursor.fetchall()
                
                if not temples:
                    st.error("No temples available in the system")
                    return
                
                # Temple selection
                temple_names = [temple['TempleName'] for temple in temples]
                selected_temple = st.selectbox("Select Temple", temple_names)
                selected_temple_id = next((temple['TempleID'] for temple in temples if temple['TempleName'] == selected_temple), None)
                
                if not selected_temple_id:
                    st.error("Temple information not available")
                    return
                
                # Admin dashboard tabs
                admin_tabs = st.tabs([
                    "Dashboard Overview", 
                    "Database Explorer", 
                    "Advanced Analytics", 
                    "Custom SQL Query",
                    "Database Maintenance"
                ])
                
                # Dashboard Overview Tab
                with admin_tabs[0]:
                    st.markdown(f"### {selected_temple} Overview")
                    
                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        cursor.execute("SELECT COUNT(*) as count FROM Visitors")
                        visitor_count = cursor.fetchone()['count']
                        
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"### {visitor_count:,}")
                        st.markdown("Registered Visitors")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col2:
                        cursor.execute("""
                        SELECT COUNT(*) as count FROM DarshanBookings b
                        JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                        WHERE ds.TempleID = %s
                        """, (selected_temple_id,))
                        booking_count = cursor.fetchone()['count']
                        
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"### {booking_count:,}")
                        st.markdown("Total Bookings")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col3:
                        cursor.execute("""
                        SELECT SUM(Amount) as total FROM Donations
                        WHERE TempleID = %s
                        """, (selected_temple_id,))
                        result = cursor.fetchone()
                        donation_total = result['total'] if result['total'] else 0
                        
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"### ₹{donation_total:,.2f}")
                        st.markdown("Total Donations")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col4:
                        # Get today's visitor count
                        cursor.execute("""
                        SELECT SUM(NumberOfPeople) as today_visitors
                        FROM DarshanBookings b
                        JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                        WHERE ds.TempleID = %s AND ds.ScheduleDate = CURDATE()
                        """, (selected_temple_id,))
                        result = cursor.fetchone()
                        today_visitors = result['today_visitors'] if result['today_visitors'] else 0
                        
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"### {today_visitors:,}")
                        st.markdown("Today's Visitors")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Recent visitors with more details
                    st.markdown("### Recent Visitors")
                    cursor.execute("""
                    SELECT v.VisitorID, v.FirstName, v.LastName, v.MobileNumber, v.EmailAddress, 
                           v.City, v.State, v.LastVisit, 
                           (SELECT COUNT(*) FROM DarshanBookings WHERE VisitorID = v.VisitorID) as BookingCount,
                           (SELECT SUM(Amount) FROM Donations WHERE VisitorID = v.VisitorID) as TotalDonations
                    FROM Visitors v
                    ORDER BY v.LastVisit DESC
                    LIMIT 10
                    """)
                    
                    recent_visitors = cursor.fetchall()
                    
                    if recent_visitors:
                        visitor_df = pd.DataFrame(recent_visitors)
                        visitor_df['LastVisit'] = pd.to_datetime(visitor_df['LastVisit']).dt.strftime('%Y-%m-%d')
                        visitor_df['TotalDonations'] = visitor_df['TotalDonations'].fillna(0).apply(lambda x: f"₹{x:,.2f}")
                        st.dataframe(visitor_df, use_container_width=True)
                    else:
                        st.info("No recent visitors found")
                    
                    # Booking trends
                    st.markdown("### Booking Trends")
                    cursor.execute("""
                    SELECT ds.ScheduleDate, COUNT(*) as BookingCount, SUM(b.NumberOfPeople) as VisitorCount
                    FROM DarshanBookings b
                    JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                    WHERE ds.TempleID = %s AND ds.ScheduleDate >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY ds.ScheduleDate
                    ORDER BY ds.ScheduleDate
                    """, (selected_temple_id,))
                    
                    booking_trends = cursor.fetchall()
                    
                    if booking_trends:
                        trend_df = pd.DataFrame(booking_trends)
                        trend_df['ScheduleDate'] = pd.to_datetime(trend_df['ScheduleDate'])
                        
                        # Calculate 7-day moving average
                        trend_df['BookingMA7'] = trend_df['BookingCount'].rolling(7, min_periods=1).mean()
                        
                        # Plot
                        st.line_chart(trend_df.set_index('ScheduleDate')[['BookingCount', 'BookingMA7']])
                    else:
                        st.info("No booking trend data available")
                
                # Database Explorer Tab
                with admin_tabs[1]:
                    st.markdown("### Database Explorer")
                    
                    # Get list of all tables
                    cursor.execute("""
                    SELECT table_name AS table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'temple_db'
                    ORDER BY table_name
                    """)
                    tables = [table['table_name'] for table in cursor.fetchall()]
                    selected_table = st.selectbox("Select Table to View", tables)
                    
                    if selected_table:
                        # Get table columns
                        cursor.execute(f"""
                        SELECT column_name, data_type, column_key, is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = 'temple_db' AND table_name = '{selected_table}'
                        ORDER BY ordinal_position
                        """)
                        
                        columns = cursor.fetchall()
                        
                        # Display table structure
                        st.markdown("#### Table Structure")
                        column_df = pd.DataFrame(columns)
                        st.dataframe(column_df, use_container_width=True)
                        
                        # Get row count
                        cursor.execute(f"SELECT COUNT(*) as count FROM {selected_table}")
                        row_count = cursor.fetchone()['count']
                        
                        # Display row count
                        st.markdown(f"*Total Rows*: {row_count:,}")
                        
                        # Set limit for viewing
                        row_limit = st.slider("Number of rows to display", 5, 100, 20)
                        
                        # Get and display data
                        cursor.execute(f"SELECT * FROM {selected_table} LIMIT {row_limit}")
                        table_data = cursor.fetchall()
                        
                        if table_data:
                            data_df = pd.DataFrame(table_data)
                            st.markdown("#### Table Data")
                            st.dataframe(data_df, use_container_width=True)
                        else:
                            st.info(f"No data found in the {selected_table} table")
                    
                    # Database schema visualization
                    st.markdown("### Database Schema")
                    
                    if st.button("Show Database Schema"):
                        # Get all tables and their columns
                        cursor.execute("""
                        SELECT 
                            t.table_name,
                            c.column_name,
                            c.column_key,
                            c.data_type
                        FROM information_schema.tables t
                        JOIN information_schema.columns c ON t.table_name = c.table_name
                        WHERE t.table_schema = 'temple_db' AND c.table_schema = 'temple_db'
                        ORDER BY t.table_name, c.ordinal_position
                        """)
                        
                        schema_data = cursor.fetchall()
                        
                        if schema_data:
                            # Prepare schema text for visualization
                            tables_dict = {}
                            for row in schema_data:
                                table_name = row['table_name']
                                if table_name not in tables_dict:
                                    tables_dict[table_name] = []
                                
                                key_info = ""
                                if row['column_key'] == 'PRI':
                                    key_info = " (PK)"
                                elif row['column_key'] == 'MUL':
                                    key_info = " (FK)"
                                
                                tables_dict[table_name].append(f"{row['column_name']}: {row['data_type']}{key_info}")
                            
                            # Create schema diagram
                            schema_code = "erDiagram\n"
                            
                            # Get foreign key relationships
                            cursor.execute("""
                            SELECT
                                tc.table_name as referencing_table,
                                kcu.column_name as referencing_column,
                                kcu.referenced_table_name,
                                kcu.referenced_column_name
                            FROM information_schema.table_constraints tc
                            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                            WHERE tc.constraint_type = 'FOREIGN KEY'
                            AND tc.table_schema = 'temple_db'
                            """)
                            
                            relations = cursor.fetchall()
                            relations_dict = {}
                            
                            # First, add all tables
                            for table, columns in tables_dict.items():
                                schema_code += f"    {table} {{\n"
                                for column in columns:
                                    schema_code += f"        {column}\n"
                                schema_code += "    }\n"
                            
                            # Then add relations
                            for rel in relations:
                                schema_code += f"    {rel['referencing_table']} ||--o{{ {rel['referenced_table_name']} : references\n"
                            
                            # Display ER diagram
                            st.markdown("#### Entity-Relationship Diagram")
                            st.code(schema_code, language="mermaid")
                        else:
                            st.info("No schema data available")
                
                # Advanced Analytics Tab
                with admin_tabs[2]:
                    st.markdown("### Advanced Analytics")
                    
                    analytics_option = st.selectbox(
                        "Select Analytics Report",
                        [
                            "Top 10 Donors", 
                            "Monthly Donation Trends", 
                            "Visitor Demographics", 
                            "Darshan Type Popularity",
                            "Peak Visiting Hours",
                            "Revenue Analysis",
                            "Top Visitors",
                            "Visitor Retention Analysis",
                            "Geographic Distribution"
                        ]
                    )
                    
                    if analytics_option == "Top 10 Donors":
                        st.markdown("#### Top 10 Donors")
    
                        cursor.execute("""
                        SELECT 
                            CASE 
                                WHEN ANY_VALUE(d.IsAnonymous) = 1 THEN COALESCE(ANY_VALUE(d.DonorName), 'Anonymous Donor')
                                ELSE CONCAT(ANY_VALUE(v.FirstName), ' ', ANY_VALUE(v.LastName))
                            END as DonorName,
                            COALESCE(ANY_VALUE(v.City), 'N/A') as City,
                            COUNT(d.DonationID) as DonationCount,
                            SUM(d.Amount) as TotalAmount,
                            MAX(d.DonationDate) as LastDonation
                        FROM Donations d
                        LEFT JOIN Visitors v ON d.VisitorID = v.VisitorID
                        WHERE d.TempleID = %s
                        GROUP BY DonorName, City
                        ORDER BY TotalAmount DESC
                        LIMIT 10
                        """, (selected_temple_id,))
    
                        top_donors = cursor.fetchall()
    
                        if top_donors:
                            donors_df = pd.DataFrame(top_donors)
                            donors_df['LastDonation'] = pd.to_datetime(donors_df['LastDonation']).dt.strftime('%Y-%m-%d')
                            donors_df['TotalAmount'] = donors_df['TotalAmount'].apply(lambda x: f"₹{x:,.2f}")
                            
                            st.dataframe(donors_df, use_container_width=True)
                            
                            # Create a pie chart of top donors
                            cursor.execute("""
                            SELECT 
                                CASE 
                                    WHEN ANY_VALUE(d.IsAnonymous) = 1 THEN COALESCE(ANY_VALUE(d.DonorName), 'Anonymous Donor')
                                    ELSE CONCAT(ANY_VALUE(v.FirstName), ' ', ANY_VALUE(v.LastName))
                                END as DonorName,
                                SUM(d.Amount) as TotalAmount
                            FROM Donations d
                            LEFT JOIN Visitors v ON d.VisitorID = v.VisitorID
                            WHERE d.TempleID = %s
                            GROUP BY DonorName
                            ORDER BY TotalAmount DESC
                            LIMIT 10
                            """, (selected_temple_id,))
                            
                            pie_data = cursor.fetchall()
                            if pie_data:
                                # Create data for pie chart
                                labels = [row['DonorName'] for row in pie_data]
                                values = [row['TotalAmount'] for row in pie_data]
                                
                                fig, ax = plt.subplots(figsize=(10, 6))
                                ax.pie(values, labels=labels, autopct='%1.1f%%')
                                ax.axis('equal')
                                plt.title('Donation Distribution Among Top 10 Donors')
                                st.pyplot(fig)
                            else:
                                st.info("No donation data available")
                    elif analytics_option == "Monthly Donation Trends":
                        st.markdown("#### Monthly Donation Trends")
                        
                        cursor.execute("""
                        SELECT 
                            DATE_FORMAT(DonationDate, '%Y-%m') as Month,
                            COUNT(*) as DonationCount,
                            SUM(Amount) as TotalAmount,
                            AVG(Amount) as AverageAmount,
                            MIN(Amount) as MinAmount,
                            MAX(Amount) as MaxAmount
                        FROM Donations
                        WHERE TempleID = %s
                        GROUP BY Month
                        ORDER BY Month
                        """, (selected_temple_id,))
                        
                        monthly_trends = cursor.fetchall()
                        
                        if monthly_trends:
                            trends_df = pd.DataFrame(monthly_trends)
                            
                            # Convert to datetime for better plotting
                            trends_df['Month'] = pd.to_datetime(trends_df['Month'] + '-01')
                            
                            # Plot the trend
                            st.markdown("##### Monthly Donation Amount Trend")
                            st.line_chart(trends_df.set_index('Month')['TotalAmount'])
                            
                            # Plot count trend
                            st.markdown("##### Monthly Donation Count Trend")
                            st.line_chart(trends_df.set_index('Month')['DonationCount'])
                            
                            # Display the data table
                            display_df = trends_df.copy()
                            display_df['Month'] = display_df['Month'].dt.strftime('%Y-%m')
                            
                            # Format currency columns
                            for col in ['TotalAmount', 'AverageAmount', 'MinAmount', 'MaxAmount']:
                                display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
                            
                            st.dataframe(display_df, use_container_width=True)
                        else:
                            st.info("No monthly donation data available")
                    
                    elif analytics_option == "Visitor Demographics":
                        st.markdown("#### Visitor Demographics")
                        
                        # State distribution
                        cursor.execute("""
                        SELECT 
                            COALESCE(State, 'Unknown') as State,
                            COUNT(*) as VisitorCount
                        FROM Visitors
                        GROUP BY State
                        ORDER BY VisitorCount DESC
                        """)
                        
                        state_data = cursor.fetchall()
                        
                        if state_data:
                            state_df = pd.DataFrame(state_data)
                            
                            # Create bar chart
                            st.markdown("##### Visitors by State")
                            fig, ax = plt.subplots(figsize=(12, 6))
                            ax.bar(state_df['State'], state_df['VisitorCount'])
                            plt.xticks(rotation=45, ha='right')
                            plt.title('Visitor Distribution by State')
                            plt.tight_layout()
                            st.pyplot(fig)
                        
                        # City distribution (top 10)
                        cursor.execute("""
                        SELECT 
                            COALESCE(City, 'Unknown') as City,
                            COUNT(*) as VisitorCount
                        FROM Visitors
                        WHERE City IS NOT NULL AND City != ''
                        GROUP BY City
                        ORDER BY VisitorCount DESC
                        LIMIT 10
                        """)
                        
                        city_data = cursor.fetchall()
                        
                        if city_data:
                            city_df = pd.DataFrame(city_data)
                            
                            # Create bar chart
                            st.markdown("##### Top 10 Cities by Visitor Count")
                            fig, ax = plt.subplots(figsize=(12, 6))
                            ax.bar(city_df['City'], city_df['VisitorCount'])
                            plt.xticks(rotation=45, ha='right')
                            plt.title('Top 10 Cities by Visitor Count')
                            plt.tight_layout()
                            st.pyplot(fig)
                        
                        # Registration trend over time
                        cursor.execute("""
                        SELECT 
                            DATE_FORMAT(RegistrationDate, '%Y-%m') as Month,
                            COUNT(*) as NewVisitors
                        FROM Visitors
                        GROUP BY Month
                        ORDER BY Month
                        """)
                        
                        reg_data = cursor.fetchall()
                        
                        if reg_data:
                            reg_df = pd.DataFrame(reg_data)
                            reg_df['Month'] = pd.to_datetime(reg_df['Month'] + '-01')
                            
                            st.markdown("##### Visitor Registration Trend")
                            st.line_chart(reg_df.set_index('Month')['NewVisitors'])
                        else:
                            st.info("No visitor registration data available")
                    
                    elif analytics_option == "Darshan Type Popularity":
                        st.markdown("#### Darshan Type Popularity")
                        
                        cursor.execute("""
                        SELECT 
                            dt.DarshanName,
                            COUNT(b.BookingID) as BookingCount,
                            SUM(b.NumberOfPeople) as VisitorCount,
                            SUM(b.TotalAmount) as Revenue
                        FROM DarshanBookings b
                        JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                        JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
                        WHERE ds.TempleID = %s
                        GROUP BY dt.DarshanName
                        ORDER BY VisitorCount DESC
                        """, (selected_temple_id,))
                        
                        darshan_data = cursor.fetchall()
                        
                        if darshan_data:
                            darshan_df = pd.DataFrame(darshan_data)
                            
                            # Create bar chart for visitor count
                            st.markdown("##### Darshan Types by Visitor Count")
                            fig, ax = plt.subplots(figsize=(12, 6))
                            ax.bar(darshan_df['DarshanName'], darshan_df['VisitorCount'])
                            plt.xticks(rotation=45, ha='right')
                            plt.title('Popularity of Darshan Types (by Visitor Count)')
                            plt.tight_layout()
                            st.pyplot(fig)
                            
                            # Create bar chart for revenue
                            st.markdown("##### Darshan Types by Revenue")
                            fig, ax = plt.subplots(figsize=(12, 6))
                            ax.bar(darshan_df['DarshanName'], darshan_df['Revenue'])
                            plt.xticks(rotation=45, ha='right')
                            plt.title('Revenue by Darshan Type')
                            plt.ylabel('Revenue (₹)')
                            plt.tight_layout()
                            st.pyplot(fig)
                            
                            # Display data table
                            display_df = darshan_df.copy()
                            display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"₹{x:,.2f}")
                            st.dataframe(display_df, use_container_width=True)
                        else:
                            st.info("No darshan popularity data available")
                
                # Custom SQL Query Tab
                with admin_tabs[3]:
                    st.markdown("### Custom SQL Query")
                    st.warning("⚠️ Warning: This feature allows direct SQL execution. Use with caution.")
                    
                    # Default queries dropdown
                    default_queries = {
                        "Select a pre-built query": "",
                        "Top 10 Donors (All Time)": """
                            SELECT 
                                CASE 
                                    WHEN d.IsAnonymous = 1 THEN COALESCE(d.DonorName, 'Anonymous Donor')
                                    ELSE CONCAT(v.FirstName, ' ', v.LastName)
                                END as DonorName,
                                COALESCE(v.City, 'N/A') as City,
                                COUNT(d.DonationID) as DonationCount,
                                SUM(d.Amount) as TotalAmount,
                                MAX(d.DonationDate) as LastDonation
                            FROM Donations d
                            LEFT JOIN Visitors v ON d.VisitorID = v.VisitorID
                            GROUP BY DonorName, City
                            ORDER BY TotalAmount DESC
                            LIMIT 10
                        """,
                        "Monthly Booking Trends": """
                            SELECT 
                                DATE_FORMAT(ds.ScheduleDate, '%Y-%m') as Month,
                                COUNT(b.BookingID) as BookingCount,
                                SUM(b.NumberOfPeople) as VisitorCount,
                                SUM(b.TotalAmount) as Revenue
                            FROM DarshanBookings b
                            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                            GROUP BY Month
                            ORDER BY Month
                        """,
                        "Most Popular Time Slots": """
                            SELECT 
                                HOUR(ds.StartTime) as HourOfDay,
                                COUNT(b.BookingID) as BookingCount,
                                SUM(b.NumberOfPeople) as VisitorCount
                            FROM DarshanBookings b
                            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                            GROUP BY HourOfDay
                            ORDER BY VisitorCount DESC
                        """,
                        "Visitors with Multiple Visit Types": """
                            SELECT 
                                CONCAT(v.FirstName, ' ', v.LastName) as VisitorName,
                                v.City,
                                v.State,
                                (SELECT COUNT(*) FROM DarshanBookings WHERE VisitorID = v.VisitorID) as DarshanCount,
                                (SELECT COUNT(*) FROM VirtualPujas WHERE VisitorID = v.VisitorID) as PujaCount,
                                (SELECT COUNT(*) FROM PrasadamOrders WHERE VisitorID = v.VisitorID) as PrasadamCount,
                                (SELECT COUNT(*) FROM Donations WHERE VisitorID = v.VisitorID) as DonationCount
                            FROM Visitors v
                            HAVING (DarshanCount + PujaCount + PrasadamCount + DonationCount) > 2
                            ORDER BY (DarshanCount + PujaCount + PrasadamCount + DonationCount) DESC
                            LIMIT 20
                        """,
                        "Current Month Revenue": """
                            SELECT 
                                'Darshan Bookings' as RevenueSource,
                                SUM(b.TotalAmount) as Revenue
                            FROM DarshanBookings b
                            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
                            WHERE MONTH(b.BookingDateTime) = MONTH(CURRENT_DATE()) 
                              AND YEAR(b.BookingDateTime) = YEAR(CURRENT_DATE())
                            
                            UNION ALL
                            
                            SELECT 
                                'Donations' as RevenueSource,
                                SUM(Amount) as Revenue
                            FROM Donations
                            WHERE MONTH(DonationDate) = MONTH(CURRENT_DATE()) 
                              AND YEAR(DonationDate) = YEAR(CURRENT_DATE())
                            
                            UNION ALL
                            
                            SELECT 
                                'Virtual Pujas' as RevenueSource,
                                SUM(TotalAmount) as Revenue
                            FROM VirtualPujas
                            WHERE MONTH(PujaDate) = MONTH(CURRENT_DATE()) 
                              AND YEAR(PujaDate) = YEAR(CURRENT_DATE())
                            
                            UNION ALL
                            
                            SELECT 
                                'Prasadam Orders' as RevenueSource,
                                SUM(TotalAmount) as Revenue
                            FROM PrasadamOrders
                            WHERE MONTH(OrderDate) = MONTH(CURRENT_DATE()) 
                              AND YEAR(OrderDate) = YEAR(CURRENT_DATE())
                        """,
                        "Yearly Comparison": """
                            SELECT 
                                YEAR(d.DonationDate) as Year,
                                SUM(d.Amount) as TotalDonations,
                                COUNT(d.DonationID) as DonationCount,
                                AVG(d.Amount) as AverageDonation
                            FROM Donations d
                            GROUP BY Year
                            ORDER BY Year
                        """
                    }
                    
                    selected_query = st.selectbox("Select a pre-built query", list(default_queries.keys()))
                    
                    # Initialize session state for custom query
                    if 'custom_query' not in st.session_state:
                        st.session_state.custom_query = default_queries[selected_query]
                    
                    # Update session state when a new default query is selected
                    if selected_query != "Select a pre-built query":
                        st.session_state.custom_query = default_queries[selected_query]
                    
                    # Display query editor
                    st.markdown("#### SQL Query Editor")
                    query = st.text_area("Enter your SQL query", value=st.session_state.custom_query, height=200)
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        execute_btn = st.button("Execute Query")
                    with col2:
                        if query:
                            st.markdown(f"*Query will return results from the `temple_db` database*")
                    
                    if execute_btn and query:
                        try:
                            # Execute the query
                            cursor.execute(query)
                            results = cursor.fetchall()
                            
                            if results:
                                # Convert results to DataFrame
                                results_df = pd.DataFrame(results)
                                
                                # Display results
                                st.markdown("#### Query Results")
                                st.markdown(f"*{len(results)} rows returned*")
                                st.dataframe(results_df, use_container_width=True)
                                
                                # Provide download link
                                csv_buffer = io.StringIO()
                                results_df.to_csv(csv_buffer, index=False)
                                csv_str = csv_buffer.getvalue()
                                
                                st.download_button(
                                    label="Download Results as CSV",
                                    data=csv_str,
                                    file_name="query_results.csv",
                                    mime="text/csv"
                                )
                                
                                # Attempt to create a visualization for the data if appropriate
                                if len(results) > 1 and len(results[0]) >= 2:
                                    st.markdown("#### Automatic Visualization")
                                    
                                    # Check if any columns look like they could be plotted
                                    numeric_cols = results_df.select_dtypes(include=['number']).columns.tolist()
                                    string_cols = results_df.select_dtypes(include=['object']).columns.tolist()
                                    date_cols = []
                                    
                                    # Try to convert string columns to dates
                                    for col in string_cols:
                                        try:
                                            pd.to_datetime(results_df[col])
                                            date_cols.append(col)
                                        except:
                                            pass
                                    
                                    if len(numeric_cols) > 0 and (len(string_cols) > 0 or len(date_cols) > 0):
                                        # We have potential x and y axes for a plot
                                        if len(string_cols) > 0:
                                            x_col = st.selectbox("Select X-axis column", string_cols)
                                        else:
                                            x_col = st.selectbox("Select X-axis column", date_cols)
                                            
                                        y_col = st.selectbox("Select Y-axis column", numeric_cols)
                                        
                                        chart_type = st.selectbox(
                                            "Select chart type", 
                                            ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"]
                                        )
                                        
                                        if st.button("Generate Chart"):
                                            if chart_type == "Bar Chart":
                                                fig, ax = plt.subplots(figsize=(12, 6))
                                                ax.bar(results_df[x_col], results_df[y_col])
                                                plt.xticks(rotation=45, ha='right')
                                                plt.title(f'{y_col} by {x_col}')
                                                plt.tight_layout()
                                                st.pyplot(fig)
                                            
                                            elif chart_type == "Line Chart":
                                                fig, ax = plt.subplots(figsize=(12, 6))
                                                ax.plot(results_df[x_col], results_df[y_col])
                                                plt.xticks(rotation=45, ha='right')
                                                plt.title(f'{y_col} by {x_col}')
                                                plt.tight_layout()
                                                st.pyplot(fig)
                                            
                                            elif chart_type == "Scatter Plot":
                                                fig, ax = plt.subplots(figsize=(12, 6))
                                                ax.scatter(results_df[x_col], results_df[y_col])
                                                plt.xticks(rotation=45, ha='right')
                                                plt.title(f'{y_col} vs {x_col}')
                                                plt.tight_layout()
                                                st.pyplot(fig)
                                            
                                            elif chart_type == "Pie Chart" and len(results_df) <= 10:
                                                fig, ax = plt.subplots(figsize=(10, 10))
                                                ax.pie(results_df[y_col], labels=results_df[x_col], autopct='%1.1f%%')
                                                ax.axis('equal')
                                                plt.title(f'Distribution of {y_col} by {x_col}')
                                                st.pyplot(fig)
                            else:
                                st.info("Query executed successfully, but no results were returned.")
                        
                        except Exception as e:
                            st.error(f"Error executing query: {e}")
                
                # Database Maintenance Tab
                with admin_tabs[4]:
                    st.markdown("### Database Maintenance")
                    
                    # Show current database status
                    st.markdown("#### Database Status")
                    
                    status_col1, status_col2 = st.columns(2)
                    
                    with status_col1:
                        # Get table counts
                        cursor.execute("""
                        SELECT 
                            COUNT(DISTINCT table_name) as table_count
                        FROM information_schema.tables 
                        WHERE table_schema = 'temple_db'
                        """)
                        table_count = cursor.fetchone()['table_count']
                        
                        # Get row counts for key tables
                        cursor.execute("""
                        SELECT 
                            (SELECT COUNT(*) FROM Visitors) as visitors_count,
                            (SELECT COUNT(*) FROM DarshanBookings) as bookings_count,
                            (SELECT COUNT(*) FROM Donations) as donations_count,
                            (SELECT COUNT(*) FROM VirtualPujas) as pujas_count,
                            (SELECT COUNT(*) FROM PrasadamOrders) as orders_count
                        """)
                        row_counts = cursor.fetchone()
                        
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"**Total Tables**: {table_count}")
                        st.markdown(f"**Visitors**: {row_counts['visitors_count']:,}")
                        st.markdown(f"**Darshan Bookings**: {row_counts['bookings_count']:,}")
                        st.markdown(f"**Donations**: {row_counts['donations_count']:,}")
                        st.markdown(f"**Virtual Pujas**: {row_counts['pujas_count']:,}")
                        st.markdown(f"**Prasadam Orders**: {row_counts['orders_count']:,}")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with status_col2:
                        # Get database size
                        cursor.execute("""
                        SELECT 
                            table_name AS table_name,
                            ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                        FROM information_schema.tables
                        WHERE table_schema = 'temple_db'
                        ORDER BY size_mb DESC
                        """)
                        size_data = cursor.fetchall()

                        total_size = sum(row['size_mb'] for row in size_data)

                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f"**Total Database Size**: {total_size:.2f} MB")
                        st.markdown("**Largest Tables:**")
                        for idx, row in enumerate(size_data[:5]):
                            st.markdown(f"- {row['table_name']}: {row['size_mb']:.2f} MB")
                        st.markdown("</div>", unsafe_allow_html=True)
                                            
                    # Add table maintenance tools
                    st.markdown("#### Table Maintenance")
                    
                    maintenance_options = st.multiselect(
                        "Select tables for maintenance",
                        tables,
                        default=[]
                    )
                    
                    if maintenance_options:
                        maintenance_action = st.selectbox(
                            "Select maintenance action",
                            ["Check Table", "Optimize Table", "Analyze Table", "Repair Table"]
                        )
                        
                        if st.button("Execute Maintenance"):
                            results = []
                            
                            for table in maintenance_options:
                                try:
                                    cursor.execute(f"{maintenance_action} {table}")
                                    results.append(f"Successfully executed {maintenance_action} on {table}")
                                except Exception as e:
                                    results.append(f"Error on {table}: {str(e)}")
                            
                            for result in results:
                                st.write(result)
                    
                    # Add query optimization tool
                    st.markdown("#### Query Optimization")
                    
                    optimization_query = st.text_area("Enter a query to analyze", height=100)
                    
                    if optimization_query and st.button("Analyze Query"):
                        try:
                            cursor.execute(f"EXPLAIN {optimization_query}")
                            explain_results = cursor.fetchall()
                            
                            if explain_results:
                                st.markdown("##### Query Execution Plan")
                                explain_df = pd.DataFrame(explain_results)
                                st.dataframe(explain_df, use_container_width=True)
                            else:
                                st.info("No query plan available")
                                
                        except Exception as e:
                            st.error(f"Error analyzing query: {e}")
                    
                    # Add data backup functionality
                    st.markdown("#### Database Backup")
                    
                    backup_tables = st.multiselect(
                        "Select tables to backup (leave empty for all tables)",
                        tables
                    )
                    
                    if st.button("Generate SQL Backup"):
                        tables_to_backup = backup_tables if backup_tables else tables
                        backup_sql = []
                        
                        try:
                            # Generate SQL statements for each table
                            for table in tables_to_backup:
                                # Get table structure
                                cursor.execute(f"SHOW CREATE TABLE {table}")
                                create_table = cursor.fetchone()
                                
                                if create_table and 'Create Table' in create_table:
                                    backup_sql.append(f"-- Table structure for {table}\n")
                                    backup_sql.append(f"DROP TABLE IF EXISTS `{table}`;\n")
                                    backup_sql.append(f"{create_table['Create Table']};\n\n")
                                
                                # Get data
                                cursor.execute(f"SELECT * FROM {table} LIMIT 1000")
                                rows = cursor.fetchall()
                                
                                if rows:
                                    backup_sql.append(f"-- Data for {table}\n")
                                    
                                    # Get column names
                                    columns = [col[0] for col in cursor.description]
                                    column_str = ", ".join([f"`{col}`" for col in columns])
                                    
                                    # Create INSERT statements
                                    values_list = []
                                    for row in rows:
                                        values = []
                                        for val in row.values():
                                            if val is None:
                                                values.append("NULL")
                                            elif isinstance(val, (int, float)):
                                                values.append(str(val))
                                            else:
                                                # Escape string values
                                                val_str = str(val).replace("'", "''")
                                                values.append(f"'{val_str}'")
                                        
                                        values_list.append(f"({', '.join(values)})")
                                    
                                    if values_list:
                                        backup_sql.append(f"INSERT INTO `{table}` ({column_str}) VALUES\n")
                                        backup_sql.append(",\n".join(values_list) + ";\n\n")
                            
                            # Combine all SQL statements
                            full_backup = "".join(backup_sql)
                            
                            # Provide download link
                            st.download_button(
                                label="Download SQL Backup",
                                data=full_backup,
                                file_name=f"temple_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
                                mime="text/plain"
                            )
                            
                            st.success(f"Backup of {len(tables_to_backup)} tables generated successfully!")
                            
                        except Exception as e:
                            st.error(f"Error generating backup: {e}")
                
                # Logout button
                st.markdown("---")
                if st.button("Logout"):
                    del st.session_state.admin_authenticated
                    st.rerun()
            
            finally:
                cursor.close()
                conn.close()
    
    except Exception as e:
        st.error(f"Error in Admin Dashboard: {e}")
        st.write(traceback.format_exc())

# Main app function
def main():
    try:
        # Create sidebar and get selected menu
        menu = create_sidebar()
        
        # Override menu if set in session state
        if 'menu' in st.session_state:
            menu = st.session_state.menu
            del st.session_state.menu
        
        # Show appropriate page based on menu selection
        if menu == "Home":
            show_home_page()
        elif menu == "Book Darshan":
            show_book_darshan_page()
        elif menu == "Make Donation":
            show_donation_page()
        elif menu == "Virtual Puja":
            show_virtual_puja_page()
        elif menu == "Order Prasadam":
            show_order_prasadam_page()
        elif menu == "View Bookings":
            show_view_bookings_page()
        elif menu == "Admin Dashboard":
            show_admin_dashboard()
        else:
            st.title(menu)
            st.write("This page is under development")
    
    except Exception as e:
        st.error(f"Application error: {e}")
        st.write(traceback.format_exc())

if __name__ == "__main__":
    main()