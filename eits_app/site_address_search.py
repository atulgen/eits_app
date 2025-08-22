# import frappe
# import re

# @frappe.whitelist(allow_guest=False)
# def search_site_addresses(search_term=None, **kwargs):
#     """
#     Universal site address search - accepts either search_term for universal search
#     or individual field parameters for specific search
    
#     Args:
#         search_term: Universal search term that searches across all fields
#         **kwargs: Individual field parameters (backward compatibility)
    
#     Returns:
#         List of matching site addresses with integrated customer/lead details
#     """
#     try:
#         # If search_term is provided, use universal search
#         if search_term:
#             return universal_search(search_term)
        
#         # Otherwise, fall back to original specific field search
#         return search_site_addresses_specific(**kwargs)
        
#     except Exception as e:
#         return {
#             "status": "error", 
#             "message": f"An error occurred: {str(e)}",
#             "data": []
#         }

# def universal_search(search_term):
#     """
#     Search the term across ALL relevant fields using OR logic
#     """
#     if not search_term or len(search_term.strip()) < 2:
#         return {
#             "status": "error",
#             "message": "Search term must be at least 2 characters long",
#             "data": []
#         }
    
#     # Clean the search term
#     search_term = search_term.strip()
    
#     # Build comprehensive OR conditions for all searchable fields
#     conditions = []
#     values = []
    
#     # Address fields
#     address_fields = [
#         'sa.custom_emirate',
#         'sa.custom_area', 
#         'sa.custom_community',
#         'sa.custom_street_name',
#         'sa.custom_property_number',
#         'sa.custom_combined_address',
#         'sa.custom_customer_email',
#         'sa.custom_lead_email',
#         'sa.custom_lead_customer_name'
#     ]
    
#     # Add LIKE conditions for address fields
#     for field in address_fields:
#         conditions.append(f"{field} LIKE %s")
#         values.append(f"%{search_term}%")
    
#     # Phone number fields (with enhanced phone search)
#     phone_fields = ['sa.custom_customer_phone_number', 'sa.custom_lead_phone_number']
#     for field in phone_fields:
#         phone_condition, phone_values = build_phone_search_condition(field, search_term)
#         if phone_condition:
#             conditions.append(phone_condition)
#             values.extend(phone_values)
    
#     # Customer and Lead name fields
#     name_fields = [
#         'c.customer_name',
#         'l.lead_name',
#         'c.email_id',
#         'l.email_id'
#     ]
    
#     for field in name_fields:
#         conditions.append(f"{field} LIKE %s")
#         values.append(f"%{search_term}%")
    
#     # Build the query with all OR conditions
#     where_clause = " OR ".join(conditions)
    
#     query = f"""
#         SELECT DISTINCT
#             sa.name as site_name,
#             sa.custom_emirate,
#             sa.custom_area,
#             sa.custom_community,
#             sa.custom_street_name,
#             sa.custom_property_number,
#             sa.custom_property_category,
#             sa.custom_property_type,
#             sa.custom_combined_address,
#             sa.custom_customer_phone_number,
#             sa.custom_customer_email,
#             sa.custom_lead_phone_number,
#             sa.custom_lead_email,
#             sa.custom_lead_customer_name,
#             sa.custom_customer_,
#             sa.custom_lead_name,
            
#             -- Customer details
#             c.customer_name,
#             c.mobile_no as customer_mobile,
#             c.email_id as customer_email,
#             c.customer_group,
#             c.territory,
            
#             -- Lead details
#             l.lead_name,
#             l.mobile_no as lead_mobile,
#             l.email_id as lead_email,
#             l.status as lead_status,
#             l.source as lead_source
            
