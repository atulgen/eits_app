import frappe

@frappe.whitelist(allow_guest=False)
def search_uae_communities(uae_area=None, community_name=None):
    """
    UAE Community search by UAE Area and/or community name
    Args:
        uae_area: UAE Area to filter communities by
        community_name: Community name to search (partial match)
    Returns:
        List of matching UAE communities with area information
    """
    try:
        # Check if at least one search parameter is provided
        if not uae_area and not community_name:
            return {
                "status": "error",
                "message": "Please provide UAE area or community name to search",
                "data": []
            }

        # Build dynamic query based on provided parameters
        conditions = []
        params = []
        
        if uae_area:
            conditions.append("area = %s")
            params.append(uae_area)
        
        if community_name:
            conditions.append("community_name LIKE %s")
            params.append(f"%{community_name}%")
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT
                name,
                community_name,
                area
            FROM `tabUAE Community`
            WHERE {where_clause}
            ORDER BY community_name
            LIMIT 50
        """
        
        communities = frappe.db.sql(query, params, as_dict=True)
        
        return {
            "status": "success",
            "message": f"Found {len(communities)} UAE communities",
            "data": communities
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        }