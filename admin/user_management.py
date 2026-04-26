# user_management.py - Employee and user management (Owner-only)

import bcrypt
from database.db import db
from database.models import User
from auth.login import auth_manager


class UserManagementManager:
    """Manages user accounts and permissions"""

    def create_user(self, username, password, role='employee'):
        """Create a new user account"""
        auth_manager.require_owner()

        if not username or not password:
            raise ValueError("Username and password are required")

        if role not in ['owner', 'employee']:
            raise ValueError("Role must be 'owner' or 'employee'")

        # Check if user exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        user = User(username=username, password_hash=password_hash, role=role)
        
        # Insert directly to database
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            ''', (username, password_hash, role))
            conn.commit()
            return cursor.lastrowid

    def get_all_users(self):
        """Get all users"""
        auth_manager.require_owner()
        
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY username')
            rows = cursor.fetchall()
            from datetime import datetime
            return [User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                role=row['role'],
                created_at=datetime.fromisoformat(row['created_at'])
            ) for row in rows]

    def update_user_role(self, user_id, new_role):
        """Change a user's role"""
        auth_manager.require_owner()

        if new_role not in ['owner', 'employee']:
            raise ValueError("Role must be 'owner' or 'employee'")

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
            conn.commit()

    def reset_password(self, user_id, new_password):
        """Reset a user's password"""
        auth_manager.require_owner()

        if not new_password:
            raise ValueError("Password cannot be empty")

        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
            conn.commit()

    def delete_user(self, user_id):
        """Delete a user account (soft delete - could be implemented)"""
        auth_manager.require_owner()

        # Prevent deleting the last owner
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "owner"')
            owner_count = cursor.fetchone()['count']

            if owner_count <= 1:
                # Check if this is an owner
                cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                if user and user['role'] == 'owner':
                    raise ValueError("Cannot delete the last owner account")

            # Delete the user
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()

    def change_own_password(self, user_id, old_password, new_password):
        """Allow a user to change their own password"""
        user = db.get_user_by_username(auth_manager.current_user.username)
        
        if not user or user.id != user_id:
            raise ValueError("Cannot change another user's password")

        if not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            raise ValueError("Current password is incorrect")

        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
            conn.commit()

# Global user management instance
user_manager = UserManagementManager()
