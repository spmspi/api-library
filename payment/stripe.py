import stripe

from app import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(borrowing, money, success_url, cancel_url):
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                        "metadata": {"borrowing_id": borrowing.id},
                    },
                    "unit_amount": int(money * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return session
