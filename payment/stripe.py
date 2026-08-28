import stripe
from django.shortcuts import redirect

from app import settings
from payment.services import calculate_amount

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(borrowing, money, success_url):
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': borrowing.book.title,
                    'metadata': {'borrowing_id': borrowing.id},
                },
                'unit_amount': int(money * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
    )

    return session