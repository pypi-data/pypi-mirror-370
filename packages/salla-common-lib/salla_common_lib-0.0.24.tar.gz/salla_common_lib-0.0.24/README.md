# Salla Common Lib

A comprehensive Python library for Salla e-commerce platform integration with Frappe/ERPNext systems.

## Installation

You can install the package using pip:

```bash
pip install salla-common-lib
```

## Features

### Core Functionality
- **Product Management**: Comprehensive item and variant synchronization with Salla
- **Inventory Sync**: Real-time inventory quantity updates between ERPNext and Salla
- **Order Processing**: Advanced order management and processing capabilities
- **Event Handling**: Robust event system for item updates, price changes, and order workflows
- **Multi-Merchant Support**: Support for multiple Salla merchants from a single ERPNext instance

### Key Modules

#### Utils (`salla_common_lib.utils`)
- `update_product_balance_warehouse()`: Updates product quantities in Salla based on warehouse balance
- `update_variant_qty()`: Manages variant-specific quantity updates
- `get_salla_defaults()`: Retrieves merchant-specific Salla configuration
- `get_pos_profile()`: POS profile management for Salla transactions

#### Event Management (`salla_common_lib.event`)
- **Item Events**: Handle item creation, updates, and variant management
- **Price Events**: Manage pricing synchronization
- **Order Events**: Process Salla orders and fulfillment
- **Field Management**: Dynamic field handling for Salla integration

### Integration Support
Compatible with both:
- `salla_connector` app
- `salla_client` app

## Usage

### Basic Item Synchronization
```python
from salla_common_lib.utils import update_product_balance_warehouse

# Update product quantities for a specific merchant
update_product_balance_warehouse(
    merchant_name="your_merchant",
    item="ITEM-001",
    is_bulk=False
)
```

### Variant Management
```python
from salla_common_lib.utils import update_variant_qty

# Update variant quantity
update_variant_qty(
    item_variant="ITEM-001-RED-L",
    merchant_name="your_merchant",
    salla_item_info_name="salla_item_info_name"
)
```

### Event Hooks
The library provides automatic event handling for:
- Item before_save and on_update events
- Price synchronization events
- Order processing workflows

## Configuration

### Prerequisites
- Frappe/ERPNext instance
- Salla merchant account and API credentials
- Warehouse configuration for inventory sync

### Setup
1. Install the library in your Frappe environment
2. Configure Salla Merchant settings
3. Set up Salla Sync Job with warehouse mapping
4. Configure Salla Defaults for each merchant

## API Integration

The library seamlessly integrates with Salla's API v2:
- Base URL: `https://api.salla.dev/admin/v2`
- Supports bulk operations for improved performance
- Handles authentication and error management

## Requirements

- Python >= 3.10
- Frappe Framework
- Active Salla merchant account

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support and questions, contact: info@golive-solutions.com

## Changelog

### Version 0.0.7
- Enhanced README documentation
- Improved API integration support
- Better error handling and validation
