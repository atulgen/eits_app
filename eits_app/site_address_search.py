# import frappe

# @frappe.whitelist(allow_guest=False)
# def search_site_addresses(custom_emirate=None, custom_area=None, custom_community=None, custom_street_name=None, custom_property_number=None):
#     """
#     Simple site address search by location fields (AND logic)
    
#     Args:
#         custom_emirate: UAE Emirate to search (partial match)
#         custom_area: UAE Area to search (partial match)
#         custom_community: UAE Community to search (partial match)
#         custom_street_name: Street Name to search (partial match)
#         custom_property_number: Property Number to search (partial match)
    
#     Returns:
#         List of matching site addresses
#     """
#     try:
#         # Build conditions
#         conditions = []
#         values = []
        
#         if custom_emirate:
#             conditions.append("custom_emirate LIKE %s")
#             values.append(f"%{custom_emirate}%")
        
#         if custom_area:
#             conditions.append("custom_area LIKE %s")
#             values.append(f"%{custom_area}%")
        
#         if custom_community:
#             conditions.append("custom_community LIKE %s")
#             values.append(f"%{custom_community}%")
        
#         if custom_street_name:
#             conditions.append("custom_street_name LIKE %s")
#             values.append(f"%{custom_street_name}%")
        
#         if custom_property_number:
#             conditions.append("custom_property_number LIKE %s")
#             values.append(f"%{custom_property_number}%")
        
#         # If no search parameters
#         if not conditions:
#             return {
#                 "status": "error",
#                 "message": "Please provide at least one search parameter",
#                 "data": []
#             }
        
#         # Join conditions with AND
#         where_clause = " AND ".join(conditions)
        
#         # Query Site Address doctype
#         query = f"""
#             SELECT 
#                 name,
#                 custom_emirate,
#                 custom_area,
#                 custom_community,
#                 custom_street_name,
#                 custom_property_number,
#                 custom_combined_address,
#                 custom_customer_
#             FROM `tabSite Address` 
#             WHERE ({where_clause})
#             ORDER BY custom_emirate, custom_area, custom_community
#             LIMIT 50
#         """
        
#         site_addresses = frappe.db.sql(query, values, as_dict=1)
        
#         # Get customer data for each site address
#         customer_data = []
#         for site_address in site_addresses:
#             if site_address.get('custom_customer_'):
#                 customer_query = """
#                     SELECT 
#                         name,
#                         customer_name,
#                         mobile_no,
#                         email_id
#                     FROM `tabCustomer`
#                     WHERE name = %s
#                 """
#                 customer_info = frappe.db.sql(customer_query, [site_address['custom_customer_']], as_dict=1)
#                 if customer_info:
#                     customer_data.append(customer_info[0])
#                 else:
#                     customer_data.append(None)
#             else:
#                 customer_data.append(None)
        
#         return {
#             "status": "success",
#             "message": f"Found {len(site_addresses)} site addresses",
#             "data": {
#                 "site_addresses": site_addresses,
#                 "customers": customer_data
#             }
#         }
        
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"An error occurred: {str(e)}",
#             "data": []
#         }




import frappe

@frappe.whitelist(allow_guest=False)
def search_site_addresses(custom_emirate=None, custom_area=None, custom_community=None, custom_street_name=None, custom_property_number=None):
    """
    Simple site address search by location fields (AND logic)
    
    Args:
        custom_emirate: UAE Emirate to search (partial match)
        custom_area: UAE Area to search (partial match)
        custom_community: UAE Community to search (partial match)
        custom_street_name: Street Name to search (partial match)
        custom_property_number: Property Number to search (partial match)
    
    Returns:
        List of matching site addresses
    """
    try:
        # Build conditions
        conditions = []
        values = []
        
        if custom_emirate:
            conditions.append("custom_emirate LIKE %s")
            values.append(f"%{custom_emirate}%")
        
        if custom_area:
            conditions.append("custom_area LIKE %s")
            values.append(f"%{custom_area}%")
        
        if custom_community:
            conditions.append("custom_community LIKE %s")
            values.append(f"%{custom_community}%")
        
        if custom_street_name:
            conditions.append("custom_street_name LIKE %s")
            values.append(f"%{custom_street_name}%")
        
        if custom_property_number:
            conditions.append("custom_property_number LIKE %s")
            values.append(f"%{custom_property_number}%")
        
        # If no search parameters
        if not conditions:
            return {
                "status": "error",
                "message": "Please provide at least one search parameter",
                "data": []
            }
        
        # Join conditions with AND
        where_clause = " AND ".join(conditions)
        
        # Query Site Address doctype
        query = f"""
            SELECT 
                name,
                custom_emirate,
                custom_area,
                custom_community,
                custom_street_name,
                custom_property_number,
                custom_combined_address,
                custom_customer_,
                custom_lead_name
            FROM `tabSite Address` 
            WHERE ({where_clause})
            ORDER BY custom_emirate, custom_area, custom_community
            LIMIT 50
        """
        
        site_addresses = frappe.db.sql(query, values, as_dict=1)
        
        # Get customer and lead data for each site address
        customer_data = []
        lead_data = []
        for site_address in site_addresses:
            # Get customer data
            if site_address.get('custom_customer_'):
                customer_query = """
                    SELECT 
                        name,
                        customer_name,
                        mobile_no,
                        email_id
                    FROM `tabCustomer`
                    WHERE name = %s
                """
                customer_info = frappe.db.sql(customer_query, [site_address['custom_customer_']], as_dict=1)
                if customer_info:
                    customer_data.append(customer_info[0])
                else:
                    customer_data.append(None)
            else:
                customer_data.append(None)
            
            # Get lead data
            if site_address.get('custom_lead_name'):
                lead_query = """
                    SELECT 
                        name,
                        lead_name,
                        mobile_no,
                        email_id
                    FROM `tabLead`
                    WHERE name = %s
                """
                lead_info = frappe.db.sql(lead_query, [site_address['custom_lead_name']], as_dict=1)
                if lead_info:
                    lead_data.append(lead_info[0])
                else:
                    lead_data.append(None)
            else:
                lead_data.append(None)
        
        return {
            "status": "success",
            "message": f"Found {len(site_addresses)} site addresses",
            "data": {
                "site_addresses": site_addresses,
                "customers": customer_data,
                "leads": lead_data
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        }