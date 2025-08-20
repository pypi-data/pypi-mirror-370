# Order Service

Manage baskets, payments, and invoices with the Order Service. This service provides comprehensive functionality for
handling order-related operations and payment processing: manage shopping baskets and checkout flow, process invoice
payments with multiple payment methods, handle payment callbacks and verification, track product variation status, and
manage payable and unpaid invoices.

## Table of Contents

- [Order Methods](#order-methods)
- [Examples](#examples)

## Order Methods

| Method                                                                    | Description                     | Parameters                                                    |
|---------------------------------------------------------------------------|----------------------------------|---------------------------------------------------------------|
| [`get_baskets()`](#get-baskets)                                   | Get active baskets              | `refresh`                                                     |
| [`get_product_variation_status()`](#get-product-variation-status) | Get product variation status    | `product_id`                                                  |
| [`create_invoice_payment()`](#create-invoice-payment)             | Create payment for invoice      | `invoice_id`, `request: CreatePaymentRequestModel`           |
| [`get_payable_invoices()`](#get-payable-invoices)                 | Get payable invoices            | `page`, `per_page`                                           |
| [`get_unpaid_invoices()`](#get-unpaid-invoices)                   | Get unpaid invoices             | `invoice_id`, `status`, `page`, `per_page`, `sort`           |
| [`get_payment_callback()`](#get-payment-callback)                 | Get payment callback            | `payment_id`, `request: PaymentCallbackRequestModel`         |
| [`create_payment_callback()`](#create-payment-callback)           | Create payment callback         | `payment_id`, `request: PaymentVerifyRequestModel`           |

## Examples

### Basic Setup

```python
from basalam_sdk import BasalamClient, PersonalToken
from basalam_sdk.order.models import (
    CreatePaymentRequestModel, 
    PaymentCallbackRequestModel, 
    PaymentVerifyRequestModel,
    PaymentDriver,
    UnpaidInvoiceStatusEnum, 
    OrderEnum, 
    BasketResponse
)

auth = PersonalToken(
    token="your_access_token",
    refresh_token="your_refresh_token"
)
client = BasalamClient(auth=auth)
```

### Get Baskets

```python
async def get_baskets_example():
    baskets = await client.get_baskets(
        refresh=True
    )
    
    print(f"Basket ID: {baskets.id}")
    print(f"Item count: {baskets.item_count}")
    
    if baskets.vendors:
        for vendor in baskets.vendors:
            print(f"Vendor: {vendor.title} - Items: {len(vendor.items) if vendor.items else 0}")
    
    return baskets
```

### Get Product Variation Status

```python
async def get_product_variation_status_example():
    status = await client.get_product_variation_status(
        product_id=123456
    )
    
    print(f"Product variation status: {status}")
    return status
```

### Create Invoice Payment

```python
async def create_invoice_payment_example():
    payment = await client.create_invoice_payment(
        invoice_id=456789,
        request=CreatePaymentRequestModel(
            pay_drivers={
                "gateway": PaymentDriver(amount=50000),
                "credit": PaymentDriver(amount=25000)
            },
            callback="https://yoursite.com/payment/callback",
            option_code="EXPRESS_DELIVERY",
            national_id="1234567890"
        )
    )
    
    print(f"Payment created: {payment}")
    return payment
```

### Get Payable Invoices

```python
async def get_payable_invoices_example():
    invoices = await client.get_payable_invoices(
        page=1,
        per_page=20
    )
    
    print(f"Payable invoices: {invoices}")
    return invoices
```

### Get Unpaid Invoices

```python
async def get_unpaid_invoices_example():
    invoices = await client.get_unpaid_invoices(
        invoice_id=123456,
        status=UnpaidInvoiceStatusEnum.UNPAID,
        page=1,
        per_page=20,
        sort=OrderEnum.DESC
    )
    
    print(f"Unpaid invoices: {invoices}")
    return invoices
```

### Get Payment Callback

```python
async def get_payment_callback_example():
    callback = await client.get_payment_callback(
        payment_id=789012,
        request=PaymentCallbackRequestModel(
            status="success",
            transaction_id="TXN_123456789",
            description="Payment completed successfully"
        )
    )
    
    print(f"Payment callback: {callback}")
    return callback
```

### Create Payment Callback

```python
async def create_payment_callback_example():
    callback = await client.create_payment_callback(
        payment_id=789012,
        request=PaymentVerifyRequestModel(
            payment_id="PAY_123456789",
            transaction_id="TXN_987654321",
            description="Payment verification completed"
        )
    )
    
    print(f"Payment callback created: {callback}")
    return callback
```


## Next Steps

- [Upload Service](./upload.md) - File upload and management
- [Search Service](./search.md) - Search for products and entities
- [Order Processing Service](./order-processing.md) - Process orders and parcels 
