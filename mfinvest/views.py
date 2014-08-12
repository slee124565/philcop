# -*- coding: utf8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response

from dateutil.relativedelta import relativedelta
from datetime import date
import logging
import calendar

from mfinvest.models import MutualFundInvestModel
from fundclear.models import FundClearModel
from bankoftaiwan.models import BotExchangeModel
import bankoftaiwan.exchange
from mfinvest.mfreport import MFReport, get_sample_date_list

TARGET_FUND_ID_LIST = ['AJSCY3','AJSCA3','LU0069970746','LU0107058785','AJSPY3']

def get_funds_dict(p_fund_id_list, p_fund_data_months):
    t_fund_dict = {}
    for t_fund_id in p_fund_id_list:
        t_fund = FundClearModel.get_fund(t_fund_id, p_fund_data_months)
        if t_fund:
            t_fund_dict[t_fund_id] = t_fund
        else:
            logging.warning('Fund Object Error,_fund_id: ' + t_fund_id)
    
    return t_fund_dict
    

def japan_yoy_compare_view(request):
    fund_data_months = 25
    fund_id_list = TARGET_FUND_ID_LIST
    #fund_id_list = ['AJSCY3','AJSCA3']
    
    #-> download fund data from FundClear
    t_fund_list = get_funds_dict(fund_id_list,fund_data_months)

    #-> sampling fund data 
    t_sample_date_list = get_sample_date_list(25,False)
    t_fund_data_list = {}
    t_fund_yoy_dict = {}

    for t_fund_id in t_fund_list:
        t_fund_data_list[t_fund_id] = t_fund_list[t_fund_id].get_sample_value_list(t_sample_date_list)
        t_fund_yoy_dict[t_fund_id] = []
        
        #-> compute YoY value for last 12 months
        t_check_date_1 = date.today()
        for i in range(12):
            t_check_date_1 = date(t_check_date_1.year, t_check_date_1.month, 1) - relativedelta(days=+1)
            t_check_date_2 = date(t_check_date_1.year-1,t_check_date_1.month,t_check_date_1.day)
            logging.debug('t_check_date_1: ' + str(t_check_date_1))
            logging.debug('t_check_date_2: ' + str(t_check_date_2))
            t_col_1_list = [row[0] for row in t_fund_data_list[t_fund_id]]
            nav1 = t_fund_data_list[t_fund_id][t_col_1_list.index(t_check_date_1)][1]
            nav2 = t_fund_data_list[t_fund_id][t_col_1_list.index(t_check_date_2)][1]
            yoy = (nav1-nav2)/nav1
            t_fund_yoy_dict[t_fund_id].append([t_check_date_1,yoy])
        t_fund_yoy_dict[t_fund_id].sort(key=lambda x: x[0])
    
    #-> formating date column for FLOT
    for t_fund_id in t_fund_yoy_dict:
        for t_entry in t_fund_yoy_dict[t_fund_id]:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 

    t_data_str = ''
    for t_fund_id in t_fund_yoy_dict:
        t_data_str += '{data: ' + str(t_fund_yoy_dict[t_fund_id]).replace('L', '') + ', label:"' + t_fund_id + '"},'


    t_tpl_args = {
                  'data' : t_data_str,
                  'page_title' : 'Fund_Japan_YoY_Compare',
                  }
    return render_to_response('fund_japans.html', t_tpl_args)
    
    
    
def japan_nav_compare_view(request):
    fund_data_months = 25
    fund_id_list = TARGET_FUND_ID_LIST
    #fund_id_list = ['AJSCY3','AJSCA3']
    
    #-> download fund data from FundClear
    t_fund_list = get_funds_dict(fund_id_list,fund_data_months)
    
    #-> sampling fund data & formating date column for FLOT
    t_sample_date_list = get_sample_date_list(25)
    t_fund_data_list = {}
    for t_fund_id in t_fund_list:
        t_fund_data_list[t_fund_id] = t_fund_list[t_fund_id].get_sample_value_list(t_sample_date_list)
        for t_entry in t_fund_data_list[t_fund_id]:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
    
    t_data_str = ''
    for t_fund_id in t_fund_data_list:
        t_data_str += '{data: ' + str(t_fund_data_list[t_fund_id]).replace('L', '') + ', label:"' + t_fund_id + '"},'

    t_tpl_args = {
                  'data' : t_data_str,
                  'page_title' : 'Fund_Japan_NAV_Compare',
                  }
    return render_to_response('fund_japans.html', t_tpl_args)

def mf_japan_view(request):

    t_fund_id = 'LU0069970746'
    t_currency_type = bankoftaiwan.exchange.CURRENCY_JPY
    mf_report = MFReport.get_mfreport_by_id(t_fund_id, t_currency_type)
    
    exchange_report = mf_report.report_exchange
    for t_entry in exchange_report:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
    
    profit_report = mf_report.report_profit
    for t_entry in profit_report:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
    
    nav_report = mf_report.report_nav
    for t_entry in nav_report:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        

    cost_report = mf_report.report_cost
    for t_entry in cost_report:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
    
    plot = {
            'data': '{data: ' + str(cost_report).replace('L', '') + ', label: "Cost", lines: {show: true, steps: true}},' + \
                    '{data: ' + str(nav_report).replace('L', '') + ', label: "NAV", lines: {show: true}, yaxis: 2},' + \
                    '{data: ' + str(profit_report).replace('L', '') + ', label: "Profit (%)", lines: {show: true}, yaxis: 3},' + \
                    '{data: ' + str(exchange_report).replace('L', '') + ', label: "JPY/TWN", lines: {show: true}, yaxis: 4},'
            }
    
    args = {
            'page_title' : 'My_Review_MF_Japan',
            'fund_title' : u'法巴百利達日本小型股票基金 C (日幣)',
            'fund_id' : t_fund_id,
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

def add_my_trade(request):
    _add_trade_record(date_invest = date(2014,7,15), \
                      fund_id = 'LU0069970746', \
                      amount_trade = 100000.0, \
                      trade_fee = 1950.0, \
                      currency_type = bankoftaiwan.exchange.CURRENCY_JPY, \
                      share = 49.144, \
                      fund_nav = 6872.0, \
                      exchange_rate = 0.2961
                      )
    return HttpResponse('add_my_trade done')
    
def _add_trade_record(date_invest, fund_id, amount_trade, trade_fee, currency_type, share, fund_nav, exchange_rate):

    key_name = fund_id + '@' + date_invest.strftime("%m/%d/%Y")
    fund_invest = MutualFundInvestModel.get_or_insert(key_name)
    fund_invest.id = fund_id
    fund_invest.currency = currency_type
    fund_invest.date_invest = date_invest
    fund_invest.share = share
    fund_invest.amount_trade = amount_trade
    fund_invest.trade_fee = trade_fee
    fund_invest.nav = fund_nav
    fund_invest.exchange_rate = exchange_rate
    fund_invest.put()
    
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
