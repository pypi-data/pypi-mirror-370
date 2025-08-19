import requests
from django.utils import timezone
from django.conf import settings
from ..utils import get_model, validate_user_for_payment, validate_payment_amount

def verify_paystack_payment(order_id, transaction_id, user):
    validation = validate_user_for_payment(user)
    if not validation["success"]:
        return validation
    # Get configured Order and Cart models
    Order = get_model('PAYMENT_ORDER_MODEL')

    # Retrieve order before constructing the URL
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return {
            "success": False,
            "message": "Order not found."
        }

    # Verify the payment with Paystack
    url = f"https://api.paystack.co/transaction/verify/{transaction_id}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        response = requests.get(url, headers=headers)
        result = response.json()
    except Exception as e:
        # print(f"[Paystack] Exception verifying transaction {transaction_id}: {e}")
        return {
            "success": False,
            "message": "Error verifying payment"
        }

    # print(f"[Paystack] Verification result for tx {transaction_id}: {result}")

    # If Paystack confirms a successful transaction
    if result.get("status") and result["data"]["status"] == "success":
        paid_amount_kobo = int(result["data"]["amount"])  # in kobo
        paid_amount = paid_amount_kobo / 100  # convert to Naira
        amount_validation = validate_payment_amount(order, paid_amount)

        if not amount_validation["success"]:
            return amount_validation
        
        order.payment_made = True
        order.order_placed = True
        order.status = "Order Placed"
        order.payment_method = 'paystack'
        order.payment_date = timezone.now()
        order.save()

        return {
            "success": True,
            "order_reference": order.order_reference
        }

    # If verification failed
    # print(f"[Paystack] Payment verification failed for tx {transaction_id}")
    # If verification failed
    return {
        "success": False,
        "message": "Payment verification failed"
    }
