# -*- coding: utf8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response

from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import date
import logging
import calendar

from mfinvest.models import MutualFundInvestModel
from fundclear.models import FundClearModel
from bankoftaiwan.models import BotExchangeModel
from phicops import utils
import bankoftaiwan.exchange
from mfinvest.mfreport import MFReport

def mf_japan_view(request):

    t_fund_id = 'LU0069970746'
    t_currency_type = bankoftaiwan.exchange.CURRENCY_JPY
    mf_report = MFReport.get_mfreport_by_id(t_fund_id, t_currency_type)
    
    nav_report = mf_report.report_nav
    for t_entry in nav_report:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        

    cost_report = mf_report.report_cost
    for t_entry in cost_report:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
    
    plot = {
            'data': '{data: ' + str(cost_report).replace('L', '') + ', label: "Cost", lines: {show: true, steps: true}},' + \
                    '{data: ' + str(nav_report).replace('L', '') + ', label: "' + t_fund_id + '", lines: {show: true}, yaxis: 2},' 
            }
    
    args = {
            'page_title' : 'My_Review_MF_Japan',
            'page_head' : u'LU0069970746 法巴百利達日本小型股票基金 C (日幣)'.encode('utf8'),
            'plot' : plot,
            }
    return render_to_response('my_fund_japan.html', args)
    
def test(request):
    trade_list = MutualFundInvestModel.all().order('date_invest')
    tmp =''
    for t_trade in trade_list:
        logging.debug('trade: ' + t_trade.key().name())
        tmp += unicode(t_trade)
    response = HttpResponse('count ' + str(trade_list.count()) + '<br/>\n' + tmp)
    response['Content-type'] = 'text/plain'
    return response

def add_sample(request):
    '''
    periodic investment since last 8 months
    '''
    fund_id = 'LU0069970746'
    amount_trade = float(100000)
    trade_fee = float(1950)
    currency_type = bankoftaiwan.exchange.CURRENCY_JPY
    date_since = date.today() - relativedelta(months=+8) - relativedelta(days=+1)
    fund = FundClearModel.get_fund(fund_id)
    exchange = BotExchangeModel.get_bot_exchange(currency_type)
    
    for i in range(0,7):
        date_invest = date_since + relativedelta(months=i)
        fund_nav = fund.get_nav_by_date(date_invest)
        exchange_rate = exchange.get_rate(date_invest)
        key_name = fund_id + '@' + date_invest.strftime("%m/%d/%Y")
        fund_invest = MutualFundInvestModel.get_or_insert(key_name)
        fund_invest.id = fund_id
        fund_invest.currency = currency_type
        fund_invest.date_invest = date_invest
        fund_invest.share = (amount_trade/exchange_rate)/fund_nav
        fund_invest.amount_trade = amount_trade
        fund_invest.trade_fee = trade_fee
        fund_invest.nav = fund_nav
        fund_invest.exchange_rate = exchange_rate
        fund_invest.put()
