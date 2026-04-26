# gui/user_management_dialog.py - User management dialog for admin functions

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QInputDialog,
    QHeaderView, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from admin.user_management import UserManagementManager
from database.db import db

class UserManagementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManagementManager()
        self.init_ui()
        self.load_users()

    def init_ui(self):
        self.setWindowTitle("User Management - Owner Only")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout()

        # Title
        title = QLabel("User Management Panel")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # User table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Username", "Role", "Created At", "Actions"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.user_table)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_user_btn = QPushButton("Add User")
        self.add_user_btn.clicked.connect(self.add_user)
        button_layout.addWidget(self.add_user_btn)

        self.reset_password_btn = QPushButton("Reset Password")
        self.reset_password_btn.clicked.connect(self.reset_password)
        button_layout.addWidget(self.reset_password_btn)

        self.change_role_btn = QPushButton("Change Role")
        self.change_role_btn.clicked.connect(self.change_role)
        button_layout.addWidget(self.change_role_btn)

        self.delete_user_btn = QPushButton("Delete User")
        self.delete_user_btn.clicked.connect(self.delete_user)
        button_layout.addWidget(self.delete_user_btn)

        layout.addLayout(button_layout)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def load_users(self):
        """Load all users into the table"""
        users = self.user_manager.get_all_users()
        self.user_table.setRowCount(len(users))

        for row, user in enumerate(users):
            # Username
            username_item = QTableWidgetItem(user.username)
            self.user_table.setItem(row, 0, username_item)

            # Role
            role_item = QTableWidgetItem(user.role)
            self.user_table.setItem(row, 1, role_item)

            # Created At
            created_item = QTableWidgetItem(user.created_at.strftime("%Y-%m-%d %H:%M"))
            self.user_table.setItem(row, 2, created_item)

            # Actions (store user ID in the row)
            self.user_table.item(row, 0).setData(Qt.UserRole, user.id)

    def add_user(self):
        """Add a new user"""
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, password, role = dialog.get_user_data()
            try:
                self.user_manager.create_user(username, password, role)
                QMessageBox.information(self, "Success", f"User '{username}' created successfully!")
                self.load_users()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to create user: {str(e)}")

    def reset_password(self):
        """Reset password for selected user"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a user first.")
            return

        username = self.user_table.item(current_row, 0).text()
        user_id = self.user_table.item(current_row, 0).data(Qt.UserRole)

        # Get new password
        new_password, ok = QInputDialog.getText(
            self, "Reset Password",
            f"Enter new password for user '{username}':",
            QLineEdit.Password
        )

        if ok and new_password:
            try:
                self.user_manager.reset_password(user_id, new_password)
                QMessageBox.information(self, "Success", f"Password reset for user '{username}'!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to reset password: {str(e)}")

    def change_role(self):
        """Change role for selected user"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a user first.")
            return

        username = self.user_table.item(current_row, 0).text()
        current_role = self.user_table.item(current_row, 1).text()
        user_id = self.user_table.item(current_row, 0).data(Qt.UserRole)

        # Role selection dialog
        roles = ["employee", "owner"]
        new_role, ok = QInputDialog.getItem(
            self, "Change Role",
            f"Select new role for user '{username}':",
            roles, roles.index(current_role), False
        )

        if ok and new_role != current_role:
            try:
                self.user_manager.update_user_role(user_id, new_role)
                QMessageBox.information(self, "Success", f"Role changed for user '{username}' to {new_role}!")
                self.load_users()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to change role: {str(e)}")

    def delete_user(self):
        """Delete selected user"""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a user first.")
            return

        username = self.user_table.item(current_row, 0).text()
        user_id = self.user_table.item(current_row, 0).data(Qt.UserRole)

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete user '{username}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.user_manager.delete_user(user_id)
                QMessageBox.information(self, "Success", f"User '{username}' deleted successfully!")
                self.load_users()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete user: {str(e)}")


class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add New User")
        self.setModal(True)
        self.resize(300, 200)

        layout = QVBoxLayout()

        form_group = QGroupBox("User Information")
        form_layout = QFormLayout()

        self.username_edit = QLineEdit()
        form_layout.addRow("Username:", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_edit)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["employee", "owner"])
        form_layout.addRow("Role:", self.role_combo)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Create")
        self.ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(button_layout)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_user_data(self):
        """Return the entered user data"""
        return (
            self.username_edit.text().strip(),
            self.password_edit.text(),
            self.role_combo.currentText()
        )