import frappe
import frappe.utils
import frappe.utils.logger
from salla_common_lib.utils import is_app_installed


def before_save(doc, method):
    frappe.utils.logger.set_log_level("DEBUG")
    logger = frappe.logger("update_price", allow_site=1)

    logger.info(f'Item Price Doc Before Adding The Other Values: {doc.as_dict()}')

    is_salla_item, variant_of, salla_variant_id = frappe.get_value(
        "Item", doc.item_code, ["custom_is_salla_item", "variant_of", "custom_salla_variant_id"]
    ) or (None, None, None)

    logger.info(f'The Fields I got From Item: {is_salla_item}, {variant_of}, {salla_variant_id}')

    if is_salla_item:
        barcode_list = frappe.get_all("Item Barcode", {"parent": doc.item_code, "custom_is_salla_barcode": 1}) 
        if barcode_list and len(barcode_list) > 0:
            barcode = frappe.get_doc("Item Barcode", barcode_list[0].name)
            merchant_salla_setting_list = frappe.get_list(
                "Salla Defaults", filters={"price_list": doc.price_list}, fields=["name"]
            )
        else:   
            logger.error(f'No Salla Barcode found for Item: {doc.item_code}')
            return
        for salla_setting in merchant_salla_setting_list:
            payload = {
                "selling": doc.selling,
                "valid_from": doc.valid_from,
                "price_list": doc.price_list,
                "price_list_rate": doc.price_list_rate,
                "item_code": doc.item_code,
                "barcode": barcode.barcode,
                "custom_is_salla_item": is_salla_item,
                "variant_of": variant_of,
                "custom_salla_variant_id": salla_variant_id,
                "merchant": salla_setting.name
            }

            logger.info(f'Merchant is {salla_setting.name}')
            logger.info(f'Payload being sent: {payload}')

            if is_app_installed("salla_connector"):
                try:
                    from salla_connector.salla_utils import update_salla_price
                    update_salla_price(payload)
                except ImportError:
                    frappe.log_error("Failed to import from salla_connector")

            if is_app_installed("salla_client"):
                try:
                    from salla_client.salla_utils import update_salla_price
                    update_salla_price(payload)
                    logger.info(f"After sending to salla_client: {payload}")
                except ImportError:
                    frappe.log_error("Failed to import from salla_client")



