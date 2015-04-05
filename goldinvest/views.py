from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from goldreport import GoldReport
from models import GoldInvestModel
import bankoftaiwan2.models_exchange as bot_ex
import bankoftaiwan2.models_gold as bot_gold
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils.util_bollingerbands import get_bollingerbands
from django.utils.translation import ugettext as _

import logging, calendar, collections

def current_price_view(request,p_currency=bot_ex.CURRENCY_TWD,p_field=bot_gold.CSV_COL_SELL_ONDEMAND):
    t_price = bot_gold.get_current_price(p_currency,p_field)
    if t_price is None:
        t_gold = bot_gold.BotGoldInfoModel.get_bot_gold(p_currency)
        t_price = t_gold.get_value(date.today(),p_field)
    return HttpResponse(t_price)
    
def price_view(request, p_currency=bot_ex.CURRENCY_TWD,p_view_months=3):
    MONTH_TO_VIEW = int(p_view_months)
    
    t_content_heads = ['Date', 
                       bot_gold.CSV_COL_SELL_ONDEMAND, 
                       bot_gold.CSV_COL_BUY_ONDEMAND,
                       'Diff']
    t_content_rows = {}
    
    if not p_currency in [bot_ex.CURRENCY_TWD, bot_ex.CURRENCY_USD]:
        return HttpResponse('Param p_currency Error!')
    
    t_plot_data = ''
    t_gold = bot_gold.BotGoldInfoModel.get_bot_gold(p_currency)
    '''
    t_ex = None
    if t_currency == bot_ex.CURRENCY_USD:
        t_ex = bot_ex.BotExchangeInfoModel.get_bot_exchange(t_currency)
    '''
    t_date_after = date.today() + relativedelta(months=-MONTH_TO_VIEW)
    t_price_list = t_gold.get_price_list(p_csv_field=bot_gold.CSV_COL_SELL_ONDEMAND)
    t_price_list_2 = t_gold.get_price_list(p_csv_field=bot_gold.CSV_COL_BUY_ONDEMAND)
    t_diff_list = []
    t_count = 0
    for t_entry in zip(t_price_list,t_price_list_2)[::-1]:
        if t_entry[0][0] >= t_date_after:
            t_diff_list.append([t_entry[0][0],100*(t_entry[0][1]-t_entry[1][1])/t_entry[0][1]])
            t_count += 1
        else:
            break
    logging.debug('t_diff_list: \n{}'.format(str(t_diff_list)))
    logging.debug('t_price_list[{}]: {}'.format(t_count,str(t_price_list[t_count])))
    t_price_list = t_price_list[-t_count:]
    t_price_list_2 = t_price_list_2[-t_count:]
    
    for t_entry in t_price_list:
        '''
        if t_currency == bot_ex.CURRENCY_USD:
            if t_ex.get_rate(t_entry[0]) == 0.0:
                return HttpResponse(t_entry[0])
            t_entry[1] = (t_ex.get_rate(t_entry[0])*t_entry[1])/oz_over_gram
        '''
        t_key = t_entry[0].strftime('%Y%m%d')
        if t_key in t_content_rows.keys():
            t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2f}'.format(t_entry[1]),)
        else:
            t_content_rows[t_entry[0].strftime("%Y%m%d")] = (t_entry[0].strftime("%Y/%m/%d"), t_entry[1],)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
    
    for t_entry in t_price_list_2:
        t_key = t_entry[0].strftime('%Y%m%d')
        if t_key in t_content_rows.keys():
            t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2f}'.format(t_entry[1]),)
        else:
            t_content_rows[t_entry[0].strftime("%Y%m%d")] = (t_entry[0].strftime("%Y/%m/%d"), t_entry[1],)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000

    for t_entry in t_diff_list:
        t_key = t_entry[0].strftime('%Y%m%d')
        if t_key in t_content_rows.keys():
            t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2f}%'.format(t_entry[1]),)
        else:
            t_content_rows[t_entry[0].strftime("%Y%m%d")] = (t_entry[0].strftime("%Y/%m/%d"), t_entry[1],)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000

    t_plot_data += '{data: ' + str(t_price_list).replace('L', '') + \
                    ', label: "Price ' + bot_gold.CSV_COL_SELL_ONDEMAND + '", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(t_price_list_2).replace('L', '') + \
                    ', label: "Price ' + bot_gold.CSV_COL_BUY_ONDEMAND + '", lines: {show: true}, yaxis: 4},' 
                                
    plot = {
            'data': t_plot_data
            }
    
    t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
    tbl_content = {
                   'heads': t_content_heads,
                   'rows': reversed(t_content_rows.values()),
                   }

    args = {
            'tpl_img_header' : _('Gold Price View') + ' ;Currency:{}'.format(p_currency),
            'plot' : plot,
            'tpl_section_title' : _('Details'),
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
    
def usd_twd_price_view(request,p_currency=bot_ex.CURRENCY_TWD):
    MONTH_TO_VIEW = 12
    oz_over_gram = 28.3495231
    
    t_content_heads = ['Date']
    t_content_rows = {}
    
    if p_currency in [bot_ex.CURRENCY_TWD, bot_ex.CURRENCY_USD]:
        currency_list = [p_currency]
        t_content_heads.append(p_currency)
    else:
        currency_list = [bot_ex.CURRENCY_TWD, bot_ex.CURRENCY_USD]
        t_content_heads += [bot_ex.CURRENCY_TWD, bot_ex.CURRENCY_USD]
    
    t_plot_data = ''
    for t_currency in currency_list:
        t_gold = bot_gold.BotGoldInfoModel.get_bot_gold(t_currency)
        '''
        t_ex = None
        if t_currency == bot_ex.CURRENCY_USD:
            t_ex = bot_ex.BotExchangeInfoModel.get_bot_exchange(t_currency)
        '''
        t_date_after = date.today() + relativedelta(months=-MONTH_TO_VIEW)
        t_price_list = []
        while t_date_after <= date.today():
            t_price_list.append([t_date_after,t_gold.get_value(t_date_after)])
            t_date_after += relativedelta(days=1)
        
        logging.debug('{}'.format(str(t_price_list)))
        for t_entry in t_price_list:
            '''
            if t_currency == bot_ex.CURRENCY_USD:
                if t_ex.get_rate(t_entry[0]) == 0.0:
                    return HttpResponse(t_entry[0])
                t_entry[1] = (t_ex.get_rate(t_entry[0])*t_entry[1])/oz_over_gram
            '''
            t_key = t_entry[0].strftime('%Y%m%d')
            if t_key in t_content_rows.keys():
                t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2f}'.format(t_entry[1]),)
            else:
                t_content_rows[t_entry[0].strftime("%Y%m%d")] = (t_entry[0].strftime("%Y/%m/%d"), t_entry[1],)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
        
        t_plot_data += '{data: ' + str(t_price_list).replace('L', '') + \
                                ', label: "Price ' + t_currency + '", lines: {show: true}, yaxis: 4},'
                                
    plot = {
            'data': t_plot_data
            }
    
    t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
    tbl_content = {
                   'heads': t_content_heads,
                   'rows': t_content_rows.values(),
                   }

    args = {
            'tpl_img_header' : _('Gold Price View') + ' ;Currency:{}'.format(p_currency),
            'plot' : plot,
            'tpl_section_title' : _('Details'),
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
    
BB_VIEW_DAILY = 'daily'
BB_VIEW_WEEKLY = 'weekly'    
def daily_bb_view(request,p_currency=bot_ex.CURRENCY_TWD,p_timeframe=10,p_sdw=100):
    return _bb_view(BB_VIEW_DAILY, p_currency, p_timeframe, p_sdw)
    
def _bb_view(p_bb_type,p_currency=bot_ex.CURRENCY_TWD,p_timeframe=None,p_sdw=None):
    func = '{} {}'.format(__name__,'_bb_view')

    if not p_currency in [bot_ex.CURRENCY_TWD, bot_ex.CURRENCY_USD]:
        logging.warning('{}: PARAM ERR p_currency {}'.format(func,p_currency))
        return HttpResponse('PARAM ERR p_currency {}'.format(p_currency))
    
    t_gold = bot_gold.BotGoldInfoModel.get_bot_gold(p_currency)

    if p_bb_type == BB_VIEW_DAILY:
        BB_VIEW_MONTHS = 6
        t_price_list = t_gold.get_price_list()
        t_date_since = date.today() + relativedelta(months=-(BB_VIEW_MONTHS*2))
        t_count = 0
        t_date_list = [row[0] for row in t_price_list]
        while not t_date_since in t_date_list:
            t_date_since = (t_date_since + relativedelta(days=-1))
            if t_count > 7: #protect infinite loop
                t_date_since = None
                break
            t_count += 1
        if t_date_since:
            t_index = t_date_list.index(t_date_since)
            t_price_list = t_price_list[t_index:]
        
        #-> default BB param
        if p_timeframe is None:
            p_timeframe = 15
            p_sdw = 100
        t_img_header = _('Gold Daily View')
    else: #BB_VIEW_WEEKLY
        BB_VIEW_MONTHS = 14
        t_date_since = date.today() + relativedelta(months=-(2*BB_VIEW_MONTHS))
        t_offset = 2 - t_date_since.weekday()
        t_date_since += relativedelta(days=t_offset)
        t_date_list = []
        while t_date_since <= date.today():
            t_date_list.append(t_date_since)
            t_date_since += relativedelta(days=+7)
        t_gold = bot_gold.BotGoldInfoModel.get_bot_gold(p_currency)
        t_price_list = t_gold.get_sample_value_list(t_date_list)

        #-> default BB param
        if p_timeframe is None:
            p_timeframe = 6
            p_sdw = 90
        t_img_header = _('Gold Weekly View')

    logging.info('{}: param {} {} {}'.format(func,p_currency,p_timeframe,p_sdw))
    sma,tb1,tb2,bb1,bb2 = get_bollingerbands(t_price_list,p_timeframe,float(p_sdw)/100)
    #logging.debug('{}: sma {}'.format(func,str(sma)))
    
    #-> compose tbl_content
    t_content_heads = ['Date','OnSell','BB2','BB1','SMA','TB1','TB2']
    t_content_rows = {}
    t_lastdate = t_price_list[-1][0]

    t_view_date_since = date.today() + relativedelta(months=-BB_VIEW_MONTHS)
    logging.info('{}: view_date_since {}'.format(func,str(t_view_date_since)))
    
    logging.debug('{}'.format(str(sma)))
    for ndx2, t_list in enumerate([t_price_list,bb2,bb1,sma,tb1,tb2]):
        t_ndx = 0
        for ndx,t_entry in enumerate(t_list):
            if t_entry[0] < t_view_date_since:
                t_ndx = ndx
            else:
                t_key = t_entry[0].strftime('%Y%m%d')
                if t_key in t_content_rows.keys():
                    t_content_rows[t_entry[0].strftime("%Y%m%d")] += ['{:.2f}'.format(t_entry[1])]
                else:
                    t_content_rows[t_entry[0].strftime("%Y%m%d")] = [t_entry[0].strftime("%Y/%m/%d"), t_entry[1]]
                t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
        #logging.debug('{}: t_list len {}, t_ndx {}'.format(func,len(t_list),t_ndx))
        if t_ndx < len(t_list):
            del t_list[:(t_ndx+1)]
    #logging.debug('{}: sma {}'.format(func,str(sma)))
    
    t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
    
    t_keys = sorted(t_content_rows.keys())
    for i in range(5):
        t_key_1, t_key_2 = t_keys[-i-1], t_keys[-i-2]
        #-> add % for NAV
        t_value_1 = float(t_content_rows[t_key_1][1])
        t_value_2 = float(t_content_rows[t_key_2][1])
        if t_value_2 != 0:
            t_content_rows[t_key_1][1] = '{} ({:.2%})'.format(t_value_1,((t_value_1/t_value_2)-1))
        #-> add % for SMA
        t_value_1 = float(t_content_rows[t_key_1][4])
        t_value_2 = float(t_content_rows[t_key_2][4])
        if t_value_2 != 0:
            t_content_rows[t_key_1][4] = '{} ({:.2%})'.format(t_value_1,((t_value_1/t_value_2)-1))
        #-> add bb width
        t_value_1 = float(t_content_rows[t_key_1][2])
        t_value_2 = float(t_content_rows[t_key_1][6])
        t_content_rows[t_key_1][6] = '{} (BW:{})'.format(t_value_2,(t_value_2-t_value_1))

    tbl_content = {
                   'heads': t_content_heads,
                   'rows': reversed(t_content_rows.values()),
                   }
    t_lable = ' lastDate:{}, {},TF:{},SDW:{}'.format(str(t_lastdate),p_bb_type,p_timeframe,p_sdw)    
    plot = {
            'data': '{data: ' + str(sma).replace('L', '') + \
                            ', label: "' + t_lable + '", color: "black", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(t_price_list).replace('L', '') + \
                            ', color: "blue", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(tb1).replace('L', '') + \
                            ', color: "red", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(tb2).replace('L', '') + \
                            ', color: "purple", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(bb1).replace('L', '') + \
                            ', color: "red", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(bb2).replace('L', '') + \
                            ', color: "purple", lines: {show: true}, yaxis: 4},' 
            }
    
    args = {
            'tpl_img_header' : t_img_header + ' ;Currency:{}; TF:{}; SD_W: {}'.format(p_currency,
                                                                                               p_timeframe,
                                                                                               p_sdw),
            'plot' : plot,
            'tpl_section_title' : _('Details'),
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)

