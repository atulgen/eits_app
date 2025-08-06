# Copyright (c) 2025, GennextIT and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2024, Aditya and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    """
    Main function that ERPNext calls to generate the report
    Returns columns and data
    """
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """
    Define the columns that will appear in the report
    Each column is a dictionary with field properties
    """
    return [
        {
            "fieldname": "name",
            "label": _("Receipt ID"),
            "fieldtype": "Link",
            "options": "Receipt EITS",
            "width": 140,
            "align": "left"
        },
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 100,
            "align": "center"
        },
        {
            "fieldname": "bill_number",
            "label": _("Bill Number"),
            "fieldtype": "Int",
            "width": 120,
            "align": "left"
        },
        {
            "fieldname": "amountaed",
            "label": _("Amount (AED)"),
            "fieldtype": "Float",
            "width": 120,
            "align": "right"
        },
        {
            "fieldname": "paid_by",
            "label": _("Paid By"),
            "fieldtype": "Data",
            "width": 130,
            "align": "left"
        },
        {
            "fieldname": "paid_from",
            "label": _("Paid From"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 130,
            "align": "left"
        },
        {
            "fieldname": "custom_mode_of_payment",
            "label": _("Payment Method"),
            "fieldtype": "Link",
            "options": "Method of Payment",
            "width": 130,
            "align": "left"
        },
        {
            "fieldname": "image_count",
            "label": _("Images"),
            "fieldtype": "Int",
            "width": 70,
            "align": "center"
        },
        {
            "fieldname": "view_images",
            "label": _("View Images"),
            "fieldtype": "Data",
            "width": 130,
            "align": "center"
        },
        {
            "fieldname": "submit_action",
            "label": _("Submit"),
            "fieldtype": "Data",
            "width": 120,
            "align": "center"
        }
    ]

def get_data(filters):
    """
    Fetch the actual data for the report
    This query ensures we get unique receipt records with image counts
    """
    conditions = get_conditions(filters)
    
    # Main query to get unique receipt records with image count
    query = f"""
        SELECT 
            er.name,
            er.date,
            er.bill_number,
            er.amountaed,
            er.paid_by,
            er.paid_from,
            er.custom_mode_of_payment,
            er.docstatus,
            COUNT(CASE 
                WHEN ca.image IS NOT NULL 
                AND ca.image != '' 
                AND ca.image != '/files/' 
                THEN 1 
            END) as image_count,
            er.name as view_images,
            er.name as submit_action
        FROM `tabReceipt EITS` er
        LEFT JOIN `tabImage Attachments` ca 
            ON ca.parent = er.name 
            AND ca.parenttype = 'Receipt EITS'
            AND ca.docstatus != 2
        WHERE 
            er.docstatus != 2 
            {conditions}
        GROUP BY 
            er.name, 
            er.date, 
            er.bill_number, 
            er.amountaed, 
            er.paid_by, 
            er.paid_from, 
            er.custom_mode_of_payment,
            er.docstatus
        ORDER BY 
            er.date DESC, 
            er.creation DESC
    """
    
    # Execute query and return results
    data = frappe.db.sql(query, filters, as_dict=True)
    
    # Process the data to add any additional formatting if needed
    for row in data:
        # Ensure amount is properly formatted
        if row.get('amountaed'):
            row['amountaed'] = float(row['amountaed']) if row['amountaed'] else 0.0
        
        # Ensure image count is an integer
        row['image_count'] = int(row['image_count']) if row['image_count'] else 0
        
        # Format the view_images column - just show text that will be handled by JS
        if row['image_count'] > 0:
            row['view_images'] = "View Images"
        else:
            row['view_images'] = "No Images"
        
        # Format submit action based on docstatus
        if row.get('docstatus') == 0:  # Draft
            row['submit_action'] = "Submit"
        elif row.get('docstatus') == 1:  # Submitted
            row['submit_action'] = "Submitted"
        else:  # Cancelled
            row['submit_action'] = "Cancelled"
    
    return data

def get_conditions(filters):
    """
    Build WHERE clause conditions based on user filters
    """
    conditions = ""
    
    # Date range filter
    if filters.get("from_date"):
        conditions += " AND er.date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND er.date <= %(to_date)s"
    
    # Paid By filter (partial match)
    if filters.get("paid_by"):
        conditions += " AND er.paid_by LIKE %(paid_by)s"
        filters["paid_by"] = f"%{filters['paid_by']}%"
    
    # Paid From filter (exact match)
    if filters.get("paid_from"):
        conditions += " AND er.paid_from = %(paid_from)s"
    
    # Payment Method filter
    if filters.get("payment_method"):
        conditions += " AND er.custom_mode_of_payment = %(payment_method)s"
    
    # Bill Number filter (partial match)
    if filters.get("bill_number"):
        conditions += " AND er.bill_number LIKE %(bill_number)s"
        filters["bill_number"] = f"%{filters['bill_number']}%"
    
    # Only show records with images filter
    if filters.get("only_with_images"):
        conditions += """
            AND EXISTS (
                SELECT 1 FROM `tabImage Attachments` ca2 
                WHERE ca2.parent = er.name 
                AND ca2.parenttype = 'Receipt EITS'
                AND ca2.image IS NOT NULL 
                AND ca2.image != '' 
                AND ca2.image != '/files/'
                AND ca2.docstatus != 2
            )
        """
    
    return conditions

# ADD THIS NEW METHOD FOR SUBMITTING RECEIPT
@frappe.whitelist()
def submit_receipt(receipt_id):
    """
    Server method to submit a receipt record
    """
    try:
        # Check if receipt exists
        if not frappe.db.exists("Receipt EITS", receipt_id):
            frappe.throw(_("Receipt record not found"))
        
        # Check if user has write permission
        if not frappe.has_permission("Receipt EITS", "write", receipt_id):
            frappe.throw(_("You don't have permission to submit this receipt record"))
        
        # Get the document
        doc = frappe.get_doc("Receipt EITS", receipt_id)
        
        # Check if already submitted
        if doc.docstatus == 1:
            frappe.throw(_("Receipt is already submitted"))
        
        # Check if cancelled
        if doc.docstatus == 2:
            frappe.throw(_("Cannot submit a cancelled receipt"))
        
        # Submit the document
        doc.submit()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Receipt {0} has been submitted successfully").format(receipt_id),
            "docstatus": doc.docstatus
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error in submit_receipt")
        frappe.throw(_("Error submitting receipt: {0}").format(str(e)))

# ADD THIS NEW METHOD FOR FETCHING IMAGES
@frappe.whitelist()
def get_receipt_images(receipt_id):
    """
    Server method to fetch images for a specific receipt
    This bypasses permission issues by using direct SQL query
    """
    try:
        # Verify the receipt exists and user has access
        if not frappe.db.exists("Receipt EITS", receipt_id):
            frappe.throw(_("Receipt record not found"))
        
        # Check if user has read permission for Receipt EITS
        if not frappe.has_permission("Receipt EITS", "read", receipt_id):
            frappe.throw(_("You don't have permission to access this receipt record"))
        
        # Fetch images using direct SQL query
        images = frappe.db.sql("""
            SELECT 
                name,
                image,
                remarks,
                idx
            FROM `tabImage Attachments`
            WHERE 
                parent = %s 
                AND parenttype = 'Receipt EITS'
                AND docstatus != 2
                AND image IS NOT NULL 
                AND image != '' 
                AND image != '/files/'
            ORDER BY idx ASC
        """, (receipt_id,), as_dict=True)
        
        return images
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_receipt_images")
        frappe.throw(_("Error fetching images: {0}").format(str(e)))

# Optional: Add a function to get summary data
def get_chart_data(data, filters):
    """
    Optional function to provide chart data for the report
    This creates a simple chart showing receipts by month
    """
    if not data:
        return None
    
    # Group data by month
    monthly_data = {}
    for row in data:
        if row.get('date'):
            month_key = frappe.utils.formatdate(row['date'], "MMM yyyy")
            if month_key not in monthly_data:
                monthly_data[month_key] = {'count': 0, 'amount': 0}
            monthly_data[month_key]['count'] += 1
            monthly_data[month_key]['amount'] += float(row.get('amountaed', 0))
    
    # Format for chart
    labels = list(monthly_data.keys())
    datasets = [
        {
            'name': 'Receipt Count',
            'values': [monthly_data[label]['count'] for label in labels]
        },
        {
            'name': 'Total Amount (AED)',
            'values': [monthly_data[label]['amount'] for label in labels]
        }
    ]
    
    return {
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        'type': 'bar',
        'height': 300
    }