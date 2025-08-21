import requests as rq

class ZarinPal:
    def __init__(self, merchant_id, callback_url, sandbox=True):
        self.merchant_id = merchant_id
        self.callback_url = callback_url
        self.sandbox = sandbox
        self.zarinpal_api = "https://sandbox.zarinpal.com/pg/rest/WebGate" if sandbox else "https://api.zarinpal.com/pg/v4/payment"

    def make_payment(self, amount: int, uuid_code: str, description: str) -> str:
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "callback_url": f"{self.callback_url}?uuid={uuid_code}",
            "description": description
        }

        response = rq.post(f"{self.zarinpal_api}/request.json", json=payload)
        res_data = response.json().get("data", {})

        if not res_data.get("authority"):
            return "Failed to connect to the payment gateway."

        authority = res_data["authority"]
        pay_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
        return pay_url

    def verify_payment(self, authority: str, amount: int) -> dict:
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority
        }

        response = rq.post(f"{self.zarinpal_api}/verify.json", json=payload)
        res_data = response.json().get("data", {})

        code = res_data.get("code", 0)
        if code == 100:
            return {"success": True, "ref_id": res_data.get("ref_id"), "message": "Payment successful"}
        elif code == 101:
            return {"success": True, "ref_id": res_data.get("ref_id"), "message": "Payment already verified"}
        else:
            return {"success": False, "ref_id": None, "message": "Payment failed"}

