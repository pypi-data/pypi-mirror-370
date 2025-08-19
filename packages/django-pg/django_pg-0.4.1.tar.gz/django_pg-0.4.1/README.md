# Django Payment Gateways Package

A pluggable Django package for integrating multiple payment gateways (starting with Paystack and Flutterwave), with an extensible architecture that supports more gateways like Stripe, etc.

---

## ✨ Features

- 🔌 Plug-and-play integration
- 🔐 Paystack support (more gateways coming)
- 📦 Dispatcher pattern for gateway switching
- 🧱 Abstract `BaseOrder` model for customization
- ✅ Built-in Payment Verification View
- 🧠 Smart unique order reference generation
- 🧪 Built-in signal handling for order reference
- 💡 Fully customizable frontend and views

---

## Example Project

A sample Django project demonstrating how to use this package is available here:

👉 [django_pg_test_project](https://github.com/niyimarc/payment_gateway_test)

---

## 📦 Installation

```bash
pip install django-pg
```

## ⚙️ Project Setup
1. **Add the app to INSTALLED_APPS**

```bash
# settings.py
INSTALLED_APPS = [
    ...
    'django_pg',  # Your payment package
]
```

2. **Define required settings in your settings.py**

```bash
# settings.py

# Models used for order
PAYMENT_ORDER_MODEL = 'yourapp.Order'

# It's recomended that you put the secret key 
# in a .env file and load it in your settings

# Paystack keys
PAYSTACK_PUBLIC_KEY = 'your-paystack-public-key'
PAYSTACK_SECRET_KEY = 'your-paystack-secret-key'

# Flutterwave keys
FLUTTERWAVE_PUBLIC_KEY = "your-flutterwave-public-key"
FLUTTERWAVE_SECRET_KEY = "your-flutterwave-secret-key"

# Interswitch keys
INTERSWITCH_MERCHANT_CODE = "your-interswitch-merchant-code"
INTERSWITCH_PAY_ITEM_ID = "your-interswitch-pay-item-id"

```

3. **Built-in Payment Verification View**
django-pg provides a built-in payment_verification view that handles verifying transactions for all the payment gateways out of the box.
#### 🔌 URL Configuration
You can use the built-in view directly in your urls.py:
```bash
from django.urls import path
from django_pg.views import payment_verification  # Import from the package

urlpatterns = [
    path("verify/<int:order_id>/<str:payment_method>/", payment_verification, name="payment_verification"),
]
```

#### 🌐 Redirect Behavior
After verifying a transaction, the view will redirect the user based on settings defined in your settings.py.

Option 1: Use named URL patterns
```bash
# settings.py
DJANGO_PG_SUCCESS_REDIRECT = 'yourapp:track_order'
DJANGO_PG_FAILURE_REDIRECT = 'yourapp:create_order'
```
Option 2: Use custom Python functions (advanced)
You can also pass a function that takes the verification result dictionary and returns a HttpResponseRedirect.
```bash
# settings.py
DJANGO_PG_SUCCESS_REDIRECT = 'yourapp.utils.payment_success_redirect'
DJANGO_PG_FAILURE_REDIRECT = 'yourapp.utils.payment_failure_redirect'
```

If you go with option 2, you will need to add the functions in yourapp/utils.py:
```bash
from django.shortcuts import redirect

def payment_success_redirect(result):
    return redirect('yourapp:track_order', order_reference=result["order_reference"])

def payment_failure_redirect(result):
    return redirect('yourapp:create_order')
```
4. **Extend the BaseOrder abstract model**
In your own app, create your order model by extending gateways.models.BaseOrder:
```bash
# yourapp/models.py
from django.db import models
from django_pg.models import BaseOrder
from django.contrib.auth.models import User

class Order(BaseOrder):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Add your fields here
```

**Note: Users attempting to make a payment via Paystack and Flutterwave must have a valid email address. The Paystack and Flutterwave gateway requires this for transaction initiation. Make sure you enforce email submission when a user register**

### 5. Add JS to Your HTML Template

If you're using multiple payment methods (e.g. Paystack, Flutterwave and Interswitch), make sure your template checks for the selected `payment_method`. If you're only using one payment method, you can pass the preferred payment method in a hidden field when the order is created.

#### ✅ Paystack Integration (HTML Template)
[Check Paystack Documentation](https://paystack.com/docs/payments/accept-payments/)
```bash
{% if payment_method == 'paystack' %}
<script src="https://js.paystack.co/v2/inline.js"></script>
<script type="text/javascript">
    function payWithPaystack() {
        var handler = PaystackPop.setup({
            key: '{{ PAYSTACK_PUBLIC_KEY }}',
            email: '{{ request.user.email }}',
            amount: {{ order.total_price|multiply:100 }},
            currency: "NGN",
            ref: '' + Math.floor((Math.random() * 1000000000) + 1),
            callback: function(response) {
                window.location.href = "{% url 'yourapp:payment_verification' order.id payment_method %}?reference=" + response.reference;
            },
            onClose: function() {
                alert('Payment was not completed.');
            }
        });
        handler.openIframe();
    }

    window.onload = function() {
        payWithPaystack();
    };
</script>
{% endif %}
```

#### ✅ Flutterwave Integration (HTML Template)
[Check Flutterwave Documentation](https://developer.flutterwave.com/docs/inline)
```bash
{% if payment_method == 'flutterwave' %}
<script src="https://checkout.flutterwave.com/v3.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function () {
    FlutterwaveCheckout({
      public_key: "{{ FLUTTERWAVE_PUBLIC_KEY }}",
      tx_ref: "{{ order.order_reference }}",
      amount: {{order.total_price}},
      currency: "NGN",
      payment_options: "card, ussd, banktransfer",
      redirect_url: "{% url 'yourapp:payment_verification' order.id payment_method %}",
      customer: {
        email: "{{ request.user.email }}",
        name: "{{ request.user.get_full_name|default:request.user.username }}"
      },
      customizations: {
        title: "My Store",
        description: "Payment for order {{ order.order_reference }}"
      }
    });
  });
</script>
{% endif %}
```
#### ✅ Interswitch Integration (HTML Template)
[Check Interswitch Documentation](https://docs.interswitchgroup.com/docs/web-checkout)
```bash
{% if payment_method == 'interswitch' %}
<script src="https://newwebpay.qa.interswitchng.com/inline-checkout.js"></script>
<script>
(function() {
    const redirectUrl = "{% url 'yourapp:payment_verification' order.id payment_method %}?reference={{ order.order_reference }}";
    const paymentAmount = {{ order.total_price|floatformat:0 }} * 100;

    function paymentCallback(response) {
        console.log("Interswitch Payment Response:", response);

        if (response?.resp === '00') {
            // Successful payment
            window.location.href = redirectUrl;
        } else {
            alert("Payment was not successful. Please try again.");
        }
    }

    const paymentRequest = {
        merchant_code: "{{ INTERSWITCH_MERCHANT_CODE }}",
        pay_item_id: "{{ INTERSWITCH_PAY_ITEM_ID }}",
        txn_ref: "{{ order.order_reference }}",
        site_redirect_url: redirectUrl,
        amount: paymentAmount,
        currency: 566,
        cust_email: "{{ request.user.email }}",
        cust_name: "{{ request.user.get_full_name|default:request.user.username }}",
        onComplete: paymentCallback,
        mode: "TEST"
    };

    window.webpayCheckout(paymentRequest);
})();
</script>
{% endif %}
```
## 🔁 Signals (Auto Order Reference)

You don’t need to register anything. The gateways app automatically registers a pre_save signal that generates a unique order_reference.
```bash
# gateways/signals.py
@receiver(pre_save, sender=Order)
def set_order_reference(sender, instance, **kwargs):
    if not instance.order_reference:
        instance.order_reference = generate_unique_order_reference()
```

## 🧠 Gateway Dispatcher (Behind the scenes)

The following function routes the verification based on the selected payment method:
```bash
# gateways/payment.py
def verify_payment(order_id, reference, user, payment_method):
    if payment_method == 'paystack':
        return verify_paystack_payment(order_id, reference, user)
    # elif payment_method == 'flutterwave': ...

```
You don't need to modify this — it's extendable internally.

## 🛡 License

This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome! If you find a bug or have a feature request, feel free to [open an issue](https://github.com/niyimarc/payment_gateways/issues).

See full [Changelog](https://github.com/niyimarc/payment_gateway/blob/master/CHANGELOG.md).