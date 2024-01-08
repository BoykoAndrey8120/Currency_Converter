from django import forms

CURRENCY_CHOICES = [
    ('EUR', 'EUR'),
    ('USD', 'USD'),
    ('UAH', 'UAH'),
]


class CurrencyConversionForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0)
    from_currency = forms.ChoiceField(label='From Currency',
                                      choices=CURRENCY_CHOICES)
    to_currency = forms.ChoiceField(label='To Currency',
                                    choices=CURRENCY_CHOICES)
