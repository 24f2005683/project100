# Vehicle Parking System

A complete web-based parking management system built with Python Flask, featuring user and admin interfaces with real-time spot management and revenue tracking.

## 🚀 Features

### User Features
- **Smart Login System**: Automatic user/admin detection based on email
- **Real-time Parking Booking**: Find and book available parking spots instantly
- **Vehicle Validation**: Prevents duplicate vehicle bookings across the system
- **Parking History**: Complete booking records with arrival/departure timestamps
- **Cost Calculation**: Automatic fee calculation based on parking duration
- **Visual Dashboard**: HTML/CSS charts showing personal parking statistics

### Admin Features
- **System Overview**: Real-time statistics and occupancy tracking
- **Parking Lot Management**: Add, edit, and manage parking facilities
- **Spot Management**: Create and manage individual parking spots
- **User Management**: View all registered users and their activities
- **Revenue Analytics**: Track total earnings and system performance
- **Parking History**: Complete reservation records with filtering options

## 🛠️ Technology Stack

- **Backend**: Python Flask 2.3.3
- **Database**: SQLite with Flask-SQLAlchemy 3.0.5
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Authentication**: Custom Base64 encoding (no external libraries)
- **Architecture**: MVC Pattern with Blueprint structure

## 🎯 Unique Features

### 1. Smart User Type Detection
The system automatically detects whether a user is an admin or regular user based on their email address, eliminating the need for separate login pages.

### 2. JavaScript-Free Implementation
All interactive features are built using pure HTML/CSS and server-side processing, making the application lightweight and fast.

### 3. Real-Time Spot Management
Parking spots are automatically updated when booked or released, with real-time availability tracking.

### 4. Custom Revenue Algorithm
Duration-based pricing with minimum charge logic and automatic cost calculation.

### 5. Visual Data Representation
Custom HTML/CSS charts for both user and admin dashboards without requiring JavaScript libraries.

## 📊 Database Schema

### Core Tables
- **Users**: User registration and profile information
- **Admins**: Administrator accounts
- **ParkingLots**: Parking facility information
- **ParkingSpots**: Individual spot management
- **Reservations**: Booking records with timestamps

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access the application at `http://localhost:5600`

### Default Admin Account
- **Email**: admin@parking.com
- **Password**: admin123

## 📱 Usage

### For Users
1. Register a new account
2. Login with your credentials
3. Browse available parking lots
4. Book a parking spot with your vehicle number
5. View your parking history and current status
6. Release your spot when done

### For Admins
1. Login with admin credentials
2. Access the admin dashboard for system overview
3. Manage parking lots and spots
4. View user activities and parking history
5. Monitor revenue and system performance

## 🎨 Design Features

- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Clean Interface**: Modern Bootstrap 5 styling with custom CSS
- **Visual Feedback**: Color-coded status indicators and progress charts
- **User-Friendly Navigation**: Intuitive menu structure and clear call-to-action buttons

## 🔒 Security Features

- **Session Management**: Secure user and admin session handling
- **Input Validation**: Form validation and data sanitization
- **Duplicate Prevention**: Vehicle booking validation to prevent conflicts
- **Access Control**: Role-based access to admin features

## 📈 Business Logic

### Parking Fee Calculation
- Minimum 1-hour charge
- Hourly rate based on parking lot pricing
- Automatic duration calculation from timestamps

### Spot Availability Management
- Real-time status updates
- Automatic availability recalculation
- Conflict prevention for vehicle bookings

### User Experience Optimization
- Smart form validation
- Clear error messages
- Intuitive navigation flow

## 🤝 AI Assistance Acknowledgment

This project was developed with approximately 20% AI assistance for conceptualization and to enhance the application's attractiveness and user experience. The AI helped with:
- Initial project structure planning
- UI/UX design suggestions
- Code optimization recommendations
- Feature enhancement ideas

However, all business logic, database design, and core functionality were implemented independently.

## 📝 License

This project is created for educational purposes and demonstration of web development skills.

## 👨‍💻 Developer

**Krishana Singh**
- Student Developer
- Focus: Web Development with Python Flask
- Specialization: Database Management and User Interface Design

---

*This Vehicle Parking System demonstrates modern web development practices with a focus on user experience, data integrity, and system reliability.*