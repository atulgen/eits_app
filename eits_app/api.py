# In your custom app's api.py or hooks.py
import frappe

@frappe.whitelist()
def get_user_with_roles(user_email):
    # Add your own permission logic here
    if not frappe.has_permission("User", "read"):
        frappe.throw("Insufficient permissions")
    
    user_doc = frappe.get_doc("User", user_email)
    
    # Explicitly include roles
    user_dict = user_doc.as_dict()
    user_dict['roles'] = [role.role for role in user_doc.roles]
    
    return user_dict