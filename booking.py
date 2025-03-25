#booking.py

import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import random
import qrcode
from io import BytesIO
import base64
from typing import Dict, List, Tuple, Optional, Any, Union

class TempleDatabase:
    """
    Handles all database operations for the Siddhivinayak Temple Booking System
    """
    
    def __init__(self, host="localhost", user="root", password="keyur123", database="temple_db"):
        """Initialize database connection"""
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connect()
    
    def connect(self) -> None:
        """Create a connection to the MySQL database"""
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            raise
    
    def disconnect(self) -> None:
        """Close the database connection"""
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
    
    def init_db(self) -> None:
        """Initialize the database with required tables"""
        try:
            # Create tables
            tables = [
                """
                CREATE TABLE IF NOT EXISTS Temples (
                    TempleID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleName VARCHAR(100) NOT NULL,
                    Location VARCHAR(100) NOT NULL,
                    MaxDailyCapacity INT NOT NULL,
                    FoundingYear INT,
                    Description TEXT,
                    OpeningTime TIME NOT NULL,
                    ClosingTime TIME NOT NULL,
                    ContactNumber VARCHAR(15),
                    EmailAddress VARCHAR(100),
                    WebsiteURL VARCHAR(200),
                    IsActive BOOLEAN DEFAULT TRUE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Visitors (
                    VisitorID INT AUTO_INCREMENT PRIMARY KEY,
                    FirstName VARCHAR(50) NOT NULL,
                    LastName VARCHAR(50) NOT NULL,
                    MobileNumber VARCHAR(15) NOT NULL,
                    EmailAddress VARCHAR(100),
                    RegistrationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Address TEXT,
                    City VARCHAR(50),
                    State VARCHAR(50),
                    PINCode VARCHAR(10),
                    LastVisit DATE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS DarshanTypes (
                    DarshanTypeID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    DarshanName VARCHAR(100) NOT NULL,
                    Description TEXT,
                    Duration INT NOT NULL,
                    MaxCapacity INT NOT NULL,
                    StandardPrice DECIMAL(10,2) NOT NULL,
                    IsSpecial BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Festivals (
                    FestivalID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    FestivalName VARCHAR(100) NOT NULL,
                    Description TEXT,
                    StartDate DATE NOT NULL,
                    EndDate DATE NOT NULL,
                    SpecialDarshanAvailable BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS DarshanSchedules (
                    ScheduleID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    DarshanTypeID INT,
                    FestivalID INT NULL,
                    ScheduleDate DATE NOT NULL,
                    StartTime TIME NOT NULL,
                    EndTime TIME NOT NULL,
                    CurrentCapacity INT NOT NULL,
                    RemainingSlots INT NOT NULL,
                    IsCancelled BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID),
                    FOREIGN KEY (DarshanTypeID) REFERENCES DarshanTypes(DarshanTypeID),
                    FOREIGN KEY (FestivalID) REFERENCES Festivals(FestivalID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS DarshanBookings (
                    BookingID INT AUTO_INCREMENT PRIMARY KEY,
                    ScheduleID INT,
                    VisitorID INT,
                    BookingDateTime DATETIME DEFAULT CURRENT_TIMESTAMP,
                    NumberOfPeople INT NOT NULL,
                    TotalAmount DECIMAL(10,2) NOT NULL,
                    PaymentStatus VARCHAR(20) NOT NULL,
                    PaymentReference VARCHAR(50),
                    QRCode LONGTEXT,
                    BookingStatus VARCHAR(20) DEFAULT 'Confirmed',
                    SpecialRequirements TEXT,
                    FOREIGN KEY (ScheduleID) REFERENCES DarshanSchedules(ScheduleID),
                    FOREIGN KEY (VisitorID) REFERENCES Visitors(VisitorID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS DonationTypes (
                    DonationTypeID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    TypeName VARCHAR(100) NOT NULL,
                    Description TEXT,
                    MinimumAmount DECIMAL(10,2) DEFAULT 0,
                    IsActive BOOLEAN DEFAULT TRUE,
                    DisplayOrder INT,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS Donations (
                    DonationID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    DonationTypeID INT,
                    VisitorID INT NULL,
                    DonationDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Amount DECIMAL(12,2) NOT NULL,
                    PaymentMode VARCHAR(50) NOT NULL,
                    TransactionReference VARCHAR(100),
                    ReceiptNumber VARCHAR(50),
                    IsAnonymous BOOLEAN DEFAULT FALSE,
                    DonorName VARCHAR(100) NULL,
                    DonorPhone VARCHAR(15) NULL,
                    DonorEmail VARCHAR(100) NULL,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID),
                    FOREIGN KEY (DonationTypeID) REFERENCES DonationTypes(DonationTypeID),
                    FOREIGN KEY (VisitorID) REFERENCES Visitors(VisitorID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS PujaTypes (
                    PujaTypeID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    PujaName VARCHAR(100) NOT NULL,
                    Description TEXT,
                    Duration INT NOT NULL,
                    Price DECIMAL(10,2) NOT NULL,
                    IsActive BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS VirtualPujas (
                    PujaID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    VisitorID INT,
                    PujaTypeID INT,
                    PujaDate DATE NOT NULL,
                    PujaTime TIME NOT NULL,
                    TotalAmount DECIMAL(10,2) NOT NULL,
                    PujaStatus VARCHAR(20) DEFAULT 'Scheduled',
                    ReceiptNumber VARCHAR(50),
                    DevoteeMessage TEXT NULL,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID),
                    FOREIGN KEY (VisitorID) REFERENCES Visitors(VisitorID),
                    FOREIGN KEY (PujaTypeID) REFERENCES PujaTypes(PujaTypeID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS PrasadamTypes (
                    PrasadamTypeID INT AUTO_INCREMENT PRIMARY KEY,
                    TempleID INT,
                    Name VARCHAR(100) NOT NULL,
                    Description TEXT,
                    Price DECIMAL(10,2) NOT NULL,
                    IsActive BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS PrasadamOrders (
                    OrderID INT AUTO_INCREMENT PRIMARY KEY,
                    VisitorID INT,
                    TempleID INT,
                    PrasadamTypeID INT,
                    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Quantity INT NOT NULL,
                    TotalAmount DECIMAL(10,2) NOT NULL,
                    ShippingAddress TEXT NOT NULL,
                    TrackingNumber VARCHAR(50) NULL,
                    OrderStatus VARCHAR(20) DEFAULT 'Processing',
                    EstimatedDelivery DATE NULL,
                    FOREIGN KEY (VisitorID) REFERENCES Visitors(VisitorID),
                    FOREIGN KEY (TempleID) REFERENCES Temples(TempleID),
                    FOREIGN KEY (PrasadamTypeID) REFERENCES PrasadamTypes(PrasadamTypeID)
                )
                """
            ]
            
            for table_query in tables:
                self.cursor.execute(table_query)
            
            self.conn.commit()
            
            # Check if we need to insert sample data
            self.cursor.execute("SELECT COUNT(*) as count FROM Temples")
            result = self.cursor.fetchone()
            
            if result['count'] == 0:
                self._insert_sample_data()
            
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")
            raise
    
    def _insert_sample_data(self) -> None:
        """Insert sample data into the database"""
        try:
            # Insert Siddhivinayak Temple
            self.cursor.execute("""
            INSERT INTO Temples (TempleName, Location, MaxDailyCapacity, FoundingYear, 
            Description, OpeningTime, ClosingTime, ContactNumber, EmailAddress, WebsiteURL)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                'Siddhivinayak Temple', 
                'Prabhadevi, Mumbai, Maharashtra', 
                25000, 
                1801,
                'Shree Siddhivinayak Ganapati Mandir is a Hindu temple dedicated to Lord Shri Ganesh. It is located in Prabhadevi, Mumbai, Maharashtra.',
                '05:30', 
                '21:30', 
                '+91-22-24373626', 
                'info@siddhivinayak.org', 
                'https://www.siddhivinayak.org'
            ))
            
            temple_id = self.cursor.lastrowid
            
            # Insert Darshan Types
            darshan_types = [
                ('Regular Darshan', 'Standard darshan for all devotees', 30, 10000, 0.00, False),
                ('VIP Darshan', 'Premium darshan with shorter wait times', 15, 2000, 200.00, True),
                ('Morning Aarti', 'Special morning aarti darshan', 45, 1000, 300.00, True),
                ('Evening Aarti', 'Special evening aarti darshan', 45, 1000, 300.00, True)
            ]
            
            for darshan in darshan_types:
                self.cursor.execute("""
                INSERT INTO DarshanTypes (TempleID, DarshanName, Description, 
                Duration, MaxCapacity, StandardPrice, IsSpecial)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (temple_id, *darshan))
            
            # Insert Donation Types
            donation_types = [
                ('General Donation', 'General donation for temple activities', 101.00, True, 1),
                ('Annadanam', 'Donation for feeding devotees', 501.00, True, 2),
                ('Temple Development', 'For temple renovation and development', 1001.00, True, 3),
                ('Special Puja', 'Donation for special pujas', 1100.00, True, 4)
            ]
            
            for donation in donation_types:
                self.cursor.execute("""
                INSERT INTO DonationTypes (TempleID, TypeName, Description, 
                MinimumAmount, IsActive, DisplayOrder)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (temple_id, *donation))
            
            # Insert Festivals
            festivals = [
                ('Ganesh Chaturthi', 'Main festival celebrating Lord Ganesh\'s birthday', 
                 '2025-09-02', '2025-09-12', True),
                ('Angarika Chaturthi', 'Monthly festival falling on Tuesdays',
                 '2025-01-14', '2025-01-14', True),
                ('Maghi Ganesh Jayanti', 'Celebration of Lord Ganesh\'s birth',
                 '2025-02-15', '2025-02-15', True)
            ]
            
            for festival in festivals:
                self.cursor.execute("""
                INSERT INTO Festivals (TempleID, FestivalName, Description, 
                StartDate, EndDate, SpecialDarshanAvailable)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (temple_id, *festival))
            
            # Insert Puja Types
            puja_types = [
                ('Ganesh Puja', 'Basic puja to Lord Ganesh', 30, 501.00, True),
                ('Abhishekam', 'Sacred bathing ritual of the deity', 45, 1001.00, True),
                ('Satyanarayan Puja', 'Full puja ritual with havan', 60, 1501.00, True)
            ]
            
            for puja in puja_types:
                self.cursor.execute("""
                INSERT INTO PujaTypes (TempleID, PujaName, Description, 
                Duration, Price, IsActive)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (temple_id, *puja))
            
            # Insert Prasadam Types
            prasadam_types = [
                ('Modak', 'Traditional sweet offering to Lord Ganesh', 101.00, True),
                ('Laddoo', 'Sweet ball-shaped prasadam', 51.00, True),
                ('Prasad Thali', 'Complete prasadam thali with multiple items', 201.00, True)
            ]
            
            for prasadam in prasadam_types:
                self.cursor.execute("""
                INSERT INTO PrasadamTypes (TempleID, Name, Description, 
                Price, IsActive)
                VALUES (%s, %s, %s, %s, %s)
                """, (temple_id, *prasadam))
            
            # Create sample Darshan schedules for the next 7 days
            for i in range(7):
                schedule_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
                
                # Regular Darshan
                self.cursor.execute("""
                INSERT INTO DarshanSchedules (TempleID, DarshanTypeID, ScheduleDate, 
                StartTime, EndTime, CurrentCapacity, RemainingSlots)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    temple_id, 
                    1,  # Regular Darshan
                    schedule_date, 
                    '05:30', 
                    '21:30', 
                    10000, 
                    10000
                ))
                
                # VIP Darshan - Morning and Evening
                for start_time, end_time in [('07:00', '10:00'), ('16:00', '19:00')]:
                    self.cursor.execute("""
                    INSERT INTO DarshanSchedules (TempleID, DarshanTypeID, ScheduleDate, 
                    StartTime, EndTime, CurrentCapacity, RemainingSlots)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        temple_id, 
                        2,  # VIP Darshan
                        schedule_date, 
                        start_time, 
                        end_time, 
                        2000, 
                        2000
                    ))
                
                # Morning Aarti
                self.cursor.execute("""
                INSERT INTO DarshanSchedules (TempleID, DarshanTypeID, ScheduleDate, 
                StartTime, EndTime, CurrentCapacity, RemainingSlots)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    temple_id, 
                    3,  # Morning Aarti
                    schedule_date, 
                    '05:30', 
                    '06:15', 
                    1000, 
                    1000
                ))
                
                # Evening Aarti
                self.cursor.execute("""
                INSERT INTO DarshanSchedules (TempleID, DarshanTypeID, ScheduleDate, 
                StartTime, EndTime, CurrentCapacity, RemainingSlots)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    temple_id, 
                    4,  # Evening Aarti
                    schedule_date, 
                    '19:00', 
                    '19:45', 
                    1000, 
                    1000
                ))
            
            self.conn.commit()
            print("Sample data inserted successfully")
            
        except mysql.connector.Error as err:
            print(f"Error inserting sample data: {err}")
            self.conn.rollback()
            raise
    
    # Visitor-related methods
    def get_visitor_by_phone(self, phone: str) -> Optional[Dict]:
        """Get visitor details by phone number"""
        try:
            self.cursor.execute(
                "SELECT * FROM Visitors WHERE MobileNumber = %s", (phone,)
            )
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(f"Error getting visitor: {err}")
            return None
    
    def register_visitor(self, first_name: str, last_name: str, mobile: str, 
                        email: str = None, address: str = None, city: str = None, 
                        state: str = None, pin: str = None) -> Optional[int]:
        """Register a new visitor"""
        try:
            query = """
            INSERT INTO Visitors (FirstName, LastName, MobileNumber, EmailAddress,
            Address, City, State, PINCode, LastVisit)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURDATE())
            """
            
            self.cursor.execute(query, (
                first_name, last_name, mobile, email, address,
                city, state, pin
            ))
            
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            print(f"Error registering visitor: {err}")
            self.conn.rollback()
            return None
    
    def update_visitor_last_visit(self, visitor_id: int) -> bool:
        """Update the last visit date for a visitor"""
        try:
            self.cursor.execute(
                "UPDATE Visitors SET LastVisit = CURDATE() WHERE VisitorID = %s", 
                (visitor_id,)
            )
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error updating visitor: {err}")
            self.conn.rollback()
            return False
    
    # Temple-related methods
    def get_temples(self) -> List[Dict]:
        """Get list of all active temples"""
        try:
            self.cursor.execute(
                "SELECT * FROM Temples WHERE IsActive = TRUE"
            )
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting temples: {err}")
            return []
    
    # Darshan-related methods
    def get_darshan_types(self, temple_id: int) -> List[Dict]:
        """Get darshan types for a temple"""
        try:
            self.cursor.execute(
                "SELECT * FROM DarshanTypes WHERE TempleID = %s", 
                (temple_id,)
            )
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting darshan types: {err}")
            return []
    
    def get_darshan_schedules(self, temple_id: int, date: str = None) -> List[Dict]:
        """Get darshan schedules for a temple, optionally filtered by date"""
        try:
            if date:
                query = """
                SELECT ds.ScheduleID, dt.DarshanName, ds.ScheduleDate, ds.StartTime, ds.EndTime, 
                       ds.RemainingSlots, dt.StandardPrice, dt.Duration
                FROM DarshanSchedules ds
                JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
                WHERE ds.TempleID = %s AND ds.ScheduleDate = %s AND ds.IsCancelled = FALSE 
                      AND ds.RemainingSlots > 0
                ORDER BY ds.StartTime
                """
                params = (temple_id, date)
            else:
                query = """
                SELECT ds.ScheduleID, dt.DarshanName, ds.ScheduleDate, ds.StartTime, ds.EndTime, 
                       ds.RemainingSlots, dt.StandardPrice, dt.Duration
                FROM DarshanSchedules ds
                JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
                WHERE ds.TempleID = %s AND ds.ScheduleDate >= CURDATE() AND ds.IsCancelled = FALSE 
                      AND ds.RemainingSlots > 0
                ORDER BY ds.ScheduleDate, ds.StartTime
                """
                params = (temple_id,)
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting darshan schedules: {err}")
            return []
    
    def get_schedule_details(self, schedule_id: int) -> Optional[Dict]:
        """Get details for a specific schedule"""
        try:
            query = """
            SELECT ds.*, dt.DarshanName, dt.StandardPrice, dt.Duration
            FROM DarshanSchedules ds
            JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
            WHERE ds.ScheduleID = %s
            """
            self.cursor.execute(query, (schedule_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error getting schedule details: {err}")
            return None
    
    def book_darshan(self, schedule_id: int, visitor_id: int, num_people: int, 
                    special_req: str = None) -> Tuple[Optional[int], Optional[str]]:
        """Book a darshan slot"""
        try:
            # Get schedule details
            schedule = self.get_schedule_details(schedule_id)
            
            if not schedule:
                return None, "Schedule not found"
            
            if schedule['RemainingSlots'] < num_people:
                return None, "Not enough slots available"
            
            total_amount = schedule['StandardPrice'] * num_people
            
            payment_ref = f"PAY-{random.randint(10000000, 99999999)}"
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f"BOOK-{schedule_id}-{visitor_id}-{num_people}-{payment_ref}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered)
            qr_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            # Insert booking
            query = """
            INSERT INTO DarshanBookings (ScheduleID, VisitorID, NumberOfPeople, TotalAmount,
            PaymentStatus, PaymentReference, QRCode, SpecialRequirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                schedule_id, visitor_id, num_people, total_amount, "Completed", 
                payment_ref, qr_img_str, special_req
            ))
            
            booking_id = self.cursor.lastrowid
            
            # Update remaining slots
            self.cursor.execute(
                "UPDATE DarshanSchedules SET RemainingSlots = RemainingSlots - %s WHERE ScheduleID = %s",
                (num_people, schedule_id)
            )
            
            # Update visitor's last visit
            self.update_visitor_last_visit(visitor_id)
            
            self.conn.commit()
            return booking_id, qr_img_str
        except mysql.connector.Error as err:
            print(f"Error booking darshan: {err}")
            self.conn.rollback()
            return None, str(err)
    
    def get_booking_details(self, booking_id: int) -> Optional[Dict]:
        """Get details for a specific booking"""
        try:
            query = """
            SELECT b.BookingID, v.FirstName, v.LastName, dt.DarshanName, 
                   ds.ScheduleDate, ds.StartTime, ds.EndTime, b.NumberOfPeople,
                   b.TotalAmount, b.PaymentStatus, b.BookingStatus, b.QRCode,
                   t.TempleName, t.Location
            FROM DarshanBookings b
            JOIN Visitors v ON b.VisitorID = v.VisitorID
            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
            JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
            JOIN Temples t ON ds.TempleID = t.TempleID
            WHERE b.BookingID = %s
            """
            self.cursor.execute(query, (booking_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error getting booking details: {err}")
            return None
    
    def get_visitor_bookings(self, visitor_id: int) -> List[Dict]:
        """Get all bookings for a visitor"""
        try:
            query = """
            SELECT b.BookingID, dt.DarshanName, ds.ScheduleDate, ds.StartTime, ds.EndTime, 
                   b.NumberOfPeople, b.TotalAmount, b.BookingStatus, t.TempleName
            FROM DarshanBookings b
            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
            JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
            JOIN Temples t ON ds.TempleID = t.TempleID
            WHERE b.VisitorID = %s
            ORDER BY ds.ScheduleDate DESC, ds.StartTime
            """
            self.cursor.execute(query, (visitor_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting visitor bookings: {err}")
            return []
    
    # Donation-related methods
    def get_donation_types(self, temple_id: int) -> List[Dict]:
        """Get donation types for a temple"""
        try:
            query = """
            SELECT DonationTypeID, TypeName, Description, MinimumAmount
            FROM DonationTypes
            WHERE TempleID = %s AND IsActive = TRUE
            ORDER BY DisplayOrder
            """
            self.cursor.execute(query, (temple_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting donation types: {err}")
            return []
    
    def make_donation(self, temple_id: int, donation_type_id: int, visitor_id: int = None, 
                     amount: float = 0, payment_mode: str = "", transaction_ref: str = None,
                     is_anonymous: bool = False, donor_name: str = None, donor_phone: str = None, 
                     donor_email: str = None) -> Tuple[Optional[int], Optional[str]]:
        """Record a donation"""
        try:
            query = """
            INSERT INTO Donations (TempleID, DonationTypeID, VisitorID, Amount,
            PaymentMode, TransactionReference, IsAnonymous, DonorName, DonorPhone, DonorEmail)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                temple_id, donation_type_id, visitor_id, amount, payment_mode, transaction_ref,
                is_anonymous, donor_name, donor_phone, donor_email
            ))
            
            donation_id = self.cursor.lastrowid
            
            # Generate receipt number
            receipt_number = f"DON-{temple_id}-{donation_id}-{datetime.now().strftime('%y%m%d')}"
            
            self.cursor.execute(
                "UPDATE Donations SET ReceiptNumber = %s WHERE DonationID = %s",
                (receipt_number, donation_id)
            )
            
            # Update visitor's last visit if applicable
            if visitor_id:
                self.update_visitor_last_visit(visitor_id)
            
            self.conn.commit()
            return donation_id, receipt_number
        except mysql.connector.Error as err:
            print(f"Error making donation: {err}")
            self.conn.rollback()
            return None, str(err)
    
    def get_visitor_donations(self, visitor_id: int) -> List[Dict]:
        """Get all donations for a visitor"""
        try:
            query = """
            SELECT d.DonationID, dt.TypeName, d.DonationDate, d.Amount, d.PaymentMode, 
                   d.ReceiptNumber, t.TempleName
            FROM Donations d
            JOIN DonationTypes dt ON d.DonationTypeID = dt.DonationTypeID
            JOIN Temples t ON d.TempleID = t.TempleID
            WHERE d.VisitorID = %s
            ORDER BY d.DonationDate DESC
            """
            self.cursor.execute(query, (visitor_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting visitor donations: {err}")
            return []
    
    # Virtual Puja methods
    def get_puja_types(self, temple_id: int) -> List[Dict]:
        """Get available puja types for a temple"""
        try:
            query = """
            SELECT * FROM PujaTypes 
            WHERE TempleID = %s AND IsActive = TRUE
            """
            self.cursor.execute(query, (temple_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting puja types: {err}")
            return []
    
    def book_virtual_puja(self, temple_id: int, visitor_id: int, puja_type_id: int, 
                         puja_date: str, puja_time: str, total_amount: float,
                         devotee_message: str = None) -> Tuple[Optional[int], Optional[str]]:
        """Book a virtual puja"""
        try:
            # Process payment
            receipt_number = f"PUJA-{random.randint(10000000, 99999999)}"
            
            query = """
            INSERT INTO VirtualPujas (TempleID, VisitorID, PujaTypeID, PujaDate, PujaTime,
            TotalAmount, DevoteeMessage, ReceiptNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                temple_id, visitor_id, puja_type_id, puja_date, puja_time,
                total_amount, devotee_message, receipt_number
            ))
            
            puja_id = self.cursor.lastrowid
            
            # Update visitor's last visit
            self.update_visitor_last_visit(visitor_id)
            
            self.conn.commit()
            return puja_id, receipt_number
        except mysql.connector.Error as err:
            print(f"Error booking virtual puja: {err}")
            self.conn.rollback()
            return None, str(err)
    
    def get_visitor_pujas(self, visitor_id: int) -> List[Dict]:
        """Get all virtual pujas for a visitor"""
        try:
            query = """
            SELECT vp.*, pt.PujaName, pt.Description 
            FROM VirtualPujas vp
            JOIN PujaTypes pt ON vp.PujaTypeID = pt.PujaTypeID
            WHERE vp.VisitorID = %s
            ORDER BY vp.PujaDate DESC, vp.PujaTime DESC
            """
            self.cursor.execute(query, (visitor_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting visitor pujas: {err}")
            return []
    
    # Prasadam Order methods
    def get_prasadam_types(self, temple_id: int) -> List[Dict]:
        """Get available prasadam types for a temple"""
        try:
            query = """
            SELECT * FROM PrasadamTypes
            WHERE TempleID = %s AND IsActive = TRUE
            """
            self.cursor.execute(query, (temple_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting prasadam types: {err}")
            return []
    
    def order_prasadam(self, visitor_id: int, temple_id: int, prasadam_type_id: int,
                      quantity: int, total_amount: float, shipping_address: str) -> Tuple[Optional[int], Optional[str]]:
        """Place an order for prasadam"""
        try:
            estimated_delivery = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            query = """
            INSERT INTO PrasadamOrders (VisitorID, TempleID, PrasadamTypeID, Quantity,
            TotalAmount, ShippingAddress, EstimatedDelivery)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                visitor_id, temple_id, prasadam_type_id, quantity,
                total_amount, shipping_address, estimated_delivery
            ))
            
            order_id = self.cursor.lastrowid
            tracking_number = f"TRACK-{random.randint(10000000, 99999999)}"
            
            self.cursor.execute(
                "UPDATE PrasadamOrders SET TrackingNumber = %s WHERE OrderID = %s",
                (tracking_number, order_id)
            )
            
            self.conn.commit()
            return order_id, tracking_number
        except mysql.connector.Error as err:
            print(f"Error ordering prasadam: {err}")
            self.conn.rollback()
            return None, str(err)
    
    def get_visitor_prasadam_orders(self, visitor_id: int) -> List[Dict]:
        """Get all prasadam orders for a visitor"""
        try:
            query = """
            SELECT po.*, pt.Name as PrasadamName, pt.Description, pt.Price
            FROM PrasadamOrders po
            JOIN PrasadamTypes pt ON po.PrasadamTypeID = pt.PrasadamTypeID
            WHERE po.VisitorID = %s
            ORDER BY po.OrderDate DESC
            """
            self.cursor.execute(query, (visitor_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting visitor prasadam orders: {err}")
            return []
    
    # Festival methods
    def get_upcoming_festivals(self, temple_id: int) -> List[Dict]:
        """Get upcoming festivals for a temple"""
        try:
            query = """
            SELECT * FROM Festivals
            WHERE TempleID = %s AND EndDate >= CURDATE()
            ORDER BY StartDate
            """
            self.cursor.execute(query, (temple_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting upcoming festivals: {err}")
            return []
    
    # Admin dashboard methods
    def get_dashboard_data(self, temple_id: int) -> Dict[str, Any]:
        """Get data for admin dashboard"""
        try:
            result = {}
            
            # Today's bookings
            today = datetime.now().strftime('%Y-%m-%d')
            bookings_query = """
            SELECT COUNT(*) as today_bookings, SUM(b.NumberOfPeople) as today_visitors,
                   SUM(b.TotalAmount) as today_booking_amount
            FROM DarshanBookings b
            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
            WHERE ds.TempleID = %s AND ds.ScheduleDate = %s
            """
            self.cursor.execute(bookings_query, (temple_id, today))
            result['bookings'] = self.cursor.fetchone()
            
            # Today's donations
            donations_query = """
            SELECT COUNT(*) as today_donations, SUM(Amount) as today_amount
            FROM Donations
            WHERE TempleID = %s AND DATE(DonationDate) = %s
            """
            self.cursor.execute(donations_query, (temple_id, today))
            result['donations'] = self.cursor.fetchone()
            
            # Recent visitors
            visitors_query = """
            SELECT v.VisitorID, v.FirstName, v.LastName, v.MobileNumber, v.LastVisit
            FROM Visitors v
            JOIN DarshanBookings b ON v.VisitorID = b.VisitorID
            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
            WHERE ds.TempleID = %s
            GROUP BY v.VisitorID
            ORDER BY v.LastVisit DESC
            LIMIT 10
            """
            self.cursor.execute(visitors_query, (temple_id,))
            result['recent_visitors'] = self.cursor.fetchall()
            
            # Darshan bookings by type
            darshan_query = """
            SELECT dt.DarshanName, COUNT(b.BookingID) as booking_count
            FROM DarshanBookings b
            JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
            JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
            WHERE ds.TempleID = %s
            GROUP BY dt.DarshanName
            """
            self.cursor.execute(darshan_query, (temple_id,))
            result['darshan_stats'] = self.cursor.fetchall()
            
            # Donation statistics
            donation_query = """
            SELECT dt.TypeName, COUNT(d.DonationID) as donation_count, SUM(d.Amount) as total_amount
            FROM Donations d
            JOIN DonationTypes dt ON d.DonationTypeID = dt.DonationTypeID
            WHERE d.TempleID = %s
            GROUP BY dt.TypeName
            """
            self.cursor.execute(donation_query, (temple_id,))
            result['donation_stats'] = self.cursor.fetchall()
            
            return result
        except mysql.connector.Error as err:
            print(f"Error getting dashboard data: {err}")
            return {}

# Utility functions
def format_currency(amount: float) -> str:
    """Format a number as INR currency"""
    if amount == 0:
        return "Free"
    return f"₹{amount:,.2f}"

def generate_qr_code_image(data: str) -> str:
    """Generate a QR code image and return base64 encoded string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")