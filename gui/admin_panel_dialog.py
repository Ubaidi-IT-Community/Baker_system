# gui/admin_panel_dialog.py - Main admin panel dialog

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QMessageBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QDateEdit, QComboBox,
    QFormLayout, QGroupBox, QSpinBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from admin.management import AdminManager
from admin.user_management import UserManagementManager
from gui.user_management_dialog import UserManagementDialog
from database.db import db
from database.models import Category, PaymentMethod, Refund

class AdminPanelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.admin_manager = AdminManager()
        self.user_manager = UserManagementManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Panel - Owner Only")
        self.setModal(True)
        self.resize(1000, 700)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Administrative Panel")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Tab widget for different admin functions
        self.tab_widget = QTabWidget()

        # User Management Tab
        self.user_tab = self.create_user_management_tab()
        self.tab_widget.addTab(self.user_tab, "User Management")

        # Categories Tab
        self.categories_tab = self.create_categories_tab()
        self.tab_widget.addTab(self.categories_tab, "Categories")

        # Payment Methods Tab
        self.payment_tab = self.create_payment_methods_tab()
        self.tab_widget.addTab(self.payment_tab, "Payment Methods")

        # Low Stock Tab
        self.low_stock_tab = self.create_low_stock_tab()
        self.tab_widget.addTab(self.low_stock_tab, "Low Stock Alerts")

        # Bill Search Tab
        self.bill_search_tab = self.create_bill_search_tab()
        self.tab_widget.addTab(self.bill_search_tab, "Bill Search")

        # Refunds Tab
        self.refunds_tab = self.create_refunds_tab()
        self.tab_widget.addTab(self.refunds_tab, "Refunds")

        layout.addWidget(self.tab_widget)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def create_user_management_tab(self):
        """Create the user management tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Quick user management buttons
        button_layout = QHBoxLayout()

        user_mgmt_btn = QPushButton("Open Full User Management")
        user_mgmt_btn.clicked.connect(self.open_user_management)
        button_layout.addWidget(user_mgmt_btn)

        layout.addLayout(button_layout)

        # User summary
        summary_label = QLabel("Quick User Summary:")
        summary_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(summary_label)

        self.user_summary = QTextEdit()
        self.user_summary.setReadOnly(True)
        self.user_summary.setMaximumHeight(150)
        layout.addWidget(self.user_summary)

        widget.setLayout(layout)
        return widget

    def create_categories_tab(self):
        """Create the categories management tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Add category form
        form_group = QGroupBox("Add New Category")
        form_layout = QFormLayout()

        self.category_name_edit = QLineEdit()
        form_layout.addRow("Category Name:", self.category_name_edit)

        self.category_desc_edit = QLineEdit()
        form_layout.addRow("Description:", self.category_desc_edit)

        add_category_btn = QPushButton("Add Category")
        add_category_btn.clicked.connect(self.add_category)
        form_layout.addRow(add_category_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Categories list
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(["Name", "Description"])
        self.categories_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.categories_table)

        widget.setLayout(layout)
        return widget

    def create_payment_methods_tab(self):
        """Create the payment methods management tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Add payment method form
        form_group = QGroupBox("Add New Payment Method")
        form_layout = QFormLayout()

        self.payment_name_edit = QLineEdit()
        form_layout.addRow("Method Name:", self.payment_name_edit)

        self.payment_desc_edit = QLineEdit()
        form_layout.addRow("Description:", self.payment_desc_edit)

        add_payment_btn = QPushButton("Add Payment Method")
        add_payment_btn.clicked.connect(self.add_payment_method)
        form_layout.addRow(add_payment_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Payment methods list
        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(2)
        self.payment_table.setHorizontalHeaderLabels(["Name", "Description"])
        self.payment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.payment_table)

        widget.setLayout(layout)
        return widget

    def create_low_stock_tab(self):
        """Create the low stock alerts tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Low stock alerts
        alert_label = QLabel("Low Stock Alerts:")
        alert_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(alert_label)

        self.low_stock_text = QTextEdit()
        self.low_stock_text.setReadOnly(True)
        layout.addWidget(self.low_stock_text)

        # Refresh button
        refresh_btn = QPushButton("Refresh Low Stock Alerts")
        refresh_btn.clicked.connect(self.refresh_low_stock)
        layout.addWidget(refresh_btn)

        widget.setLayout(layout)
        return widget

    def create_bill_search_tab(self):
        """Create the bill search tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Search form
        search_group = QGroupBox("Search Bills")
        search_layout = QFormLayout()

        self.search_term_edit = QLineEdit()
        self.search_term_edit.setPlaceholderText("Customer name or bill details...")
        search_layout.addRow("Search Term:", self.search_term_edit)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        search_layout.addRow("Start Date:", self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        search_layout.addRow("End Date:", self.end_date_edit)

        search_btn = QPushButton("Search Bills")
        search_btn.clicked.connect(self.search_bills)
        search_layout.addRow(search_btn)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Results table
        self.bill_results_table = QTableWidget()
        self.bill_results_table.setColumnCount(5)
        self.bill_results_table.setHorizontalHeaderLabels(["Bill ID", "Customer", "Total", "Net Amount", "Date"])
        self.bill_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.bill_results_table)

        widget.setLayout(layout)
        return widget

    def create_refunds_tab(self):
        """Create the refunds management tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Add refund form
        form_group = QGroupBox("Process Refund")
        form_layout = QFormLayout()

        self.refund_bill_id_edit = QSpinBox()
        self.refund_bill_id_edit.setMinimum(1)
        form_layout.addRow("Bill ID:", self.refund_bill_id_edit)

        self.refund_reason_edit = QLineEdit()
        form_layout.addRow("Reason:", self.refund_reason_edit)

        self.refund_amount_edit = QLineEdit()
        self.refund_amount_edit.setPlaceholderText("0.00")
        form_layout.addRow("Amount:", self.refund_amount_edit)

        process_refund_btn = QPushButton("Process Refund")
        process_refund_btn.clicked.connect(self.process_refund)
        form_layout.addRow(process_refund_btn)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Refunds list
        self.refunds_table = QTableWidget()
        self.refunds_table.setColumnCount(4)
        self.refunds_table.setHorizontalHeaderLabels(["Bill ID", "Reason", "Amount", "Date"])
        self.refunds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.refunds_table)

        widget.setLayout(layout)
        return widget

    def open_user_management(self):
        """Open the full user management dialog"""
        dialog = UserManagementDialog(self)
        dialog.exec_()
        self.refresh_user_summary()

    def add_category(self):
        """Add a new category"""
        name = self.category_name_edit.text().strip()
        description = self.category_desc_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Category name is required.")
            return

        try:
            category = Category(name=name, description=description)
            self.admin_manager.add_category(category)
            QMessageBox.information(self, "Success", f"Category '{name}' added successfully!")
            self.category_name_edit.clear()
            self.category_desc_edit.clear()
            self.refresh_categories()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add category: {str(e)}")

    def add_payment_method(self):
        """Add a new payment method"""
        name = self.payment_name_edit.text().strip()
        description = self.payment_desc_edit.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Payment method name is required.")
            return

        try:
            method = PaymentMethod(name=name, description=description)
            self.admin_manager.add_payment_method(method)
            QMessageBox.information(self, "Success", f"Payment method '{name}' added successfully!")
            self.payment_name_edit.clear()
            self.payment_desc_edit.clear()
            self.refresh_payment_methods()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add payment method: {str(e)}")

    def process_refund(self):
        """Process a refund"""
        bill_id = self.refund_bill_id_edit.value()
        reason = self.refund_reason_edit.text().strip()
        amount_text = self.refund_amount_edit.text().strip()

        if not reason or not amount_text:
            QMessageBox.warning(self, "Input Error", "Reason and amount are required.")
            return

        try:
            amount = float(amount_text)
            refund = Refund(bill_id=bill_id, reason=reason, amount=amount)
            self.admin_manager.create_refund(refund)
            QMessageBox.information(self, "Success", f"Refund processed for bill {bill_id}!")
            self.refund_reason_edit.clear()
            self.refund_amount_edit.clear()
            self.refresh_refunds()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid amount format.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process refund: {str(e)}")

    def refresh_user_summary(self):
        """Refresh the user summary display"""
        users = self.user_manager.get_all_users()
        summary = f"Total Users: {len(users)}\n\n"
        owners = [u for u in users if u.role == 'owner']
        employees = [u for u in users if u.role == 'employee']

        summary += f"Owners: {len(owners)}\n"
        for owner in owners:
            summary += f"  - {owner.username}\n"

        summary += f"\nEmployees: {len(employees)}\n"
        for emp in employees:
            summary += f"  - {emp.username}\n"

        self.user_summary.setText(summary)

    def refresh_categories(self):
        """Refresh the categories table"""
        categories = self.admin_manager.get_all_categories()
        self.categories_table.setRowCount(len(categories))

        for row, category in enumerate(categories):
            self.categories_table.setItem(row, 0, QTableWidgetItem(category.name))
            self.categories_table.setItem(row, 1, QTableWidgetItem(category.description or ""))

    def refresh_payment_methods(self):
        """Refresh the payment methods table"""
        methods = self.admin_manager.get_all_payment_methods()
        self.payment_table.setRowCount(len(methods))

        for row, method in enumerate(methods):
            self.payment_table.setItem(row, 0, QTableWidgetItem(method.name))
            self.payment_table.setItem(row, 1, QTableWidgetItem(method.description or ""))

    def refresh_low_stock(self):
        """Refresh low stock alerts"""
        alerts = self.admin_manager.get_low_stock_alerts()
        self.low_stock_text.setText(alerts)

    def search_bills(self):
        """Search bills based on criteria"""
        search_term = self.search_term_edit.text().strip()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        try:
            bills = self.admin_manager.search_bills(search_term or None, start_date, end_date)
            self.bill_results_table.setRowCount(len(bills))

            for row, bill in enumerate(bills):
                self.bill_results_table.setItem(row, 0, QTableWidgetItem(str(bill.id)))
                self.bill_results_table.setItem(row, 1, QTableWidgetItem(bill.customer_name or ""))
                self.bill_results_table.setItem(row, 2, QTableWidgetItem(f"${bill.total_amount:.2f}"))
                self.bill_results_table.setItem(row, 3, QTableWidgetItem(f"${bill.net_amount:.2f}"))
                self.bill_results_table.setItem(row, 4, QTableWidgetItem(bill.created_at.strftime("%Y-%m-%d %H:%M")))

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to search bills: {str(e)}")

    def refresh_refunds(self):
        """Refresh the refunds table"""
        # For now, show all refunds - in a real app you'd filter by date or bill
        refunds = []  # This would need a method to get all refunds
        self.refunds_table.setRowCount(len(refunds))

        for row, refund in enumerate(refunds):
            self.refunds_table.setItem(row, 0, QTableWidgetItem(str(refund.bill_id)))
            self.refunds_table.setItem(row, 1, QTableWidgetItem(refund.reason))
            self.refunds_table.setItem(row, 2, QTableWidgetItem(f"${refund.amount:.2f}"))
            self.refunds_table.setItem(row, 3, QTableWidgetItem(refund.created_at.strftime("%Y-%m-%d %H:%M")))

    def showEvent(self, event):
        """Called when dialog is shown - refresh all data"""
        super().showEvent(event)
        self.refresh_user_summary()
        self.refresh_categories()
        self.refresh_payment_methods()
        self.refresh_low_stock()
        self.refresh_refunds()