from django.http import HttpResponse
from models_gold import BotGoldDataModel, BotGoldInfoModel
import models_exchange as bot_ex
from datetime import date
from dateutil.relativedelta import relativedelta

#test_4
def test_get_value(request):
    end_date = date.today() + relativedelta(years=-1)
    t_date = date.today()
    t_content = ''
    t_currency = bot_ex.CURRENCY_TWD
    t_gold = BotGoldInfoModel.get_bot_gold(t_currency)
    while t_date > end_date:
        t_date = t_date + relativedelta(days=-1)
        t_content += '{} get value {}<br/>'.format(t_date,t_gold.get_value(t_date))
    
    return HttpResponse(t_content)

#test_3
def test_get_price_list(request):
    p_currency = bot_ex.CURRENCY_TWD # bot_ex.CURRENCY_USD
    t_gold = BotGoldInfoModel.get_bot_gold(p_currency)
    t_content = ''
    for t_entry in t_gold.get_price_list():
        t_content += '{}<br/>'.format(t_entry)
        
    return HttpResponse(t_content)
    
#test_2
def test_get_data_dict(request):
    p_currency = bot_ex.CURRENCY_TWD
    this_year = date.today().year
    this_year = 2008
    t_gold = BotGoldInfoModel.get_bot_gold(p_currency)
    t_gold._load_year_data(this_year)
    t_content = '{}'.format(t_gold.data_year_dict[str(this_year)])
    return HttpResponse(t_content)
    
#test_1
def test_update_from_web(request):
    p_currency = bot_ex.CURRENCY_TWD
    this_year = date.today().year-1
    
    t_content = ''
    if BotGoldDataModel._update_from_web(p_currency, this_year):
        t_content += '{} _update_from_web success<br/>'.format(p_currency)
    else:
        t_content += '{} _update_from_web fail<br/>'.format(p_currency)
    
    p_currency = bot_ex.CURRENCY_USD
    if BotGoldDataModel._update_from_web(p_currency, this_year):
        t_content += '{} _update_from_web success<br/>'.format(p_currency)
    else:
        t_content += '{} _update_from_web fail<br/>'.format(p_currency)
    
    return HttpResponse(t_content)