# seed.py - Populate database with initial inventory data

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.db import db
from database.models import Product

def seed_inventory():
    """Add default inventory items to the database"""
    
    # Initial inventory data
    items = [
        {"name": "Cakes", "price": 12, "stock": 12},
        {"name": "Cupcakes", "price": 8, "stock": 12},
        {"name": "Cookies", "price": 5, "stock": 12},
        {"name": "Biscuits", "price": 6, "stock": 12},
        {"name": "Savory", "price": 10, "stock": 12},
        {"name": "Snacks", "price": 4, "stock": 12},
        {"name": "Pastries", "price": 15, "stock": 12},
    ]
    
    print("Adding inventory items to database...")
    
    for item in items:
        # Check if product already exists
        products = db.get_all_products()
        if any(p.name == item["name"] for p in products):
            print(f"  ✓ {item['name']} already exists")
            continue
        
        # Create and add product
        product = Product(
            name=item["name"],
            price=item["price"],
            stock=item["stock"]
        )
        product_id = db.add_product(product)
        print(f"  ✓ Added {item['name']} (ID: {product_id})")
    
    print("\nInventory seeding complete!")

if __name__ == "__main__":
    # Initialize database if needed
    db.create_tables()
    db.initialize_default_users()
    
    # Seed inventory
    seed_inventory()