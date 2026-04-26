# Customer module initialization
from .customer import customer_manager, CustomerManager
from .loyalty import loyalty_manager, LoyaltyManager

__all__ = ['customer_manager', 'CustomerManager', 'loyalty_manager', 'LoyaltyManager']
