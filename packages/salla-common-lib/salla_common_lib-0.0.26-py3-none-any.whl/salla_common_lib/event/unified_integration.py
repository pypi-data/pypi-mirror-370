# unified_integration.py
import frappe
import erpnext
from frappe import _
from frappe.utils import flt, cint
from datetime import timedelta
from frappe.utils.data import now_datetime
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
from salla_common_lib.utils import get_pos_profile, get_salla_defaults
from erpnext.setup.utils import get_exchange_rate
from frappe.utils import today

def before_submit(doc, method=None):
    """
    Unified integration handler that creates appropriate document based on Salla Defaults configuration
    """
    salla_default = get_salla_defaults(doc)
    if doc.salla_shipping_method and not get_shipping_item(doc.salla_shipping_method):
        frappe.throw(
            "The shipping method <b>{0}</b> is not mapped to any item. "
            .format(doc.salla_shipping_method),
            title="Missing Shipping Mapping"
        )

    if doc.salla_payment_method and not get_payment_method(doc.salla_payment_method):
        frappe.throw(
            "The payment method <b>{0}</b> is not mapped to any Mode Of Payment. "
            .format(doc.salla_payment_method),
            title="Missing Payment Mapping"
        )
    # Update item status
    for salla_item in doc.items:
        salla_item.is_document_submitted = 1
        salla_item.order_status = doc.order_status
    
    # Route to appropriate integration based on configuration
    integration_type = salla_default.get('integration_type', 'pos_invoice')
    
    if integration_type == 'POS Invoice':
        create_pos_invoice(doc, salla_default)
    elif integration_type == 'Sales Invoice':
        create_sales_invoice(doc, salla_default)
    elif integration_type == 'Sales Order':
        create_sales_order(doc, salla_default)
    else:
        frappe.throw(_("Invalid integration type: {0}").format(integration_type))

def create_pos_invoice(doc, salla_default):
    """Create POS Invoice from Salla Order"""
    if doc.custom_pos_invoice_name:
        return
        
    pos_profile_doc = get_pos_profile(doc, salla_default)
    
    pos_invoice = frappe.get_doc({'doctype': 'POS Invoice'})
    pos_invoice.customer = doc.customer
    pos_invoice.company = doc.company
    pos_invoice.customer_name = doc.customer_full_name
    pos_invoice.pos_profile = doc.pos_profile
    pos_invoice.is_online = True
    pos_invoice.custom_is_salla_item = True
    pos_invoice.posting_date = today()
    pos_invoice.set_warehouse = pos_profile_doc.warehouse
    pos_invoice.online_order = doc.salla_order_no
    pos_invoice.selling_price_list = salla_default.price_list
    pos_invoice.currency = doc.currency
    pos_invoice.ignore_pricing_rule = 1
    pos_invoice.is_store_delivery = doc.is_store_delivery

    # Get payment and shipping methods
    payment_method = get_payment_method(doc.salla_payment_method)
    shipping_item = get_shipping_item(doc.salla_shipping_method)

    # Add regular items
    add_invoice_items(pos_invoice, doc.items, pos_profile_doc, 'POS Invoice Item')

    # Add shipping fees
    if shipping_item:
        add_shipping_item(pos_invoice, shipping_item, doc.shipping_cost, pos_profile_doc, 'POS Invoice Item')

    # Add COD fees
    if str(doc.salla_payment_method).casefold() == 'cod':
        add_cod_item(pos_invoice, salla_default.cod_item, doc.cod_cost, pos_profile_doc, 'POS Invoice Item')
    else:
        pos_invoice.taxes_and_charges = pos_profile_doc.taxes_and_charges

    # Add taxes
    if not salla_default.taxe_included_in_basic_rate:
        add_tax_charges(pos_invoice, doc.total_tax, salla_default)

    # Add payment
    if payment_method:
        add_payment(pos_invoice, payment_method, doc.grand_total, 'Sales Invoice Payment', doc.currency, doc.company)

    pos_invoice.update_stock = True
    pos_invoice.docstatus = 1
    pos_invoice.insert()

    doc.custom_pos_invoice_name = pos_invoice.name
    update_order_fulfillment(doc.salla_order_no, pos_invoice.name)

