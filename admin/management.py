# admin_management.py - User and system administration

from database.db import db
from database.models import Category, PaymentMethod, Refund
from auth.login import auth_manager


class AdminManager:
    """Manages administrative functions (owner-only)"""

    def add_category(self, name, description=''):
        """Add a new product category"""
        auth_manager.require_owner()
        category = Category(name=name, description=description)
        return db.add_category(category)

    def get_all_categories(self):
        """Get all categories"""
        return db.get_all_categories()

    def add_payment_method(self, name, description=''):
        """Add a payment method"""
        auth_manager.require_owner()
        method = PaymentMethod(name=name, description=description)
        db.add_payment_method(method)

    def get_all_payment_methods(self):
        """Get all payment methods"""
        return db.get_all_payment_methods()

    def create_refund(self, bill_id, reason, amount):
        """Create a refund for a bill"""
        auth_manager.require_owner()
        refund = Refund(bill_id=bill_id, reason=reason, amount=amount)
        return db.create_refund(refund)

    def get_refunds_by_bill(self, bill_id):
        """Get refunds for a bill"""
        return db.get_refunds_by_bill(bill_id)

    def set_low_stock_threshold(self, product_id, min_stock):
        """Set minimum stock threshold for a product"""
        auth_manager.require_owner()
        if min_stock < 0:
            raise ValueError("Minimum stock cannot be negative")
        db.update_product_min_stock(product_id, min_stock)

    def get_low_stock_alerts(self):
        """Get all products below minimum stock"""
        return db.get_low_stock_products()

    def search_bills(self, customer_name=None, start_date=None, end_date=None):
        """Search bills by customer or date range"""
        return db.search_bills(customer_name, start_date, end_date)

    def format_low_stock_alert(self, products):
        """Format low stock products for display"""
        if not products:
            return "All products are in stock."
        
        output = []
        output.append("\n" + "="*60)
        output.append("LOW STOCK ALERT - REORDER REQUIRED")
        output.append("="*60)
        
        for product in products:
            shortage = product.min_stock - product.stock
            output.append(
                f"ID: {product.id} | {product.name:<25} | "
                f"Stock: {product.stock}/{product.min_stock} | "
                f"Shortage: {shortage}"
            )
        
        output.append("="*60 + "\n")
        return "\n".join(output)

# Global admin manager instance
admin_manager = AdminManager()
