# db.py - Database operations and connection management

import sqlite3
from datetime import datetime
from .models import User, Product, Bill, BillItem
import config

class Database:
    def __init__(self, db_path=config.DATABASE_PATH):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def create_tables(self):
        """Create all required tables"""
        with self.connect() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('owner', 'employee')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Bills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    total_amount REAL NOT NULL,
                    discount REAL DEFAULT 0,
                    net_amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Bill items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bill_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL,
                    product_id INTEGER,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (bill_id) REFERENCES bills (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            conn.commit()

    def initialize_default_users(self):
        """Insert default users if they don't exist"""
        import bcrypt

        with self.connect() as conn:
            cursor = conn.cursor()

            for user_data in config.DEFAULT_USERS:
                # Check if user exists
                cursor.execute('SELECT id FROM users WHERE username = ?', (user_data['username'],))
                if cursor.fetchone():
                    continue

                # Hash password
                password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                # Insert user
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role)
                    VALUES (?, ?, ?)
                ''', (user_data['username'], password_hash, user_data['role']))

            conn.commit()

    # User operations
    def get_user_by_username(self, username):
        """Get user by username"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    role=row['role'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
        return None

    # Product operations
    def add_product(self, product):
        """Add a new product"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, price, stock)
                VALUES (?, ?, ?)
            ''', (product.name, product.price, product.stock))
            conn.commit()
            return cursor.lastrowid

    def get_all_products(self):
        """Get all products"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY name')
            rows = cursor.fetchall()
            return [Product(
                id=row['id'],
                name=row['name'],
                price=row['price'],
                stock=row['stock'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in rows]

    def get_product_by_id(self, product_id):
        """Get product by ID"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(
                    id=row['id'],
                    name=row['name'],
                    price=row['price'],
                    stock=row['stock'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
        return None

    def update_product(self, product):
        """Update product details"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE products
                SET name = ?, price = ?, stock = ?
                WHERE id = ?
            ''', (product.name, product.price, product.stock, product.id))
            conn.commit()

    def update_product_stock(self, product_id, new_stock):
        """Update product stock"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE products SET stock = ? WHERE id = ?', (new_stock, product_id))
            conn.commit()

    # Bill operations
    def create_bill(self, bill):
        """Create a new bill"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bills (customer_name, total_amount, discount, net_amount)
                VALUES (?, ?, ?, ?)
            ''', (bill.customer_name, bill.total_amount, bill.discount, bill.net_amount))
            conn.commit()
            return cursor.lastrowid

    def add_bill_item(self, bill_item):
        """Add an item to a bill"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bill_items (bill_id, product_id, product_name, quantity, price, total)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (bill_item.bill_id, bill_item.product_id, bill_item.product_name,
                  bill_item.quantity, bill_item.price, bill_item.total))
            conn.commit()

    def get_bill_with_items(self, bill_id):
        """Get bill with all its items"""
        with self.connect() as conn:
            cursor = conn.cursor()

            # Get bill
            cursor.execute('SELECT * FROM bills WHERE id = ?', (bill_id,))
            bill_row = cursor.fetchone()
            if not bill_row:
                return None

            bill = Bill(
                id=bill_row['id'],
                customer_name=bill_row['customer_name'],
                total_amount=bill_row['total_amount'],
                discount=bill_row['discount'],
                net_amount=bill_row['net_amount'],
                created_at=datetime.fromisoformat(bill_row['created_at'])
            )

            # Get bill items
            cursor.execute('SELECT * FROM bill_items WHERE bill_id = ?', (bill_id,))
            item_rows = cursor.fetchall()
            bill.items = [BillItem(
                id=row['id'],
                bill_id=row['bill_id'],
                product_id=row['product_id'],
                product_name=row['product_name'],
                quantity=row['quantity'],
                price=row['price'],
                total=row['total']
            ) for row in item_rows]

            return bill

    def get_all_bills(self):
        """Get all bills with basic info"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bills ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [Bill(
                id=row['id'],
                customer_name=row['customer_name'],
                total_amount=row['total_amount'],
                discount=row['discount'],
                net_amount=row['net_amount'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in rows]

# Global database instance
db = Database()