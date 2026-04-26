# Baker Management System (Using Python)

## Overview

A lightweight, modular **Baker Shop Management System** built in Python.
Designed for small-to-medium bakery businesses to handle daily operations including authentication, inventory, billing, and customer tracking.

The system is built **CLI-first** (command-line interface) for stability and testing, with a future upgrade path to a full graphical POS dashboard.

---

## Core Features

### Authentication System

* Role-based login:
  * Owner (full control)
  * Employee (limited access)
* Secure password hashing (bcrypt)
* Predefined user accounts supported

---

### Inventory Management

* Add, update, and view products
* Track stock quantity
* Prepare for low-stock alerts (future)

---

### Billing System

* Create customer bills
* Add multiple items with quantity
* Automatic total calculation
* Discount support
* Net amount calculation

---

### Receipt Generation

* Auto timestamp (date & time)
* Itemized bill format
* Includes:
  * Total
  * Discount
  * Net amount
* Footer branding support

---

### Customer Data

* Store customer name with bill
* Customer loyalty tracking with points and tiers
* Loyalty customer profiles and transaction history

---

### Receipt Export

* Export receipts to text files
* Export receipts to PDF using reportlab
* Receipt file management for sales records

---

### Sales Reporting

* Daily sales reports
* Monthly sales analysis
* Top product performance tracking

---

### Logging System

* Activity logging for logins, billing, and exports
* Daily log files for audit and troubleshooting
* Owner-only log review support

---

### GUI Support

* PyQt5 POS dashboard
* Click-to-add product cart system
* Modern product grid and checkout experience
* Three color themes: Light, Dark, Modern

---

### Database

* Local database using SQLite
* No external setup required
* Easy migration to advanced databases later

---

## Project Structure

```
Baker_system/
│── main.py                 # Main entry point
│── config.py               # Configuration settings
│── requirements.txt        # Python dependencies
│
├── auth/
│   ├── login.py            # Authentication logic
│
├── database/
│   ├── db.py               # Database operations
│   ├── models.py           # Data models
│
├── inventory/
│   ├── products.py         # Product management
│
├── billing/
│   ├── bill.py             # Billing and receipts
│
├── receipt/
│   ├── export.py           # Receipt file export (PDF / text)
│
├── reports/
│   ├── sales.py            # Sales reporting and analytics
│
├── app_logging/
│   ├── logger.py           # Application logging system
│
├── customer/
│   ├── customer.py         # Customer management (future)
│   ├── loyalty.py          # Customer loyalty tracking
│
├── gui/
│   ├── pos_dashboard.py    # PyQt POS dashboard
│   ├── app.py              # GUI application launcher
│
└── utils/
    ├── helpers.py          # Utility functions
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Ubaidi-IT-Community/Baker_system.git
cd Baker_system
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

**Windows**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## First Run

Initialize database:

```bash
python main.py
```

This will:

* Create database file (`baker.db`)
* Generate required tables
* Insert default user accounts

---

## Default Test Users

```
Employee:
username: emp@001
password: 221121

username: emp@002
password: 221121

Owner:
username: Baker@Owner.name
password: Owner1234@
```

---

## Usage

Run the console application:

```bash
python main.py
```

Run the GUI application:

```bash
python main.py --gui
```

If you prefer direct GUI launch, you can also run:

```bash
python gui/pos_dashboard.py
```

### Main Menu Options

1. **Login** - Authenticate with username/password
2. **Add Product** - Add new products to inventory
3. **View Products** - Display all products
4. **Create Bill** - Generate customer bills
5. **Update Product** - Modify product details (Owner only)
6. **View All Bills** - View billing history (Owner only)

### Creating a Bill

1. Enter customer name
2. Add products by ID and quantity
3. Apply discount (optional)
4. Finalize bill
5. Receipt is displayed automatically

---

## Example Bill Format

```
         Baker Shop
==============================
Date: 2024-01-15   Time: 14:30
Customer: John Doe

Item               Qty     Price
------------------------------
Bread               2     50.00
Cake                1    500.00
------------------------------
Total:                  600.00
Discount:                50.00
Net Amount:             550.00

Best Wishes!
Ubaidi IT Solution
03420372799
```

---

## Development Roadmap

### Phase 1 (Current) ✅

* Database setup
* Authentication
* Product management
* Billing engine
* Console receipt

---

### Phase 2 (Completed) ✅

* Receipt file export (PDF / text)
* Inventory auto-update
* Sales reports (daily/monthly)
* Logging system

---

### Phase 3 (Completed) ✅

* GUI POS system (PyQt)
* Product image-based dashboard
* Click-to-add cart system
* Customer loyalty tracking

---

### Phase 4 (Commercial Features)

* License / credit system
* Expiry-based software lock
* Owner recharge activation

---

## Future GUI Concept

```
[ Product Grid with Images ]
        ↓
[ Click Product → Add Qty ]
        ↓
[ Cart Panel (Right Side) ]
        ↓
[ Total + Discount + Checkout ]
```

---

## Tech Stack

* Python 3.x
* SQLite (default database)
* bcrypt (security)
* Optional:
  * reportlab (PDF receipts)
  * PyQt5 (GUI)

---

## Testing

The system includes built-in validation:

* Input validation for all forms
* Stock checking before sales
* Permission checks for operations
* Error handling for database operations

---

## Contribution

Contributions are welcome.
Fork the repo and submit a pull request with improvements.

---

## License

This project is intended for educational and commercial prototype use.
Custom licensing can be applied for production deployment.

---

## Author

**Ubaidi IT Solution IT Community**
Developer: Samiullah Samejo
Email: devsamiubaidi@gmail.com
Contact: 03420372799

---

## Notes

* This project is designed to evolve into a real-world POS system.
* Keep modules clean and independent.
* Avoid mixing UI logic with business logic.