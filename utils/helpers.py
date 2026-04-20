# helpers.py - Utility functions and helpers

import os
import sys

def clear_screen():
    """Clear the console screen"""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/Mac
        os.system('clear')

def get_float_input(prompt, min_value=None, max_value=None):
    """Get float input with validation"""
    while True:
        try:
            value = float(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}")
                continue
            return value
        except ValueError:
            print("Please enter a valid number")

def get_int_input(prompt, min_value=None, max_value=None):
    """Get integer input with validation"""
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f"Value must be at least {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Value must be at most {max_value}")
                continue
            return value
        except ValueError:
            print("Please enter a valid integer")

def get_string_input(prompt, allow_empty=False):
    """Get string input with validation"""
    while True:
        value = input(prompt).strip()
        if not allow_empty and not value:
            print("This field cannot be empty")
            continue
        return value

def confirm_action(prompt):
    """Get yes/no confirmation"""
    while True:
        response = input(prompt + " (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 50)
    print(title.center(50))
    print("=" * 50)

def print_menu(options):
    """Print a numbered menu"""
    print("\nMenu:")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("0. Exit")

def select_menu_option(options):
    """Get menu selection"""
    while True:
        try:
            choice = int(input("\nSelect option: "))
            if choice == 0:
                return 0
            if 1 <= choice <= len(options):
                return choice
            else:
                print(f"Please enter a number between 0 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")