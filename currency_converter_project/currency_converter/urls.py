from django.urls import path
from .views import convert_currency, index, CurrencyListView

urlpatterns = [
    path('api/convert_currency/', convert_currency, name='convert_currency'),
    path('', index, name='index'),
    path('all_operations', CurrencyListView.as_view(), name='all_operations'),
]

