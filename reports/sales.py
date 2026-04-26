"""
Sales Reports Module - Generates daily/monthly sales reports
Phase 2: Sales reports (daily/monthly)
"""

from datetime import datetime, timedelta
from database.db import db


class SalesReporter:
    """Generates sales analytics and reports"""

    def get_daily_sales(self, date=None):
        """
        Get sales data for a specific date
        
        Args:
            date (datetime): Date to report on (defaults to today)
            
        Returns:
            dict: Daily sales data including total, items sold, revenue
        """
        if date is None:
            date = datetime.now().date()
        
        try:
            cursor = db.connection.cursor()
            
            # Get bills for the date
            query = """
            SELECT id, total_amount, discount, net_amount, created_at
            FROM bills
            WHERE DATE(created_at) = ?
            ORDER BY created_at
            """
            
            cursor.execute(query, (date,))
            bills = cursor.fetchall()
            
            if not bills:
                return {
                    'date': date.isoformat(),
                    'total_sales': 0,
                    'total_discount': 0,
                    'net_revenue': 0,
                    'bills_count': 0,
                    'items_sold': 0,
                    'bills': []
                }
            
            total_sales = 0
            total_discount = 0
            net_revenue = 0
            items_sold = 0
            bills_list = []
            
            for bill in bills:
                bill_id, total, discount, net_amount, created_at = bill
                total_sales += total
                total_discount += discount
                net_revenue += net_amount
                
                # Count items in this bill
                item_query = "SELECT SUM(quantity) FROM bill_items WHERE bill_id = ?"
                cursor.execute(item_query, (bill_id,))
                qty_result = cursor.fetchone()
                bill_items_count = qty_result[0] if qty_result[0] else 0
                items_sold += bill_items_count
                
                bills_list.append({
                    'id': bill_id,
                    'total': total,
                    'discount': discount,
                    'net_amount': net_amount,
                    'time': created_at
                })
            
            return {
                'date': date.isoformat(),
                'total_sales': total_sales,
                'total_discount': total_discount,
                'net_revenue': net_revenue,
                'bills_count': len(bills_list),
                'items_sold': items_sold,
                'bills': bills_list
            }
            
        except Exception as e:
            print(f"Error generating daily report: {str(e)}")
            return None

    def get_monthly_sales(self, year=None, month=None):
        """
        Get sales data for a specific month
        
        Args:
            year (int): Year (defaults to current)
            month (int): Month 1-12 (defaults to current)
            
        Returns:
            dict: Monthly sales data with daily breakdown
        """
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        try:
            cursor = db.connection.cursor()
            
            # Get all bills for the month
            query = """
            SELECT id, total_amount, discount, net_amount, created_at
            FROM bills
            WHERE STRFTIME('%Y-%m', created_at) = ?
            ORDER BY created_at
            """
            
            month_str = f"{year:04d}-{month:02d}"
            cursor.execute(query, (month_str,))
            bills = cursor.fetchall()
            
            daily_breakdown = {}
            total_sales = 0
            total_discount = 0
            net_revenue = 0
            items_sold = 0
            bills_count = 0
            
            for bill in bills:
                bill_id, total, discount, net_amount, created_at = bill
                
                # Parse date
                bill_date = datetime.fromisoformat(created_at).date()
                date_key = bill_date.isoformat()
                
                if date_key not in daily_breakdown:
                    daily_breakdown[date_key] = {
                        'total_sales': 0,
                        'total_discount': 0,
                        'net_revenue': 0,
                        'bills_count': 0,
                        'items_sold': 0
                    }
                
                daily_breakdown[date_key]['total_sales'] += total
                daily_breakdown[date_key]['total_discount'] += discount
                daily_breakdown[date_key]['net_revenue'] += net_amount
                daily_breakdown[date_key]['bills_count'] += 1
                
                total_sales += total
                total_discount += discount
                net_revenue += net_amount
                bills_count += 1
                
                # Count items
                item_query = "SELECT SUM(quantity) FROM bill_items WHERE bill_id = ?"
                cursor.execute(item_query, (bill_id,))
                qty_result = cursor.fetchone()
                bill_items_count = qty_result[0] if qty_result[0] else 0
                daily_breakdown[date_key]['items_sold'] += bill_items_count
                items_sold += bill_items_count
            
            return {
                'year': year,
                'month': month,
                'month_str': f"{year}-{month:02d}",
                'total_sales': total_sales,
                'total_discount': total_discount,
                'net_revenue': net_revenue,
                'bills_count': bills_count,
                'items_sold': items_sold,
                'daily_breakdown': daily_breakdown,
                'average_daily_sales': total_sales / len(daily_breakdown) if daily_breakdown else 0,
                'average_bill_value': total_sales / bills_count if bills_count > 0 else 0
            }
            
        except Exception as e:
            print(f"Error generating monthly report: {str(e)}")
            return None

    def get_top_products(self, days=30):
        """
        Get top selling products in last N days
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            list: List of products sorted by quantity sold
        """
        try:
            cursor = db.connection.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = """
            SELECT product_id, product_name, SUM(quantity) as total_qty, SUM(total) as revenue
            FROM bill_items
            WHERE bill_id IN (
                SELECT id FROM bills WHERE created_at >= ?
            )
            GROUP BY product_id
            ORDER BY total_qty DESC
            """
            
            cursor.execute(query, (since_date,))
            products = cursor.fetchall()
            
            return [
                {
                    'product_id': p[0],
                    'product_name': p[1],
                    'quantity_sold': p[2],
                    'revenue': p[3]
                }
                for p in products
            ]
            
        except Exception as e:
            print(f"Error getting top products: {str(e)}")
            return []

    def format_daily_report(self, report):
        """
        Format daily report for display
        
        Args:
            report (dict): Daily report data
            
        Returns:
            str: Formatted report string
        """
        if not report:
            return "No sales data available"
        
        output = []
        output.append("\n" + "="*50)
        output.append("DAILY SALES REPORT")
        output.append("="*50)
        output.append(f"Date: {report['date']}")
        output.append(f"Total Sales: Rs. {report['total_sales']:.2f}")
        output.append(f"Total Discount: Rs. {report['total_discount']:.2f}")
        output.append(f"Net Revenue: Rs. {report['net_revenue']:.2f}")
        output.append(f"Number of Bills: {report['bills_count']}")
        output.append(f"Items Sold: {report['items_sold']}")
        
        if report['bills_count'] > 0:
            avg_bill = report['total_sales'] / report['bills_count']
            output.append(f"Avg Bill Value: Rs. {avg_bill:.2f}")
        
        output.append("="*50)
        return "\n".join(output)

    def format_monthly_report(self, report):
        """
        Format monthly report for display
        
        Args:
            report (dict): Monthly report data
            
        Returns:
            str: Formatted report string
        """
        if not report:
            return "No sales data available"
        
        output = []
        output.append("\n" + "="*50)
        output.append("MONTHLY SALES REPORT")
        output.append("="*50)
        output.append(f"Period: {report['month_str']}")
        output.append(f"Total Sales: Rs. {report['total_sales']:.2f}")
        output.append(f"Total Discount: Rs. {report['total_discount']:.2f}")
        output.append(f"Net Revenue: Rs. {report['net_revenue']:.2f}")
        output.append(f"Number of Bills: {report['bills_count']}")
        output.append(f"Items Sold: {report['items_sold']}")
        output.append(f"Avg Daily Sales: Rs. {report['average_daily_sales']:.2f}")
        output.append(f"Avg Bill Value: Rs. {report['average_bill_value']:.2f}")
        output.append("="*50)
        
        if report['daily_breakdown']:
            output.append("\nDAILY BREAKDOWN:")
            output.append("-"*50)
            for date, data in sorted(report['daily_breakdown'].items()):
                output.append(f"{date}: Rs. {data['net_revenue']:.2f} ({data['bills_count']} bills)")
        
        output.append("="*50 + "\n")
        return "\n".join(output)


# Global instance
reporter = SalesReporter()
