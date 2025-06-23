import frappe

@frappe.whitelist()
def get_user_roles(user=None):
    """Get roles for current user or specified user"""
    if not user:
        user = frappe.session.user
    
    # Check if current user can access other user's roles
    if user != frappe.session.user and not frappe.has_permission("User", "read"):
        frappe.throw("Not permitted to access other user's roles")
    
    roles = frappe.get_roles(user)
    return roles