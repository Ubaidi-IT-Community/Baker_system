"""
Customer Loyalty Tracking Module
Phase 3: Customer loyalty tracking
"""

from datetime import datetime
from database.db import db


class LoyaltyManager:
    """Manages customer loyalty points and rewards program"""

    POINTS_PER_RUPEE = 1  # 1 point for every rupee spent
    POINTS_REDEMPTION_VALUE = 100  # 100 points = Rs. 100 discount

    def __init__(self):
        """Initialize loyalty manager"""
        self.points_per_rupee = self.POINTS_PER_RUPEE
        self.points_redemption_value = self.POINTS_REDEMPTION_VALUE

    def add_customer(self, name, email=None, phone=None):
        """
        Add new customer to loyalty program
        
        Args:
            name (str): Customer name
            email (str): Customer email (optional)
            phone (str): Customer phone (optional)
            
        Returns:
            int: Customer ID or None on failure
        """
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                """
                INSERT INTO customers (name, email, phone, loyalty_points, total_spent, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, email, phone, 0, 0, datetime.now().isoformat())
            )
            db.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding customer: {str(e)}")
            return None

    def get_customer_by_name(self, name):
        """
        Get customer by name
        
        Args:
            name (str): Customer name
            
        Returns:
            dict: Customer data or None
        """
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                "SELECT id, name, email, phone, loyalty_points, total_spent, created_at FROM customers WHERE name = ?",
                (name,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'email': result[2],
                    'phone': result[3],
                    'loyalty_points': result[4],
                    'total_spent': result[5],
                    'created_at': result[6]
                }
            return None
        except Exception as e:
            print(f"Error fetching customer: {str(e)}")
            return None

    def get_customer_by_id(self, customer_id):
        """
        Get customer by ID
        
        Args:
            customer_id (int): Customer ID
            
        Returns:
            dict: Customer data or None
        """
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                "SELECT id, name, email, phone, loyalty_points, total_spent, created_at FROM customers WHERE id = ?",
                (customer_id,)
            )
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'email': result[2],
                    'phone': result[3],
                    'loyalty_points': result[4],
                    'total_spent': result[5],
                    'created_at': result[6]
                }
            return None
        except Exception as e:
            print(f"Error fetching customer: {str(e)}")
            return None

    def get_all_customers(self):
        """
        Get all customers
        
        Returns:
            list: List of customer dictionaries
        """
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                "SELECT id, name, email, phone, loyalty_points, total_spent, created_at FROM customers ORDER BY name"
            )
            results = cursor.fetchall()
            
            customers = []
            for row in results:
                customers.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'loyalty_points': row[4],
                    'total_spent': row[5],
                    'created_at': row[6]
                })
            return customers
        except Exception as e:
            print(f"Error fetching customers: {str(e)}")
            return []

    def add_loyalty_points(self, customer_id, bill_amount):
        """
        Add loyalty points based on bill amount
        
        Args:
            customer_id (int): Customer ID
            bill_amount (float): Bill amount (before discount)
            
        Returns:
            int: Points added or None on failure
        """
        try:
            points_to_add = int(bill_amount * self.points_per_rupee)
            
            cursor = db.connection.cursor()
            
            # Update customer loyalty points and total spent
            cursor.execute(
                """
                UPDATE customers
                SET loyalty_points = loyalty_points + ?,
                    total_spent = total_spent + ?
                WHERE id = ?
                """,
                (points_to_add, bill_amount, customer_id)
            )
            
            # Log transaction
            cursor.execute(
                """
                INSERT INTO loyalty_transactions (customer_id, points, transaction_type, amount, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (customer_id, points_to_add, 'EARNED', bill_amount, datetime.now().isoformat())
            )
            
            db.connection.commit()
            return points_to_add
            
        except Exception as e:
            print(f"Error adding loyalty points: {str(e)}")
            return None

    def redeem_loyalty_points(self, customer_id, points):
        """
        Redeem loyalty points for discount
        
        Args:
            customer_id (int): Customer ID
            points (int): Points to redeem
            
        Returns:
            float: Discount amount or None on failure
        """
        try:
            # Get customer current points
            customer = self.get_customer_by_id(customer_id)
            if not customer or customer['loyalty_points'] < points:
                return None
            
            discount = (points / self.points_redemption_value) * 100
            
            cursor = db.connection.cursor()
            
            # Update customer loyalty points
            cursor.execute(
                """
                UPDATE customers
                SET loyalty_points = loyalty_points - ?
                WHERE id = ?
                """,
                (points, customer_id)
            )
            
            # Log transaction
            cursor.execute(
                """
                INSERT INTO loyalty_transactions (customer_id, points, transaction_type, amount, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (customer_id, -points, 'REDEEMED', discount, datetime.now().isoformat())
            )
            
            db.connection.commit()
            return discount
            
        except Exception as e:
            print(f"Error redeeming points: {str(e)}")
            return None

    def get_loyalty_tier(self, customer_id):
        """
        Get customer loyalty tier based on total spent
        
        Args:
            customer_id (int): Customer ID
            
        Returns:
            str: Tier name (Bronze, Silver, Gold, Platinum)
        """
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            return "Unknown"
        
        total_spent = customer['total_spent']
        
        if total_spent < 5000:
            return "Bronze"
        elif total_spent < 15000:
            return "Silver"
        elif total_spent < 50000:
            return "Gold"
        else:
            return "Platinum"

    def get_tier_benefits(self, tier):
        """
        Get benefits for a loyalty tier
        
        Args:
            tier (str): Tier name
            
        Returns:
            dict: Tier benefits
        """
        benefits = {
            'Bronze': {
                'min_spent': 0,
                'max_spent': 5000,
                'discount_percent': 0,
                'points_multiplier': 1
            },
            'Silver': {
                'min_spent': 5000,
                'max_spent': 15000,
                'discount_percent': 2,
                'points_multiplier': 1.25
            },
            'Gold': {
                'min_spent': 15000,
                'max_spent': 50000,
                'discount_percent': 5,
                'points_multiplier': 1.5
            },
            'Platinum': {
                'min_spent': 50000,
                'max_spent': float('inf'),
                'discount_percent': 10,
                'points_multiplier': 2
            }
        }
        return benefits.get(tier, {})

    def get_loyalty_transactions(self, customer_id, limit=50):
        """
        Get loyalty transaction history
        
        Args:
            customer_id (int): Customer ID
            limit (int): Maximum transactions to retrieve
            
        Returns:
            list: List of transactions
        """
        try:
            cursor = db.connection.cursor()
            cursor.execute(
                """
                SELECT id, points, transaction_type, amount, created_at
                FROM loyalty_transactions
                WHERE customer_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (customer_id, limit)
            )
            
            results = cursor.fetchall()
            transactions = []
            for row in results:
                transactions.append({
                    'id': row[0],
                    'points': row[1],
                    'type': row[2],
                    'amount': row[3],
                    'created_at': row[4]
                })
            return transactions
        except Exception as e:
            print(f"Error fetching transactions: {str(e)}")
            return []

    def format_customer_profile(self, customer):
        """
        Format customer profile for display
        
        Args:
            customer (dict): Customer data
            
        Returns:
            str: Formatted profile string
        """
        if not customer:
            return "Customer not found"
        
        tier = self.get_loyalty_tier(customer['id'])
        
        output = []
        output.append("\n" + "="*50)
        output.append("CUSTOMER LOYALTY PROFILE")
        output.append("="*50)
        output.append(f"Name: {customer['name']}")
        output.append(f"Email: {customer['email'] or 'N/A'}")
        output.append(f"Phone: {customer['phone'] or 'N/A'}")
        output.append(f"Loyalty Tier: {tier}")
        output.append(f"Loyalty Points: {customer['loyalty_points']}")
        output.append(f"Total Spent: Rs. {customer['total_spent']:.2f}")
        output.append(f"Member Since: {customer['created_at'][:10]}")
        output.append("="*50 + "\n")
        
        return "\n".join(output)


# Global instance
loyalty_manager = LoyaltyManager()
