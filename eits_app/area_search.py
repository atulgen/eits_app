import frappe

@frappe.whitelist(allow_guest=False)
def search_uae_areas(area_name=None, emirate=None):
    """
    Enhanced UAE Area search by area_name and/or emirate
    Args:
        area_name: Area name to search (partial match)
        emirate: Emirate to filter by (partial match)
    Returns:
        List of matching UAE areas with emirate information
    """
    try:
        # Check if at least one search parameter is provided
        if not area_name and not emirate:
            return {
                "status": "error",
                "message": "Please provide area name or emirate to search",
                "data": []
            }

        # Build dynamic query based on provided parameters
        conditions = []
        params = []
        
        if area_name:
            conditions.append("area_name LIKE %s")
            params.append(f"%{area_name}%")
        
        if emirate:
            conditions.append("emirate LIKE %s")
            params.append(f"%{emirate}%")
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT
                name,
                area_name,
                emirate
            FROM `tabUAE Area`
            WHERE {where_clause}
            ORDER BY emirate, area_name
            LIMIT 50
        """
        
        areas = frappe.db.sql(query, params, as_dict=True)
        
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