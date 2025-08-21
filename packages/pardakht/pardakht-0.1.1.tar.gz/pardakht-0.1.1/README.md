# Pardakht 🏦

**Pardakht** is a simple Python library to integrate bots or applications with payment gateways.
Currently, it supports **ZarinPal** and is designed for **Telegram bots**.

![Downloads](https://static.pepy.tech/personalized-badge/pardakht?period=total&units=international_system&left_color=grey&right_color=blue)


> ⚡ Coming soon: Support for web applications and other platforms.
> For now, you can use it directly in your bot projects.


---

## Installation

```bash
pip install pardakht
```

---

## Usage

### 1️⃣ Import and Initialize

```python
from pardakht.dargah import ZarinPal

# Settings
MERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
CALLBACK_URL = "https://yourdomain.com/check-payment"

# Create an instance of ZarinPalBot
zarinpal = ZarinPalBot(merchant_id=MERCHANT_ID, callback_url=CALLBACK_URL, sandbox=True)
```

---

### 2️⃣ Create a Payment and Get the Payment Link

```python
amount = 10000  # Amount in Tomans
uuid_code = "some-unique-id-1234"  # You can use uuid.uuid4() for unique transactions
description = "Premium subscription purchase"

pay_url = zarinpal.make_payment(amount, uuid_code, description)

if pay_url.startswith("http"):
    print("Payment link:", pay_url)
else:
    print("Error:", pay_url)
```

> ⚡ If there is an issue connecting to the gateway, it will return:
> `"Failed to connect to the payment gateway."`

---

### 3️⃣ Verify the Payment After User Returns from Gateway

```python
authority = "A1B2C3D4E5"  # Obtained from query params or gateway payload
result = zarinpal.verify_payment(authority, amount)

if result["success"]:
    print("Payment successful ✅")
    print("Tracking code:", result["ref_id"])
else:
    print("Payment failed ❌")
    print("Message:", result["message"])
```

---

### 4️⃣ Notes

* Always generate a **unique ID (uuid)** for each transaction to track it in your database.
* In **Telegram bots**, you can use `pay_url` as an inline button for users to click.
* Use `sandbox=True` during testing to avoid real transactions.

---
