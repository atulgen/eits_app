# import frappe
# import re

# def build_phone_search_condition(field_name, search_phone):
#     """
#     Build SQL condition for phone number search that handles various formats
#     """
#     if not search_phone:
#         return None, []
    
#     # Create condition that will match phone numbers in different formats
#     condition = f"""(
#         {field_name} LIKE %s OR 
#         REPLACE(REPLACE(REPLACE(REPLACE(REPLACE({field_name}, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') LIKE %s
#     )"""
    
#     # Normalize search phone for second condition
#     normalized_search = re.sub(r'[^\d]', '', str(search_phone))
    
#     values = [f"%{search_phone}%", f"%{normalized_search}%"]
    
#     return condition, values

# @frappe.whitelist(allow_guest=False)
# def search_site_addresses(custom_emirate=None, custom_area=None, custom_community=None, 
#                          custom_street_name=None, custom_property_number=None, 
#                          custom_customer_phone_number=None, custom_customer_email=None,
#                          custom_lead_phone_number=None, custom_lead_email=None):
#     """
#     Comprehensive site address search by any field using AND logic
#     Searches both Site Address table and Customer/Lead tables for phone/email
    
#     Args:
#         custom_emirate: UAE Emirate to search (partial match)
#         custom_area: UAE Area to search (partial match)
#         custom_community: UAE Community to search (partial match)
#         custom_street_name: Street Name to search (partial match)
#         custom_property_number: Property Number to search (partial match)
#         custom_customer_phone_number: Customer phone number to search (partial match)
#         custom_customer_email: Customer email to search (partial match)
#         custom_lead_phone_number: Lead phone number to search (partial match)
#         custom_lead_email: Lead email to search (partial match)
    
#     Returns:
#         List of matching site addresses with integrated customer/lead details
#     """
#     try:
#         all_site_addresses = []
        
#         # Method 1: Direct search in Site Address table
#         site_addresses_direct = search_site_addresses_direct(
#             custom_emirate, custom_area, custom_community, 
#             custom_street_name, custom_property_number,
#             custom_customer_phone_number, custom_customer_email,
#             custom_lead_phone_number, custom_lead_email
#         )
        
#         # Method 2: Search by phone/email in Customer/Lead tables
#         site_addresses_indirect = []
        
#         # Search customers by phone/email and get their site addresses
#         if custom_customer_phone_number or custom_customer_email:
#             customer_sites = search_by_customer_contact(
#                 custom_customer_phone_number, custom_customer_email
#             )
#             site_addresses_indirect.extend(customer_sites)
        
#         # Search leads by phone/email and get their site addresses  
#         if custom_lead_phone_number or custom_lead_email:
#             lead_sites = search_by_lead_contact(
#                 custom_lead_phone_number, custom_lead_email
#             )
#             site_addresses_indirect.extend(lead_sites)
        
#         # Combine and deduplicate results
#         all_site_addresses = site_addresses_direct + site_addresses_indirect
        
#         # Remove duplicates based on site address name
#         unique_sites = {}
#         for site in all_site_addresses:
#             site_name = site.get('name') or site.get('site_name')
#             if site_name not in unique_sites:
#                 unique_sites[site_name] = site
        
#         site_addresses = list(unique_sites.values())
        
#         # If no results from any method and we have search criteria
#         if not site_addresses:
#             # Check if we have any search parameters
#             has_params = any([
#                 custom_emirate, custom_area, custom_community, 
#                 custom_street_name, custom_property_number,
#                 custom_customer_phone_number, custom_customer_email,
#                 custom_lead_phone_number, custom_lead_email
#             ])
            
#             if not has_params:
#                 return {
#                     "status": "error",
#                     "message": "Please provide at least one search parameter",
#                     "data": []
#                 }
#             else:
#                 return {
#                     "status": "success",
#                     "message": "No site addresses found matching your criteria",
#                     "data": []
#                 }
        
#         # Integrate customer and lead data for each site address
#         integrated_results = []
#         for site_address in site_addresses:
#             # Get customer and lead data
#             customer_info, lead_info = get_customer_lead_data(site_address)
            
#             # Create integrated result
#             integrated_record = {
#                 # Site Address fields
#                 "site_name": site_address.get('name'),
#                 "custom_emirate": site_address.get('custom_emirate'),
#                 "custom_area": site_address.get('custom_area'),
#                 "custom_community": site_address.get('custom_community'),
#                 "custom_street_name": site_address.get('custom_street_name'),
#                 "custom_property_number": site_address.get('custom_property_number'),
#                 "custom_combined_address": site_address.get('custom_combined_address'),
#                 "custom_customer_phone_number": site_address.get('custom_customer_phone_number'),
#                 "custom_customer_email": site_address.get('custom_customer_email'),
#                 "custom_lead_phone_number": site_address.get('custom_lead_phone_number'),
#                 "custom_lead_email": site_address.get('custom_lead_email'),
                
