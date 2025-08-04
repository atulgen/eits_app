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
#                 custom_customer_,
#                 custom_lead_name
#             FROM `tabSite Address` 
#             WHERE ({where_clause})
#             ORDER BY custom_emirate, custom_area, custom_community
#             LIMIT 50
#         """
        
#         site_addresses = frappe.db.sql(query, values, as_dict=1)
        
#         # Get customer and lead data for each site address
#         customer_data = []
#         lead_data = []
#         for site_address in site_addresses:
#             # Get customer data
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
            
#             # Get lead data
#             if site_address.get('custom_lead_name'):
#                 lead_query = """
#                     SELECT 
#                         name,
#                         lead_name,
#                         mobile_no,
#                         email_id
#                     FROM `tabLead`
#                     WHERE name = %s
#                 """
#                 lead_info = frappe.db.sql(lead_query, [site_address['custom_lead_name']], as_dict=1)
#                 if lead_info:
#                     lead_data.append(lead_info[0])
#                 else:
#                     lead_data.append(None)
#             else:
#                 lead_data.append(None)
        
#         return {
#             "status": "success",
#             "message": f"Found {len(site_addresses)} site addresses",
#             "data": {
#                 "site_addresses": site_addresses,
#                 "customers": customer_data,
#                 "leads": lead_data
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
def search_site_addresses(custom_emirate=None, custom_area=None, custom_community=None, 
                         custom_street_name=None, custom_property_number=None, 
                         custom_customer_phone_number=None, custom_customer_email=None,
                         custom_lead_phone_number=None, custom_lead_email=None):
    """
    Enhanced site address search by any field using AND logic
    
    Args:
        custom_emirate: UAE Emirate to search (partial match)
        custom_area: UAE Area to search (partial match)
        custom_community: UAE Community to search (partial match)
        custom_street_name: Street Name to search (partial match)
        custom_property_number: Property Number to search (partial match)
        custom_customer_phone_number: Customer phone number to search (partial match)
        custom_customer_email: Customer email to search (partial match)
        custom_lead_phone_number: Lead phone number to search (partial match)
        custom_lead_email: Lead email to search (partial match)
    
    Returns:
        List of matching site addresses with customer/lead details
    """
    try:
        # Build conditions for direct search on Site Address table
        conditions = []
        values = []
        
        # Address fields
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
        
        # Contact fields
        if custom_customer_phone_number:
            conditions.append("custom_customer_phone_number LIKE %s")
            values.append(f"%{custom_customer_phone_number}%")
        
        if custom_customer_email:
            conditions.append("custom_customer_email LIKE %s")
            values.append(f"%{custom_customer_email}%")
        
        if custom_lead_phone_number:
            conditions.append("custom_lead_phone_number LIKE %s")
            values.append(f"%{custom_lead_phone_number}%")
        
        if custom_lead_email:
            conditions.append("custom_lead_email LIKE %s")
            values.append(f"%{custom_lead_email}%")
        
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
                custom_lead_name,
                custom_customer_phone_number,
                custom_customer_email,
                custom_lead_phone_number,
                custom_lead_email
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
            customer_info, lead_info = get_customer_lead_data(site_address)
            customer_data.append(customer_info)
            lead_data.append(lead_info)
        
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


def search_by_contact_details(phone_number=None, email=None):
    """Search site addresses by phone number or email from customers/leads"""
    site_addresses = []
    
    try:
        # Search in customers
        if phone_number or email:
            customer_conditions = []
            customer_values = []
            
            if phone_number:
                customer_conditions.append("mobile_no LIKE %s")
                customer_values.append(f"%{phone_number}%")
            
            if email:
                customer_conditions.append("email_id LIKE %s") 
                customer_values.append(f"%{email}%")
            
            if customer_conditions:
                customer_where = " OR ".join(customer_conditions)
                customer_query = f"""
                    SELECT name
                    FROM `tabCustomer`
                    WHERE ({customer_where})
                """
                customers = frappe.db.sql(customer_query, customer_values, as_dict=1)
                
                # Get site addresses linked to these customers
                for customer in customers:
                    site_query = """
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
                        WHERE custom_customer_ = %s
                    """
                    customer_sites = frappe.db.sql(site_query, [customer['name']], as_dict=1)
                    site_addresses.extend(customer_sites)
        
        # Search in leads
        if phone_number or email:
            lead_conditions = []
            lead_values = []
            
            if phone_number:
                lead_conditions.append("mobile_no LIKE %s")
                lead_values.append(f"%{phone_number}%")
            
            if email:
                lead_conditions.append("email_id LIKE %s")
                lead_values.append(f"%{email}%")
            
            if lead_conditions:
                lead_where = " OR ".join(lead_conditions)
                lead_query = f"""
                    SELECT name
                    FROM `tabLead`
                    WHERE ({lead_where})
                """
                leads = frappe.db.sql(lead_query, lead_values, as_dict=1)
                
                # Get site addresses linked to these leads
                for lead in leads:
                    site_query = """
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
                        WHERE custom_lead_name = %s
                    """
                    lead_sites = frappe.db.sql(site_query, [lead['name']], as_dict=1)
                    site_addresses.extend(lead_sites)
                    
    except Exception as e:
        frappe.log_error(f"Error in search_by_contact_details: {str(e)}")
    
    return site_addresses


def search_by_address_fields(custom_emirate=None, custom_area=None, custom_community=None, 
                           custom_street_name=None, custom_property_number=None):
    """Search site addresses by address fields (original logic)"""
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
    
    if not conditions:
        return []
    
    where_clause = " AND ".join(conditions)
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
    
    return frappe.db.sql(query, values, as_dict=1)


def get_customer_lead_data(site_address):
    """Get customer and lead data for a site address"""
    customer_info = None
    lead_info = None
    
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
        customer_result = frappe.db.sql(customer_query, [site_address['custom_customer_']], as_dict=1)
        if customer_result:
            customer_info = customer_result[0]
    
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
        lead_result = frappe.db.sql(lead_query, [site_address['custom_lead_name']], as_dict=1)
        if lead_result:
            lead_info = lead_result[0]
    
    return customer_info, lead_info