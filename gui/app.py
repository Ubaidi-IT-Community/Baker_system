# app.py - PySide6 GUI for Baker Management System

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QFormLayout,
    QMessageBox,
    QSpinBox,
    QStackedWidget,
    QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette

from auth.login import auth_manager
from inventory.products import product_manager
from billing.bill import bill_manager


class StyledWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Baker Shop POS")
        self.setFixedSize(900, 640)
        self.setStyleSheet("background-color: #1e1f29; color: #eceff4;")
        self.init_palette()

    def init_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1e1f29"))
        palette.setColor(QPalette.WindowText, QColor("#eceff4"))
        palette.setColor(QPalette.Base, QColor("#272a3c"))
        palette.setColor(QPalette.AlternateBase, QColor("#232635"))
        palette.setColor(QPalette.Text, QColor("#eceff4"))
        palette.setColor(QPalette.Button, QColor("#3b4252"))
        palette.setColor(QPalette.ButtonText, QColor("#eceff4"))
        palette.setColor(QPalette.Highlight, QColor("#88c0d0"))
        palette.setColor(QPalette.HighlightedText, QColor("#2e3440"))
        self.setPalette(palette)


class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Baker Shop POS")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Secure login with role-based access")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #a3be8c")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet("background: #2e3440; border: 1px solid #4c566a; padding: 8px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("background: #2e3440; border: 1px solid #4c566a; padding: 8px;")

        form.addRow("Username:", self.username_input)
        form.addRow("Password:", self.password_input)

        button = QPushButton("Login")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(44)
        button.setStyleSheet(
            "background-color: #88c0d0; color: #2e3440; border-radius: 10px; font-weight: bold;"
        )
        button.clicked.connect(self.handle_login)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addLayout(form)
        layout.addSpacing(10)
        layout.addWidget(button)
        layout.addStretch()

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if auth_manager.login(username, password):
            self.parent.open_dashboard()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")


class DashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)

        header = QLabel("Welcome to Baker Shop POS")
        header.setFont(QFont("Segoe UI", 22, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #8fbcbb;")

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.products_button = QPushButton("View Products")
        self.products_button.clicked.connect(self.parent.show_product_page)
        self.products_button.setCursor(Qt.PointingHandCursor)
        self.products_button.setMinimumHeight(44)
        self.products_button.setStyleSheet(self.button_style())

        self.bill_button = QPushButton("Create Bill")
        self.bill_button.clicked.connect(self.parent.show_billing_page)
        self.bill_button.setCursor(Qt.PointingHandCursor)
        self.bill_button.setMinimumHeight(44)
        self.bill_button.setStyleSheet(self.button_style())

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.parent.logout)
        self.logout_button.setCursor(Qt.PointingHandCursor)
        self.logout_button.setMinimumHeight(44)
        self.logout_button.setStyleSheet(self.button_style())

        self.reports_button = QPushButton("Refresh Inventory")
        self.reports_button.clicked.connect(self.parent.refresh_products)
        self.reports_button.setCursor(Qt.PointingHandCursor)
        self.reports_button.setMinimumHeight(44)
        self.reports_button.setStyleSheet(self.button_style())

        buttons_layout.addWidget(self.products_button)
        buttons_layout.addWidget(self.bill_button)
        buttons_layout.addWidget(self.reports_button)
        buttons_layout.addWidget(self.logout_button)

        layout.addWidget(header)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        self.setLayout(layout)

    @staticmethod
    def button_style():
        return (
            "background-color: #5e81ac; color: #eceff4; border:none; border-radius: 10px;"
            "font-size: 14px; font-weight: 600;"
        )


class ProductsPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("Product Inventory")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #88c0d0;")

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(
            "QTableWidget { background: #2e3440; border: 1px solid #4c566a; }"
            "QHeaderView::section { background: #434c5e; color: #eceff4; }"
            "QTableWidget::item { color: #eceff4; }"
        )

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent.open_dashboard)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setStyleSheet("background-color: #81a1c1; border-radius: 10px; color: #2e3440;")
        back_button.setMinimumHeight(40)

        layout.addWidget(header)
        layout.addWidget(self.table)
        layout.addWidget(back_button)
        self.setLayout(layout)

    def refresh(self):
        products = product_manager.get_all_products()
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(product.id)))
            self.table.setItem(row, 1, QTableWidgetItem(product.name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product.price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(product.stock)))


class BillingPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.selected_items = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("Create Bill")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setStyleSheet("color: #8fbcbb;")

        form_layout = QFormLayout()
        self.customer_input = QLineEdit()
        self.customer_input.setPlaceholderText("Customer name")
        self.product_id_input = QSpinBox()
        self.product_id_input.setMinimum(1)
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(1000)

        form_layout.addRow("Customer:", self.customer_input)
        form_layout.addRow("Product ID:", self.product_id_input)
        form_layout.addRow("Quantity:", self.quantity_input)

        add_button = QPushButton("Add Item")
        add_button.clicked.connect(self.add_item)
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.setStyleSheet("background-color: #88c0d0; border-radius: 10px; color:#2e3440;")
        add_button.setMinimumHeight(40)

        self.items_table = QTableWidget(0, 4)
        self.items_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Total"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.verticalHeader().setVisible(False)
        self.items_table.setStyleSheet(
            "QTableWidget { background: #2e3440; border: 1px solid #4c566a; }"
            "QHeaderView::section { background: #434c5e; color: #eceff4; }"
            "QTableWidget::item { color: #eceff4; }"
        )

        footer_layout = QHBoxLayout()
        finalize_button = QPushButton("Finalize Bill")
        finalize_button.setCursor(Qt.PointingHandCursor)
        finalize_button.setStyleSheet("background-color: #a3be8c; border-radius: 10px; color: #2e3440;")
        finalize_button.setMinimumHeight(40)
        finalize_button.clicked.connect(self.finalize_bill)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent.open_dashboard)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setStyleSheet("background-color: #81a1c1; border-radius: 10px; color: #2e3440;")
        back_button.setMinimumHeight(40)

        footer_layout.addWidget(finalize_button)
        footer_layout.addWidget(back_button)

        layout.addWidget(header)
        layout.addLayout(form_layout)
        layout.addWidget(add_button)
        layout.addWidget(self.items_table)
        layout.addLayout(footer_layout)
        self.setLayout(layout)

    def add_item(self):
        product_id = self.product_id_input.value()
        quantity = self.quantity_input.value()
        try:
            bill_manager.start_new_bill(self.customer_input.text().strip() or "Walk-in")
            bill_manager.add_item_to_bill(product_id, quantity)
            self.refresh_table()
        except Exception as exc:
            QMessageBox.warning(self, "Add Item Failed", str(exc))

    def refresh_table(self):
        items = bill_manager.current_bill_items
        self.items_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.items_table.setItem(row, 0, QTableWidgetItem(item.product_name))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item.price:.2f}"))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item.total:.2f}"))

    def finalize_bill(self):
        try:
            bill = bill_manager.finalize_bill(0.0)
            QMessageBox.information(self, "Bill Created", "Bill saved successfully.")
            self.items_table.setRowCount(0)
            self.customer_input.clear()
            bill_manager.current_bill_items = []
        except Exception as exc:
            QMessageBox.warning(self, "Finalize Failed", str(exc))


class BakerGuiApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = StyledWindow()
        self.stack = QStackedWidget()

        self.login_page = LoginPage(self)
        self.dashboard_page = DashboardPage(self)
        self.products_page = ProductsPage(self)
        self.billing_page = BillingPage(self)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.billing_page)

        self.window.setCentralWidget(self.stack)
        self.open_login()

    def open_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def open_dashboard(self):
        self.dashboard_page = DashboardPage(self)
        self.stack.insertWidget(1, self.dashboard_page)
        self.stack.setCurrentWidget(self.dashboard_page)

    def show_product_page(self):
        self.products_page.refresh()
        self.stack.setCurrentWidget(self.products_page)

    def refresh_products(self):
        self.products_page.refresh()
        QMessageBox.information(self.window, "Inventory Refreshed", "Product inventory has been refreshed.")

    def show_billing_page(self):
        self.billing_page = BillingPage(self)
        self.stack.insertWidget(3, self.billing_page)
        self.stack.setCurrentWidget(self.billing_page)

    def logout(self):
        auth_manager.logout()
        self.open_login()

    def run(self):
        self.window.show()
        return self.app.exec()


if __name__ == "__main__":
    BakerGuiApp().run()