#         FROM `tabSite Address` sa
#         LEFT JOIN `tabCustomer` c ON sa.custom_customer_ = c.name
#         LEFT JOIN `tabLead` l ON sa.custom_lead_name = l.name
#         WHERE ({where_clause})
#         ORDER BY 
#             CASE 
#                 WHEN sa.custom_emirate LIKE %s THEN 1
#                 WHEN sa.custom_area LIKE %s THEN 2  
#                 WHEN sa.custom_community LIKE %s THEN 3
#                 WHEN c.customer_name LIKE %s THEN 4
#                 WHEN l.lead_name LIKE %s THEN 5
#                 ELSE 6 
#             END,
#             sa.custom_emirate, sa.custom_area, sa.custom_community
#         LIMIT 100
#     """
    
#     # Add search term for ORDER BY clause (5 times for the CASE statement)
#     order_values = [f"%{search_term}%"] * 5
#     all_values = values + order_values
    
#     results = frappe.db.sql(query, all_values, as_dict=1)
    
#     # Format results
#     formatted_results = []
#     for row in results:
#         # Determine which field matched for relevance scoring
#         match_info = determine_match_field(row, search_term)
        
#         formatted_record = {
#             "site_name": row.get('site_name'),
#             "custom_emirate": row.get('custom_emirate'),
#             "custom_area": row.get('custom_area'), 
#             "custom_community": row.get('custom_community'),
#             "custom_street_name": row.get('custom_street_name'),
#             "custom_property_number": row.get('custom_property_number'),
#             "custom_property_category": row.get('custom_property_category'),
#             "custom_property_type": row.get('custom_property_type'),
#             "custom_combined_address": row.get('custom_combined_address'),
#             "custom_customer_phone_number": row.get('custom_customer_phone_number'),
#             "custom_customer_email": row.get('custom_customer_email'),
#             "custom_lead_phone_number": row.get('custom_lead_phone_number'),
#             "custom_lead_email": row.get('custom_lead_email'),
#             "custom_lead_customer_name": row.get('custom_lead_customer_name'),
            
#             "customer_details": {
#                 "name": row.get('custom_customer_'),
#                 "customer_name": row.get('customer_name'),
#                 "mobile_no": row.get('customer_mobile'),
#                 "email_id": row.get('customer_email'),
#                 "customer_group": row.get('customer_group'),
#                 "territory": row.get('territory')
#             } if row.get('custom_customer_') else None,
            
#             "lead_details": {
#                 "name": row.get('custom_lead_name'),
#                 "lead_name": row.get('lead_name'),
#                 "mobile_no": row.get('lead_mobile'),
#                 "email_id": row.get('lead_email'),
#                 "status": row.get('lead_status'),
#                 "source": row.get('lead_source')
#             } if row.get('custom_lead_name') else None,
            
#             # Add match information for frontend highlighting
#             "match_info": match_info,
#             "search_term": search_term
#         }
        
#         formatted_results.append(formatted_record)
    
#     return {
#         "status": "success",
#         "message": f"Found {len(formatted_results)} site addresses matching '{search_term}'",
#         "data": formatted_results,
#         "search_term": search_term
#     }

# def determine_match_field(row, search_term):
#     """
#     Determine which field(s) matched the search term for relevance/highlighting
#     """
#     matches = []
#     search_lower = search_term.lower()
    
#     field_mapping = {
#         'custom_emirate': 'Emirate',
#         'custom_area': 'Area',
#         'custom_community': 'Community', 
#         'custom_street_name': 'Street',
#         'custom_property_number': 'Property Number',
#         'customer_name': 'Customer Name',
#         'lead_name': 'Lead Name',
#         'custom_customer_phone_number': 'Customer Phone',
#         'custom_lead_phone_number': 'Lead Phone',
#         'custom_customer_email': 'Customer Email',
#         'custom_lead_email': 'Lead Email'
#     }
    
#     for field, display_name in field_mapping.items():
#         value = row.get(field)
#         if value and search_lower in str(value).lower():
#             matches.append({
#                 'field': field,
#                 'display_name': display_name,
#                 'value': value
#             })
    
