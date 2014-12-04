from django.http import HttpResponse
from datetime import date
from bankoftaiwan2.models_exchange import BotExchangeDataModel, BotExchangeInfoModel
from dateutil.relativedelta import relativedelta
import bankoftaiwan2.models_exchange as bot
from bankoftaiwan.exchange import CURRENCY_USD

def test_get_exchange_list(request):
    t_currency = bot.CURRENCY_CNY
    t_ex = BotExchangeInfoModel.get_bot_exchange(t_currency)
    return HttpResponse(str(t_ex.get_exchange_list()))
    
def test_get_sample_value_list(request):
    t_currency = bot.CURRENCY_JPY
    t_date = date.today() + relativedelta(days=-1)
    t_date_list = [ (t_date+relativedelta(days=-d)) for d in range(365)]
    t_ex = BotExchangeInfoModel.get_bot_exchange(t_currency)
    
    return HttpResponse(str(t_ex.get_sample_value_list(t_date_list)))

def test_get_rate(request):
    t_date = date.today() + relativedelta(days=-1)
    t_end_date = t_date + relativedelta(years=-1)
    t_currency = bot.CURRENCY_JPY
    
    t_ex =BotExchangeInfoModel.get_bot_exchange(t_currency)
    t_content = ''
    while t_date > t_end_date:
        t_content += '{} get rate {}<br/>'.format(str(t_date),t_ex.get_rate(t_date))
        t_date = t_date + relativedelta(days=-1)
    
    return HttpResponse(t_content)

def test_update_from_web(request):
    t_year = date.today().year - 1
    t_currency = bot.CURRENCY_JPY
    if BotExchangeDataModel._update_from_web(t_currency,t_year):
        return HttpResponse('_update_from_web success')
    else:
        return HttpResponse('_update_from_web fail')
        
def test_get_data_dict(request):
    t_year = date.today().year
    t_currency = bot.CURRENCY_JPY
    t_ex = BotExchangeInfoModel.get_by_key_name(t_currency)
    t_keyname = BotExchangeDataModel.compose_key_name(t_currency, t_year)
    t_data = BotExchangeDataModel.get_by_key_name(t_keyname, parent=t_ex)
    if not t_data is None:
        t_dict = t_data._get_data_dict()
        t_content = ''
        for t_entry in t_dict.items():
            t_content += '{}<br/>\n'.format(str(t_entry))
        return HttpResponse(t_content)
    else:
        return HttpResponse('get_by_key_name fail')
    
def test_get_exchange(request):
    test_currency = [bot.CURRENCY_CNY,bot.CURRENCY_USD,bot.CURRENCY_JPY]
    t_content = ''
    for t_currency in test_currency:
        t_ex = BotExchangeInfoModel.get_exchange(t_currency)
        t_content += '{}:<br/>\n{}<br/>\n'.format(t_currency, str(t_ex.data_year_dict))
    
    return HttpResponse(t_content)