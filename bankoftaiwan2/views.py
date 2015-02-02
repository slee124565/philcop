from django.http import HttpResponse
from datetime import date
import models_exchange as bot_ex

def get_exchange_view(request,p_currency=bot_ex.CURRENCY_USD,p_date=date.today()):
    t_ex = bot_ex.BotExchangeInfoModel.get_bot_exchange(p_currency)
    t_rate = t_ex.get_rate(p_date)
    return HttpResponse(t_rate)

