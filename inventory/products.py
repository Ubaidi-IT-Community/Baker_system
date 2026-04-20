# products.py - Product management operations

from database.db import db
from database.models import Product
from auth.login import auth_manager

class ProductManager:
    def add_product(self, name, price, stock):
        """Add a new product"""
        auth_manager.require_login()

        if price < 0 or stock < 0:
            raise ValueError("Price and stock must be non-negative")

        product = Product(name=name, price=price, stock=stock)
        product_id = db.add_product(product)
        return product_id

    def get_all_products(self):
        """Get all products"""
        auth_manager.require_login()
        return db.get_all_products()

    def get_product_by_id(self, product_id):
        """Get product by ID"""
        auth_manager.require_login()
        return db.get_product_by_id(product_id)

    def update_product(self, product_id, name=None, price=None, stock=None):
        """Update product details"""
        auth_manager.require_owner()  # Only owner can update products

        product = db.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        if name is not None:
            product.name = name
        if price is not None:
            if price < 0:
                raise ValueError("Price must be non-negative")
            product.price = price
        if stock is not None:
            if stock < 0:
                raise ValueError("Stock must be non-negative")
            product.stock = stock

        db.update_product(product)

    def update_stock(self, product_id, quantity_sold):
        """Reduce stock after sale"""
        product = db.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        if product.stock < quantity_sold:
            raise ValueError(f"Insufficient stock. Available: {product.stock}")

        new_stock = product.stock - quantity_sold
        db.update_product_stock(product_id, new_stock)

# Global product manager instance
product_manager = ProductManager()