# import frappe
# import re

# @frappe.whitelist(allow_guest=False)
# def search_site_addresses(custom_emirate=None, custom_area=None, custom_community=None, 
#                          custom_street_name=None, custom_property_number=None, 
#                          custom_customer_phone_number=None, custom_customer_email=None,
#                          custom_lead_phone_number=None, custom_lead_email=None,
#                          customer_name=None, lead_name=None, custom_lead_customer_name=None):
#     """
#     Comprehensive site address search by any field using AND logic
#     Now includes customer name, lead name, and lead customer name search
    
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
#         customer_name: Customer name to search (partial match)
#         lead_name: Lead name to search (partial match)  
#         custom_lead_customer_name: Lead Customer name to search (partial match)
    
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
#             custom_lead_phone_number, custom_lead_email,
#             customer_name, lead_name, custom_lead_customer_name
#         )
        
#         # Method 2: Search by phone/email/name in Customer/Lead tables
#         site_addresses_indirect = []
        
#         # Search customers by phone/email/name and get their site addresses
#         if custom_customer_phone_number or custom_customer_email or customer_name:
#             customer_sites = search_by_customer_contact(
#                 custom_customer_phone_number, custom_customer_email, customer_name
#             )
#             site_addresses_indirect.extend(customer_sites)
        
#         # Search leads by phone/email/name and get their site addresses  
#         if custom_lead_phone_number or custom_lead_email or lead_name:
#             lead_sites = search_by_lead_contact(
#                 custom_lead_phone_number, custom_lead_email, lead_name
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
#                 custom_lead_phone_number, custom_lead_email,
#                 customer_name, lead_name, custom_lead_customer_name
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
#                 "custom_lead_customer_name": site_address.get('custom_lead_customer_name'),
                
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



#                                  custom_street_name=None, custom_property_number=None, 
#                                  custom_customer_phone_number=None, custom_customer_email=None,
#                                  custom_lead_phone_number=None, custom_lead_email=None,
#                                  customer_name=None, lead_name=None, custom_lead_customer_name=None):
#     """
#     Enhanced site address search with detailed customer/lead information using JOINs
#     Now includes customer name, lead name, and lead customer name search
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
        
#         # Email fields
#         if custom_customer_email:
#             conditions.append("sa.custom_customer_email LIKE %s")
#             values.append(f"%{custom_customer_email}%")
        
#         if custom_lead_email:
#             conditions.append("sa.custom_lead_email LIKE %s")
#             values.append(f"%{custom_lead_email}%")
        
#         # NEW: Name search conditions
#         if custom_lead_customer_name:
#             conditions.append("sa.custom_lead_customer_name LIKE %s")
#             values.append(f"%{custom_lead_customer_name}%")
        
#         if customer_name:
#             conditions.append("c.customer_name LIKE %s")
#             values.append(f"%{customer_name}%")
        
#         if lead_name:
#             conditions.append("l.lead_name LIKE %s")
#             values.append(f"%{lead_name}%")
        
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
#                 sa.custom_lead_customer_name,
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
#                 "custom_lead_customer_name": row.get('custom_lead_customer_name'),
                
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

@frappe.whitelist(allow_guest=False)
def search_site_addresses(search_term=None, **kwargs):
    """
    Universal site address search - accepts either search_term for universal search
    or individual field parameters for specific search
    
    Args:
        search_term: Universal search term that searches across all fields
        **kwargs: Individual field parameters (backward compatibility)
    
    Returns:
        List of matching site addresses with integrated customer/lead details
    """
    try:
        # If search_term is provided, use universal search
        if search_term:
            return universal_search(search_term)
        
        # Otherwise, fall back to original specific field search
        return search_site_addresses_specific(**kwargs)
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"An error occurred: {str(e)}",
            "data": []
        }

