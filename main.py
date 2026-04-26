# main.py - Main entry point for Baker Management System

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.db import db
from auth.login import auth_manager
from inventory.products import product_manager
from billing.bill import bill_manager
from utils.helpers import *

try:
    from gui import POSApplication
except ImportError:
    POSApplication = None


def run_gui():
    """Run the PyQt5 GUI if available."""
    if not POSApplication:
        print("GUI is not available in this environment.")
        print("Install dependencies with: pip install -r requirements.txt")
        return False

    try:
        print("Starting GUI application...")
        from PyQt5.QtWidgets import QApplication
        import sys

        app = QApplication(sys.argv)
        window = POSApplication()
        window.show()
        print("GUI window created and shown.")
        sys.exit(app.exec_())
        return True
    except Exception as e:
        print(f"GUI failed to start: {e}")
        print("Falling back to console mode...")
        print()
        return False


def initialize_system():
    """Initialize database and default data"""
    print("Initializing Baker Management System...")
    db.create_tables()
    db.initialize_default_users()
    print("System initialized successfully!")

def login_menu():
    """Handle user login"""
    clear_screen()
    print_header("Baker Shop Management System - Login")

    username = get_string_input("Username: ")
    password = get_string_input("Password: ")

    if auth_manager.login(username, password):
        print(f"\nWelcome, {username}! ({auth_manager.get_current_user().role})")
        input("Press Enter to continue...")
        return True
    else:
        print("\nInvalid credentials. Please try again.")
        input("Press Enter to continue...")
        return False

def show_main_menu():
    """Display main menu based on user role"""
    clear_screen()
    print_header("Baker Shop Management System")

    user = auth_manager.get_current_user()
    print(f"Logged in as: {user.username} ({user.role})")
    print()

    # Common options
    options = ["Logout"]

    if auth_manager.is_owner() or auth_manager.is_employee():
        options.extend([
            "Add Product",
            "View Products",
            "Create Bill"
        ])

    if auth_manager.is_owner():
        options.extend([
            "Update Product",
            "View All Bills"
        ])

    print_menu(options)
    return options

def handle_main_menu():
    """Handle main menu interactions"""
    while True:
        options = show_main_menu()
        choice = select_menu_option(options)

        if choice == 0:  # Exit
            auth_manager.logout()
            break
        elif choice == 1:  # Logout
            auth_manager.logout()
            print("\nLogged out successfully!")
            input("Press Enter to continue...")
            break
        elif options[choice-1] == "Add Product":
            add_product_menu()
        elif options[choice-1] == "View Products":
            view_products_menu()
        elif options[choice-1] == "Create Bill":
            create_bill_menu()
        elif options[choice-1] == "Update Product":
            update_product_menu()
        elif options[choice-1] == "View All Bills":
            view_bills_menu()

def add_product_menu():
    """Add new product"""
    clear_screen()
    print_header("Add New Product")

    try:
        name = get_string_input("Product name: ")
        price = get_float_input("Price: ", min_value=0)
        stock = get_int_input("Initial stock: ", min_value=0)

        product_id = product_manager.add_product(name, price, stock)
        print(f"\nProduct '{name}' added successfully with ID: {product_id}")
    except Exception as e:
        print(f"\nError: {e}")

    input("\nPress Enter to continue...")

def view_products_menu():
    """View all products"""
    clear_screen()
    print_header("Product Inventory")

    products = product_manager.get_all_products()

    if not products:
        print("No products found.")
    else:
        print("ID".ljust(5) + "Name".ljust(20) + "Price".rjust(10) + "Stock".rjust(8))
        print("-" * 43)
        for product in products:
            print(f"{product.id:<5}{product.name:<20}{product.price:>10.2f}{product.stock:>8}")

    input("\nPress Enter to continue...")

def create_bill_menu():
    """Create a new bill"""
    clear_screen()
    print_header("Create New Bill")

    try:
        customer_name = get_string_input("Customer name: ")
        bill_manager.start_new_bill(customer_name)

        while True:
            clear_screen()
            print_header("Create New Bill")
            print(f"Customer: {customer_name}")
            print("\nCurrent items:")
            if bill_manager.current_bill_items:
                print("Product".ljust(20) + "Qty".rjust(5) + "Price".rjust(10) + "Total".rjust(10))
                print("-" * 45)
                for item in bill_manager.current_bill_items:
                    print(f"{item.product_name:<20}{item.quantity:>5}{item.price:>10.2f}{item.total:>10.2f}")
                total = sum(item.total for item in bill_manager.current_bill_items)
                print("-" * 45)
                print(f"{'Subtotal:':<35}{total:>10.2f}")
            else:
                print("No items added yet.")

            print("\nOptions:")
            print("1. Add item")
            print("2. Finalize bill")
            print("0. Cancel")

            choice = select_menu_option(["Add item", "Finalize bill"])

            if choice == 0:  # Cancel
                bill_manager.current_bill_items = []
                break
            elif choice == 1:  # Add item
                add_item_to_bill()
            elif choice == 2:  # Finalize
                finalize_bill()
                break

    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to continue...")