#                 # Customer details (if exists)
#                 "customer_details": customer_info,
                
#                 # Lead details (if exists)
#                 "lead_details": lead_info,
                
#                 # Reference fields
#                 "custom_customer_": site_address.get('custom_customer_'),
#                 "custom_lead_name": site_address.get('custom_lead_name'),
                
#                 # Search method indicator
#                 "found_via": site_address.get('found_via', 'direct_search')
#             }
            
#             integrated_results.append(integrated_record)
        
#         return {
#             "status": "success",
#             "message": f"Found {len(integrated_results)} site addresses",
#             "data": integrated_results
#         }
        
#     except Exception as e:
#         return {
#             "status": "error", 
#             "message": f"An error occurred: {str(e)}",
#             "data": []
#         }


# def search_site_addresses_direct(custom_emirate=None, custom_area=None, custom_community=None, 
#                                custom_street_name=None, custom_property_number=None,
#                                custom_customer_phone_number=None, custom_customer_email=None,
#                                custom_lead_phone_number=None, custom_lead_email=None):
#     """Search directly in Site Address table"""
#     conditions = []
#     values = []
    
#     # Address fields
#     if custom_emirate:
#         conditions.append("custom_emirate LIKE %s")
#         values.append(f"%{custom_emirate}%")
    
#     if custom_area:
#         conditions.append("custom_area LIKE %s")
#         values.append(f"%{custom_area}%")
    
#     if custom_community:
#         conditions.append("custom_community LIKE %s")
#         values.append(f"%{custom_community}%")
    
#     if custom_street_name:
#         conditions.append("custom_street_name LIKE %s")
#         values.append(f"%{custom_street_name}%")
    
#     if custom_property_number:
#         conditions.append("custom_property_number LIKE %s")
#         values.append(f"%{custom_property_number}%")
    
#     # Enhanced phone number search for Site Address
#     if custom_customer_phone_number:
#         phone_condition, phone_values = build_phone_search_condition(
#             "custom_customer_phone_number", custom_customer_phone_number
#         )
#         if phone_condition:
#             conditions.append(phone_condition)
#             values.extend(phone_values)
    
#     if custom_lead_phone_number:
#         phone_condition, phone_values = build_phone_search_condition(
#             "custom_lead_phone_number", custom_lead_phone_number
#         )
#         if phone_condition:
#             conditions.append(phone_condition)
#             values.extend(phone_values)
    
#     # Email fields (unchanged)
#     if custom_customer_email:
#         conditions.append("custom_customer_email LIKE %s")
#         values.append(f"%{custom_customer_email}%")
    
#     if custom_lead_email:
#         conditions.append("custom_lead_email LIKE %s")
#         values.append(f"%{custom_lead_email}%")
    
#     if not conditions:
#         return []
    
#     where_clause = " AND ".join(conditions)
#     query = f"""
#         SELECT 
#             name,
#             custom_emirate,
#             custom_area,
#             custom_community,
#             custom_street_name,
#             custom_property_number,
#             custom_combined_address,
#             custom_customer_,
#             custom_lead_name,
#             custom_customer_phone_number,
#             custom_customer_email,
#             custom_lead_phone_number,
#             custom_lead_email
#         FROM `tabSite Address` 
#         WHERE ({where_clause})
#         ORDER BY custom_emirate, custom_area, custom_community
#         LIMIT 50
#     """
    
#     results = frappe.db.sql(query, values, as_dict=1)
    
#     # Add search method indicator
#     for result in results:
#         result['found_via'] = 'direct_search'
    
#     return results


# def search_by_customer_contact(phone_number=None, email=None):
#     """Search site addresses by customer phone/email from Customer table"""
#     if not phone_number and not email:
#         return []
    
#     try:
#         customer_conditions = []
#         customer_values = []
        
#         # Enhanced phone number search for Customer table
#         if phone_number:
#             phone_condition, phone_values = build_phone_search_condition("mobile_no", phone_number)
#             if phone_condition:
#                 customer_conditions.append(phone_condition)
#                 customer_values.extend(phone_values)
        
#         if email:
#             customer_conditions.append("email_id LIKE %s")
#             customer_values.append(f"%{email}%")
        
#         customer_where = " OR ".join(customer_conditions)
#         customer_query = f"""
#             SELECT name, customer_name, mobile_no, email_id
#             FROM `tabCustomer`
#             WHERE ({customer_where})
#         """
        
#         customers = frappe.db.sql(customer_query, customer_values, as_dict=1)
        
