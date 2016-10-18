import calendar
import logging

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.conf import settings

from fundclear.models import FundClearModel
import bankoftaiwan2.models_exchange as bot_ex
import os
from django.conf import settings

def home(request):
    return HttpResponseRedirect('/mf/fc/')
    #return render_to_response('dashboard.tpl.html')

def django_settings_view(request):
    t_content = ''
    for t_key in dir(settings):
        t_content += '{}:{}\n'.format(t_key,getattr(settings, t_key))
    response = HttpResponse(content_type='text/plain')
    response.content = t_content
    return response
    
def os_environment_view(request):
    t_content = ''
    for t_key in os.environ:
        t_content += '{}:{}\n'.format(t_key,str(os.environ[t_key]))
    response = HttpResponse(content_type='text/plain')
    response.content = t_content
    return response
    
def test_l10n(request):
    return render_to_response('dashboard.tpl.html')
    
def print_config(request):
    t_result = ''
    for name in dir(settings):
        t_result += name + ':' + str(getattr(settings, name)) + '<br/>'
    return HttpResponse(t_result)
    
def default_view(request):
    bot_exchange = bot_ex.BotExchangeInfoModel.get_bot_exchange(bot_ex.CURRENCY_JPY)
    exchange_data = []
    if bot_exchange:
        bot_list = bot_exchange.get_exchange_list(bot_ex.CSV_COL_SELL_ONDEMAND)
        for t_entry in bot_list:
            exchange_data.append([calendar.timegm((t_entry[0]).timetuple()) * 1000 , t_entry[1]])
    
    fund_id_list = ['LU0069970746', 'AJSCY3']
    #fund_id = 'LU0069970746'
    fund_data_set = []
    for fund_id in fund_id_list:
        fund = FundClearModel.get_fund(fund_id)
        fund_value = []
        if fund:
            fund_data_list = fund.get_value_list()
            for t_entry in fund_data_list:
                fund_value.append([calendar.timegm((t_entry[0]).timetuple()) * 1000 , t_entry[1]])
            fund_data_set.append({
                                   'id' : fund_id,
                                   'value_list' : fund_value,
                                   })
    data_str = ''
    for fund_data in fund_data_set:
        data_str += '{ data: \n' + str(fund_data['value_list']).replace('L', '') + \
                    '\n,label: "' + fund_data['id'] + ' = 00000.0000" },\n'
    data_str += '{ data: \n' + str(exchange_data).replace('L', '') + \
                    '\n,label: "JPY/TWN = 0.0000", yaxis: 2 }' 
    plot = {'data': data_str}
    args = {
            #'fund_label' : fund_id,
            ##'fund_data' : str(fund_value).replace('L', ''),
            #'exchange_data' : str(exchange_data).replace('L', ''),
            'plot' : plot,
            }
    #return HttpResponse('Default View')
    #return render_to_response('index.html')
    return render_to_response('fund_japan.html', args)