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
    def __init__(self, id=None, name='', price=0.0, stock=0, created_at=None):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.created_at = created_at or datetime.now()

# Bill model
class Bill:
    def __init__(self, id=None, customer_name='', total_amount=0.0, discount=0.0, net_amount=0.0, created_at=None):
        self.id = id
        self.customer_name = customer_name
        self.total_amount = total_amount
        self.discount = discount
        self.net_amount = net_amount
        self.created_at = created_at or datetime.now()

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