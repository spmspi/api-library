from django.db import models


class Payment(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"

    class TypeEnum(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"

    status = models.CharField(
        choices=StatusEnum.choices, max_length=10, default=TypeEnum.PENDING
    )
    type = models.CharField(choices=TypeEnum.choices, max_length=10)
    borrowing = models.ForeignKey(
        "borrowing.Borrowing", on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(max_length=500, blank=True, null=True)
    session_id = models.CharField(max_length=500, blank=True, null=True)
    money = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.type} ({self.status}) - {self.money} USD"
