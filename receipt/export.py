"""
Receipt Export Module - Handles PDF and Text file export for bills
Phase 2: Receipt file export (PDF / text)
"""

import os
from datetime import datetime
from pathlib import Path


class ReceiptExporter:
    """Exports bills to PDF and text file formats"""

    def __init__(self, export_dir="receipts"):
        """
        Initialize exporter with output directory
        
        Args:
            export_dir (str): Directory to save exported receipts
        """
        self.export_dir = export_dir
        self._create_export_dir()

    def _create_export_dir(self):
        """Create export directory if it doesn't exist"""
        Path(self.export_dir).mkdir(exist_ok=True)

    def export_to_text(self, bill, receipt_text):
        """
        Export receipt to text file
        
        Args:
            bill: Bill object with id, customer_name, created_at
            receipt_text (str): Formatted receipt text
            
        Returns:
            str: Path to exported file or None on failure
        """
        try:
            timestamp = bill.created_at.strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{bill.id}_{timestamp}.txt"
            filepath = os.path.join(self.export_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            
            return filepath
        except Exception as e:
            print(f"Error exporting to text: {str(e)}")
            return None

    def export_to_pdf(self, bill, receipt_text):
        """
        Export receipt to PDF using reportlab
        
        Args:
            bill: Bill object with id, customer_name, created_at, bill_items
            receipt_text (str): Formatted receipt text
            
        Returns:
            str: Path to exported file or None on failure
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            
            timestamp = bill.created_at.strftime("%Y%m%d_%H%M%S")
            filename = f"receipt_{bill.id}_{timestamp}.pdf"
            filepath = os.path.join(self.export_dir, filename)
            
            # Create PDF
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - 0.5 * inch, "Baker Shop")
            
            c.setFont("Helvetica", 10)
            line_height = 0.2 * inch
            y_pos = height - 0.8 * inch
            
            # Date and time
            date_str = bill.created_at.strftime("%Y-%m-%d   %H:%M")
            c.drawString(0.5 * inch, y_pos, f"Date: {date_str}")
            y_pos -= line_height
            
            # Customer
            c.drawString(0.5 * inch, y_pos, f"Customer: {bill.customer_name}")
            y_pos -= line_height * 1.5
            
            # Items table header
            c.drawString(0.5 * inch, y_pos, "Item")
            c.drawString(3.5 * inch, y_pos, "Qty")
            c.drawString(4.5 * inch, y_pos, "Price")
            y_pos -= line_height
            
            # Draw line
            c.line(0.5 * inch, y_pos + 0.1 * inch, 7.5 * inch, y_pos + 0.1 * inch)
            y_pos -= line_height
            
            # Items
            c.setFont("Helvetica", 9)
            for item in bill.bill_items:
                item_text = f"{item.product_name}"
                c.drawString(0.5 * inch, y_pos, item_text)
                c.drawString(3.5 * inch, y_pos, str(item.quantity))
                c.drawString(4.5 * inch, y_pos, f"{item.total:.2f}")
                y_pos -= line_height
            
            # Draw line
            y_pos -= 0.1 * inch
            c.line(0.5 * inch, y_pos, 7.5 * inch, y_pos)
            y_pos -= line_height
            
            # Totals
            c.setFont("Helvetica-Bold", 10)
            c.drawString(3.5 * inch, y_pos, "Total:")
            c.drawString(5.5 * inch, y_pos, f"{bill.total_amount:.2f}")
            y_pos -= line_height
            
            if bill.discount > 0:
                c.drawString(3.5 * inch, y_pos, "Discount:")
                c.drawString(5.5 * inch, y_pos, f"{bill.discount:.2f}")
                y_pos -= line_height
            
            c.drawString(3.5 * inch, y_pos, "Net Amount:")
            c.drawString(5.5 * inch, y_pos, f"{bill.net_amount:.2f}")
            
            # Footer
            y_pos -= line_height * 2
            c.setFont("Helvetica", 8)
            c.drawCentredString(width / 2, y_pos, "Best Wishes!")
            y_pos -= line_height
            c.drawCentredString(width / 2, y_pos, "Ubaidi IT Solution")
            y_pos -= line_height
            c.drawCentredString(width / 2, y_pos, "03420372799")
            
            c.save()
            return filepath
            
        except ImportError:
            print("Error: reportlab not installed. Install with: pip install reportlab")
            return None
        except Exception as e:
            print(f"Error exporting to PDF: {str(e)}")
            return None

    def get_receipt_list(self):
        """
        Get list of all exported receipts
        
        Returns:
            list: List of receipt file paths
        """
        try:
            files = []
            if os.path.exists(self.export_dir):
                files = [os.path.join(self.export_dir, f) 
                        for f in os.listdir(self.export_dir) 
                        if f.startswith("receipt_")]
            return sorted(files, reverse=True)
        except Exception as e:
            print(f"Error listing receipts: {str(e)}")
            return []

    def view_receipt(self, filepath):
        """
        Display receipt file content
        
        Args:
            filepath (str): Path to receipt file
            
        Returns:
            str: File content or None on failure
        """
        try:
            if os.path.exists(filepath) and filepath.endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading receipt: {str(e)}")
            return None


# Global instance
receipt_exporter = ReceiptExporter()
