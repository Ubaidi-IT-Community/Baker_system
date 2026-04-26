"""
GUI POS System - PyQt-based graphical point-of-sale dashboard
Phase 3: GUI POS system with product image dashboard and click-to-add cart
"""

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QDialog, QScrollArea, QGridLayout, QComboBox, QDialogButtonBox,
    QTabWidget, QListWidget, QListWidgetItem, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QGroupBox

from auth.login import auth_manager
from database.db import db
from inventory.products import product_manager
from billing.bill import bill_manager
from customer.loyalty import loyalty_manager
from receipt.export import receipt_exporter
from reports.sales import reporter
from app_logging.logger import system_logger
from gui.admin_panel_dialog import AdminPanelDialog


class POSApplication(QMainWindow):
    """Main POS Application Window"""

    def __init__(self):
        super().__init__()
        self.current_user = None
        self.init_ui()
        self.setWindowTitle("Baker Management System - POS")
        self.setGeometry(100, 100, 1400, 900)

    def init_ui(self):
        """Initialize user interface"""
        self.login_window = LoginWindow(self)
        self.setCentralWidget(self.login_window)

    def show_main_pos(self, user):
        """Show main POS interface after login"""
        self.current_user = user
        self.pos_window = POSMainWindow(self, user)
        self.setCentralWidget(self.pos_window)
        self.setWindowTitle(f"Baker POS - {user.role} ({user.username})")


class LoginWindow(QWidget):
    """Login interface for POS system"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        """Initialize login UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Baker Shop Management System")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("POS Dashboard")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Password
        layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        layout.addSpacing(20)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 12, QFont.Bold))
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        # Demo users info
        layout.addSpacing(20)
        info = QLabel(
            "Demo Users:\n"
            "Employee: emp@001 / 221121\n"
            "Owner: Baker@Owner.name / Owner1234@"
        )
        info.setFont(QFont("Arial", 10))
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        layout.addStretch()
        self.setLayout(layout)

    def login(self):
        """Handle login"""
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return

        try:
            user = auth_manager.login(username, password)
            system_logger.log_login(username, user.role)
            self.parent.show_main_pos(user)
        except Exception as e:
            system_logger.log_login(username, "", success=False)
            QMessageBox.critical(self, "Login Failed", str(e))