def add_item_to_bill():
    """Add item to current bill"""
    products = product_manager.get_all_products()
    if not products:
        print("No products available.")
        input("Press Enter to continue...")
        return

    print("\nAvailable products:")
    for product in products:
        print(f"{product.id}. {product.name} - ${product.price:.2f} (Stock: {product.stock})")

    product_id = get_int_input("Enter product ID: ", min_value=1)
    quantity = get_int_input("Enter quantity: ", min_value=1)

    try:
        bill_manager.add_item_to_bill(product_id, quantity)
        print("Item added to bill.")
    except Exception as e:
        print(f"Error: {e}")

    input("Press Enter to continue...")

def finalize_bill():
    """Finalize the current bill"""
    try:
        discount = get_float_input("Discount (0 for none): ", min_value=0)
        bill = bill_manager.finalize_bill(discount)

        print("\nBill created successfully!")
        print("\n" + "="*50)
        print(bill_manager.generate_receipt(bill))
        print("="*50)

    except Exception as e:
        print(f"Error: {e}")

    input("\nPress Enter to continue...")

def update_product_menu():
    """Update product details"""
    clear_screen()
    print_header("Update Product")

    products = product_manager.get_all_products()
    if not products:
        print("No products to update.")
        input("Press Enter to continue...")
        return

    print("Available products:")
    for product in products:
        print(f"{product.id}. {product.name} - ${product.price:.2f} (Stock: {product.stock})")

    product_id = get_int_input("Enter product ID to update: ", min_value=1)

    product = product_manager.get_product_by_id(product_id)
    if not product:
        print("Product not found.")
        input("Press Enter to continue...")
        return

    print(f"\nCurrent details: {product.name} - ${product.price:.2f} (Stock: {product.stock})")

    name = get_string_input("New name (leave empty to keep current): ", allow_empty=True)
    if not name:
        name = None

    price_input = input("New price (leave empty to keep current): ").strip()
    price = float(price_input) if price_input else None

    stock_input = input("New stock (leave empty to keep current): ").strip()
    stock = int(stock_input) if stock_input else None

    try:
        product_manager.update_product(product_id, name=name, price=price, stock=stock)
        print("Product updated successfully!")
    except Exception as e:
        print(f"Error: {e}")

    input("\nPress Enter to continue...")

def view_bills_menu():
    """View all bills"""
    clear_screen()
    print_header("All Bills")

    bills = bill_manager.get_all_bills()

    if not bills:
        print("No bills found.")
    else:
        print("ID".ljust(5) + "Customer".ljust(20) + "Date".ljust(12) + "Total".rjust(10) + "Net".rjust(10))
        print("-" * 57)
        for bill in bills:
            print(f"{bill.id:<5}{bill.customer_name:<20}{bill.created_at.strftime('%Y-%m-%d'):<12}{bill.total_amount:>10.2f}{bill.net_amount:>10.2f}")

        # Option to view receipt
        bill_id = get_int_input("\nEnter bill ID to view receipt (0 to skip): ", min_value=0)
        if bill_id > 0:
            bill = db.get_bill_with_items(bill_id)
            if bill:
                clear_screen()
                print_header("Bill Receipt")
                print(bill_manager.generate_receipt(bill))
                input("\nPress Enter to continue...")
            else:
                print("Bill not found.")
                input("Press Enter to continue...")

    input("\nPress Enter to continue...")

def main():
    """Main application loop"""
    print("Starting Baker Management System...")
    initialize_system()

    # Try to run GUI by default
    if POSApplication:
        print("Attempting to launch GUI...")
        if run_gui():
            return  # GUI ran successfully

    # Console mode
    if "--console" in sys.argv or not POSApplication:
        if POSApplication:
            print("GUI support is available. Launch it with: python main.py --gui")
            input("Press Enter to continue to console mode...")

        while True:
            clear_screen()
            print_header("Baker Shop Management System")

            if not auth_manager.get_current_user():
                if not login_menu():
                    continue
            else:
                handle_main_menu()

            # Check if user wants to exit completely
            if not auth_manager.get_current_user():
                if not confirm_action("\nDo you want to exit the application?" ):
                    continue
                else:
                    break
    else:
        print("GUI is not available in this environment.")
        print("Install dependencies with: pip install -r requirements.txt")
        print("Or run in console mode with: python main.py --console")
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()