from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import resolve_redirect
from django.http import JsonResponse
from django.views import View
import json

SUCCESS_REDIRECT = getattr(settings, 'DJANGO_PG_SUCCESS_REDIRECT', None)
FAILURE_REDIRECT = getattr(settings, 'DJANGO_PG_FAILURE_REDIRECT', None)

@login_required
def payment_verification(request, order_id, payment_method):
    if payment_method == "paystack":
        transaction_id = request.GET.get('reference')
    elif payment_method == "flutterwave":
        transaction_id = request.GET.get('transaction_id')
    elif payment_method == "interswitch":
        transaction_id = request.GET.get('reference')
    else:
        messages.error(request, "Unsupported payment method")
        return redirect(resolve_redirect(FAILURE_REDIRECT))

    from .payment import verify_payment
    result = verify_payment(order_id, transaction_id, request.user, payment_method)

    if result.get("success"):
        return resolve_redirect(SUCCESS_REDIRECT, result)
    else:
        messages.error(request, result.get("message", "Payment verification failed"))
        return redirect(resolve_redirect(FAILURE_REDIRECT, result))
    
class PaymentVerificationJSONView(View):
    def post(self, request, order_id, payment_method):
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            body = {}

        if payment_method == "paystack":
            transaction_id = body.get("reference")
        elif payment_method == "flutterwave":
            transaction_id = body.get("reference") or body.get("transaction_id")
        elif payment_method == "interswitch":
            transaction_id = body.get("reference")
        else:
            return JsonResponse(
                {"success": False, "message": "Unsupported payment method"},
                status=400
            )

        from .payment import verify_payment
        result = verify_payment(order_id, transaction_id, request.user, payment_method)

        if result.get("success"):
            return JsonResponse(
                {"success": True, "message": "Payment verified", "data": result}
            )
        else:
            return JsonResponse(
                {"success": False, "message": result.get("message", "Payment verification failed")},
                status=400
            )