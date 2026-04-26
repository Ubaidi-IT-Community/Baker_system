# login.py - Authentication and user management

import bcrypt
from database.db import db
from database.models import User

class AuthManager:
    def __init__(self):
        self.current_user = None

    def login(self, username, password):
        """Authenticate user and set current user"""
        user = db.get_user_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            self.current_user = user
            return user
        return False

    def logout(self):
        """Clear current user session"""
        self.current_user = None

    def get_current_user(self):
        """Get currently logged in user"""
        return self.current_user

    def is_owner(self):
        """Check if current user is owner"""
        return self.current_user and self.current_user.role == 'owner'

    def is_employee(self):
        """Check if current user is employee"""
        return self.current_user and self.current_user.role == 'employee'

    def require_owner(self):
        """Raise error if not owner"""
        if not self.is_owner():
            raise PermissionError("Owner access required")

    def require_login(self):
        """Raise error if not logged in"""
        if not self.current_user:
            raise PermissionError("Login required")

# Global auth manager instance
auth_manager = AuthManager()