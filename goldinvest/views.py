from django.http import HttpResponse
from django.shortcuts import render_to_response
from goldreport import GoldReport
from models import GoldInvestModel
from bankoftaiwan import exchange
from datetime import datetime
from django.utils.translation import ugettext as _

import logging, calendar, collections

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
        t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2}%'.format(t_entry[1]),)
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
                   'rows': t_content_rows.values(),
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
        ['2013/11/19', 19440.0, 0.0, exchange.CURRENCY_TWD, 16.0, 1215.0, 1.0],
        ['2013/12/31', 20000.0, 25.0, exchange.CURRENCY_TWD, 17.0, 1176.47, 1.0],
        ['2014/1/2', 20000.0, 25.0, exchange.CURRENCY_TWD, 16.56, 1207.73, 1.0],
        ['2014/2/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 62.84, 1273.07, 1.0],
        ['2014/3/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 60.92, 1313.20, 1.0],
        ['2014/4/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 63.01, 1269.64, 1.0],
        ['2014/4/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 63.01, 1269.64, 1.0],
        ['2014/5/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 63.67, 1256.48, 1.0],
        ['2014/6/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 64.47, 1240.89, 1.0],
        ['2014/7/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 62.96, 1270.65, 1.0],
        ['2014/8/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 63.72, 1255.49, 1.0],
        ['2014/9/1', 80000.0, 25.0, exchange.CURRENCY_TWD, 66.29, 1206.82, 1.0],
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
    
