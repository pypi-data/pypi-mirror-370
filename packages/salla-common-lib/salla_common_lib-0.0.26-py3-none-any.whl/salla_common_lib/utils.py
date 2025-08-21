import pytz
import frappe
from frappe.utils import today, get_datetime, get_time
from datetime import datetime

salla_base_url = "https://api.salla.dev/admin/v2"
update_bulk_url = "products/quantities/bulkSkus"

@frappe.whitelist()
def update_product_balance_warehouse(merchant_name=None, item=None, is_bulk=False):
    payload = format_doc_for_reception(merchant_name, item, is_bulk)
    if is_app_installed("salla_connector"):
        from salla_connector.salla_utils import update_product_balance_warehouse
        update_product_balance_warehouse(payload)
    elif is_app_installed("salla_client"):
        from salla_client.salla_utils import update_product_balance_warehouse
        update_product_balance_warehouse(payload)

@frappe.whitelist()
def update_variant_qty(item_variant, merchant_name, salla_item_info_name):
    payload = format_variant_data(item_variant, merchant_name, salla_item_info_name)
    if is_app_installed("salla_connector"):
        from salla_connector.salla_utils import update_variant_qty
        update_variant_qty(payload)
    elif is_app_installed("salla_client"):
        from salla_client.salla_utils import update_variant_qty
        update_variant_qty(payload)



def format_variant_data(item_variant, merchant_name, salla_item_info_name):
    custom_salla_variant_id = frappe.get_value("Item", item_variant, "custom_salla_variant_id")

    data = []
    qty = 0
    if not frappe.db.exists(
        "Salla Sync Job", merchant_name
    ):
        frappe.throw("You Have To Put Warehouse In Salla Sync Job")

    salla_job_setting = frappe.get_doc(
        "Salla Sync Job", merchant_name
    )

    if salla_job_setting.warehouse:
        report_doc = frappe.get_doc("Report", "Stock Projected Qty")
        columns, data = report_doc.get_data(
            filters={
            "warehouse": salla_job_setting.warehouse,
            "item_code": item_variant
        }, as_dict= 1)
        
        # print(warehouse_balance)
    salla_item_info = frappe.get_doc("Salla Item Info", salla_item_info_name)
    if len(data):
        qty = data[0]["actual_qty"] - salla_item_info.pending_online_quantity - data[0]["reserved_qty"] - data[0]["reserved_qty_for_pos"]
    return {
        "merchant_name": merchant_name,
        "custom_salla_variant_id": custom_salla_variant_id,
        "qty": qty
    }

def format_doc_for_reception(merchant_name=None, item=None,is_bulk=False):
        
    payload = {"merchants": [], "is_bulk": is_bulk}
    data = []

    merchant_filters = {"name": merchant_name} if merchant_name else {}
    merchant_list = frappe.get_all(
        "Salla Merchant", filters=merchant_filters, fields=["name", "merchant_name"]
    )

    for merchant in merchant_list:
        merchant_data = {"merchant": merchant.name, "items": []}

        salla_job_setting = frappe.get_doc("Salla Sync Job", merchant.name)
        if not salla_job_setting:
            continue
        if is_bulk and compare_field_time_with_now(docname=salla_job_setting.name):
            continue
        warehouse = frappe.get_doc("Warehouse", salla_job_setting.warehouse)
        company = warehouse.company
        item_filters = {"merchant": merchant.name}
        item_filters.update(
            {"last_update": ("<", today())} if not item else {"parent": item}
        )

        merchant_item_info_list = frappe.get_all(
            "Salla Item Info",
            filters=item_filters,
            fields=[
                "name",
                "pending_online_quantity",
                "parent",
                "is_unlimited_qty",
            ],
			limit_page_length = 100
        )

        for info in merchant_item_info_list:
            if salla_job_setting.warehouse:
                report_doc = frappe.get_doc("Report", "Stock Projected Qty")
                columns, data = report_doc.get_data(
                    filters={
                    "company": company,
                    "warehouse": salla_job_setting.warehouse,
                    "item_code": info.parent
                },ignore_prepared_report=True, as_dict= 1)

            
            item_doc = frappe.get_doc("Item", info.parent)
            salla_product_sku = None
            if not item_doc.custom_salla_variant_id:
                salla_product_sku = frappe.get_value(
                "Item Barcode",
                filters={
                    "parent": info.parent,
                    "custom_is_salla_barcode": 1,
                },
                fieldname="barcode",
            )

            if not salla_product_sku and not item_doc.custom_salla_variant_id:
                continue
            quantity = 0
            if len(data):
                quantity = data[0]["actual_qty"] - info.pending_online_quantity - data[0]["reserved_qty"] - data[0]["reserved_qty_for_pos"]
                quantity = max(quantity, 0)
            if not item_doc.has_variants:
                if item_doc.variant_of:
                    variant_data = format_variant_data(item_doc.name,merchant.name,info.name)
                    merchant_data["items"].append(variant_data)
                else:
                    merchant_data["items"].append({
                        "id": item_doc.custom_salla_variant_id,
                        "sku": salla_product_sku,
                        "quantity": quantity,
                        "unlimited_quantity": bool(info.is_unlimited_qty),
                    })
            frappe.db.set_value("Salla Item Info", info.name, "last_update", today())
            frappe.db.commit()

        payload["merchants"].append(merchant_data)

    return payload

