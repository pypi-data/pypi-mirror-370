import requests
from typing import Dict, List, Optional, Tuple


class TsPayClient:
    """TSPay uchun rasmiy Python klienti"""

    BASE_URL = "https://tspay.uz/api/v1"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or self.BASE_URL

    def get_access_token(self, email: str, password: str) -> Optional[str]:
        """Foydalanuvchi tokenini olish"""
        url = f"{self.base_url}/auth/login/"
        try:
            response = requests.post(url, json={"email": email, "password": password})

            if response.status_code == 401:
                raise TsPayError("Login amalga oshmadi: Email yoki parol noto'g'ri")

            response.raise_for_status()
            data = response.json()

            if not data.get("access_token"):
                raise TsPayError("Serverdan token qaytmadi")

            return data.get("access_token")

        except requests.RequestException as e:
            raise TsPayError(f"Tarmoq xatosi: {str(e)}")
        except ValueError as e:
            raise TsPayError(f"JSON javobini tahlil qilishda xato: {str(e)}")

    def get_user_shops(self, user_access_token: str) -> List[Dict]:
        """Foydalanuvchi do'konlarini olish"""
        url = f"{self.base_url}/shops/access-token/"
        headers = {"Authorization": f"Bearer {user_access_token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data.get("shops"), list):
                raise TsPayError("Serverdan do'konlar ro'yxati qaytmadi")

            shops = data.get("shops", [])

            if not shops:
                raise TsPayError("Foydalanuvchining do'konlari topilmadi")

            return shops

        except requests.RequestException as e:
            raise TsPayError(f"Do'kon tokenini olishda xato: {str(e)}")
        except ValueError as e:
            raise TsPayError(f"JSON javobini tahlil qilishda xato: {str(e)}")

    def create_transaction(
            self,
            amount: float,
            redirect_url: str = "",
            comment: str = "",
            access_token: str = None
    ) -> Dict:
        """Yangi tranzaksiya yaratish"""
        url = f"{self.base_url}/transactions/create/"

        if not access_token:
            raise TsPayError("Do'kon tokeni (access_token) ko'rsatilmagan")

        data = {
            "amount": amount,
            "redirect_url": redirect_url,
            "comment": comment,
            "access_token": access_token,
        }

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            transaction_data = response.json()

            if not transaction_data.get("transaction"):
                raise TsPayError("Tranzaksiya ma'lumotlari qaytmadi")

            return transaction_data.get("transaction")

        except requests.RequestException as e:
            raise TsPayError(f"Tranzaksiya yaratishda xato: {str(e)}")
        except ValueError as e:
            raise TsPayError(f"JSON javobini tahlil qilishda xato: {str(e)}")

    def check_transaction(self, user_access_token: str, transaction_id: str) -> Dict:
        """Tranzaksiya holatini tekshirish"""
        if not transaction_id:
            raise TsPayError("Tranzaksiya IDsi ko'rsatilmagan")

        url = f"{self.base_url}/transactions/{transaction_id}/"
        headers = {"Authorization": f"Bearer {user_access_token}"}

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 404:
                raise TsPayError("Bunday IDga ega tranzaksiya topilmadi")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise TsPayError(f"Tranzaksiyani tekshirishda xato: {str(e)}")
        except ValueError as e:
            raise TsPayError(f"JSON javobini tahlil qilishda xato: {str(e)}")


class TsPayError(Exception):
    """TSPay xatolari uchun base exception"""
    pass