#         site_addresses = []
#         for customer in customers:
#             site_query = """
#                 SELECT 
#                     name,
#                     custom_emirate,
#                     custom_area,
#                     custom_community,
#                     custom_street_name,
#                     custom_property_number,
#                     custom_combined_address,
#                     custom_customer_,
#                     custom_lead_name,
#                     custom_customer_phone_number,
#                     custom_customer_email,
#                     custom_lead_phone_number,
#                     custom_lead_email
#                 FROM `tabSite Address`
#                 WHERE custom_customer_ = %s
#             """
#             customer_sites = frappe.db.sql(site_query, [customer['name']], as_dict=1)
            
#             # Add search method indicator
#             for site in customer_sites:
#                 site['found_via'] = 'customer_contact_search'
#                 site['matched_customer'] = customer
            
#             site_addresses.extend(customer_sites)
        
#         return site_addresses
        
#     except Exception as e:
#         frappe.log_error(f"Error in search_by_customer_contact: {str(e)}")
#         return []


# def search_by_lead_contact(phone_number=None, email=None):
#     """Search site addresses by lead phone/email from Lead table"""
#     if not phone_number and not email:
#         return []
    
#     try:
#         lead_conditions = []
#         lead_values = []
        
#         # Enhanced phone number search for Lead table
#         if phone_number:
#             phone_condition, phone_values = build_phone_search_condition("mobile_no", phone_number)
#             if phone_condition:
#                 lead_conditions.append(phone_condition)
#                 lead_values.extend(phone_values)
        
#         if email:
#             lead_conditions.append("email_id LIKE %s")
#             lead_values.append(f"%{email}%")
        
#         lead_where = " OR ".join(lead_conditions)
#         lead_query = f"""
#             SELECT name, lead_name, mobile_no, email_id, status
#             FROM `tabLead`
#             WHERE ({lead_where})
#         """
        
#         leads = frappe.db.sql(lead_query, lead_values, as_dict=1)
        
#         site_addresses = []
#         for lead in leads:
#             site_query = """
#                 SELECT 
#                     name,
#                     custom_emirate,
#                     custom_area,
#                     custom_community,
#                     custom_street_name,
#                     custom_property_number,
#                     custom_combined_address,
#                     custom_customer_,
#                     custom_lead_name,
#                     custom_customer_phone_number,
#                     custom_customer_email,
#                     custom_lead_phone_number,
#                     custom_lead_email
#                 FROM `tabSite Address`
#                 WHERE custom_lead_name = %s
#             """
#             lead_sites = frappe.db.sql(lead_query, [lead['name']], as_dict=1)
            
#             # Add search method indicator
#             for site in lead_sites:
#                 site['found_via'] = 'lead_contact_search'
#                 site['matched_lead'] = lead
            
#             site_addresses.extend(lead_sites)
        
#         return site_addresses
        
#     except Exception as e:
#         frappe.log_error(f"Error in search_by_lead_contact: {str(e)}")
#         return []


# def get_customer_lead_data(site_address):
#     """Get customer and lead data for a site address"""
#     customer_info = None
#     lead_info = None
    
#     # Get customer data
#     if site_address.get('custom_customer_'):
#         try:
#             customer_query = """
#                 SELECT 
#                     name,
#                     customer_name,
#                     mobile_no,
#                     email_id,
#                     customer_group,
#                     territory
#                 FROM `tabCustomer`
#                 WHERE name = %s
#             """
#             customer_result = frappe.db.sql(customer_query, [site_address['custom_customer_']], as_dict=1)
#             if customer_result:
#                 customer_info = customer_result[0]
#         except Exception as e:
#             frappe.log_error(f"Error fetching customer data: {str(e)}")
    
#     # Get lead data
#     if site_address.get('custom_lead_name'):
#         try:
#             lead_query = """
#                 SELECT 
#                     name,
#                     lead_name,
#                     mobile_no,
#                     email_id,
#                     status,
#                     source
#                 FROM `tabLead`
#                 WHERE name = %s
#             """
#             lead_result = frappe.db.sql(lead_query, [site_address['custom_lead_name']], as_dict=1)
#             if lead_result:
#                 lead_info = lead_result[0]
#         except Exception as e:
#             frappe.log_error(f"Error fetching lead data: {str(e)}")
    
#     return customer_info, lead_info


# # Alternative method for even more detailed customer/lead info
# @frappe.whitelist(allow_guest=False)
# def search_site_addresses_detailed(custom_emirate=None, custom_area=None, custom_community=None, 
#                                  custom_street_name=None, custom_property_number=None, 
#                                  custom_customer_phone_number=None, custom_customer_email=None,
#                                  custom_lead_phone_number=None, custom_lead_email=None):
#     """
#     Enhanced site address search with detailed customer/lead information using JOINs
#     """
#     try:
#         # Build conditions for search
#         conditions = []
#         values = []
        