def create_sales_invoice(doc, salla_default):
    """Create Sales Invoice from Salla Order"""
    if doc.custom_sales_invoice_name:
        return
        
    pos_profile_doc = get_pos_profile(doc, salla_default)
    
    sales_invoice = frappe.get_doc({'doctype': 'Sales Invoice'})
    sales_invoice.customer = doc.customer
    sales_invoice.customer_name = doc.customer_full_name
    sales_invoice.pos_profile = salla_default.pos_profile
    sales_invoice.posting_date = today()
    sales_invoice.set_warehouse = pos_profile_doc.warehouse
    sales_invoice.selling_price_list = salla_default.price_list
    sales_invoice.currency = doc.currency
    sales_invoice.ignore_pricing_rule = 1

    # Get payment and shipping methods
    payment_method = get_payment_method(doc.salla_payment_method)
    shipping_item = get_shipping_item(doc.salla_shipping_method)

    # Add regular items
    add_invoice_items(sales_invoice, doc.items, pos_profile_doc, 'Sales Invoice Item')

    # Add shipping fees
    if shipping_item:
        add_shipping_item(sales_invoice, shipping_item, doc.shipping_cost, pos_profile_doc, 'Sales Invoice Item')

    # Add COD fees
    if doc.salla_payment_method == 'cod':
        add_cod_item(sales_invoice, salla_default.cod_item, doc.cod_cost, pos_profile_doc, 'Sales Invoice Item')

    # Add taxes
    if not salla_default.taxe_included_in_basic_rate:
        add_tax_charges(sales_invoice, doc.total_tax, salla_default)
    else:
        sales_invoice.taxes_and_charges = pos_profile_doc.taxes_and_charges

    # Add payment
    if payment_method:
        add_payment(sales_invoice, payment_method, doc.grand_total, 'Sales Invoice Payment', doc.currency, doc.company)
        sales_invoice.is_pos = 1
        sales_invoice.paid_amount = doc.grand_total

    sales_invoice.update_stock = True
    sales_invoice.disable_rounded_total = 1
    sales_invoice.docstatus = 1
    sales_invoice.save()

    doc.custom_sales_invoice_name = sales_invoice.name
    update_order_fulfillment(doc.salla_order_no, sales_invoice.name)

def create_sales_order(doc, salla_default):
    """Create Sales Order from Salla Order"""
    if doc.custom_sales_order_name:
        return
        
    pos_profile_doc = get_pos_profile(doc, salla_default) if salla_default.taxe_included_in_basic_rate else None
    
    sales_order = frappe.get_doc({'doctype': 'Sales Order'})
    sales_order.customer = doc.customer
    sales_order.customer_name = doc.customer_full_name
    sales_order.company = doc.company
    sales_order.selling_price_list = salla_default.price_list
    sales_order.ignore_pricing_rule = 1
    sales_order.set_warehouse = salla_default.custom_warehouse
    sales_order.transaction_date = doc.date
    sales_order.currency = doc.currency
    sales_order.disable_rounded_total = 1
    sales_order.custom_salla_order_name = doc.name
    sales_order.custom_salla_order_custom_status = doc.custom_status

    # Get payment and shipping methods
    payment_method = get_payment_method(doc.salla_payment_method)
    shipping_item = get_shipping_item(doc.salla_shipping_method)

    # Add regular items
    add_order_items(sales_order, doc.items, salla_default)

    # Add shipping fees
    if shipping_item:
        add_shipping_order_item(sales_order, shipping_item, doc.shipping_cost, salla_default)

    # Add COD fees
    if doc.salla_payment_method == 'cod':
        add_cod_order_item(sales_order, salla_default.cod_item, doc.cod_cost, salla_default)

    # Add taxes
    if not salla_default.taxe_included_in_basic_rate:
        add_tax_charges(sales_order, doc.total_tax, salla_default)
    elif pos_profile_doc:
        sales_order.taxes_and_charges = pos_profile_doc.taxes_and_charges

    sales_order.docstatus = 1
    sales_order.save()

    # Create payment entry for non-COD orders
    if payment_method and doc.salla_payment_method != 'cod':
        create_payment_entry(sales_order, payment_method, doc)

    doc.custom_sales_order_name = sales_order.name

