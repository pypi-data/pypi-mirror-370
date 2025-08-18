from docutils.nodes import comment

# TsPay Python Client

![Python](https://img.shields.io/badge/python-3.6%252B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PyPI Version](https://img.shields.io/pypi/v/tspay-client)

**TsPayClient** — TSPay.uz to‘lov gateway API bilan ishlash uchun rasmiy Python klienti.  
U orqali foydalanuvchi tokenini olish, do‘konlarni olish, tranzaksiyalar yaratish va holatini tekshirish mumkin.

---

## Table of Contents

1. [Installation](#installation)  
2. [Quick Start](#quick-start)  
3. [API Reference](#api-reference)  
4. [Error Handling](#error-handling)  
5. [Examples](#examples)
6. [License](#license)  

---

## Installation

```bash
pip install tspay-client
```

## Quick Start

```python
from tspay import TsPayClient

# Klient yaratish
client = TsPayClient()

# Foydalanuvchi tokenini olish
token = client.get_access_token("your_email@example.com", "your_password")

# Do'konlarni olish
shops = client.get_user_shops(token)

# Tranzaksiya yaratish
transaction = client.create_transaction(
    amount=10000,  # UZS
    redirect_url="https://yourwebsite.com/payment/callback",
    comment="Order #12345",
    access_token=shops[0]['access_token']
)

# Tranzaksiya holatini tekshirish
status = client.check_transaction(token, transaction['cheque_id'])

print("Payment URL:", transaction['payment_url'])
print("Transaction status:", status['status'])
```

## API Reference
    TsPayClient(base_url=None)
    • base_url (str, optional): API ning custom URL manzili, default: `https://api.tspay.uz`

## Authentication Methods

get_access_token(email, password)

Foydalanuvchi tokenini olish.
	•	Parameters:
	•	email (str) — foydalanuvchi emaili
	•	password (str) — foydalanuvchi paroli
	•	Returns: Access token (str)
	•	Raises: TsPayError agar autentifikatsiya xato bo‘lsa

## Shop Methods

get_user_shops(user_access_token)

## Foydalanuvchiga tegishli do‘konlar ro‘yxatini olish.
	•	Parameters:
	•	user_access_token (str) — foydalanuvchi access tokeni
	•	Returns: List[dict] — do‘konlar ro‘yxati
	•	Raises: TsPayError agar so‘rov xato bo‘lsa

## Transaction Methods

create_transaction(amount, redirect_url="", description="", access_token=None)

## Yangi tranzaksiya yaratish.
	•	Parameters:
	•	amount (float) — summa UZS
	•	redirect_url (str) — callback URL
	•	description (str, optional) — tranzaksiya tavsifi
	•	access_token (str) — do‘kon access tokeni
	•	Returns: dict — tranzaksiya ma’lumotlari
	•	Raises: TsPayError agar yaratish xato bo‘lsa

check_transaction(user_access_token, transaction_id)

## Tranzaksiya holatini tekshirish.
	•	Parameters:
	•	user_access_token (str) — foydalanuvchi tokeni
	•	transaction_id (str) — tranzaksiya IDsi
	•	Returns: dict — tranzaksiya holati
	•	Raises: TsPayError agar xato bo‘lsa

## Error Handling

```python
class TsPayError(Exception):
    """TSPay API xatoliklari uchun asosiy istisno."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code
```

## Examples

Complete Payment Flow

```python
from tspay import TsPayClient, TsPayError

def process_payment(amount, commment):
    try:
        client = TsPayClient()
        token = client.get_access_token("merchant@example.com", "securepassword")
        shops = client.get_user_shops(token)
        if not shops:
            raise Exception("No shops available")
        
        transaction = client.create_transaction(
            amount=amount,
            redirect_url="https://example.com/payment/callback",
            comment=comment,
            access_token=shops[0]['access_token']
        )
        
        return {
            'success': True,
            'payment_url': transaction['payment_url'],
            'transaction_id': transaction['cheque_id']
        }
    
    except TsPayError as e:
        return {'success': False, 'error': str(e)}
```

## License

MIT License — LICENSE

Batafsil: https://tspay.uz