#         # Address fields
#         if custom_emirate:
#             conditions.append("sa.custom_emirate LIKE %s")
#             values.append(f"%{custom_emirate}%")
        
#         if custom_area:
#             conditions.append("sa.custom_area LIKE %s")
#             values.append(f"%{custom_area}%")
        
#         if custom_community:
#             conditions.append("sa.custom_community LIKE %s")
#             values.append(f"%{custom_community}%")
        
#         if custom_street_name:
#             conditions.append("sa.custom_street_name LIKE %s")
#             values.append(f"%{custom_street_name}%")
        
#         if custom_property_number:
#             conditions.append("sa.custom_property_number LIKE %s")
#             values.append(f"%{custom_property_number}%")
        
#         # Enhanced phone number search for detailed search
#         if custom_customer_phone_number:
#             phone_condition, phone_values = build_phone_search_condition(
#                 "sa.custom_customer_phone_number", custom_customer_phone_number
#             )
#             if phone_condition:
#                 conditions.append(phone_condition)
#                 values.extend(phone_values)
        
#         if custom_lead_phone_number:
#             phone_condition, phone_values = build_phone_search_condition(
#                 "sa.custom_lead_phone_number", custom_lead_phone_number
#             )
#             if phone_condition:
#                 conditions.append(phone_condition)
#                 values.extend(phone_values)
        
#         # Email fields (unchanged)
#         if custom_customer_email:
#             conditions.append("sa.custom_customer_email LIKE %s")
#             values.append(f"%{custom_customer_email}%")
        
#         if custom_lead_email:
#             conditions.append("sa.custom_lead_email LIKE %s")
#             values.append(f"%{custom_lead_email}%")
        
#         if not conditions:
#             return {
#                 "status": "error",
#                 "message": "Please provide at least one search parameter",
#                 "data": []
#             }
        
#         where_clause = " AND ".join(conditions)
        
#         # Query with JOINs to get all data at once
#         query = f"""
#             SELECT 
#                 sa.name as site_name,
#                 sa.custom_emirate,
#                 sa.custom_area,
#                 sa.custom_community,
#                 sa.custom_street_name,
#                 sa.custom_property_number,
#                 sa.custom_combined_address,
#                 sa.custom_customer_phone_number,
#                 sa.custom_customer_email,
#                 sa.custom_lead_phone_number,
#                 sa.custom_lead_email,
#                 sa.custom_customer_,
#                 sa.custom_lead_name,
                
#                 -- Customer details
#                 c.customer_name,
#                 c.mobile_no as customer_mobile,
#                 c.email_id as customer_email,
#                 c.customer_group,
#                 c.territory,
                
#                 -- Lead details
#                 l.lead_name,
#                 l.mobile_no as lead_mobile,
#                 l.email_id as lead_email,
#                 l.status as lead_status,
#                 l.source as lead_source
                
#             FROM `tabSite Address` sa
#             LEFT JOIN `tabCustomer` c ON sa.custom_customer_ = c.name
#             LEFT JOIN `tabLead` l ON sa.custom_lead_name = l.name
#             WHERE ({where_clause})
#             ORDER BY sa.custom_emirate, sa.custom_area, sa.custom_community
#             LIMIT 50
#         """
        
#         results = frappe.db.sql(query, values, as_dict=1)
        
#         # Format the results
#         formatted_results = []
#         for row in results:
#             formatted_record = {
#                 "site_name": row.get('site_name'),
#                 "custom_emirate": row.get('custom_emirate'),
#                 "custom_area": row.get('custom_area'),
#                 "custom_community": row.get('custom_community'),
#                 "custom_street_name": row.get('custom_street_name'),
#                 "custom_property_number": row.get('custom_property_number'),
#                 "custom_combined_address": row.get('custom_combined_address'),
#                 "custom_customer_phone_number": row.get('custom_customer_phone_number'),
#                 "custom_customer_email": row.get('custom_customer_email'),
#                 "custom_lead_phone_number": row.get('custom_lead_phone_number'),
#                 "custom_lead_email": row.get('custom_lead_email'),
                
#                 "customer_details": {
#                     "name": row.get('custom_customer_'),
#                     "customer_name": row.get('customer_name'),
#                     "mobile_no": row.get('customer_mobile'),
#                     "email_id": row.get('customer_email'),
#                     "customer_group": row.get('customer_group'),
#                     "territory": row.get('territory')
#                 } if row.get('custom_customer_') else None,
                
