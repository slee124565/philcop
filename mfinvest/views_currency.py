from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from datetime import date
from dateutil.relativedelta import relativedelta

import bankoftaiwan2.models_exchange as bot_ex
from utils import util_date
import calendar, logging, collections
 
def tw_exchange_changing_view(request):
    target_currency = [bot_ex.CURRENCY_CNY, bot_ex.CURRENCY_USD, bot_ex.CURRENCY_JPY]
    
    content_head_list = ['Date'] + target_currency
    content_rows = {}

    t_show_daily = True
    if t_show_daily:
        date_list = util_date.get_sample_date_list_2(p_date_begin=(date.today()+relativedelta(years=-1)), \
                                                     p_date_end=date.today(), \
                                                     p_inc_everyday_of_last_month=True)
    else:
        date_list = util_date.get_sample_date_list()
    for t_date in date_list:
        content_rows[t_date.strftime('%Y%m%d')] = (t_date.strftime('%Y/%m/%d'),)
    
    tw_exchanges = {}
    for t_currency in target_currency:
        #logging.debug('currency: ' + str(t_currency))
        t_exchange = bot_ex.BotExchangeInfoModel.get_bot_exchange(t_currency)
        tw_exchanges[t_currency] =  t_exchange.get_sample_value_list(date_list,bot_ex.CSV_COL_SELL_CASH)
        #logging.debug(str(tw_exchanges[t_currency]))
        prev_rate = tw_exchanges[t_currency][0][1]
        for ndx, t_entry in enumerate(tw_exchanges[t_currency]):
            content_rows[t_entry[0].strftime('%Y%m%d')] += ('{:.4f}'.format(t_entry[1]),)
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
    
    content_rows = collections.OrderedDict(sorted(content_rows.items()))
    tbl_content = {
                   'heads': content_head_list,
                   'rows': content_rows.values(),
                   }

    args = {
            'tpl_img_header' : _('HEADER_EX_RATE_CHANGE_WITH_TWD'), #str(target_currency) + ' Exchange Rate Changing with TWD' ,
            'plot' : plot,
            'tpl_section_title' : _('TITLE_BOT_CURRENCY_CASH_SELL'), 
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
