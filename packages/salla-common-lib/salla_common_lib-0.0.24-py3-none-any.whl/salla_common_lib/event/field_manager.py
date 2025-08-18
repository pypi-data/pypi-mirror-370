
import frappe
from frappe import _

# Field configurations for each integration type
INTEGRATION_FIELDS = {
    'POS Invoice': {
        'Salla Order': [
            {
                'fieldname': 'custom_pos_invoice_name',
                'label': 'POS Invoice Name',
                'fieldtype': 'Link',
                'options': 'POS Invoice',
                'read_only': 1,
                'insert_after': 'connections_tab'
            }
        ],
        'POS Invoice': [
            {
                'fieldname': 'custom_is_salla_item',
                'label': 'Is Salla Item',
                'fieldtype': 'Check',
                'default': '0',
                'insert_after': 'online_order'
            }
        ]
    },
    'Sales Invoice': {
        'Salla Order': [
            {
                'fieldname': 'custom_sales_invoice_name',
                'label': 'Sales Invoice Name',
                'fieldtype': 'Link',
                'options': 'Sales Invoice',
                'read_only': 1,
                'insert_after': 'connections_tab'
            }
        ]
    },
    'Sales Order': {
        'Salla Defaults': [
        {
            'fieldname': 'custom_warehouse',
            'label': 'Warehouse',
            'fieldtype': 'Link',
            'options': 'Warehouse',
            'depends_on': 'eval:doc.integration_type=="Sales Order"',
            'insert_after': 'custom_days_to_delivery_order'
        },
        {
            'fieldname': 'custom_days_to_delivery_order',
            'label': 'Days To Delivery Order',
            'fieldtype': 'Int',
            'insert_after': 'price_list'
        },
        
        ],
        'Salla Order': [
            {
                'fieldname': 'custom_sales_order_name',
                'label': 'Sales Order Name',
                'fieldtype': 'Link',
                'options': 'Sales Order',
                'read_only': 0,
                'insert_after': 'connections_tab'
            },
            {
                'fieldname': 'custom_payment_entry_name',
                'label': 'Payment Entry Name',
                'fieldtype': 'Link',
                'options': 'Payment Entry',
                'read_only': 0,
                'insert_after': 'custom_sales_order_name'
            }
        ],
        'Sales Order': [
            {
                'fieldname': 'custom_salla_order_name',
                'label': 'Salla Order Name',
                'fieldtype': 'Data',
                'insert_after': 'order_type'
            },
            {
                'fieldname': 'custom_salla_order_custom_status',
                'label': 'Salla Order Custom Status',
                'fieldtype': 'Data',
                'allow_on_submit': 1,
                'insert_after': 'custom_salla_order_name'
            }
        ],
        'Payment Entry': [
            {
                'fieldname': 'custom_salla_order_name',
                'label': 'Salla Order Name',
                'fieldtype': 'Data',
                'insert_after': 'mode_of_payment'
            }
        ]
    }
}

# Core fields that are always present


def manage_custom_fields(doc, method=None):
    """
    Dynamically manage custom fields based on integration type
    """
    if not doc.integration_type:
        return
    
    # Remove all integration-specific fields first
    remove_all_integration_fields()
    
    # Create fields for selected integration type
    create_integration_fields(doc.integration_type)
    
    frappe.clear_cache()


def create_integration_fields(integration_type):
    """Create fields for specific integration type"""
    if integration_type not in INTEGRATION_FIELDS:
        return
    
    for doctype, fields in INTEGRATION_FIELDS[integration_type].items():
        for field_config in fields:
            create_custom_field(doctype, field_config)

def remove_all_integration_fields():
    """Remove all integration-specific custom fields"""
    all_fields = []
    
    for integration_type, doctypes in INTEGRATION_FIELDS.items():
        for doctype, fields in doctypes.items():
            for field_config in fields:
                field_name = f"{doctype}-{field_config['fieldname']}"
                all_fields.append(field_name)
    
    # Delete existing custom fields
    for field_name in all_fields:
        if frappe.db.exists("Custom Field", field_name):
            try:
                frappe.delete_doc("Custom Field", field_name)
            except Exception as e:
                frappe.log_error(f"Error deleting custom field {field_name}: {str(e)}")

def create_custom_field(doctype, field_config):
    """Create a single custom field if it doesn't exist"""
    field_name = f"{doctype}-{field_config['fieldname']}"
    
    if frappe.db.exists("Custom Field", field_name):
        return
    
    try:
        custom_field = frappe.get_doc({
            "doctype": "Custom Field",
            "dt": doctype,
            "fieldname": field_config['fieldname'],
            "label": field_config['label'],
            "fieldtype": field_config['fieldtype'],
            "options": field_config.get('options', ''),
            "insert_after": field_config.get('insert_after', ''),
            "read_only": field_config.get('read_only', 0),
            "reqd": field_config.get('reqd', 0),
            "default": field_config.get('default', ''),
            "depends_on": field_config.get('depends_on', ''),
            "description": field_config.get('description', '')
        })
        custom_field.insert()
        
    except Exception as e:
        frappe.log_error(f"Error creating custom field {field_name}: {str(e)}")

