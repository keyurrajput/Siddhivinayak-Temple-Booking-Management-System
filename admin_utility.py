import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import traceback

# Set page configuration
st.set_page_config(
    page_title="Temple Database Manager",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Apply basic styling
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
</style>
""", unsafe_allow_html=True)

# Authentication
def authenticate():
    st.sidebar.title("Database Manager Login")
    phone = st.sidebar.text_input("Admin Phone Number", type="password")
    
    if st.sidebar.button("Login"):
        if phone == "9372735933":  # Using the phone number from your screenshot
            st.session_state.authenticated = True
            st.sidebar.success("Logged in successfully!")
        else:
            st.sidebar.error("Invalid phone number")
    
    return 'authenticated' in st.session_state and st.session_state.authenticated

# Main app
def main():
    st.markdown('<h1 class="main-header">Temple Database Manager</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    if authenticate():
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Select Table to Manage",
            ["Overview", "Visitors", "Darshan Bookings", "Donations", "Virtual Pujas", "Prasadam Orders"]
        )
        
        # Get database connection
        conn = get_database_connection()
        if not conn:
            st.error("Could not connect to database. Please try again later.")
            return
        
        cursor = conn.cursor(dictionary=True)
        
        try:
            if page == "Overview":
                show_overview(cursor)
            elif page == "Visitors":
                manage_visitors(cursor, conn)
            elif page == "Darshan Bookings":
                manage_bookings(cursor, conn)
            elif page == "Donations":
                manage_donations(cursor, conn)
            elif page == "Virtual Pujas":
                manage_pujas(cursor, conn)
            elif page == "Prasadam Orders":
                manage_orders(cursor, conn)
        
        finally:
            cursor.close()
            conn.close()

def show_overview(cursor):
    st.markdown('<h2 class="sub-header">Database Overview</h2>', unsafe_allow_html=True)
    
    # Get table counts
    tables = [
        "Visitors", "DarshanBookings", "Donations", "VirtualPujas", "PrasadamOrders"
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Record Counts")
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                st.write(f"**{table}**: {count} records")
            except Exception as e:
                st.write(f"**{table}**: Error fetching count")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Recent Activity")
        
        # Get most recent entries from each table
        recent_bookings = None
        try:
            cursor.execute("""
            SELECT 'Booking' as type, BookingDateTime as datetime, CONCAT('Booking ID: ', BookingID) as details 
            FROM DarshanBookings ORDER BY BookingDateTime DESC LIMIT 3
            """)
            recent_bookings = cursor.fetchall()
        except Exception:
            pass
        
        recent_donations = None
        try:
            cursor.execute("""
            SELECT 'Donation' as type, DonationDate as datetime, CONCAT('Amount: ₹', Amount) as details 
            FROM Donations ORDER BY DonationDate DESC LIMIT 3
            """)
            recent_donations = cursor.fetchall()
        except Exception:
            pass
        
        # Combine and display
        recent = []
        if recent_bookings:
            recent.extend(recent_bookings)
        if recent_donations:
            recent.extend(recent_donations)
        
        # Sort by datetime
        if recent:
            recent.sort(key=lambda x: x['datetime'], reverse=True)
            
            for item in recent[:5]:  # Show top 5
                st.write(f"**{item['type']}** - {item['datetime']} - {item['details']}")
        else:
            st.write("No recent activity found")
        
        st.markdown("</div>", unsafe_allow_html=True)

def manage_visitors(cursor, conn):
    st.markdown('<h2 class="sub-header">Manage Visitors</h2>', unsafe_allow_html=True)
    
    # Search functionality
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input("Search by Name or Phone Number")
    with search_col2:
        search_by = st.selectbox("Search By", ["Name", "Phone"])
    
    # Execute search
    if search_term:
        if search_by == "Name":
            cursor.execute("""
            SELECT * FROM Visitors
            WHERE FirstName LIKE %s OR LastName LIKE %s
            ORDER BY LastVisit DESC
            """, (f"%{search_term}%", f"%{search_term}%"))
        else:  # Phone
            cursor.execute("""
            SELECT * FROM Visitors
            WHERE MobileNumber LIKE %s
            ORDER BY LastVisit DESC
            """, (f"%{search_term}%",))
    else:
        cursor.execute("""
        SELECT * FROM Visitors
        ORDER BY LastVisit DESC
        LIMIT 100
        """)
    
    visitors = cursor.fetchall()
    
    if visitors:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(visitors)
        
        # Display visitors
        st.dataframe(df, use_container_width=True)
        
        # Delete functionality
        st.markdown("### Delete Visitor")
        
        visitor_ids = [str(visitor['VisitorID']) + " - " + visitor['FirstName'] + " " + visitor['LastName'] for visitor in visitors]
        selected_visitor = st.selectbox("Select Visitor to Delete", visitor_ids)
        
        if selected_visitor:
            visitor_id = int(selected_visitor.split(" - ")[0])
            
            if st.button("Delete Selected Visitor"):
                try:
                    # Check if visitor has any related records
                    related_tables = []
                    
                    cursor.execute("SELECT COUNT(*) as count FROM DarshanBookings WHERE VisitorID = %s", (visitor_id,))
                    if cursor.fetchone()['count'] > 0:
                        related_tables.append("DarshanBookings")
                    
                    cursor.execute("SELECT COUNT(*) as count FROM Donations WHERE VisitorID = %s", (visitor_id,))
                    if cursor.fetchone()['count'] > 0:
                        related_tables.append("Donations")
                    
                    cursor.execute("SELECT COUNT(*) as count FROM VirtualPujas WHERE VisitorID = %s", (visitor_id,))
                    if cursor.fetchone()['count'] > 0:
                        related_tables.append("VirtualPujas")
                    
                    cursor.execute("SELECT COUNT(*) as count FROM PrasadamOrders WHERE VisitorID = %s", (visitor_id,))
                    if cursor.fetchone()['count'] > 0:
                        related_tables.append("PrasadamOrders")
                    
                    if related_tables:
                        st.error(f"Cannot delete visitor because they have records in: {', '.join(related_tables)}")
                        st.info("Delete the related records first, or use cascade delete option below.")
                        
                        if st.checkbox("I understand the risks. Delete visitor and all related records (CASCADE DELETE)"):
                            # Delete from related tables first
                            for table in related_tables:
                                cursor.execute(f"DELETE FROM {table} WHERE VisitorID = %s", (visitor_id,))
                            
                            # Then delete visitor
                            cursor.execute("DELETE FROM Visitors WHERE VisitorID = %s", (visitor_id,))
                            conn.commit()
                            st.success(f"Visitor and all related records deleted successfully!")
                            st.rerun()
                    else:
                        # No related records, safe to delete
                        cursor.execute("DELETE FROM Visitors WHERE VisitorID = %s", (visitor_id,))
                        conn.commit()
                        st.success("Visitor deleted successfully!")
                        st.rerun()
                
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error deleting visitor: {e}")
                    st.write(traceback.format_exc())
    else:
        st.info("No visitors found")

def manage_bookings(cursor, conn):
    st.markdown('<h2 class="sub-header">Manage Darshan Bookings</h2>', unsafe_allow_html=True)
    
    # Search functionality
    search_col1, search_col2, search_col3 = st.columns([2, 2, 1])
    with search_col1:
        search_term = st.text_input("Search by Visitor Name or Phone")
    with search_col2:
        search_date = st.date_input("Search by Date", value=None)
    with search_col3:
        search_button = st.button("Search")
    
    # Build query based on search criteria
    query = """
    SELECT b.BookingID, v.FirstName, v.LastName, v.MobileNumber, 
           dt.DarshanName, ds.ScheduleDate, ds.StartTime, ds.EndTime,
           b.NumberOfPeople, b.TotalAmount, b.BookingStatus
    FROM DarshanBookings b
    JOIN Visitors v ON b.VisitorID = v.VisitorID
    JOIN DarshanSchedules ds ON b.ScheduleID = ds.ScheduleID
    JOIN DarshanTypes dt ON ds.DarshanTypeID = dt.DarshanTypeID
    """
    
    where_clauses = []
    params = []
    
    if search_term:
        where_clauses.append("(v.FirstName LIKE %s OR v.LastName LIKE %s OR v.MobileNumber LIKE %s)")
        params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
    
    if search_date:
        where_clauses.append("ds.ScheduleDate = %s")
        params.append(search_date.strftime('%Y-%m-%d'))
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY ds.ScheduleDate DESC, ds.StartTime"
    
    # Execute query
    cursor.execute(query, params)
    bookings = cursor.fetchall()
    
    if bookings:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(bookings)
        
        # Display bookings
        st.dataframe(df, use_container_width=True)
        
        # Delete functionality
        st.markdown("### Delete Booking")
        
        booking_ids = [str(booking['BookingID']) + " - " + booking['FirstName'] + " " + booking['LastName'] + 
                      " - " + booking['DarshanName'] + " - " + str(booking['ScheduleDate']) for booking in bookings]
        selected_booking = st.selectbox("Select Booking to Delete", booking_ids)
        
        if selected_booking:
            booking_id = int(selected_booking.split(" - ")[0])
            
            if st.button("Delete Selected Booking"):
                try:
                    # Get schedule ID and number of people before deleting
                    cursor.execute("""
                    SELECT ScheduleID, NumberOfPeople FROM DarshanBookings
                    WHERE BookingID = %s
                    """, (booking_id,))
                    booking = cursor.fetchone()
                    
                    if booking:
                        schedule_id = booking['ScheduleID']
                        num_people = booking['NumberOfPeople']
                        
                        # Delete booking
                        cursor.execute("DELETE FROM DarshanBookings WHERE BookingID = %s", (booking_id,))
                        
                        # Update remaining slots
                        cursor.execute("""
                        UPDATE DarshanSchedules SET RemainingSlots = RemainingSlots + %s
                        WHERE ScheduleID = %s
                        """, (num_people, schedule_id))
                        
                        conn.commit()
                        st.success("Booking deleted successfully and slots restored!")
                        st.rerun()
                    else:
                        st.error("Booking not found")
                
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error deleting booking: {e}")
                    st.write(traceback.format_exc())
    else:
        st.info("No bookings found")

def manage_donations(cursor, conn):
    st.markdown('<h2 class="sub-header">Manage Donations</h2>', unsafe_allow_html=True)
    
    # Search functionality
    search_col1, search_col2, search_col3 = st.columns([2, 2, 1])
    with search_col1:
        search_term = st.text_input("Search by Donor Name or Phone")
    with search_col2:
        search_date = st.date_input("Search by Date", value=None)
    with search_col3:
        search_button = st.button("Search")
    
    # Build query based on search criteria
    query = """
    SELECT d.DonationID, COALESCE(v.FirstName, d.DonorName) AS FirstName, 
           COALESCE(v.LastName, '') AS LastName, 
           COALESCE(v.MobileNumber, d.DonorPhone) AS MobileNumber,
           dt.TypeName, d.DonationDate, d.Amount, d.PaymentMode,
           d.ReceiptNumber, d.IsAnonymous
    FROM Donations d
    LEFT JOIN Visitors v ON d.VisitorID = v.VisitorID
    JOIN DonationTypes dt ON d.DonationTypeID = dt.DonationTypeID
    """
    
    where_clauses = []
    params = []
    
    if search_term:
        where_clauses.append("""
        (v.FirstName LIKE %s OR v.LastName LIKE %s OR v.MobileNumber LIKE %s OR
         d.DonorName LIKE %s OR d.DonorPhone LIKE %s)
        """)
        params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", 
                     f"%{search_term}%", f"%{search_term}%"])
    
    if search_date:
        where_clauses.append("DATE(d.DonationDate) = %s")
        params.append(search_date.strftime('%Y-%m-%d'))
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY d.DonationDate DESC"
    
    # Execute query
    cursor.execute(query, params)
    donations = cursor.fetchall()
    
    if donations:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(donations)
        
        # Display donations
        st.dataframe(df, use_container_width=True)
        
        # Delete functionality
        st.markdown("### Delete Donation")
        
        donation_ids = [str(donation['DonationID']) + " - " + donation['FirstName'] + " " + donation['LastName'] + 
                      " - " + donation['TypeName'] + " - ₹" + str(donation['Amount']) for donation in donations]
        selected_donation = st.selectbox("Select Donation to Delete", donation_ids)
        
        if selected_donation:
            donation_id = int(selected_donation.split(" - ")[0])
            
            if st.button("Delete Selected Donation"):
                try:
                    cursor.execute("DELETE FROM Donations WHERE DonationID = %s", (donation_id,))
                    conn.commit()
                    st.success("Donation deleted successfully!")
                    st.rerun()
                
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error deleting donation: {e}")
                    st.write(traceback.format_exc())
    else:
        st.info("No donations found")

def manage_pujas(cursor, conn):
    st.markdown('<h2 class="sub-header">Manage Virtual Pujas</h2>', unsafe_allow_html=True)
    
    # Search functionality
    search_col1, search_col2, search_col3 = st.columns([2, 2, 1])
    with search_col1:
        search_term = st.text_input("Search by Visitor Name or Phone")
    with search_col2:
        search_date = st.date_input("Search by Date", value=None)
    with search_col3:
        search_button = st.button("Search")
    
    # Build query based on search criteria
    query = """
    SELECT vp.PujaID, v.FirstName, v.LastName, v.MobileNumber,
           pt.PujaName, vp.PujaDate, vp.PujaTime, 
           vp.TotalAmount, vp.PujaStatus, vp.ReceiptNumber
    FROM VirtualPujas vp
    JOIN Visitors v ON vp.VisitorID = v.VisitorID
    JOIN PujaTypes pt ON vp.PujaTypeID = pt.PujaTypeID
    """
    
    where_clauses = []
    params = []
    
    if search_term:
        where_clauses.append("(v.FirstName LIKE %s OR v.LastName LIKE %s OR v.MobileNumber LIKE %s)")
        params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
    
    if search_date:
        where_clauses.append("vp.PujaDate = %s")
        params.append(search_date.strftime('%Y-%m-%d'))
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY vp.PujaDate DESC, vp.PujaTime"
    
    # Execute query
    try:
        cursor.execute(query, params)
        pujas = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching pujas: {e}")
        pujas = []
    
    if pujas:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(pujas)
        
        # Display pujas
        st.dataframe(df, use_container_width=True)
        
        # Delete functionality
        st.markdown("### Delete Virtual Puja")
        
        puja_ids = [str(puja['PujaID']) + " - " + puja['FirstName'] + " " + puja['LastName'] + 
                  " - " + puja['PujaName'] + " - " + str(puja['PujaDate']) for puja in pujas]
        selected_puja = st.selectbox("Select Puja to Delete", puja_ids)
        
        if selected_puja:
            puja_id = int(selected_puja.split(" - ")[0])
            
            if st.button("Delete Selected Puja"):
                try:
                    cursor.execute("DELETE FROM VirtualPujas WHERE PujaID = %s", (puja_id,))
                    conn.commit()
                    st.success("Virtual Puja deleted successfully!")
                    st.rerun()
                
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error deleting puja: {e}")
                    st.write(traceback.format_exc())
    else:
        st.info("No virtual pujas found")

def manage_orders(cursor, conn):
    st.markdown('<h2 class="sub-header">Manage Prasadam Orders</h2>', unsafe_allow_html=True)
    
    # Search functionality
    search_col1, search_col2, search_col3 = st.columns([2, 2, 1])
    with search_col1:
        search_term = st.text_input("Search by Visitor Name or Phone")
    with search_col2:
        search_date = st.date_input("Search by Date", value=None)
    with search_col3:
        search_button = st.button("Search")
    
    # Build query based on search criteria
    query = """
    SELECT po.OrderID, v.FirstName, v.LastName, v.MobileNumber,
           pt.Name as PrasadamName, po.OrderDate, po.Quantity, 
           po.TotalAmount, po.OrderStatus, po.TrackingNumber
    FROM PrasadamOrders po
    JOIN Visitors v ON po.VisitorID = v.VisitorID
    JOIN PrasadamTypes pt ON po.PrasadamTypeID = pt.PrasadamTypeID
    """
    
    where_clauses = []
    params = []
    
    if search_term:
        where_clauses.append("(v.FirstName LIKE %s OR v.LastName LIKE %s OR v.MobileNumber LIKE %s)")
        params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
    
    if search_date:
        where_clauses.append("DATE(po.OrderDate) = %s")
        params.append(search_date.strftime('%Y-%m-%d'))
    
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " ORDER BY po.OrderDate DESC"
    
    # Execute query
    try:
        cursor.execute(query, params)
        orders = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        orders = []
    
    if orders:
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(orders)
        
        # Display orders
        st.dataframe(df, use_container_width=True)
        
        # Delete functionality
        st.markdown("### Delete Prasadam Order")
        
        order_ids = [str(order['OrderID']) + " - " + order['FirstName'] + " " + order['LastName'] + 
                   " - " + order['PrasadamName'] + " - " + str(order['OrderDate']) for order in orders]
        selected_order = st.selectbox("Select Order to Delete", order_ids)
        
        if selected_order:
            order_id = int(selected_order.split(" - ")[0])
            
            if st.button("Delete Selected Order"):
                try:
                    cursor.execute("DELETE FROM PrasadamOrders WHERE OrderID = %s", (order_id,))
                    conn.commit()
                    st.success("Prasadam Order deleted successfully!")
                    st.rerun()
                
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error deleting order: {e}")
                    st.write(traceback.format_exc())
    else:
        st.info("No prasadam orders found")

if __name__ == "__main__":
    main()