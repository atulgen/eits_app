import frappe

@frappe.whitelist(allow_guest=False)
def search_uae_areas(area_name=None):
    """
    Simple UAE Area search by area_name
    Args:
        area_name: Area name to search (partial match)
    Returns:
        List of matching UAE areas
    """
    try:
        # Check if search parameter is provided
        if not area_name:
            return {
                "status": "error",
                "message": "Please provide area name to search",
                "data": []
            }
        
        # Simple query with area_name field
        query = """
            SELECT
                name,
                area_name
            FROM `tabUAE Area`
            WHERE area_name LIKE %s
            ORDER BY area_name
            LIMIT 50
        """
        
        areas = frappe.db.sql(query, [f"%{area_name}%"], as_dict=True)
        
        return {
            "status": "success",
            "message": f"Found {len(areas)} UAE areas",
            "data": areas
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        }