#     return matches


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
    
    # First, search in Site Address
    site_results = search_in_site_address(search_term)
    
    if site_results.get("data"):
        return site_results
    
    # If no results in Site Address, search in Lead
    lead_results = search_in_lead(search_term)
    
    if lead_results.get("data"):
        return lead_results
    
    # If no results in Lead, search in Customer
    customer_results = search_in_customer(search_term)
    
    if customer_results.get("data"):
        return customer_results
    
    # If no results found anywhere
    return {
        "status": "success",
        "message": f"No results found for '{search_term}' in Site Addresses, Leads or Customers",
        "data": [],
        "search_term": search_term
    }

def search_in_site_address(search_term):
    """
    Search the term in Site Address doctype
    """
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
    where_clause = " OR ".join(conditions) if conditions else "1=0"
    
    query = f"""
        SELECT DISTINCT
            sa.name as site_name,
            sa.custom_emirate,
            sa.custom_area,
            sa.custom_community,
            sa.custom_street_name,
            sa.custom_property_number,
            sa.custom_property_category,
            sa.custom_property_type,
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
            "custom_property_category": row.get('custom_property_category'),
            "custom_property_type": row.get('custom_property_type'),
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

def search_in_lead(search_term):
    """
    Search in Lead doctype if no results found in Site Address
    """
    query = """
        SELECT 
            name,
            lead_name,
            first_name,
            last_name,
            mobile_no,
            email_id,
            status,
            source
        FROM `tabLead`
        WHERE lead_name LIKE %s OR first_name LIKE %s OR last_name LIKE %s
        ORDER BY 
            CASE 
                WHEN lead_name LIKE %s THEN 1
                WHEN first_name LIKE %s THEN 2
                ELSE 3
            END
        LIMIT 100
    """
    
    search_value = f"%{search_term}%"
    results = frappe.db.sql(query, [search_value]*5, as_dict=1)
    
    formatted_results = []
    for row in results:
        formatted_record = {
            "lead_details": {
                "name": row.get('name'),
                "lead_name": row.get('lead_name'),
                "first_name": row.get('first_name'),
                "last_name": row.get('last_name'),
                "mobile_no": row.get('mobile_no'),
                "email_id": row.get('email_id'),
                "status": row.get('status'),
                "source": row.get('source')
            },
            "match_info": [{
                'field': 'lead_name',
                'display_name': 'Lead Name',
                'value': row.get('lead_name')
            }],
            "search_term": search_term
        }
        formatted_results.append(formatted_record)
    
    return {
        "status": "success",
        "message": f"Found {len(formatted_results)} leads matching '{search_term}'",
        "data": formatted_results,
        "search_term": search_term
    }

def search_in_customer(search_term):
    """
    Search in Customer doctype if no results found in Site Address or Lead
    """
    query = """
        SELECT 
            name,
            customer_name,
            mobile_no,
            email_id,
            customer_group,
            territory
        FROM `tabCustomer`
        WHERE customer_name LIKE %s
        ORDER BY customer_name
        LIMIT 100
    """
    
    search_value = f"%{search_term}%"
    results = frappe.db.sql(query, [search_value], as_dict=1)
    
    formatted_results = []
    for row in results:
        formatted_record = {
            "customer_details": {
                "name": row.get('name'),
                "customer_name": row.get('customer_name'),
                "mobile_no": row.get('mobile_no'),
                "email_id": row.get('email_id'),
                "customer_group": row.get('customer_group'),
                "territory": row.get('territory')
            },
            "match_info": [{
                'field': 'customer_name',
                'display_name': 'Customer Name',
                'value': row.get('customer_name')
            }],
            "search_term": search_term
        }
        formatted_results.append(formatted_record)
    
    return {
        "status": "success",
        "message": f"Found {len(formatted_results)} customers matching '{search_term}'",
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
    




@frappe.whitelist(allow_guest=False)
def search_site_addresses_customers_only(search_term=None):
    """
    Search site addresses that have ONLY customer details (no lead details)
    
    Args:
        search_term: Universal search term that searches across customer-related fields only
    
    Returns:
        List of matching site addresses with customer details only (excludes leads)
    """
    try:
        if not search_term:
            return {
                "status": "error",
                "message": "Search term is required",
                "data": []
            }
            
        return customer_only_universal_search(search_term)
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"An error occurred: {str(e)}",
            "data": []
        }

def customer_only_universal_search(search_term):
    """
    Search the term across customer-related fields only in Site Addresses that have customers
    """
    if not search_term or len(search_term.strip()) < 2:
        return {
            "status": "error",
            "message": "Search term must be at least 2 characters long",
            "data": []
        }
    
    # Clean the search term
    search_term = search_term.strip()
    
    # First, search in Site Address with customer details
    site_results = search_customer_site_addresses(search_term)
    
    if site_results.get("data"):
        return site_results
    
    # If no results in Site Address, search directly in Customer table
    customer_results = search_customers_only(search_term)
    
    if customer_results.get("data"):
        return customer_results
    
    # If no results found anywhere
    return {
        "status": "success",
        "message": f"No results found for '{search_term}' in Customer Site Addresses",
        "data": [],
        "search_term": search_term
    }

def search_customer_site_addresses(search_term):
    """
    Search the term in Site Address doctype for records that have customer details only
    """
    # Build comprehensive OR conditions for customer-related fields only
    conditions = []
    values = []
    
    # Site Address fields (general location fields)
    address_fields = [
        'sa.custom_emirate',
        'sa.custom_area', 
        'sa.custom_community',
        'sa.custom_street_name',
        'sa.custom_property_number',
        'sa.custom_combined_address'
    ]
    
    # Add LIKE conditions for address fields
    for field in address_fields:
        conditions.append(f"{field} LIKE %s")
        values.append(f"%{search_term}%")
    
    # Customer-related fields in Site Address
    customer_fields_sa = [
        'sa.custom_customer_email'
    ]
    
    for field in customer_fields_sa:
        conditions.append(f"{field} LIKE %s")
        values.append(f"%{search_term}%")
    
    # Customer phone number field (with enhanced phone search)
    phone_condition, phone_values = build_phone_search_condition('sa.custom_customer_phone_number', search_term)
    if phone_condition:
        conditions.append(phone_condition)
        values.extend(phone_values)
    
    # Customer table fields
    customer_fields = [
        'c.customer_name',
        'c.email_id'
    ]
    
    for field in customer_fields:
        conditions.append(f"{field} LIKE %s")
        values.append(f"%{search_term}%")
    
    # Customer mobile phone with enhanced search
    customer_mobile_condition, customer_mobile_values = build_phone_search_condition('c.mobile_no', search_term)
    if customer_mobile_condition:
        conditions.append(customer_mobile_condition)
        values.extend(customer_mobile_values)
    
    # Build the query with all OR conditions
    where_clause = " OR ".join(conditions) if conditions else "1=0"
    
    query = f"""
        SELECT DISTINCT
            sa.name as site_name,
            sa.custom_emirate,
            sa.custom_area,
            sa.custom_community,
            sa.custom_street_name,
            sa.custom_property_number,
            sa.custom_property_category,
            sa.custom_property_type,
            sa.custom_combined_address,
            sa.custom_customer_phone_number,
            sa.custom_customer_email,
            sa.custom_customer_,
            
            -- Customer details
            c.customer_name,
            c.mobile_no as customer_mobile,
            c.email_id as customer_email,
            c.customer_group,
            c.territory
            
        FROM `tabSite Address` sa
        INNER JOIN `tabCustomer` c ON sa.custom_customer_ = c.name
        WHERE (sa.custom_customer_ IS NOT NULL AND sa.custom_customer_ != '')
        AND (sa.custom_lead_name IS NULL OR sa.custom_lead_name = '')
        AND ({where_clause})
        ORDER BY 
            CASE 
                WHEN sa.custom_emirate LIKE %s THEN 1
                WHEN sa.custom_area LIKE %s THEN 2  
                WHEN sa.custom_community LIKE %s THEN 3
                WHEN c.customer_name LIKE %s THEN 4
                ELSE 5 
            END,
            sa.custom_emirate, sa.custom_area, sa.custom_community
        LIMIT 100
    """
    
    # Add search term for ORDER BY clause (4 times for the CASE statement)
    order_values = [f"%{search_term}%"] * 4
    all_values = values + order_values
    
    results = frappe.db.sql(query, all_values, as_dict=1)
    
    # Format results
    formatted_results = []
    for row in results:
        # Determine which field matched for relevance scoring
        match_info = determine_customer_match_field(row, search_term)
        
        formatted_record = {
            "site_name": row.get('site_name'),
            "custom_emirate": row.get('custom_emirate'),
            "custom_area": row.get('custom_area'), 
            "custom_community": row.get('custom_community'),
            "custom_street_name": row.get('custom_street_name'),
            "custom_property_number": row.get('custom_property_number'),
            "custom_property_category": row.get('custom_property_category'),
            "custom_property_type": row.get('custom_property_type'),
            "custom_combined_address": row.get('custom_combined_address'),
            "custom_customer_phone_number": row.get('custom_customer_phone_number'),
            "custom_customer_email": row.get('custom_customer_email'),
            
            "customer_details": {
                "name": row.get('custom_customer_'),
                "customer_name": row.get('customer_name'),
                "mobile_no": row.get('customer_mobile'),
                "email_id": row.get('customer_email'),
                "customer_group": row.get('customer_group'),
                "territory": row.get('territory')
            },
            
            # Add match information for frontend highlighting
            "match_info": match_info,
            "search_term": search_term
        }
        
        formatted_results.append(formatted_record)
    
    return {
        "status": "success",
        "message": f"Found {len(formatted_results)} customer site addresses matching '{search_term}'",
        "data": formatted_results,
        "search_term": search_term
    }

def search_customers_only(search_term):
    """
    Search in Customer doctype only (fallback when no site addresses found)
    """
    # Enhanced customer search with phone number support
    conditions = ['customer_name LIKE %s', 'email_id LIKE %s']
    values = [f"%{search_term}%", f"%{search_term}%"]
    
    # Add phone search condition
    phone_condition, phone_values = build_phone_search_condition('mobile_no', search_term)
    if phone_condition:
        conditions.append(phone_condition)
        values.extend(phone_values)
    
    where_clause = " OR ".join(conditions)
    
    query = f"""
        SELECT 
            name,
            customer_name,
            mobile_no,
            email_id,
            customer_group,
            territory
        FROM `tabCustomer`
        WHERE {where_clause}
        ORDER BY 
            CASE 
                WHEN customer_name LIKE %s THEN 1
                WHEN email_id LIKE %s THEN 2
                ELSE 3
            END,
            customer_name
        LIMIT 100
    """
    
    # Add values for ORDER BY
    order_values = [f"%{search_term}%", f"%{search_term}%"]
    all_values = values + order_values
    
    results = frappe.db.sql(query, all_values, as_dict=1)
    
    formatted_results = []
    for row in results:
        formatted_record = {
            "customer_details": {
                "name": row.get('name'),
                "customer_name": row.get('customer_name'),
                "mobile_no": row.get('mobile_no'),
                "email_id": row.get('email_id'),
                "customer_group": row.get('customer_group'),
                "territory": row.get('territory')
            },
            "match_info": [{
                'field': 'customer_name',
                'display_name': 'Customer Name',
                'value': row.get('customer_name')
            }],
            "search_term": search_term
        }
        formatted_results.append(formatted_record)
    
    return {
        "status": "success",
        "message": f"Found {len(formatted_results)} customers matching '{search_term}'",
        "data": formatted_results,
        "search_term": search_term
    }

def determine_customer_match_field(row, search_term):
    """
    Determine which customer-related field(s) matched the search term
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
        'custom_customer_phone_number': 'Customer Phone',
        'custom_customer_email': 'Customer Email',
        'customer_email': 'Customer Email (Main)'
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