#                 "lead_details": {
#                     "name": row.get('custom_lead_name'),
#                     "lead_name": row.get('lead_name'),
#                     "mobile_no": row.get('lead_mobile'),
#                     "email_id": row.get('lead_email'),
#                     "status": row.get('lead_status'),
#                     "source": row.get('lead_source')
#                 } if row.get('custom_lead_name') else None
#             }
            
#             formatted_results.append(formatted_record)
        
#         return {
#             "status": "success",
#             "message": f"Found {len(formatted_results)} site addresses",
#             "data": formatted_results
#         }
        
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"An error occurred: {str(e)}",
#             "data": []
#         }


import frappe
import re

def build_phone_search_condition(field_name, search_phone):
    """
    Build SQL condition for phone number search that handles various formats
    """
    if not search_phone:
        return None, []
    
    # Create condition that will match phone numbers in different formats
    condition = f"""(
        {field_name} LIKE %s OR 
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE({field_name}, ' ', ''), '-', ''), '(', ''), ')', ''), '+', '') LIKE %s
    )"""
    
    # Normalize search phone for second condition
    normalized_search = re.sub(r'[^\d]', '', str(search_phone))
    
    values = [f"%{search_phone}%", f"%{normalized_search}%"]
    
    return condition, values

@frappe.whitelist(allow_guest=False)
def search_site_addresses(custom_emirate=None, custom_area=None, custom_community=None, 
                         custom_street_name=None, custom_property_number=None, 
                         custom_customer_phone_number=None, custom_customer_email=None,
                         custom_lead_phone_number=None, custom_lead_email=None,
                         customer_name=None, lead_name=None, custom_lead_customer_name=None):
    """
    Comprehensive site address search by any field using AND logic
    Now includes customer name, lead name, and lead customer name search
    
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
        customer_name: Customer name to search (partial match)
        lead_name: Lead name to search (partial match)  
        custom_lead_customer_name: Lead Customer name to search (partial match)
    
    Returns:
        List of matching site addresses with integrated customer/lead details
    """
    try:
        all_site_addresses = []
        
        # Method 1: Direct search in Site Address table
        site_addresses_direct = search_site_addresses_direct(
            custom_emirate, custom_area, custom_community, 
            custom_street_name, custom_property_number,
            custom_customer_phone_number, custom_customer_email,
            custom_lead_phone_number, custom_lead_email,
            customer_name, lead_name, custom_lead_customer_name
        )
        
        # Method 2: Search by phone/email/name in Customer/Lead tables
        site_addresses_indirect = []
        
        # Search customers by phone/email/name and get their site addresses
        if custom_customer_phone_number or custom_customer_email or customer_name:
            customer_sites = search_by_customer_contact(
                custom_customer_phone_number, custom_customer_email, customer_name
            )
            site_addresses_indirect.extend(customer_sites)
        
        # Search leads by phone/email/name and get their site addresses  
        if custom_lead_phone_number or custom_lead_email or lead_name:
            lead_sites = search_by_lead_contact(
                custom_lead_phone_number, custom_lead_email, lead_name
            )
            site_addresses_indirect.extend(lead_sites)
        
        # Combine and deduplicate results
        all_site_addresses = site_addresses_direct + site_addresses_indirect
        
        # Remove duplicates based on site address name
        unique_sites = {}
        for site in all_site_addresses:
            site_name = site.get('name') or site.get('site_name')
            if site_name not in unique_sites:
                unique_sites[site_name] = site
        
        site_addresses = list(unique_sites.values())
        
        # If no results from any method and we have search criteria
        if not site_addresses:
            # Check if we have any search parameters
            has_params = any([
                custom_emirate, custom_area, custom_community, 
                custom_street_name, custom_property_number,
                custom_customer_phone_number, custom_customer_email,
                custom_lead_phone_number, custom_lead_email,
                customer_name, lead_name, custom_lead_customer_name
            ])
            
            if not has_params:
                return {
                    "status": "error",
                    "message": "Please provide at least one search parameter",
                    "data": []
                }
            else:
                return {
                    "status": "success",
                    "message": "No site addresses found matching your criteria",
                    "data": []
                }
        
        # Integrate customer and lead data for each site address
        integrated_results = []
        for site_address in site_addresses:
            # Get customer and lead data
            customer_info, lead_info = get_customer_lead_data(site_address)
            
            # Create integrated result
            integrated_record = {
                # Site Address fields
                "site_name": site_address.get('name'),
                "custom_emirate": site_address.get('custom_emirate'),
                "custom_area": site_address.get('custom_area'),
                "custom_community": site_address.get('custom_community'),
                "custom_street_name": site_address.get('custom_street_name'),
                "custom_property_number": site_address.get('custom_property_number'),
                "custom_combined_address": site_address.get('custom_combined_address'),
                "custom_customer_phone_number": site_address.get('custom_customer_phone_number'),
                "custom_customer_email": site_address.get('custom_customer_email'),
                "custom_lead_phone_number": site_address.get('custom_lead_phone_number'),
                "custom_lead_email": site_address.get('custom_lead_email'),
                "custom_lead_customer_name": site_address.get('custom_lead_customer_name'),
                
                # Customer details (if exists)
                "customer_details": customer_info,
                
                # Lead details (if exists)
                "lead_details": lead_info,
                
                # Reference fields
                "custom_customer_": site_address.get('custom_customer_'),
                "custom_lead_name": site_address.get('custom_lead_name'),
                
                # Search method indicator
                "found_via": site_address.get('found_via', 'direct_search')
            }
            
            integrated_results.append(integrated_record)
        
        return {
            "status": "success",
            "message": f"Found {len(integrated_results)} site addresses",
            "data": integrated_results
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"An error occurred: {str(e)}",
            "data": []
        }


