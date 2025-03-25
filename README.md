# Siddhivinayak Temple Management System

**Streamlining temple operations with comprehensive digital transformation**

## Overview
The Siddhivinayak Temple Management System is a feature-rich web application designed to modernize and digitize operations at Hindu temples. Built with Streamlit and MySQL, this comprehensive platform seamlessly integrates traditional religious practices with modern technology, creating a user-friendly experience for both devotees and temple administrators. The application addresses critical challenges faced by popular temples including crowd management, donation processing, remote accessibility, and administrative oversight through a carefully designed relational database system and intuitive interface.

## Core Features

### 🛕 Darshan Booking
- Easy scheduling of temple visits with multiple darshan options (Regular, VIP, Aarti)
- Real-time availability tracking and capacity management
- Digital QR-coded entry passes
- Special requirements accommodation

### 💰 Online Donations
- Multiple donation categories with customizable amounts
- Support for both anonymous and identified contributions
- Automatic receipt generation for tax purposes
- Complete donation history tracking

### 🙏 Virtual Puja Services
- Remote participation in temple rituals
- Scheduling pujas with personal prayer requests
- Various puja types with transparent pricing
- Seamless integration with prasadam delivery

### 🍽️ Prasadam Ordering
- Browse and order traditional temple offerings
- Doorstep delivery tracking
- Quantity customization and shipping options
- Order history and status updates

### 📊 Administrative Dashboard
- Comprehensive analytics on visitor patterns
- Financial reporting and donation tracking
- Database exploration and management tools
- Custom SQL query capabilities for advanced insights

## Technical Implementation

The system architecture demonstrates advanced database design principles through:

- **Normalized Database Schema**: 12+ interconnected tables with proper relationships
- **Transaction Management**: Ensuring data integrity across related operations
- **Complex Queries**: Advanced SQL implementation for reporting and analytics
- **User Session Management**: Maintaining state across the application flow
- **Data Visualization**: Converting raw data into actionable insights

The application leverages:
- **Backend**: Python with MySQL database integration
- **Frontend**: Streamlit with custom styling for intuitive user experience
- **Data Processing**: Pandas for analytics and reporting
- **Visualization**: Matplotlib and Plotly for interactive charts

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/temple-management-system.git
   cd temple-management-system
   ```

2. **Set up environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python init_db.py
   ```

4. **Launch the application**
   ```bash
   streamlit run app.py
   ```

5. **Access admin dashboard**
   ```
   Username: admin
   Password: admin123
   ```

## Impact and Value

For temples, this system delivers significant operational improvements through:
- Reduced administrative overhead with digitized record-keeping
- Enhanced visitor experience with streamlined processes
- Expanded reach to remote devotees through virtual services
- Improved financial transparency and reporting
- Data-driven decision making capabilities

For devotees, the platform offers:
- Convenience of online booking to avoid long waiting times
- Accessibility to temple services regardless of location
- Personalized experience based on preferences and history
- Transparent record-keeping of all interactions

This project demonstrates how technology can respectfully enhance traditional religious practices while preserving their cultural significance, making them more accessible in the digital age.
