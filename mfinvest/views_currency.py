from django.shortcuts import render_to_response
from django.http import HttpResponse

from datetime import date
from dateutil.relativedelta import relativedelta

from bankoftaiwan.models import BotExchangeModel
from utils import util_date
import bankoftaiwan.exchange as bot
import calendar, logging
 
def tw_exchange_changing_view(request):
    target_currency = [bot.CURRENCY_CNY, bot.CURRENCY_USD, bot.CURRENCY_JPY]
    #target_currency = [bot.CURRENCY_CNY]
    
    #date_list = util_date.get_sample_date_list_2(p_date_begin=(date.today()+relativedelta(years=-1)), \
    #                                             p_date_end=date.today(), \
    #                                             p_inc_everyday_of_last_month=True)
    date_list = util_date.get_sample_date_list()
    tw_exchanges = {}
    for t_currency in target_currency:
        #logging.debug('currency: ' + str(t_currency))
        t_exchange = BotExchangeModel.get_bot_exchange(p_currency_type=t_currency)
        #tw_exchanges[t_currency] =  t_exchange.get_exchange_list(bot.FIELD_SELL_CASH)
        tw_exchanges[t_currency] =  t_exchange.get_sample_value_list(date_list,bot.FIELD_SELL_CASH)
        #logging.debug(str(tw_exchanges[t_currency]))
        prev_rate = tw_exchanges[t_currency][0][1]
        for ndx, t_entry in enumerate(tw_exchanges[t_currency]):
            this_rate = t_entry[1]
            if t_entry[1] == 0:
                t_entry[1] = 0
            else:
                t_entry[1] = 100*(t_entry[1]-prev_rate)/t_entry[1]
            prev_rate = this_rate
    
    #logging.debug(str(tw_exchanges))
    plot_data = ''
    for t_currency, t_list in tw_exchanges.items():
        #logging.debug(str(tw_exchanges[t_currency]))
        for t_entry in t_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
        plot_data += '{data: ' + str(t_list).replace('L', '') + \
                            ', label: "' + t_currency + '", lines: {show: true}},\n'
        
    plot = {
            'data': plot_data 
            }

    args = {
            'tpl_img_header' : str(target_currency) + ' Exchange Rate Changing with TWD' ,
            'plot' : plot,
            'tpl_section_title' : 'Developed by lee.shiueh@gmail.com',
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