def search_site_addresses_direct(custom_emirate=None, custom_area=None, custom_community=None, 
                               custom_street_name=None, custom_property_number=None,
                               custom_customer_phone_number=None, custom_customer_email=None,
                               custom_lead_phone_number=None, custom_lead_email=None,
                               customer_name=None, lead_name=None, custom_lead_customer_name=None):
    """Search directly in Site Address table with name searches"""
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
    
    # Enhanced phone number search for Site Address
    if custom_customer_phone_number:
        phone_condition, phone_values = build_phone_search_condition(
            "custom_customer_phone_number", custom_customer_phone_number
        )
        if phone_condition:
            conditions.append(phone_condition)
            values.extend(phone_values)
    
    if custom_lead_phone_number:
        phone_condition, phone_values = build_phone_search_condition(
            "custom_lead_phone_number", custom_lead_phone_number
        )
        if phone_condition:
            conditions.append(phone_condition)
            values.extend(phone_values)
    
    # Email fields
    if custom_customer_email:
        conditions.append("custom_customer_email LIKE %s")
        values.append(f"%{custom_customer_email}%")
    
    if custom_lead_email:
        conditions.append("custom_lead_email LIKE %s")
        values.append(f"%{custom_lead_email}%")
    
    # NEW: Direct Lead Customer Name search (Data field)
    if custom_lead_customer_name:
        conditions.append("custom_lead_customer_name LIKE %s")
        values.append(f"%{custom_lead_customer_name}%")
    
    # NEW: Customer Name search via JOIN
    if customer_name:
        conditions.append("""
            custom_customer_ IN (
                SELECT name FROM `tabCustomer` 
                WHERE customer_name LIKE %s
            )
        """)
        values.append(f"%{customer_name}%")
    
    # NEW: Lead Name search via JOIN
    if lead_name:
        conditions.append("""
            custom_lead_name IN (
                SELECT name FROM `tabLead` 
                WHERE lead_name LIKE %s
            )
        """)
        values.append(f"%{lead_name}%")
    
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
            custom_lead_name,
            custom_customer_phone_number,
            custom_customer_email,
            custom_lead_phone_number,
            custom_lead_email,
            custom_lead_customer_name
        FROM `tabSite Address` 
        WHERE ({where_clause})
        ORDER BY custom_emirate, custom_area, custom_community
        LIMIT 50
    """
    
    results = frappe.db.sql(query, values, as_dict=1)
    
    # Add search method indicator
    for result in results:
        result['found_via'] = 'direct_search'
    
    return results


def search_by_customer_contact(phone_number=None, email=None, customer_name=None):
    """Search site addresses by customer phone/email/name from Customer table"""
    if not phone_number and not email and not customer_name:
        return []
    
    try:
        customer_conditions = []
        customer_values = []
        
        # Enhanced phone number search for Customer table
        if phone_number:
            phone_condition, phone_values = build_phone_search_condition("mobile_no", phone_number)
            if phone_condition:
                customer_conditions.append(phone_condition)
                customer_values.extend(phone_values)
        
        if email:
            customer_conditions.append("email_id LIKE %s")
            customer_values.append(f"%{email}%")
        
        # NEW: Customer name search
        if customer_name:
            customer_conditions.append("customer_name LIKE %s")
            customer_values.append(f"%{customer_name}%")
        
        customer_where = " OR ".join(customer_conditions)
        customer_query = f"""
            SELECT name, customer_name, mobile_no, email_id
            FROM `tabCustomer`
            WHERE ({customer_where})
        """
        
        customers = frappe.db.sql(customer_query, customer_values, as_dict=1)
        
        site_addresses = []
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
                    custom_lead_name,
                    custom_customer_phone_number,
                    custom_customer_email,
                    custom_lead_phone_number,
                    custom_lead_email,
                    custom_lead_customer_name
                FROM `tabSite Address`
                WHERE custom_customer_ = %s
            """
            customer_sites = frappe.db.sql(site_query, [customer['name']], as_dict=1)
            
            # Add search method indicator
            for site in customer_sites:
                site['found_via'] = 'customer_contact_search'
                site['matched_customer'] = customer
            
            site_addresses.extend(customer_sites)
        
        return site_addresses
        
    except Exception as e:
        frappe.log_error(f"Error in search_by_customer_contact: {str(e)}")
        return []


