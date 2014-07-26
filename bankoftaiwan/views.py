from django.http import HttpResponse
from django.shortcuts import render_to_response

from models import BotExchangeModel

import logging
import calendar
from bankoftaiwan import exchange

#'http://rate.bot.com.tw/Pages/UIP004/Download0042.ashx?lang=zh-TW&fileType=1&afterOrNot=1&whom=JPY&date1=20090722&date2=20140722'

def exchange_jpy_view(request):
    
    currency_type = 'JPY'
    
    webCsv = BotExchangeModel.get_bot_exchange(p_currency_type=currency_type)
    
    if webCsv == None:
        return HttpResponse('Fail to fetch Web CSV content!!!')

    if webCsv.currency_name == None:
        webCsv.currency_name = currency_type
        webCsv.put()
        logging.debug('currency name not exist, set as ' + currency_type)

    #exchange_list = webCsv.get_exchange_list(exchange.FIELD_SELL_ON_DEMAND)
    #exchange_list = webCsv.get_discrete_exchange_list(exchange.FIELD_SELL_ON_DEMAND,exchange.MONTH_DAY_BEGIN)
    exchange_list = webCsv.get_discrete_exchange_list(exchange.FIELD_SELL_ON_DEMAND,exchange.MONTH_DAY_END)
    #exchange_list = webCsv.get_discrete_exchange_list(exchange.FIELD_SELL_ON_DEMAND,exchange.MONTH_DAY_MIDDLE)
    #exchange_list = webCsv.get_discrete_exchange_list(exchange.FIELD_SELL_ON_DEMAND,exchange.MONTH_DAY_TODAY)
    dataset = []
    for t_entry in exchange_list:
        dataset.append([calendar.timegm((t_entry[0]).timetuple()) * 1000 , t_entry[1]])

    args = {
            'page_title' : 'JPY Sell On Demand Exchange',
            'dataset' : str(dataset).replace('L', ''),
            'data_list' : exchange_list,
            }
    return render_to_response('bot_axes_time_view.html',args)
