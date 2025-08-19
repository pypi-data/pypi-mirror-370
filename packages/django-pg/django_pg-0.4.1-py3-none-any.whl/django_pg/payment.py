from django_pg.paystack.paystack_payment import verify_paystack_payment
from django_pg.flutterwave.flutterwave_payment import verify_flutterwave_payment
from django_pg.interswitch.interswitch_payment import verify_interswitch_payment

def verify_payment(order_id, transaction_id, user, payment_method):
    # Dispatches the payment verification to the correct gateway handler..
    if payment_method == 'paystack':
        return verify_paystack_payment(order_id, transaction_id, user)
    elif payment_method == 'flutterwave':
        return verify_flutterwave_payment(order_id, transaction_id, user)
    elif payment_method == 'interswitch':
        return verify_interswitch_payment(order_id, transaction_id, user)
    else:
        return {"success": False, "message": "Unsupported payment method"}
