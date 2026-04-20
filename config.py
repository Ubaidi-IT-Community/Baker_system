# config.py - Configuration settings for Baker Management System

import os

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'baker.db')

# Shop information
SHOP_NAME = "Baker Shop"
SHOP_CONTACT = "Ubaidi IT Solution 03420372799"

# Default users (for initial setup)
DEFAULT_USERS = [
    {
        'username': 'emp@001',
        'password': '221121',
        'role': 'employee'
    },
    {
        'username': 'emp@002',
        'password': '221121',
        'role': 'employee'
    },
    {
        'username': 'Baker@Owner.name',
        'password': 'Owner1234@',
        'role': 'owner'
    }
]

# Receipt footer
RECEIPT_FOOTER = "Best Wishes!\nUbaidi IT Solution\n03420372799"