def weekly_bb_view(request,p_currency=bot_ex.CURRENCY_TWD,p_timeframe=6,p_sdw=90):
    return _bb_view(BB_VIEW_WEEKLY, p_currency, p_timeframe, p_sdw)

    BB_VIEW_MONTHS = 14
    
    func = '{} {}'.format(__name__,'weekly_bb_view')
    t_date_since = date.today() + relativedelta(months=-(2*BB_VIEW_MONTHS))
    t_offset = 2 - t_date_since.weekday()
    t_date_since += relativedelta(days=t_offset)
    t_date_list = []
    while t_date_since <= date.today():
        t_date_list.append(t_date_since)
        t_date_since += relativedelta(days=+7)
    #t_date_list.append(date.today())
    #return HttpResponse(str(t_date_list))
    t_gold = bot_gold.BotGoldInfoModel.get_bot_gold(p_currency)
    t_price_list = t_gold.get_sample_value_list(t_date_list)
    logging.debug('{}: get_sample_value_list:\n{}'.format(func,str(t_price_list)))
    #return HttpResponse(str(t_price_list))

    sma,tb1,tb2,bb1,bb2 = get_bollingerbands(t_price_list,p_timeframe,float(p_sdw)/100)
    
    #-> compose tbl_content
    t_content_heads = ['Date','OnSell','BB2','BB1','SMA','TB1','TB2']
    t_content_rows = {}
    
    t_view_date_since = date.today() + relativedelta(months=-BB_VIEW_MONTHS)
    t_ndx = 0

    for ndx2, t_list in enumerate([t_price_list,bb2,bb1,sma,tb1,tb2]):
        for ndx,t_entry in enumerate(t_list):
            if t_entry[0] < t_view_date_since:
                t_ndx = ndx
            else:
                t_key = t_entry[0].strftime('%Y%m%d')
                if t_key in t_content_rows.keys():
                    t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2f}'.format(t_entry[1]),)
                else:
                    t_content_rows[t_entry[0].strftime("%Y%m%d")] = (t_entry[0].strftime("%Y/%m/%d"), t_entry[1],)
                t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
        del t_list[:(t_ndx+1)]
    
    t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
    tbl_content = {
                   'heads': t_content_heads,
                   'rows': reversed(t_content_rows.values()),
                   }
        
    plot = {
            'data': '{data: ' + str(sma).replace('L', '') + \
                            ', label: "SMA", color: "black", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(t_price_list).replace('L', '') + \
                            ', label: "NAV", color: "blue", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(tb1).replace('L', '') + \
                            ', label: "TB1", color: "red", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(tb2).replace('L', '') + \
                            ', label: "TB2", color: "purple", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(bb1).replace('L', '') + \
                            ', label: "BB1", color: "red", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(bb2).replace('L', '') + \
                            ', label: "BB2", color: "purple", lines: {show: true}, yaxis: 4},' 
            }
    
    args = {
            'tpl_img_header' : _('Gold Weekly View') + ' ;Currency:{}; TF:{}; SD_W: {}'.format(p_currency,
                                                                                               p_timeframe,
                                                                                               p_sdw),
            'plot' : plot,
            'tpl_section_title' : _('Details'),
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)

