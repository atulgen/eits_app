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
            "label": _("Payment ID"),
            "fieldtype": "Link",
            "options": "EITS Payment",
            "width": 160,
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
            "fieldtype": "Data",
            "width": 130,
            "align": "left"
        },
        {
            "fieldname": "amountaed",
            "label": _("Amount (AED)"),
            "fieldtype": "Currency",
            "width": 120,
            "align": "right"
        },
        {
            "fieldname": "paid_by",
            "label": _("Paid By"),
            "fieldtype": "Data",
            "width": 150,
            "align": "left"
        },
        {
            "fieldname": "paid_to",
            "label": _("Paid To"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150,
            "align": "left"
        },
        {
            "fieldname": "custom_mode_of_payment",
            "label": _("Payment Method"),
            "fieldtype": "Link",
            "options": "Method of Payment",
            "width": 140,
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
    This query ensures we get unique payment records with image counts
    """
    conditions = get_conditions(filters)
    
    # Main query to get unique payment records with image count
    query = f"""
        SELECT 
            ep.name,
            ep.date,
            ep.bill_number,
            ep.amountaed,
            ep.paid_by,
            ep.paid_to,
            ep.custom_mode_of_payment,
            ep.docstatus,
            COUNT(CASE 
                WHEN ca.image IS NOT NULL 
                AND ca.image != '' 
                AND ca.image != '/files/' 
                THEN 1 
            END) as image_count,
            ep.name as view_images,
            ep.name as submit_action
        FROM `tabEITS Payment` ep
        LEFT JOIN `tabImage Attachments` ca 
            ON ca.parent = ep.name 
            AND ca.parenttype = 'EITS Payment'
            AND ca.docstatus != 2
        WHERE 
            ep.docstatus != 2 
            {conditions}
        GROUP BY 
            ep.name, 
            ep.date, 
            ep.bill_number, 
            ep.amountaed, 
            ep.paid_by, 
            ep.paid_to, 
            ep.custom_mode_of_payment,
            ep.docstatus
        ORDER BY 
            ep.date DESC, 
            ep.creation DESC
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
        conditions += " AND ep.date >= %(from_date)s"
    
    if filters.get("to_date"):
        conditions += " AND ep.date <= %(to_date)s"
    
    # Paid By filter (partial match)
    if filters.get("paid_by"):
        conditions += " AND ep.paid_by LIKE %(paid_by)s"
        filters["paid_by"] = f"%{filters['paid_by']}%"
    
    # Paid To filter (exact match)
    if filters.get("paid_to"):
        conditions += " AND ep.paid_to = %(paid_to)s"
    
    # Payment Method filter
    if filters.get("payment_method"):
        conditions += " AND ep.custom_mode_of_payment = %(payment_method)s"
    
    # Bill Number filter (partial match)
    if filters.get("bill_number"):
        conditions += " AND ep.bill_number LIKE %(bill_number)s"
        filters["bill_number"] = f"%{filters['bill_number']}%"
    
    # Only show records with images filter
    if filters.get("only_with_images"):
        conditions += """
            AND EXISTS (
                SELECT 1 FROM `tabImage Attachments` ca2 
                WHERE ca2.parent = ep.name 
                AND ca2.parenttype = 'EITS Payment'
                AND ca2.image IS NOT NULL 
                AND ca2.image != '' 
                AND ca2.image != '/files/'
                AND ca2.docstatus != 2
            )
        """
    
    return conditions

# ADD THIS NEW METHOD FOR SUBMITTING PAYMENT
@frappe.whitelist()
def submit_payment(payment_id):
    """
    Server method to submit a payment record
    """
    try:
        # Check if payment exists
        if not frappe.db.exists("EITS Payment", payment_id):
            frappe.throw(_("Payment record not found"))
        
        # Check if user has write permission
        if not frappe.has_permission("EITS Payment", "write", payment_id):
            frappe.throw(_("You don't have permission to submit this payment record"))
        
        # Get the document
        doc = frappe.get_doc("EITS Payment", payment_id)
        
        # Check if already submitted
        if doc.docstatus == 1:
            frappe.throw(_("Payment is already submitted"))
        
        # Check if cancelled
        if doc.docstatus == 2:
            frappe.throw(_("Cannot submit a cancelled payment"))
        
        # Submit the document
        doc.submit()
        
        frappe.db.commit()
        
        return {
            "success": True,
            "message": _("Payment {0} has been submitted successfully").format(payment_id),
            "docstatus": doc.docstatus
        }
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Error in submit_payment")
        frappe.throw(_("Error submitting payment: {0}").format(str(e)))

# ADD THIS NEW METHOD FOR FETCHING IMAGES
@frappe.whitelist()
def get_payment_images(payment_id):
    """
    Server method to fetch images for a specific payment
    This bypasses permission issues by using direct SQL query
    """
    try:
        # Verify the payment exists and user has access
        if not frappe.db.exists("EITS Payment", payment_id):
            frappe.throw(_("Payment record not found"))
        
        # Check if user has read permission for EITS Payment
        if not frappe.has_permission("EITS Payment", "read", payment_id):
            frappe.throw(_("You don't have permission to access this payment record"))
        
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
                AND parenttype = 'EITS Payment'
                AND docstatus != 2
                AND image IS NOT NULL 
                AND image != '' 
                AND image != '/files/'
            ORDER BY idx ASC
        """, (payment_id,), as_dict=True)
        
        return images
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in get_payment_images")
        frappe.throw(_("Error fetching images: {0}").format(str(e)))

# Optional: Add a function to get summary data
def get_chart_data(data, filters):
    """
    Optional function to provide chart data for the report
    This creates a simple chart showing payments by month
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
            'name': 'Payment Count',
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