def universal_search(search_term):
    """
    Search the term across ALL relevant fields using OR logic
    """
    if not search_term or len(search_term.strip()) < 2:
        return {
            "status": "error",
            "message": "Search term must be at least 2 characters long",
            "data": []
        }
    
    # Clean the search term
    search_term = search_term.strip()
    
    # Build comprehensive OR conditions for all searchable fields
    conditions = []
    values = []
    
    # Address fields
    address_fields = [
        'sa.custom_emirate',
        'sa.custom_area', 
        'sa.custom_community',
        'sa.custom_street_name',
        'sa.custom_property_number',
        'sa.custom_combined_address',
        'sa.custom_customer_email',
        'sa.custom_lead_email',
        'sa.custom_lead_customer_name'
    ]
    
    # Add LIKE conditions for address fields
    for field in address_fields:
        conditions.append(f"{field} LIKE %s")
        values.append(f"%{search_term}%")
    
    # Phone number fields (with enhanced phone search)
    phone_fields = ['sa.custom_customer_phone_number', 'sa.custom_lead_phone_number']
    for field in phone_fields:
        phone_condition, phone_values = build_phone_search_condition(field, search_term)
        if phone_condition:
            conditions.append(phone_condition)
            values.extend(phone_values)
    
    # Customer and Lead name fields
    name_fields = [
        'c.customer_name',
        'l.lead_name',
        'c.email_id',
        'l.email_id'
    ]
    
    for field in name_fields:
        conditions.append(f"{field} LIKE %s")
        values.append(f"%{search_term}%")
    
    # Build the query with all OR conditions
    where_clause = " OR ".join(conditions)
    
    query = f"""
        SELECT DISTINCT
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
        ORDER BY 
            CASE 
                WHEN sa.custom_emirate LIKE %s THEN 1
                WHEN sa.custom_area LIKE %s THEN 2  
                WHEN sa.custom_community LIKE %s THEN 3
                WHEN c.customer_name LIKE %s THEN 4
                WHEN l.lead_name LIKE %s THEN 5
                ELSE 6 
            END,
            sa.custom_emirate, sa.custom_area, sa.custom_community
        LIMIT 100
    """
    
    # Add search term for ORDER BY clause (5 times for the CASE statement)
    order_values = [f"%{search_term}%"] * 5
    all_values = values + order_values
    
    results = frappe.db.sql(query, all_values, as_dict=1)
    
    # Format results
    formatted_results = []
    for row in results:
        # Determine which field matched for relevance scoring
        match_info = determine_match_field(row, search_term)
        
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
            } if row.get('custom_lead_name') else None,
            
            # Add match information for frontend highlighting
            "match_info": match_info,
            "search_term": search_term
        }
        
        formatted_results.append(formatted_record)
    
    return {
        "status": "success",
        "message": f"Found {len(formatted_results)} site addresses matching '{search_term}'",
        "data": formatted_results,
        "search_term": search_term
    }

def determine_match_field(row, search_term):
    """
    Determine which field(s) matched the search term for relevance/highlighting
    """
    matches = []
    search_lower = search_term.lower()
    
    field_mapping = {
        'custom_emirate': 'Emirate',
        'custom_area': 'Area',
        'custom_community': 'Community', 
        'custom_street_name': 'Street',
        'custom_property_number': 'Property Number',
        'customer_name': 'Customer Name',
        'lead_name': 'Lead Name',
        'custom_customer_phone_number': 'Customer Phone',
        'custom_lead_phone_number': 'Lead Phone',
        'custom_customer_email': 'Customer Email',
        'custom_lead_email': 'Lead Email'
    }
    
    for field, display_name in field_mapping.items():
        value = row.get(field)
        if value and search_lower in str(value).lower():
            matches.append({
                'field': field,
                'display_name': display_name,
                'value': value
            })
    
    return matches

def build_phone_search_condition(field_name, phone_number):
    """
    Enhanced phone number search handling different formats
    """
    if not phone_number:
        return None, []
    
    # Remove all non-digits for comparison
    clean_phone = re.sub(r'[^\d]', '', phone_number)
    
    if len(clean_phone) < 3:  # Too short to be meaningful
        return None, []
    
    conditions = []
    values = []
    
    # Direct match
    conditions.append(f"{field_name} LIKE %s")
    values.append(f"%{phone_number}%")
    
    # Clean number match  
    conditions.append(f"REPLACE(REPLACE(REPLACE({field_name}, ' ', ''), '-', ''), '+', '') LIKE %s")
    values.append(f"%{clean_phone}%")
    
    # Last digits match (for partial searches)
    if len(clean_phone) >= 4:
        conditions.append(f"{field_name} LIKE %s")
        values.append(f"%{clean_phone[-4:]}%")
    
    return f"({' OR '.join(conditions)})", values

def search_site_addresses_specific(custom_emirate=None, custom_area=None, custom_community=None, 
                                 custom_street_name=None, custom_property_number=None, 
                                 custom_customer_phone_number=None, custom_customer_email=None,
                                 custom_lead_phone_number=None, custom_lead_email=None,
                                 customer_name=None, lead_name=None, custom_lead_customer_name=None):
    """
    Original specific field search (backward compatibility)
    """
    # Your existing specific search logic here
    # (I'll keep this short since you already have it)
    
    try:
        conditions = []
        values = []
        
        # Build AND conditions for specific fields
        if custom_emirate:
            conditions.append("sa.custom_emirate LIKE %s")
            values.append(f"%{custom_emirate}%")
        
        if custom_area:
            conditions.append("sa.custom_area LIKE %s")
            values.append(f"%{custom_area}%")
        
        # ... add all your existing specific field conditions
        
        if not conditions:
            return {
                "status": "error",
                "message": "Please provide at least one search parameter",
                "data": []
            }
        
        where_clause = " AND ".join(conditions)
        
        # Use similar query structure as universal search
        query = f"""
            SELECT DISTINCT
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
                
                c.customer_name,
                c.mobile_no as customer_mobile,
                c.email_id as customer_email,
                c.customer_group,
                c.territory,
                
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
        
        # Format results similar to universal search
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