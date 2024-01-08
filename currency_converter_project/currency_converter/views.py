import requests
from decimal import Decimal

from django.shortcuts import render
from django.http import (JsonResponse,
                         HttpRequest)
from django.views.generic import ListView

from .forms import CurrencyConversionForm
from .models import ConversionResult
from typing import Dict
from typing import Any
from typing import List
from typing import Optional

PB_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5'


def index(request):
    return render(request, 'index.html')


def get_exchange_rates() -> List[Dict[str, Any]]:
    response = requests.get(PB_API_URL)
    response.raise_for_status()
    print(response.json())
    return response.json()


def find_currency_rate(exchange_rates: List[Dict[str, Any]],
                       currency_code: str) -> Dict[str, Any]:
    try:
        return next(rate for rate in exchange_rates
                    if rate['ccy'] == currency_code)
    except StopIteration:
        raise ValueError(f"Currency rate not found for {currency_code}")


def convert_to_uah(amount: Decimal, base_currency_rate: Decimal) -> Decimal:
    return amount * base_currency_rate


def convert_from_uah(amount: Decimal, sale_rate: Decimal) -> Decimal:
    return amount / sale_rate


def convert_currency(request: HttpRequest) -> JsonResponse:
    result: Optional[Any] = None
    if request.method == 'POST':
        form = CurrencyConversionForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            from_currency = form.cleaned_data['from_currency']
            to_currency = form.cleaned_data['to_currency']

            try:
                exchange_rates = get_exchange_rates()

                if from_currency == 'UAH':
                    from_currency_rate = find_currency_rate(exchange_rates,
                                                            to_currency)
                else:
                    from_currency_rate = find_currency_rate(exchange_rates,
                                                            from_currency)

                if to_currency == 'UAH':
                    to_currency_rate = find_currency_rate(exchange_rates,
                                                          from_currency)
                else:
                    to_currency_rate = find_currency_rate(exchange_rates,
                                                          to_currency)

            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': f'Error fetching exchange rates: '
                                              f'{str(e)}'})
            except ValueError as e:
                return JsonResponse({'error': str(e)})

            amount = Decimal(amount)

            if to_currency == 'UAH':
                conversion_rate = Decimal(to_currency_rate['sale'])
                converted_amount = amount * conversion_rate
            elif from_currency == 'UAH':
                sale_rate = Decimal(from_currency_rate['sale'])
                converted_amount = amount / sale_rate
            elif from_currency == 'UAH' and to_currency == 'UAH':
                converted_amount = amount

            else:
                conversion_rate = (Decimal(to_currency_rate['buy']) /
                                   Decimal(from_currency_rate['sale']))
                converted_amount = amount * conversion_rate

            result = ConversionResult.objects.create(
                from_currency=from_currency,
                to_currency=to_currency,
                amount=amount,
                converted_amount=converted_amount
            )

            return render(request,
                          'currency_converter.html',
                          {'form': form, 'result': result})

        else:
            return JsonResponse({'error': 'Invalid form data',
                                 'errors': form.errors})
    else:
        form = CurrencyConversionForm()

    return render(request,
                  'currency_converter.html',
                  {'form': form, 'result': result})


class CurrencyListView(ListView):
    model = ConversionResult
    template_name = 'all_operations.html'
    context_object_name = 'all_operations'

