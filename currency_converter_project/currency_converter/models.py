from django.db import models


class ConversionResult(models.Model):
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    converted_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (f"{self.amount} {self.from_currency} to "
                f"{self.converted_amount} {self.to_currency}")