def search_by_lead_contact(phone_number=None, email=None, lead_name=None):
    """Search site addresses by lead phone/email/name from Lead table"""
    if not phone_number and not email and not lead_name:
        return []
    
    try:
        lead_conditions = []
        lead_values = []
        
        # Enhanced phone number search for Lead table
        if phone_number:
            phone_condition, phone_values = build_phone_search_condition("mobile_no", phone_number)
            if phone_condition:
                lead_conditions.append(phone_condition)
                lead_values.extend(phone_values)
        
        if email:
            lead_conditions.append("email_id LIKE %s")
            lead_values.append(f"%{email}%")
        
        # NEW: Lead name search
        if lead_name:
            lead_conditions.append("lead_name LIKE %s")
            lead_values.append(f"%{lead_name}%")
        
        lead_where = " OR ".join(lead_conditions)
        lead_query = f"""
            SELECT name, lead_name, mobile_no, email_id, status
            FROM `tabLead`
            WHERE ({lead_where})
        """
        
        leads = frappe.db.sql(lead_query, lead_values, as_dict=1)
        
        site_addresses = []
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
                    custom_lead_name,
                    custom_customer_phone_number,
                    custom_customer_email,
                    custom_lead_phone_number,
                    custom_lead_email,
                    custom_lead_customer_name
                FROM `tabSite Address`
                WHERE custom_lead_name = %s
            """
            lead_sites = frappe.db.sql(lead_query, [lead['name']], as_dict=1)
            
            # Add search method indicator
            for site in lead_sites:
                site['found_via'] = 'lead_contact_search'
                site['matched_lead'] = lead
            
            site_addresses.extend(lead_sites)
        
        return site_addresses
        
    except Exception as e:
        frappe.log_error(f"Error in search_by_lead_contact: {str(e)}")
        return []


def get_customer_lead_data(site_address):
    """Get customer and lead data for a site address"""
    customer_info = None
    lead_info = None
    
    # Get customer data
    if site_address.get('custom_customer_'):
        try:
            customer_query = """
                SELECT 
                    name,
                    customer_name,
                    mobile_no,
                    email_id,
                    customer_group,
                    territory
                FROM `tabCustomer`
                WHERE name = %s
            """
            customer_result = frappe.db.sql(customer_query, [site_address['custom_customer_']], as_dict=1)
            if customer_result:
                customer_info = customer_result[0]
        except Exception as e:
            frappe.log_error(f"Error fetching customer data: {str(e)}")
    
    # Get lead data
    if site_address.get('custom_lead_name'):
        try:
            lead_query = """
                SELECT 
                    name,
                    lead_name,
                    mobile_no,
                    email_id,
                    status,
                    source
                FROM `tabLead`
                WHERE name = %s
            """
            lead_result = frappe.db.sql(lead_query, [site_address['custom_lead_name']], as_dict=1)
            if lead_result:
                lead_info = lead_result[0]
        except Exception as e:
            frappe.log_error(f"Error fetching lead data: {str(e)}")
    
    return customer_info, lead_info


# Enhanced detailed search method with name searches
@frappe.whitelist(allow_guest=False)
def search_site_addresses_detailed(custom_emirate=None, custom_area=None, custom_community=None, 
                                 custom_street_name=None, custom_property_number=None, 
                                 custom_customer_phone_number=None, custom_customer_email=None,
                                 custom_lead_phone_number=None, custom_lead_email=None,
                                 customer_name=None, lead_name=None, custom_lead_customer_name=None):
    """
    Enhanced site address search with detailed customer/lead information using JOINs
    Now includes customer name, lead name, and lead customer name search
    """
    try:
        # Build conditions for search
        conditions = []
        values = []
        
        # Address fields
        if custom_emirate:
            conditions.append("sa.custom_emirate LIKE %s")
            values.append(f"%{custom_emirate}%")
        
        if custom_area:
            conditions.append("sa.custom_area LIKE %s")
            values.append(f"%{custom_area}%")
        
        if custom_community:
            conditions.append("sa.custom_community LIKE %s")
            values.append(f"%{custom_community}%")
        
        if custom_street_name:
            conditions.append("sa.custom_street_name LIKE %s")
            values.append(f"%{custom_street_name}%")
        
        if custom_property_number:
            conditions.append("sa.custom_property_number LIKE %s")
            values.append(f"%{custom_property_number}%")
        
        # Enhanced phone number search for detailed search
        if custom_customer_phone_number:
            phone_condition, phone_values = build_phone_search_condition(
                "sa.custom_customer_phone_number", custom_customer_phone_number
            )
            if phone_condition:
                conditions.append(phone_condition)
                values.extend(phone_values)
        
        if custom_lead_phone_number:
            phone_condition, phone_values = build_phone_search_condition(
                "sa.custom_lead_phone_number", custom_lead_phone_number
            )
            if phone_condition:
                conditions.append(phone_condition)
                values.extend(phone_values)
        
        # Email fields
        if custom_customer_email:
            conditions.append("sa.custom_customer_email LIKE %s")
            values.append(f"%{custom_customer_email}%")
        
        if custom_lead_email:
            conditions.append("sa.custom_lead_email LIKE %s")
            values.append(f"%{custom_lead_email}%")
        
        # NEW: Name search conditions
        if custom_lead_customer_name:
            conditions.append("sa.custom_lead_customer_name LIKE %s")
            values.append(f"%{custom_lead_customer_name}%")
        
        if customer_name:
            conditions.append("c.customer_name LIKE %s")
            values.append(f"%{customer_name}%")
        
        if lead_name:
            conditions.append("l.lead_name LIKE %s")
            values.append(f"%{lead_name}%")
        
        if not conditions:
            return {
                "status": "error",
                "message": "Please provide at least one search parameter",
                "data": []
            }
        
        where_clause = " AND ".join(conditions)
        
        # Query with JOINs to get all data at once
        query = f"""
            SELECT 
                sa.name as site_name,
                sa.custom_emirate,
                sa.custom_area,
                sa.custom_community,
                sa.custom_street_name,
                sa.custom_property_number,
                sa.custom_combined_address,
                sa.custom_customer_phone_number,
                sa.custom_customer_email,
                sa.custom_lead_phone_number,
                sa.custom_lead_email,
                sa.custom_lead_customer_name,
                sa.custom_customer_,
                sa.custom_lead_name,
                
                -- Customer details
                c.customer_name,
                c.mobile_no as customer_mobile,
                c.email_id as customer_email,
                c.customer_group,
                c.territory,
                
                -- Lead details
                l.lead_name,
                l.mobile_no as lead_mobile,
                l.email_id as lead_email,
                l.status as lead_status,
                l.source as lead_source
                
            FROM `tabSite Address` sa
            LEFT JOIN `tabCustomer` c ON sa.custom_customer_ = c.name
            LEFT JOIN `tabLead` l ON sa.custom_lead_name = l.name
            WHERE ({where_clause})
            ORDER BY sa.custom_emirate, sa.custom_area, sa.custom_community
            LIMIT 50
        """
        
        results = frappe.db.sql(query, values, as_dict=1)
        
        # Format the results
        formatted_results = []
        for row in results:
            formatted_record = {
                "site_name": row.get('site_name'),
                "custom_emirate": row.get('custom_emirate'),
                "custom_area": row.get('custom_area'),
                "custom_community": row.get('custom_community'),
                "custom_street_name": row.get('custom_street_name'),
                "custom_property_number": row.get('custom_property_number'),
                "custom_combined_address": row.get('custom_combined_address'),
                "custom_customer_phone_number": row.get('custom_customer_phone_number'),
                "custom_customer_email": row.get('custom_customer_email'),
                "custom_lead_phone_number": row.get('custom_lead_phone_number'),
                "custom_lead_email": row.get('custom_lead_email'),
                "custom_lead_customer_name": row.get('custom_lead_customer_name'),
                
                "customer_details": {
                    "name": row.get('custom_customer_'),
                    "customer_name": row.get('customer_name'),
                    "mobile_no": row.get('customer_mobile'),
                    "email_id": row.get('customer_email'),
                    "customer_group": row.get('customer_group'),
                    "territory": row.get('territory')
                } if row.get('custom_customer_') else None,
                
                "lead_details": {
                    "name": row.get('custom_lead_name'),
                    "lead_name": row.get('lead_name'),
                    "mobile_no": row.get('lead_mobile'),
                    "email_id": row.get('lead_email'),
                    "status": row.get('lead_status'),
                    "source": row.get('lead_source')
                } if row.get('custom_lead_name') else None
            }
            
            formatted_results.append(formatted_record)
        
        return {
            "status": "success",
            "message": f"Found {len(formatted_results)} site addresses",
            "data": formatted_results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}",
            "data": []
        }