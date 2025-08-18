import frappe
from http.client import HTTPException
from frappe import _, msgprint

def validate(doc, method=None):
    if not frappe.db.exists("Salla Defaults", doc.merchant):
        frappe.throw(f"Merchant {doc.merchant} Defaults Not Exist.")

def before_insert(doc, method=None):
    salla_default = frappe.get_doc("Salla Defaults", doc.merchant)
    doc.pos_profile = salla_default.pos_profile
    doc.old_order_status = ""

def before_save(doc, method=None):
    salla_default = frappe.get_doc("Salla Defaults", doc.merchant)
    if not doc.company:
        doc.company = salla_default.company

    ready_to_complete = 0
    for salla_item in doc.items:
        salla_item.order_status = doc.order_status
        if not salla_item.merchant:
            salla_item.merchant = doc.merchant

        bundle_barcode_separator = salla_default.bundle_barcode_separator
        print(f"bundle_barcode_separator : {bundle_barcode_separator} ")
        if bundle_barcode_separator and  bundle_barcode_separator in salla_item.barcode:
            salla_item.is_bundle = 1
        if salla_item.barcode and not salla_item.item_code:
            barcode_data = frappe.db.get_value(
                "Item Barcode",
                {"barcode": salla_item.barcode, "custom_is_salla_barcode": 1},
                ["barcode", "parent as item_code"],
                as_dict=True,
            )
           
            if barcode_data:
                item = frappe.get_doc("Item",barcode_data.item_code)
                salla_item.item_code = item.name
                salla_item.item_name = item.item_name
                ready_to_complete = 1
        if  salla_item.item_code :
            item = frappe.get_doc("Item",salla_item.item_code)
            qty = get_chqanged_quantity(salla_item, doc)
            if doc.order_status != doc.old_order_status and doc.order_status == "ملغي":
                qty = -1 * salla_item.qty
            # if we get order with canceled status for first time (old_order_status = "")    
            if doc.old_order_status == "" and doc.order_status == "ملغي":
                qty = 0 #(qty = 0) to avoid negative pending online quantity when canceling order for first time
            if qty != 0:    
                salla_item_info = get_salla_item_info(item, doc.merchant)    
                update_pending_onlin_qty(salla_item_info, qty)
                item.save()   
                if  salla_item.is_bundle :
                    barcodeList = salla_item.barcode.split(bundle_barcode_separator)
                    for barcode in barcodeList:
                        item_code = frappe.db.get_value(
                            "Item Barcode",
                            {"barcode": barcode, "custom_is_salla_barcode": 1},
                            ["barcode", "parent as item_code"],
                            as_dict=True,
                        )
                        if item_code:
                            item = frappe.get_doc("Item", item_code)
                            salla_item_info = get_salla_item_info(item, doc.merchant)    
                            update_pending_onlin_qty(salla_item_info, qty)
                            item.save()      

    doc.old_order_status = doc.order_status                  
    doc.ready_to_complete = ready_to_complete

def get_chqanged_quantity(salla_item, doc):
    old_doc = doc.get_doc_before_save()
    qty = salla_item.qty
    if old_doc :
        old_salla_item = next((item for item in old_doc.items if item.name == salla_item.name), None)
        if old_salla_item:
            qty = salla_item.qty - old_salla_item.qty
    return qty

def get_salla_item_info(item, merchant):
    salla_item_info_list = [item_info for item_info in item.custom_salla_item if item_info.merchant == merchant] 
    if len(salla_item_info_list) > 0 :
        salla_item_info = salla_item_info_list[0]
    else:
        salla_item_info = frappe.get_doc({"doctype": "Salla Item Info"})
        salla_item_info.parent = item.item_code
        salla_item_info.merchant = merchant
        item.append("custom_salla_item", salla_item_info)
    print(f"salla_item_info : {salla_item_info.name} , pending_online_quantity : {salla_item_info.pending_online_quantity}")    
    return salla_item_info

