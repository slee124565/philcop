import calendar

from django.http import HttpResponse
from django.shortcuts import render_to_response

from fundclear.models import FundClearModel
from bankoftaiwan.models import BotExchangeModel, exchange


def default_view(request):
    bot_exchange = BotExchangeModel.get_bot_exchange(exchange.CURRENCY_JPY)
    exchange_data = []
    if bot_exchange:
        bot_list = bot_exchange.get_exchange_list(exchange.FIELD_SELL_ON_DEMAND)
        for t_entry in bot_list:
            exchange_data.append([calendar.timegm((t_entry[0]).timetuple()) * 1000 , t_entry[1]])
    
    #fund_id_list = ['LU0069970746', 'AJSCY3']
    fund_id = 'LU0069970746'
    fund = FundClearModel.get_fund(fund_id)
    fund_value = []
    if fund:
        fund_data_list = fund.get_value_list ()
        for t_entry in fund_data_list:
            fund_value.append([calendar.timegm((t_entry[0]).timetuple()) * 1000 , t_entry[1]])
    
    args = {
            'fund_label' : fund.fund_name,
            'fund_data' : str(fund_value).replace('L', ''),
            'exchange_data' : str(exchange_data).replace('L', ''),
            }
    #return HttpResponse('Default View')
    #return render_to_response('index.html')
    return render_to_response('fund_japan.html', args)