def get_salla_defaults(doc):
    if frappe.db.exists("Salla Defaults", doc.merchant):
        return frappe.get_doc("Salla Defaults", doc.merchant)
    else:
        frappe.msgprint(f"Please Set Salla Deafults For Merchant {doc.merchant}")
        return
    
def get_pos_profile(doc,salla_default) :   
    if not salla_default.pos_profile :
        frappe.throw(f"Please Set POS Profile For Merchant {doc.merchant} in Salla Defaults")
        return
    else :
        PosProfileDoc = frappe.get_doc("POS Profile", salla_default.pos_profile)
        if salla_default.taxe_included_in_basic_rate:
            if not PosProfileDoc.taxes_and_charges:
                frappe.throw(f"Please Set Taxes and Charges For Merchant {doc.merchant} in Salla Defaults")
                return
    return  PosProfileDoc 

def is_app_installed(app_name):
    """Check if an app is installed."""
    installe_app_list = frappe.get_installed_apps()
    return app_name in installe_app_list

def compare_field_time_with_now(docname,doctype="Salla Sync Job", time_field="time_to_execute", use_current_time=False):
    """
    Cast both stored time and current time to user's timezone and compare.
    If use_current_time=True, set field_time to current time.
    """
    try:
        # Get the user's timezone
        user_tz_str = frappe.db.get_value("User", frappe.session.user, "time_zone") or "UTC"
        user_tz = pytz.timezone(user_tz_str)

        # Get or set the time field value
        if use_current_time:
            # Set field_time to current time in user's timezone
            now_utc = datetime.now(pytz.UTC)  # Get current UTC time
            now_user_tz = now_utc.astimezone(user_tz)
            field_time_str = now_user_tz.strftime("%H:%M:%S")
            # Optionally update the database field
            frappe.db.set_value(doctype, docname, time_field, field_time_str)
        else:
            # Get the stored time field value
            field_time = frappe.db.get_value(doctype, docname, time_field)
            if hasattr(field_time, 'total_seconds'):
                seconds = int(field_time.total_seconds())
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                field_time_str = f"{hours:02d}:{minutes:02d}:00"
            else:
                field_time_str = str(field_time)

        # Get current time in UTC and convert to user's timezone
        now_utc = datetime.now(pytz.UTC)  # Use Python's datetime for reliable UTC
        now_user_tz = now_utc.astimezone(user_tz)  # Convert to user's timezone
        now_str = now_user_tz.strftime("%H:%M:%S")

        # Both times are now in the same timezone context
        field_time_obj = get_time(field_time_str)
        now_time_obj = get_time(now_str)

        # Compare
        return now_time_obj < field_time_obj 

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Time Comparison Error")
        return {"error": str(e)}
