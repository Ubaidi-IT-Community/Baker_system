"""
Logging System - Tracks user actions and system events
Phase 2: Logging system

Note: This module avoids importing Python's standard library 'logging' module
to prevent naming conflicts with the local 'logging' directory package.
"""

import os
from datetime import datetime
from pathlib import Path


class SimpleLogger:
    """Simple file-based logger without stdlib logging module dependency"""
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.level = "DEBUG"
    
    def _write_log(self, level, message):
        """Write log entry to file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - BakerSystem - {level:8s} - {message}\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Also print to console for INFO level and above
            if level in ["INFO", "WARNING", "ERROR", "CRITICAL"]:
                print(f"[{level}] {message}")
                
        except Exception as e:
            print(f"Error writing log: {str(e)}")
    
    def debug(self, message):
        self._write_log("DEBUG", message)
    
    def info(self, message):
        self._write_log("INFO", message)
    
    def warning(self, message):
        self._write_log("WARNING", message)
    
    def error(self, message):
        self._write_log("ERROR", message)
    
    def critical(self, message):
        self._write_log("CRITICAL", message)


class SystemLogger:
    """Manages application logging with file-based output"""

    def __init__(self, log_dir="logs"):
        """
        Initialize logger
        
        Args:
            log_dir (str): Directory to store log files
        """
        self.log_dir = log_dir
        self._create_log_dir()
        self._setup_logger()

    def _create_log_dir(self):
        """Create log directory if it doesn't exist"""
        Path(self.log_dir).mkdir(exist_ok=True)

    def _setup_logger(self):
        """Configure logging with file handler"""
        today = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(self.log_dir, f"baker_system_{today}.log")
        self.logger = SimpleLogger(log_file)

    def log_login(self, username, role, success=True):
        """Log user login attempt"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"LOGIN {status}: username={username}, role={role}")

    def log_logout(self, username):
        """Log user logout"""
        self.logger.info(f"LOGOUT: username={username}")

    def log_product_add(self, username, product_name, price, stock):
        """Log product addition"""
        self.logger.info(
            f"PRODUCT_ADD: user={username}, name={product_name}, "
            f"price={price}, stock={stock}"
        )

    def log_product_update(self, username, product_id, name, price, stock):
        """Log product update"""
        self.logger.info(
            f"PRODUCT_UPDATE: user={username}, id={product_id}, "
            f"name={name}, price={price}, stock={stock}"
        )

    def log_product_stock_update(self, username, product_id, quantity_sold):
        """Log product stock update"""
        self.logger.info(
            f"STOCK_UPDATE: user={username}, product_id={product_id}, "
            f"quantity_sold={quantity_sold}"
        )

    def log_bill_create(self, username, customer_name, bill_id, total, items_count):
        """Log bill creation"""
        self.logger.info(
            f"BILL_CREATE: user={username}, customer={customer_name}, "
            f"bill_id={bill_id}, total={total}, items={items_count}"
        )

    def log_receipt_export(self, username, bill_id, export_format, filepath):
        """Log receipt export"""
        self.logger.info(
            f"RECEIPT_EXPORT: user={username}, bill_id={bill_id}, "
            f"format={export_format}, path={filepath}"
        )

    def log_report_generated(self, username, report_type, date_range):
        """Log report generation"""
        self.logger.info(
            f"REPORT_GENERATED: user={username}, type={report_type}, "
            f"range={date_range}"
        )

    def log_error(self, username, operation, error_msg):
        """Log error with user context"""
        self.logger.error(
            f"ERROR: user={username}, operation={operation}, error={error_msg}"
        )

    def log_permission_denied(self, username, operation):
        """Log permission denied attempt"""
        self.logger.warning(
            f"PERMISSION_DENIED: user={username}, operation={operation}"
        )

    def log_system_event(self, event_type, message):
        """Log general system event"""
        self.logger.info(f"SYSTEM_EVENT [{event_type}]: {message}")

    def get_logs(self, lines=100):
        """
        Get recent log entries
        
        Args:
            lines (int): Number of recent lines to retrieve
            
        Returns:
            str: Recent log content
        """
        try:
            today = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(self.log_dir, f"baker_system_{today}.log")
            
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return ''.join(all_lines[-lines:])
            return "No logs available"
        except Exception as e:
            return f"Error reading logs: {str(e)}"

    def get_user_activity(self, username, days=7):
        """
        Get activity log for a specific user
        
        Args:
            username (str): Username to filter by
            days (int): Number of days to look back
            
        Returns:
            list: List of user activities
        """
        from datetime import timedelta
        
        try:
            # Combine logs from recent days
            activities = []
            for i in range(days):
                date_str = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
                log_file = os.path.join(self.log_dir, f"baker_system_{date_str}.log")
                
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if username in line:
                                activities.append(line.strip())
            
            return sorted(activities, reverse=True)
        except Exception as e:
            print(f"Error retrieving user activity: {str(e)}")
            return []


# Global instance
system_logger = SystemLogger()



