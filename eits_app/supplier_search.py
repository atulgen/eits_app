import frappe

@frappe.whitelist(allow_guest=False)
def search_suppliers(supplier_name=None, mobile_no=None, email_id=None):
    """
    Simple supplier search by name, mobile_no, or email_id
    
    Args:
        supplier_name: Supplier name to search (partial match)
        mobile_no: Mobile number to search (partial match) 
        email_id: Email to search (partial match)
    
    Returns:
        List of matching suppliers
    """
    try:
        # Build conditions
        conditions = []
        values = []
        
        if supplier_name:
            conditions.append("supplier_name LIKE %s")
            values.append(f"%{supplier_name}%")
        
        if mobile_no:
            conditions.append("mobile_no LIKE %s")
            values.append(f"%{mobile_no}%")
        
        if email_id:
            conditions.append("email_id LIKE %s") 
            values.append(f"%{email_id}%")
        
        # If no search parameters
        if not conditions:
            return {
                "status": "error",
                "message": "Please provide at least one search parameter",
                "data": []
            }
        
        # Join conditions with OR
        where_clause = " OR ".join(conditions)
        
        # Simple query with only the 3 fields you want
        query = f"""
            SELECT 
                name,
                supplier_name,
                mobile_no,
                email_id
            FROM `tabSupplier` 
            WHERE ({where_clause})
            AND disabled = 0
            ORDER BY supplier_name
            LIMIT 50
        """
        
        suppliers = frappe.db.sql(query, values, as_dict=True)
        
        return {
            "status": "success",
            "message": f"Found {len(suppliers)} suppliers",
            "data": suppliers
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        }