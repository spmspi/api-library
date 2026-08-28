from decimal import Decimal

from borrowing.models import Borrowing
from payment.models import Payment


def calculate_amount(borrowing: Borrowing, payment_type: str) -> Decimal:
    if payment_type == Payment.TypeEnum.FINE:
        overdue_days = (borrowing.actual_return_date - borrowing.expected_return_date).days
        overdue_days = max(overdue_days, 1)
        return Decimal(overdue_days) * borrowing.book.daily_fee * Decimal("2.0")

    return_date = borrowing.expected_return_date or borrowing.actual_return_date
    date = (return_date - borrowing.expected_return_date).days
    days = max(date, 1)
    return Decimal(days) * borrowing.book.daily_fee


def create_payment_for_borrowing(borrowing: Borrowing,
    payment_type: str,
    session_url: str,
    session_id: str
) -> Payment:
    money_to_pay = calculate_amount(borrowing, payment_type)
    return Payment.objects.create(
        status=Payment.StatusEnum.PENDING,
        type=payment_type,
        borrowing=borrowing,
        session_url=session_url,
        session_id=session_id,
        money_to_pay=money_to_pay,
    )