def get_payment_method(salla_payment_method):
    """Get mapped payment method"""
    payment_methods = frappe.get_list("Salla Payment Method Mapping", 
        filters=[["salla_payment_method", "=", salla_payment_method]], 
        fields=["next_payment_method"])
    return payment_methods[0].next_payment_method if payment_methods else None

def get_shipping_item(salla_shipping_method):
    """Get mapped shipping item"""
    shipping_methods = frappe.get_list("Salla Shipment Method Mapping", 
        filters=[["salla_shipment_method", "=", salla_shipping_method]], 
        fields=["next_shipment_item"])
    return shipping_methods[0].next_shipment_item if shipping_methods else None

def add_invoice_items(invoice, items, pos_profile_doc, item_doctype):
    """Add regular items to invoice"""
    for salla_item in items:
        invoice_item = frappe.get_doc({'doctype': item_doctype})
        invoice_item.barcode = salla_item.barcode
        invoice_item.item_code = salla_item.item_code
        invoice_item.item_name = salla_item.salla_item_name
        invoice_item.description = salla_item.salla_item_name
        invoice_item.income_account = pos_profile_doc.income_account
        invoice_item.cost_center = pos_profile_doc.cost_center
        invoice_item.qty = salla_item.qty
        invoice_item.rate = salla_item.rate - salla_item.discount_amount
        invoice_item.price_list_rate = 0
        invoice_item.serial_no = salla_item.serial_no
        invoice.append('items', invoice_item)

def add_shipping_item(invoice, shipping_item, shipping_cost, pos_profile_doc, item_doctype):
    """Add shipping item to invoice"""
    shipping_invoice_item = frappe.get_doc({'doctype': item_doctype})
    shipping_invoice_item.item_code = shipping_item
    shipping_invoice_item.item_name = shipping_item
    shipping_invoice_item.description = shipping_item
    shipping_invoice_item.income_account = pos_profile_doc.income_account
    shipping_invoice_item.cost_center = pos_profile_doc.cost_center
    shipping_invoice_item.qty = 1
    shipping_invoice_item.rate = shipping_cost
    shipping_invoice_item.price_list_rate = 0
    invoice.append('items', shipping_invoice_item)

def add_cod_item(invoice, cod_item, cod_cost, pos_profile_doc, item_doctype):
    """Add COD item to invoice"""
    cod_invoice_item = frappe.get_doc({'doctype': item_doctype})
    cod_invoice_item.item_code = cod_item
    cod_invoice_item.item_name = cod_item
    cod_invoice_item.description = cod_item
    cod_invoice_item.income_account = pos_profile_doc.income_account
    cod_invoice_item.cost_center = pos_profile_doc.cost_center
    cod_invoice_item.qty = 1
    cod_invoice_item.rate = cod_cost
    cod_invoice_item.price_list_rate = 0
    invoice.append('items', cod_invoice_item)

def add_order_items(sales_order, items, salla_default):
    """Add regular items to sales order"""
    for salla_item in items:
        sales_order_item = frappe.get_doc({'doctype': 'Sales Order Item'})
        sales_order_item.barcode = salla_item.barcode
        sales_order_item.item_code = salla_item.item_code
        sales_order_item.item_name = salla_item.salla_item_name
        sales_order_item.description = salla_item.salla_item_name
        sales_order_item.delivery_date = now_datetime() + timedelta(days=salla_default.custom_days_to_delivery_order)
        sales_order_item.qty = salla_item.qty
        sales_order_item.rate = salla_item.rate - salla_item.discount_amount
        sales_order_item.price_list_rate = 0
        sales_order_item.serial_no = salla_item.serial_no
        sales_order.append('items', sales_order_item)