class POSMainWindow(QWidget):
    """Main POS window with product dashboard and cart"""

    def __init__(self, parent, user):
        super().__init__()
        self.parent = parent
        self.current_user = user
        self.current_bill = None
        self.cart_items = {}
        self.current_theme = "Light"
        self.themes = {
            "Light": {
                "window_bg": "#f3f6fb",
                "panel_bg": "#ffffff",
                "border": "#dfe2e8",
                "input_bg": "#ffffff",
                "text": "#2e3a45",
                "card_bg": "#ffffff",
                "card_hover": "#eef3fb",
                "primary": "#4c63d2",
                "primary_hover": "#3b52c4",
                "secondary": "#6c757d",
                "success": "#28a745",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "group_bg": "#f8f9fa"
            },
            "Dark": {
                "window_bg": "#1e1f29",
                "panel_bg": "#292d3e",
                "border": "#3c4156",
                "input_bg": "#313544",
                "text": "#e7e9f1",
                "card_bg": "#24283b",
                "card_hover": "#2a3047",
                "primary": "#5e81ac",
                "primary_hover": "#4c6998",
                "secondary": "#4c566a",
                "success": "#a3be8c",
                "warning": "#ebcb8b",
                "danger": "#bf616a",
                "group_bg": "#32374c"
            },
            "Modern": {
                "window_bg": "#f8fafb",
                "panel_bg": "#ffffff",
                "border": "#cbd5e1",
                "input_bg": "#f1f5f9",
                "text": "#0f172a",
                "card_bg": "#ffffff",
                "card_hover": "#e2e8f0",
                "primary": "#0ea5e9",
                "primary_hover": "#0284c7",
                "secondary": "#64748b",
                "success": "#16a34a",
                "warning": "#f59e0b",
                "danger": "#dc2626",
                "group_bg": "#eef2ff"
            }
        }
        self.init_ui()

    def init_ui(self):
        """Initialize main POS UI"""
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Left side: Products Grid
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)

        # Products header
        products_header = QLabel("Products")
        products_header.setFont(QFont("Arial", 16, QFont.Bold))
        products_header.setStyleSheet("color: #2e3440; margin-bottom: 10px;")
        left_layout.addWidget(products_header)

        self.products_scroll = QScrollArea()
        self.products_scroll.setWidgetResizable(True)
        self.products_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.products_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.products_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
            QScrollArea QWidget {
                background-color: transparent;
            }
        """)

        self.products_grid = QGridLayout()
        self.products_grid.setSpacing(15)
        self.products_grid.setContentsMargins(15, 15, 15, 15)

        products_widget = QWidget()
        products_widget.setLayout(self.products_grid)
        products_widget.setStyleSheet("background-color: transparent;")
        self.products_scroll.setWidget(products_widget)
        left_layout.addWidget(self.products_scroll)

        left_frame = QFrame()
        left_frame.setLayout(left_layout)
        left_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(left_frame, 3)

        # Right side: Cart and Checkout
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(15, 15, 15, 15)

        # Theme selector
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(8)
        theme_label = QLabel("Theme:")
        theme_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark", "Modern"])
        self.theme_selector.setCurrentText(self.current_theme)
        self.theme_selector.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_selector)
        right_layout.addLayout(theme_layout)

        # Customer info
        customer_group = QGroupBox("Customer Information")
        customer_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(8)
        customer_layout.addWidget(QLabel("Name:"))
        self.customer_name = QLineEdit()
        self.customer_name.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        customer_layout.addWidget(self.customer_name)
        customer_group.setLayout(customer_layout)
        right_layout.addWidget(customer_group)

        # Cart
        cart_group = QGroupBox("Shopping Cart")
        cart_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        cart_layout = QVBoxLayout()
        cart_layout.setSpacing(8)
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Total", "Remove"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                gridline-color: #e9ecef;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #ced4da;
                font-weight: bold;
            }
        """)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setStyleSheet(self.cart_table.styleSheet() + """
            QTableWidget {
                alternate-background-color: #f8f9fa;
            }
        """)
        cart_layout.addWidget(self.cart_table)
        cart_group.setLayout(cart_layout)
        right_layout.addWidget(cart_group)

        # Totals
        totals_group = QGroupBox("Order Summary")
        totals_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        totals_layout = QVBoxLayout()
        totals_layout.setSpacing(8)

        # Subtotal
        subtotal_layout = QHBoxLayout()
        subtotal_layout.addWidget(QLabel("Subtotal:"))
        self.subtotal_label = QLabel("Rs. 0.00")
        self.subtotal_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.subtotal_label.setStyleSheet("color: #495057;")
        subtotal_layout.addWidget(self.subtotal_label)
        totals_layout.addLayout(subtotal_layout)

        # Discount
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("Discount (%):"))
        self.discount_spin = QSpinBox()
        self.discount_spin.setMaximum(100)
        self.discount_spin.setFixedWidth(80)
        self.discount_spin.setStyleSheet("""
            QSpinBox {
                padding: 3px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
            }
        """)
        self.discount_spin.valueChanged.connect(self.update_totals)
        discount_layout.addWidget(self.discount_spin)
        totals_layout.addLayout(discount_layout)

        # Discount Amount
        discount_amount_layout = QHBoxLayout()
        discount_amount_layout.addWidget(QLabel("Discount Amount:"))
        self.discount_amount_label = QLabel("Rs. 0.00")
        self.discount_amount_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.discount_amount_label.setStyleSheet("color: #dc3545;")
        discount_amount_layout.addWidget(self.discount_amount_label)
        totals_layout.addLayout(discount_amount_layout)

        # Net Amount
        net_layout = QHBoxLayout()
        net_layout.addWidget(QLabel("Net Amount:"))
        self.net_amount_label = QLabel("Rs. 0.00")
        self.net_amount_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.net_amount_label.setStyleSheet("color: #28a745;")
        net_layout.addWidget(self.net_amount_label)
        totals_layout.addLayout(net_layout)

        totals_group.setLayout(totals_layout)
        right_layout.addWidget(totals_group)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        clear_btn = QPushButton("Clear Cart")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:pressed {
                background-color: #d39e00;
            }
        """)
        clear_btn.clicked.connect(self.clear_cart)
        buttons_layout.addWidget(clear_btn)

        checkout_btn = QPushButton("Checkout")
        checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        checkout_btn.clicked.connect(self.checkout)
        buttons_layout.addWidget(checkout_btn)

        right_layout.addLayout(buttons_layout)

        # Menu buttons
        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(10)

        reports_btn = QPushButton("Reports")
        reports_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        reports_btn.clicked.connect(self.show_reports)
        menu_layout.addWidget(reports_btn)

        loyalty_btn = QPushButton("Loyalty")
        loyalty_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        loyalty_btn.clicked.connect(self.show_loyalty)
        menu_layout.addWidget(loyalty_btn)

        # Admin button (only for owners)
        if self.current_user.role == 'owner':
            admin_btn = QPushButton("Admin")
            admin_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6f42c1;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #5a359a;
                }
                QPushButton:pressed {
                    background-color: #4e2e87;
                }
            """)
            admin_btn.clicked.connect(self.show_admin_panel)
            menu_layout.addWidget(admin_btn)

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        menu_layout.addWidget(logout_btn)

        right_layout.addLayout(menu_layout)

        right_frame = QFrame()
        right_frame.setLayout(right_layout)
        right_frame.setMaximumWidth(450)
        self.right_frame = right_frame
        main_layout.addWidget(right_frame, 1)

        self.setLayout(main_layout)
        self.apply_theme(self.current_theme)

    def apply_theme(self, theme_name):
        """Apply the selected theme to the POS window."""
        if theme_name not in self.themes:
            return

        self.current_theme = theme_name
        colors = self.themes[theme_name]

        self.setStyleSheet(f"background-color: {colors['window_bg']}; color: {colors['text']};")
        self.products_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {colors['border']};
                border-radius: 8px;
                background-color: {colors['group_bg']};
            }}
            QScrollArea QWidget {{
                background-color: transparent;
            }}
        """)
        self.right_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['panel_bg']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
            }}
        """)
        self.customer_name.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {colors['border']};
                border-radius: 4px;
                background-color: {colors['input_bg']};
                color: {colors['text']};
            }}
        """)
        self.cart_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                background-color: {colors['panel_bg']};
                gridline-color: {colors['border']};
                color: {colors['text']};
            }}
            QHeaderView::section {{
                background-color: {colors['group_bg']};
                padding: 8px;
                border: 1px solid {colors['border']};
                font-weight: bold;
                color: {colors['text']};
            }}
            QTableWidget {{
                alternate-background-color: {colors['group_bg']};
            }}
        """)
        self.update_cart_display()
        self.load_products()

    def load_products(self):
        """Load and display all products"""
        products = product_manager.get_all_products()

        # Clear grid
        while self.products_grid.count():
            self.products_grid.takeAt(0).widget().deleteLater()

        for i, product in enumerate(products):
            row = i // 3
            col = i % 3

            # Product card
            card_widget = QFrame()
            colors = self.themes[self.current_theme]
            card_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors['card_bg']};
                    border: 1px solid {colors['border']};
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px;
                }}
                QFrame:hover {{
                    border: 2px solid {colors['primary']};
                    background-color: {colors['card_hover']};
                }}
            """)
            card_widget.setFixedSize(220, 180)

            card_layout = QVBoxLayout(card_widget)
            card_layout.setSpacing(8)
            card_layout.setContentsMargins(12, 12, 12, 12)

            # Product name
            name_label = QLabel(product.name)
            name_label.setFont(QFont("Arial", 12, QFont.Bold))
            name_label.setStyleSheet("color: #2e3440; margin-bottom: 5px;")
            name_label.setWordWrap(True)
            card_layout.addWidget(name_label)

            # Price
            price_label = QLabel(f"Rs. {product.price:.2f}")
            price_label.setFont(QFont("Arial", 11))
            price_label.setStyleSheet("color: #4c63d2; font-weight: bold; margin-bottom: 5px;")
            card_layout.addWidget(price_label)

            # Stock
            stock_label = QLabel(f"Stock: {product.stock}")
            stock_label.setFont(QFont("Arial", 9))
            stock_label.setStyleSheet("color: #6c757d; margin-bottom: 8px;")
            card_layout.addWidget(stock_label)

            # Quantity selector
            qty_layout = QHBoxLayout()
            qty_layout.addWidget(QLabel("Qty:"))
            qty_spinbox = QSpinBox()
            qty_spinbox.setMinimum(1)
            qty_spinbox.setMaximum(product.stock)
            qty_spinbox.setFixedWidth(60)
            qty_spinbox.setStyleSheet("""
                QSpinBox {
                    padding: 3px;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    background-color: white;
                }
            """)
            qty_layout.addWidget(qty_spinbox)
            qty_layout.addStretch()
            card_layout.addLayout(qty_layout)

            # Add to cart button
            add_btn = QPushButton("Add to Cart")
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4c63d2;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #3b52c4;
                }
                QPushButton:pressed {
                    background-color: #2e3ea6;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
            add_btn.clicked.connect(
                lambda checked, pid=product.id, pname=product.name, pprice=product.price:
                    self.add_to_cart(pid, pname, pprice, qty_spinbox)
            )
            card_layout.addWidget(add_btn)

            self.products_grid.addWidget(card_widget, row, col)

    def add_to_cart(self, product_id, product_name, price, qty_spinbox):
        """Add product to cart"""
        quantity = qty_spinbox.value()
        
        if product_id in self.cart_items:
            self.cart_items[product_id]['quantity'] += quantity
        else:
            self.cart_items[product_id] = {
                'name': product_name,
                'price': price,
                'quantity': quantity
            }

        self.update_cart_display()
        qty_spinbox.setValue(1)

    def update_cart_display(self):
        """Update cart table display"""
        self.cart_table.setRowCount(len(self.cart_items))

        row = 0
        for product_id, item in self.cart_items.items():
            # Item name
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            
            # Quantity
            qty_spinbox = QSpinBox()
            qty_spinbox.setValue(item['quantity'])
            qty_spinbox.valueChanged.connect(
                lambda val, pid=product_id: self.update_cart_quantity(pid, val)
            )
            self.cart_table.setCellWidget(row, 1, qty_spinbox)

            # Price
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"Rs. {item['price']:.2f}"))

            # Total
            total = item['price'] * item['quantity']
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"Rs. {total:.2f}"))

            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked, pid=product_id: self.remove_from_cart(pid))
            self.cart_table.setCellWidget(row, 4, remove_btn)

            row += 1

        self.update_totals()

    def update_cart_quantity(self, product_id, quantity):
        """Update quantity for cart item"""
        if quantity <= 0:
            self.remove_from_cart(product_id)
        else:
            self.cart_items[product_id]['quantity'] = quantity
            self.update_cart_display()

    def remove_from_cart(self, product_id):
        """Remove item from cart"""
        if product_id in self.cart_items:
            del self.cart_items[product_id]
            self.update_cart_display()

    def clear_cart(self):
        """Clear entire cart"""
        self.cart_items = {}
        self.update_cart_display()
        self.customer_name.clear()

    def update_totals(self):
        """Update subtotal, discount, and net amount"""
        subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items.values())
        
        discount_percent = self.discount_spin.value()
        discount_amount = (subtotal * discount_percent) / 100
        net_amount = subtotal - discount_amount

        self.subtotal_label.setText(f"Rs. {subtotal:.2f}")
        self.discount_amount_label.setText(f"Rs. {discount_amount:.2f}")
        self.net_amount_label.setText(f"Rs. {net_amount:.2f}")

    def checkout(self):
        """Process checkout"""
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart")
            return

        customer_name = self.customer_name.text().strip()
        if not customer_name:
            QMessageBox.warning(self, "No Customer", "Please enter customer name")
            return

        try:
            # Create bill
            bill_manager.start_new_bill(customer_name)
            
            for product_id, item in self.cart_items.items():
                bill_manager.add_item_to_bill(product_id, item['quantity'])

            discount_amount = float(self.discount_amount_label.text().split()[-1].replace(',', ''))
            bill = bill_manager.finalize_bill(discount_amount)

            # Try to link to loyalty customer
            try:
                customer = loyalty_manager.get_customer_by_name(customer_name)
                if not customer:
                    customer_id = loyalty_manager.add_customer(customer_name)
                else:
                    customer_id = customer['id']
                
                loyalty_manager.add_loyalty_points(customer_id, bill.total_amount)
            except:
                pass  # Loyalty tracking optional

            system_logger.log_bill_create(
                self.current_user.username,
                customer_name,
                bill.id,
                bill.total_amount,
                len(self.cart_items)
            )

            # Show receipt
            receipt_text = bill_manager.generate_receipt(bill)
            receipt_dialog = ReceiptDialog(self, receipt_text, bill)
            receipt_dialog.exec_()

            # Clear cart
            self.clear_cart()

        except Exception as e:
            system_logger.log_error(self.current_user.username, "CHECKOUT", str(e))
            QMessageBox.critical(self, "Checkout Error", str(e))

    def show_reports(self):
        """Show sales reports"""
        if not self.current_user or self.current_user.role != "owner":
            QMessageBox.warning(self, "Permission Denied", "Only owners can view reports")
            return

        dialog = ReportsDialog(self)
        dialog.exec_()

    def show_loyalty(self):
        """Show loyalty management"""
        dialog = LoyaltyDialog(self)
        dialog.exec_()

    def show_admin_panel(self):
        """Show admin panel (owner only)"""
        if not self.current_user or self.current_user.role != "owner":
            QMessageBox.warning(self, "Permission Denied", "Only owners can access admin panel")
            return

        dialog = AdminPanelDialog(self)
        dialog.exec_()

    def logout(self):
        """Logout user"""
        system_logger.log_logout(self.current_user.username)
        auth_manager.logout()
        
        login_window = LoginWindow(self.parent)
        self.parent.setCentralWidget(login_window)


class ReceiptDialog(QDialog):
    """Receipt display and export dialog"""

    def __init__(self, parent, receipt_text, bill):
        super().__init__(parent)
        self.receipt_text = receipt_text
        self.bill = bill
        self.init_ui()

    def init_ui(self):
        """Initialize receipt dialog"""
        self.setWindowTitle("Receipt")
        self.setGeometry(200, 200, 600, 700)

        layout = QVBoxLayout()

        # Receipt display
        receipt_display = QLabel(self.receipt_text)
        receipt_display.setFont(QFont("Courier", 9))
        receipt_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll = QScrollArea()
        scroll.setWidget(receipt_display)
        layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()

        export_txt_btn = QPushButton("Export as Text")
        export_txt_btn.clicked.connect(self.export_text)
        button_layout.addWidget(export_txt_btn)

        export_pdf_btn = QPushButton("Export as PDF")
        export_pdf_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(export_pdf_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def export_text(self):
        """Export receipt as text file"""
        filepath = receipt_exporter.export_to_text(self.bill, self.receipt_text)
        if filepath:
            QMessageBox.information(self, "Exported", f"Receipt saved to:\n{filepath}")
        else:
            QMessageBox.critical(self, "Export Failed", "Could not export receipt")

    def export_pdf(self):
        """Export receipt as PDF"""
        filepath = receipt_exporter.export_to_pdf(self.bill, self.receipt_text)
        if filepath:
            QMessageBox.information(self, "Exported", f"Receipt saved to:\n{filepath}")
        else:
            QMessageBox.critical(self, "Export Failed", "Could not export as PDF")


class ReportsDialog(QDialog):
    """Sales reports dialog"""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize reports dialog"""
        self.setWindowTitle("Sales Reports")
        self.setGeometry(150, 150, 800, 600)

        layout = QVBoxLayout()

        # Report type selector
        report_layout = QHBoxLayout()
        report_layout.addWidget(QLabel("Report Type:"))
        
        self.report_type = QComboBox()
        self.report_type.addItems(["Daily", "Monthly", "Top Products"])
        self.report_type.currentTextChanged.connect(self.generate_report)
        report_layout.addWidget(self.report_type)
        layout.addLayout(report_layout)

        # Report display
        self.report_display = QLabel()
        self.report_display.setFont(QFont("Courier", 10))
        self.report_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll = QScrollArea()
        scroll.setWidget(self.report_display)
        layout.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
        self.generate_report()

    def generate_report(self):
        """Generate selected report"""
        report_type = self.report_type.currentText()

        if report_type == "Daily":
            report = reporter.get_daily_sales()
            text = reporter.format_daily_report(report)
        elif report_type == "Monthly":
            report = reporter.get_monthly_sales()
            text = reporter.format_monthly_report(report)
        else:  # Top Products
            products = reporter.get_top_products()
            text = self._format_top_products(products)

        self.report_display.setText(text)

    def _format_top_products(self, products):
        """Format top products report"""
        if not products:
            return "No product sales data available"

        output = []
        output.append("\n" + "="*50)
        output.append("TOP SELLING PRODUCTS")
        output.append("="*50)
        output.append(f"{'Rank':<5} {'Product':<25} {'Qty':<8} {'Revenue':<10}")
        output.append("-"*50)

        for i, product in enumerate(products[:10], 1):
            output.append(
                f"{i:<5} {product['product_name']:<25} "
                f"{product['quantity_sold']:<8} Rs. {product['revenue']:.2f}"
            )

        output.append("="*50 + "\n")
        return "\n".join(output)


class LoyaltyDialog(QDialog):
    """Customer loyalty management dialog"""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize loyalty dialog"""
        self.setWindowTitle("Loyalty Program")
        self.setGeometry(150, 150, 700, 600)

        layout = QVBoxLayout()

        # Search customer
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Customer Name:"))
        self.customer_input = QLineEdit()
        search_layout.addWidget(self.customer_input)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_customer)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)

        # Customer info display
        self.info_display = QLabel()
        self.info_display.setFont(QFont("Arial", 10))
        self.info_display.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        scroll = QScrollArea()
        scroll.setWidget(self.info_display)
        layout.addWidget(scroll)

        # Action buttons
        action_layout = QHBoxLayout()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        action_layout.addWidget(close_btn)

        layout.addLayout(action_layout)
        self.setLayout(layout)

    def search_customer(self):
        """Search for customer"""
        name = self.customer_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter customer name")
            return

        customer = loyalty_manager.get_customer_by_name(name)
        if customer:
            self.info_display.setText(loyalty_manager.format_customer_profile(customer))
        else:
            self.info_display.setText("Customer not found. Register new customer?")


def main():
    """Main entry point for GUI"""
    app = QApplication(sys.argv)
    window = POSApplication()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
