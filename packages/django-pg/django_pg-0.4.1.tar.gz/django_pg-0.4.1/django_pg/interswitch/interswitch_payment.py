import requests
from django.utils import timezone
from django.conf import settings
from ..utils import get_model, validate_user_for_payment, validate_payment_amount

def verify_interswitch_payment(order_id, transaction_id, user):
    validation = validate_user_for_payment(user)
    if not validation["success"]:
        return validation

    Order = get_model('PAYMENT_ORDER_MODEL')

    # Retrieve order before constructing the URL
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return {
            "success": False,
            "message": "Order not found."
        }

    amount = int(float(order.total_price) * 100)

    base_url = "https://qa.interswitchng.com/collections/api/v1/gettransaction.json"
    url = f"{base_url}?merchantcode={settings.INTERSWITCH_MERCHANT_CODE}&transactionreference={transaction_id}&amount={amount}"
    print(url)
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        result = response.json()

        # If Interswitch confirms a successful transaction
        if result.get("ResponseCode") == "00":
            paid_amount_kobo = int(result["Amount"])  # in kobo
            paid_amount = paid_amount_kobo / 100  # convert to Naira
            amount_validation = validate_payment_amount(order, paid_amount)

            if not amount_validation["success"]:
                return amount_validation
            
            order.payment_made = True
            order.order_placed = True
            order.status = "Order Placed"
            order.payment_method = 'interswitch'
            order.payment_date = timezone.now()
            order.save()

            return {
                "success": True,
                "order_reference": order.order_reference
            }

        # Add more detail from the Flutterwave response if available
        error_message = result.get("message", "Unknown error during payment verification.")

        return {
            "success": False,
            "message": f"Payment verification failed: {error_message}"
        }

    except requests.RequestException as e:
        print("❌ Request error while verifying Flutterwave payment:", str(e))
        return {
            "success": False,
            "message": "Error connecting to Flutterwave for verification."
        }
