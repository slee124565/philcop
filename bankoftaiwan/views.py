from django.http import HttpResponse
from django.shortcuts import render_to_response

from datetime import date
from dateutil.relativedelta import relativedelta

from models import BotExchangeModel

import logging
import calendar
from bankoftaiwan import exchange

#'http://rate.bot.com.tw/Pages/UIP004/Download0042.ashx?lang=zh-TW&fileType=1&afterOrNot=1&whom=JPY&date1=20090722&date2=20140722'
URL_EXCHANGE_TEMPLATE = 'http://rate.bot.com.tw/Pages/UIP004/Download0042.ashx?lang=zh-TW&fileType=1&afterOrNot=1&whom={currency_type}&date1={date1}&date2={date2}'

def exchange_jpy_view(request):
    
    currency_type = 'JPY'
    
    end_date = date.today() - relativedelta(days=+1)
    begin_date = end_date - relativedelta(years=+1)
    url = URL_EXCHANGE_TEMPLATE.format(currency_type=currency_type,
                                       date1=begin_date.strftime("%Y%m%d"),
                                       date2=end_date.strftime("%Y%m%d"))
    webCsv = BotExchangeModel.get_or_insert_webcontent(currency_type, url, date.today())
    
    if webCsv == None:
        return HttpResponse('Fail to fetch Web CSV content!!!')

    if webCsv.currency_name == None:
        webCsv.currency_name = currency_type
        webCsv.put()
        logging.debug('currency name not exist, set as ' + currency_type)

    exchange_list = webCsv.get_exchange_list(exchange.FIELD_SELL_ON_DEMAND)
    dataset = []
    for t_entry in exchange_list:
        dataset.append([calendar.timegm((t_entry[0]).timetuple()) * 1000 , t_entry[1]])

    args = {
            'page_title' : 'JPY Sell On Demand Exchange',
            'dataset' : str(dataset).replace('L', ''),
            'data_list' : exchange_list,
            }
    return render_to_response('bot_axes_time_view.html',args)
