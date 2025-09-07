import paypalrestsdk
from typing import Dict


paypalrestsdk.configure({
    "mode": "sandbox",
    "client_id": "",  # filled from env in create_payment
    "client_secret": "",
})


def create_payment(total: str, description: str, return_url: str, cancel_url: str, client_id: str, client_secret: str) -> Dict:
    paypalrestsdk.configure({"client_id": client_id, "client_secret": client_secret})
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {"return_url": return_url, "cancel_url": cancel_url},
        "transactions": [{"amount": {"total": total, "currency": "USD"}, "description": description}],
    })
    if payment.create():
        return {"approval_url": payment.links[1].href}
    else:
        raise RuntimeError(payment.error)