def add_shipping_order_item(sales_order, shipping_item, shipping_cost, salla_default):
    """Add shipping item to sales order"""
    shipping_order_item = frappe.get_doc({'doctype': 'Sales Order Item'})
    shipping_order_item.item_code = shipping_item
    shipping_order_item.item_name = shipping_item
    shipping_order_item.description = shipping_item
    shipping_order_item.delivery_date = now_datetime() + timedelta(days=salla_default.custom_days_to_delivery_order)
    shipping_order_item.qty = 1
    shipping_order_item.rate = shipping_cost
    shipping_order_item.price_list_rate = 0
    sales_order.append('items', shipping_order_item)

def add_cod_order_item(sales_order, cod_item, cod_cost, salla_default):
    """Add COD item to sales order"""
    cod_order_item = frappe.get_doc({'doctype': 'Sales Order Item'})
    cod_order_item.item_code = cod_item
    cod_order_item.item_name = cod_item
    cod_order_item.description = cod_item
    cod_order_item.delivery_date = now_datetime() + timedelta(days=salla_default.custom_days_to_delivery_order)
    cod_order_item.qty = 1
    cod_order_item.rate = cod_cost
    cod_order_item.price_list_rate = 0
    sales_order.append('items', cod_order_item)

def add_tax_charges(document, total_tax, salla_default):
    """Add tax charges to document"""
    tax_charge = frappe.get_doc({'doctype': 'Sales Taxes and Charges'})
    tax_charge.tax_amount = total_tax
    tax_charge.charge_type = salla_default.tax_type
    tax_charge.account_head = salla_default.tax_account
    tax_charge.description = salla_default.tax_description
    document.append('taxes', tax_charge)

def add_payment(invoice, payment_method, amount, payment_doctype, currency, company):
    """Add payment to invoice"""
    default_currency = erpnext.get_company_currency(company)
    conversion_rate = get_exchange_rate(currency, default_currency, today())
    mode_of_payment_account = frappe.get_doc("Mode of Payment Account", {"parent": payment_method}).default_account
    payment = frappe.get_doc({'doctype': payment_doctype})
    payment.mode_of_payment = payment_method
    payment.amount = amount
    payment.base_amount = amount * conversion_rate
    payment.account = mode_of_payment_account
    invoice.paid_amount = amount
    invoice.append('payments', payment)

def create_payment_entry(sales_order, payment_method, doc):
    """Create payment entry for sales order"""
    mode_of_payment_account = frappe.get_doc("Mode of Payment Account", 
        {"parent": payment_method, "company": doc.company}).default_account
    mode_of_payment = frappe.get_doc("Mode of Payment", payment_method)
    
    payment = get_payment_entry(dt=sales_order.doctype, dn=sales_order.name, payment_type="Receive")
    payment.mode_of_payment = payment_method
    payment.paid_to = mode_of_payment_account
    payment.custom_salla_order_name = doc.name
    
    if mode_of_payment.type == "Bank":
        payment.reference_no = doc.bank_reference if doc.bank_reference else doc.name
    
    payment.docstatus = 1
    payment.save()
    doc.custom_payment_entry_name = payment.name

def update_order_fulfillment(salla_order_no, invoice_name):
    """Update Salla Order Fulfillment with invoice reference"""
    fulfillment_list = frappe.get_list("Salla Order Fulfilment", 
        filters=[["salla_order_no", "=", salla_order_no]], 
        fields=["name"])
    
    if fulfillment_list:
        fulfillment = frappe.get_doc('Salla Order Fulfilment', fulfillment_list[0].name)
        fulfillment.pos_invoice = invoice_name
        fulfillment.save()

def update_custom_status_sales_order(doc):
    """Update custom status in linked sales order"""
    if hasattr(doc, "custom_sales_order_name"):
        if doc.docstatus == 1 and doc.custom_sales_order_name:
            if frappe.db.exists("Sales Order", doc.custom_sales_order_name):
                sales_order = frappe.get_doc("Sales Order", doc.custom_sales_order_name)
                if sales_order.custom_salla_order_custom_status != doc.custom_status:
                    sales_order.custom_salla_order_custom_status = doc.custom_status
                    sales_order.save()

# Hook methods for Sales Order events
def before_save(doc, method=None):
    """Sales Order before_save hook"""
    update_custom_status_sales_order(doc)

def on_update_after_submit(doc, method=None):
    """Sales Order on_update_after_submit hook"""
    update_custom_status_sales_order(doc)
