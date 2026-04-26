# models.py - Database models and schema definitions

from datetime import datetime

# User model
class User:
    def __init__(self, id=None, username='', password_hash='', role='employee', created_at=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now()

# Product model
class Product:
    def __init__(self, id=None, name='', price=0.0, stock=0, category_id=None, min_stock=5, created_at=None):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.category_id = category_id
        self.min_stock = min_stock
        self.created_at = created_at or datetime.now()

# Category model
class Category:
    def __init__(self, id=None, name='', description='', created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now()

# Payment Method model
class PaymentMethod:
    def __init__(self, id=None, name='', description=''):
        self.id = id
        self.name = name
        self.description = description

# Refund model
class Refund:
    def __init__(self, id=None, bill_id=None, reason='', amount=0.0, created_at=None):
        self.id = id
        self.bill_id = bill_id
        self.reason = reason
        self.amount = amount
        self.created_at = created_at or datetime.now()

# Bill model
class Bill:
    def __init__(self, id=None, customer_name='', total_amount=0.0, discount=0.0, net_amount=0.0, payment_method='Cash', created_at=None):
        self.id = id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.discount = discount
        self.net_amount = net_amount
        self.payment_method = payment_method
        self.created_at = created_at or datetime.now()
        self.items = []  # List of BillItem objects
        self.bill_items = []  # Alias for items (used in some contexts)

# BillItem model
class BillItem:
    def __init__(self, id=None, bill_id=None, product_id=None, product_name='', quantity=0, price=0.0, total=0.0):
        self.id = id
        self.bill_id = bill_id
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.total = total


# Customer model (Phase 3: Loyalty)
class Customer:
    def __init__(self, id=None, name='', email=None, phone=None, loyalty_points=0, total_spent=0.0, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.loyalty_points = loyalty_points
        self.total_spent = total_spent
        self.created_at = created_at or datetime.now()


# LoyaltyTransaction model (Phase 3)
class LoyaltyTransaction:
    def __init__(self, id=None, customer_id=None, points=0, transaction_type='EARNED', amount=0.0, created_at=None):
        self.id = id
        self.customer_id = customer_id
        self.points = points
        self.transaction_type = transaction_type  # EARNED or REDEEMED
        self.amount = amount
        self.created_at = created_at or datetime.now()