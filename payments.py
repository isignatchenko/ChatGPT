from aiogram import types

from aiogram.utils.json import json

from config import exchange_rate_coefficient


def make_prices(price_to_use):
    prices_to_send = [
        types.LabeledPrice(label='Покупка токенов', amount=(price_to_use * 100))
    ]
    return prices_to_send


def exchange_rate_converter(rub):
    tokens = rub * exchange_rate_coefficient
    return tokens


def make_providers_data(price_to_use):
    data = {
        "receipt": {
            "items": [{
                "description": "Покупка токенов для использования в приложении генерации ответов на основе "
                               "искусственного интеллекта",
                "quantity": 1.00,
                "amount": {
                    "value": f'{price_to_use}.00',
                    "currency": "RUB"
                },
                "vat_code": "1"
            }]
        }
    }
    return json.dumps(data)


shipping_options = [
    types.ShippingOption(id='instant', title='instant').add(types.LabeledPrice('instant', 1000)),
    types.ShippingOption(id='pickup', title='pickup').add(types.LabeledPrice('instant', 300))
]