def default_view(request):
    t_report = GoldReport.get_report()
    if t_report is None:
        return HttpResponse('GoldReport Fail')
    
    t_content_heads = []
    t_content_rows = {}

    exchange_report = t_report.report_exchange
    for t_entry in exchange_report:
        t_content_rows[t_entry[0].strftime("%Y%m%d")] = (t_entry[0].strftime("%Y/%m/%d"), t_entry[1],)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
    t_content_heads.append('Date')
    t_content_heads.append('ExRate')

    profit_report = t_report.report_profit
    for t_entry in profit_report:
        t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2f}%'.format(t_entry[1]),)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
    t_content_heads.append('Profit')

    sell_price_report = t_report.report_sell_price
    for t_entry in sell_price_report:
        t_content_rows[t_entry[0].strftime("%Y%m%d")] += (t_entry[1],)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
    t_content_heads.append('SellPrice')

    cost_report = t_report.report_cost
    for t_entry in cost_report:
        t_content_rows[t_entry[0].strftime("%Y%m%d")] += (t_entry[1],)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
    t_content_heads.append('Cost')

    t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))

    plot = {
            'data': '{data: ' + str(cost_report).replace('L', '') + ', label: "Cost", lines: {show: true, steps: true}},' + \
                    '{data: ' + str(sell_price_report).replace('L', '') + ', label: "Sell Price", lines: {show: true}, yaxis: 2},' + \
                    '{data: ' + str(profit_report).replace('L', '') + ', label: "Profit (%)", lines: {show: true}, yaxis: 3},' + \
                    '{data: ' + str(exchange_report).replace('L', '') + ', label: "ExRate", lines: {show: true}, yaxis: 4},'
            }
    
    tbl_content = {
                   'heads': t_content_heads,
                   'rows': reversed(t_content_rows.values()),
                   }

    args = {
            'tpl_img_header' : _("HEADER_MY_GOLD") , 
            'tpl_section_title' : _("TITLE_MY_GOLD_DETAIL"), 
            'plot' : plot,
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_my_japan.tpl.html',args)

def add_my_trade(request):
    #-> [trade_date,amount_trade,trade_fee,currency_type,weight_purchase,bid_price,exchange_rate]
    my_trade_logs = [
        ['2013/11/19', 19440.0, 0.0, bot_ex.CURRENCY_TWD, 16.0, 1215.0, 1.0],
        ['2013/12/31', 20000.0, 25.0, bot_ex.CURRENCY_TWD, 17.0, 1176.47, 1.0],
        ['2014/1/2', 20000.0, 25.0, bot_ex.CURRENCY_TWD, 16.56, 1207.73, 1.0],
        ['2014/2/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 62.84, 1273.07, 1.0],
        ['2014/3/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 60.92, 1313.20, 1.0],
        ['2014/4/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 63.01, 1269.64, 1.0],
        ['2014/4/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 63.01, 1269.64, 1.0],
        ['2014/5/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 63.67, 1256.48, 1.0],
        ['2014/6/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 64.47, 1240.89, 1.0],
        ['2014/7/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 62.96, 1270.65, 1.0],
        ['2014/8/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 63.72, 1255.49, 1.0],
        ['2014/9/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 66.29, 1206.82, 1.0],
        ['2014/10/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 66.47, 1203.55, 1.0],
        ['2014/11/1', 80000.0, 25.0, bot_ex.CURRENCY_TWD, 68.61, 1166.01, 1.0],
                     ]
    
    for t_trade in my_trade_logs:
        _add_trade_record(
                          datetime.strptime(t_trade[0], "%Y/%m/%d").date(),
                          t_trade[1],
                          t_trade[2],
                          t_trade[3],
                          t_trade[4],
                          t_trade[5],
                          t_trade[6],
                          )
    return HttpResponseRedirect('/gi/')
    return HttpResponse(__name__ + ': add_my_trade')

def _add_trade_record(date_invest, amount_trade, trade_fee, currency_type, weight_purchse, bid_price, exchange_rate):

    key_name = currency_type + '@' + date_invest.strftime("%m/%d/%Y")
    gold_invest = GoldInvestModel.get_or_insert(key_name)
    gold_invest.currency_type = currency_type
    gold_invest.date_invest = date_invest
    gold_invest.exchange_rate = exchange_rate
    gold_invest.weight_purchase = weight_purchse
    gold_invest.trade_fee = trade_fee
    gold_invest.amount_trade = amount_trade
    gold_invest.bid_price = bid_price
    gold_invest.put()
    
