import frappe
from salla_common_lib.utils import is_app_installed

def before_save(doc, method):
    if is_app_installed("salla_connector"):
        from salla_connector.salla_utils import Update_salla_online_qty, has_barcode, setup_variant_data, update_item_barcode
        if doc.custom_update_pending_online_quantity and doc.custom_is_salla_item:
            Update_salla_online_qty(doc)
            doc.custom_update_pending_online_quantity = 0
        update_item_barcode(doc)
        handle_variant(doc, has_barcode, setup_variant_data)

    if is_app_installed("salla_client"):
        from salla_client.salla_utils import Update_salla_online_qty, has_barcode, setup_variant_data, update_item_barcode
        if doc.custom_update_pending_online_quantity and doc.custom_is_salla_item:
            Update_salla_online_qty(doc)
            doc.custom_update_pending_online_quantity = 0
        update_item_barcode(doc)
        handle_variant(doc, has_barcode, setup_variant_data)


def handle_variant(doc, has_barcode, setup_variant_data):
    if doc.variant_of and not has_barcode(doc):
        parent = frappe.get_doc("Item", doc.variant_of)
        send_to_salla = parent.custom_send_item_to_salla == 1
        merchant_name = parent.custom_salla_item[0].merchant if send_to_salla else None
        setup_variant_data(doc, send_to_salla, merchant_name)


def on_update(doc, method):
    if doc.custom_require_shipping and not doc.weight_per_unit:
        frappe.throw(
        "Weight per Unit is required when <b>Require Shipping</b> is enabled.",
         title="Missing Weight"
        )
    for row in doc.custom_salla_item:
        print("ON UPDATE !!!!!")
        barcode = frappe.get_doc(
            "Item Barcode", {"parent": doc.name, "custom_is_salla_barcode": 1}
        )
        payload = {
            "name": doc.name,
            "item_name": doc.item_name,
            "standard_rate": doc.standard_rate if doc.standard_rate else 0,
            "custom_product_type": doc.custom_product_type,
            "description": doc.description,
            "custom_send_item_to_salla": doc.custom_send_item_to_salla,
            "barcode": barcode.barcode,
            "custom_product_image": doc.custom_product_image,
            "variant_of": doc.variant_of,
            "weight_per_unit": doc.weight_per_unit,
            "custom_salla_image_id": doc.custom_salla_image_id,
			"with_tax": True if doc.custom_with_tax else False,
            "require_shipping": True if doc.custom_require_shipping else False
        }

        if doc.variant_of:
            barcode = frappe.get_doc(
                "Item Barcode", {"parent": doc.variant_of, "custom_is_salla_barcode": 1}
            )

            payload.update({
                "parent_barcode": barcode.barcode,
                "custom_salla_variant_id": doc.custom_salla_variant_id,
                "attributes": [row.as_dict() for row in doc.attributes]
            })
        ## This should be optimized for bulk processing to reduce api calls
        is_salla_connector_installed = is_app_installed("salla_connector")
        if is_salla_connector_installed:
            from salla_connector.salla_item_utils import create_or_update_salla_item
            create_or_update_salla_item(payload, row.merchant)

        is_salla_client_installed = is_app_installed("salla_client")
        if  is_salla_client_installed :
            from salla_client.salla_utils import create_or_update_salla_item
            if not doc.custom_is_synced:
                create_or_update_salla_item(payload, row.merchant)