def update_pending_onlin_qty(salla_item_info, qty): 
    print(f"salla_item_info : {salla_item_info.name} , qty : {qty}")
    if qty < 0 and salla_item_info.pending_online_quantity < abs(qty):
        salla_item_info.pending_online_quantity = 0
        print(f"salla_item_info : {salla_item_info.name} , salla_item_info : {salla_item_info.pending_online_quantity}")
    else:
        salla_item_info.pending_online_quantity = salla_item_info.pending_online_quantity + qty
        print(f"salla_item_info : {salla_item_info.name} , pending_online_quantity : {salla_item_info.pending_online_quantity}")
       

def before_update_after_submit(doc,method=None):
    for salla_item in doc.items:
        salla_item.is_document_submitted = 1
        salla_item.order_status = doc.order_status

def on_cancel(doc, method=None):
    try:
        msgprint(
            _(
                "The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment about the error on this Salla Order  and revert to the Submitted stage"
            )
        )
        doc.queue_action("cancel", timeout=2000)
    except HTTPException as e:
        doc.status = "Failed"
        return e

def before_submit(doc, method=None):
    salla_default = frappe.get_doc("Salla Defaults", doc.merchant)

    if not doc.customer:
        CustomerList = frappe.get_all(
            "Customer",
            filters=[["mobile_no", "=", doc.phone_number]],
            fields=["name", "customer_name"],
        )
        if len(CustomerList) > 0:
            doc.customer = CustomerList[0].name
            doc.customer_full_name = CustomerList[0].customer_name
        else:
            customer = frappe.get_doc({"doctype": "Customer"})

            last_name = ""
            if doc.customer_last_name:
                last_name = doc.customer_last_name

            customer.customer_name = (
                doc.customer_first_name + " " + last_name
            )  # + " - "+doc.phone_number
            customer.mobile_no = doc.phone_number
            customer.customer_name_in_arabic = customer.customer_name
            customer.mobile_number = doc.phone_number
            if frappe.db.exists(
                "Salla Currency Mapping", {"name": doc.customer_currency}
            ):
                currency_mapping_customer_group = frappe.get_doc(
                    "Salla Currency Mapping", doc.customer_currency
                )
                customer.customer_group = currency_mapping_customer_group.customer_group
            else:
                frappe.throw(
                    f"This Customer Cannot Be Created because This Currency {doc.customer_currency} Didn't Mapped To Customer Group"
                )
            customer.territory = salla_default.territory
            customer.customer_type = doc.customer_type
            customer.email_id = doc.customer_email

            customer.insert()
            doc.customer = customer.name
            doc.customer_full_name = customer.customer_name

    if salla_default.taxe_included_in_basic_rate and doc.total_tax:
        frappe.throw("Total tax must be zero when 'Tax Included In Basic Rate' is enabled in Salla Default Settings.")

    for item in doc.items:
        if not item.barcode:
            frappe.throw("All items must have a barcode!")
        
        ItemCodeList = frappe.get_all(
                "Item Barcode",
                filters=[
                    [
                        "barcode",
                        "=",
                         item.barcode,
                    ],
                    [
                        "custom_is_salla_barcode",
                        "=",
                        1
                    ]
                ],
                fields=["parent"],
            )
    
        if len(ItemCodeList) > 0:
            item_doc = frappe.get_doc('Item', ItemCodeList[0].parent)
            salla_item_info = None
            salla_item_info_exist = frappe.db.exists('Salla Item Info', {"merchant": doc.merchant, "parent": item_doc.name})
            if salla_item_info_exist:
                salla_item_info = frappe.get_doc('Salla Item Info', {"merchant": doc.merchant, "parent": item_doc.name})
            else :
                salla_item_info = frappe.get_doc({'doctype':'Salla Item Info'})
                salla_item_info.parent = item_doc.name
                salla_item_info.merchant = doc.merchant

            if salla_item_info.pending_online_quantity and salla_item_info.pending_online_quantity >= item.qty :
                salla_item_info.pending_online_quantity = salla_item_info.pending_online_quantity - item.qty
            else :
                salla_item_info.pending_online_quantity = 0
            item_doc.append('custom_salla_item',salla_item_info)
            salla_item_info.save()
