# bill.py - Billing and receipt generation

from datetime import datetime
from database.db import db
from database.models import Bill, BillItem
from inventory.products import product_manager
from auth.login import auth_manager
import config

class BillManager:
    def __init__(self):
        self.current_bill_items = []

    def start_new_bill(self, customer_name):
        """Start a new bill session"""
        auth_manager.require_login()

        if not customer_name.strip():
            raise ValueError("Customer name is required")

        self.current_bill_items = []
        self.customer_name = customer_name

    def add_item_to_bill(self, product_id, quantity):
        """Add an item to the current bill"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        product = product_manager.get_product_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        if product.stock < quantity:
            raise ValueError(f"Insufficient stock. Available: {product.stock}")

        # Check if product already in bill
        for item in self.current_bill_items:
            if item.product_id == product_id:
                item.quantity += quantity
                item.total = item.quantity * item.price
                return

        # Add new item
        item = BillItem(
            product_id=product_id,
            product_name=product.name,
            quantity=quantity,
            price=product.price,
            total=quantity * product.price
        )
        self.current_bill_items.append(item)

    def calculate_totals(self, discount=0.0):
        """Calculate bill totals"""
        total_amount = sum(item.total for item in self.current_bill_items)
        if discount < 0 or discount > total_amount:
            raise ValueError("Invalid discount amount")
        net_amount = total_amount - discount
        return total_amount, net_amount

    def finalize_bill(self, discount=0.0):
        """Finalize and save the bill"""
        if not self.current_bill_items:
            raise ValueError("No items in bill")

        total_amount, net_amount = self.calculate_totals(discount)

        # Create bill record
        bill = Bill(
            customer_name=self.customer_name,
            total_amount=total_amount,
            discount=discount,
            net_amount=net_amount
        )
        bill_id = db.create_bill(bill)

        # Add bill items and update stock
        for item in self.current_bill_items:
            item.bill_id = bill_id
            db.add_bill_item(item)
            product_manager.update_stock(item.product_id, item.quantity)

        # Clear current bill
        finalized_bill = db.get_bill_with_items(bill_id)
        self.current_bill_items = []
        return finalized_bill

    def generate_receipt(self, bill):
        """Generate receipt text"""
        receipt_lines = []
        receipt_lines.append(config.SHOP_NAME.center(30))
        receipt_lines.append("=" * 30)
        receipt_lines.append(f"Date: {bill.created_at.strftime('%Y-%m-%d')}   Time: {bill.created_at.strftime('%H:%M')}")
        receipt_lines.append("")
        receipt_lines.append("Customer: " + bill.customer_name)
        receipt_lines.append("")
        receipt_lines.append("Item".ljust(15) + "Qty".rjust(5) + "Price".rjust(10))
        receipt_lines.append("-" * 30)

        for item in bill.items:
            receipt_lines.append(
                item.product_name.ljust(15) +
                str(item.quantity).rjust(5) +
                f"{item.price:.2f}".rjust(10)
            )

        receipt_lines.append("-" * 30)
        receipt_lines.append(f"Total:".ljust(20) + f"{bill.total_amount:.2f}".rjust(10))
        if bill.discount > 0:
            receipt_lines.append(f"Discount:".ljust(20) + f"{bill.discount:.2f}".rjust(10))
        receipt_lines.append(f"Net Amount:".ljust(20) + f"{bill.net_amount:.2f}".rjust(10))
        receipt_lines.append("")
        receipt_lines.append(config.RECEIPT_FOOTER)

        return "\n".join(receipt_lines)

    def get_all_bills(self):
        """Get all bills (owner only)"""
        auth_manager.require_owner()
        return db.get_all_bills()

# Global bill manager instance
bill_manager = BillManager()