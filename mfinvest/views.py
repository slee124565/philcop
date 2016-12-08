# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.utils.translation import ugettext as _

from dateutil.relativedelta import relativedelta
from datetime import date

import logging, calendar, collections

from mfinvest.models import MutualFundInvestModel
from fundclear.models import FundClearModel
from fundclear.fundreview.models import FundReviewModel
import bankoftaiwan2.models_exchange as bot_ex
from mfinvest.mfreport import MFReport
from mfinvest import fundreview
from fundclear.fcreader import get_fundcode_list, get_fundcode_dictlist, get_name_with_fundcode_list
from utils import util_date

TARGET_FUND_ID_LIST = ['AJSCY3','AJSCA3','LU0069970746','LU0107058785'] #,'AJSPY3', 'AJNHA3']

def get_funds_dict(p_fund_id_list, p_fund_data_months):
    t_fund_dict = {}
    for t_fund_id in p_fund_id_list:
        t_fund = FundClearModel.get_fund(t_fund_id, p_fund_data_months)
        if t_fund:
            t_fund_dict[t_fund_id] = t_fund
        else:
            logging.warning('Fund Object Error,_fund_id: ' + t_fund_id)
    
    return t_fund_dict

def fund_review_view_4(request):
    t_fund_info_list = get_fundcode_dictlist()
    if request.POST:
        f_fund_id = request.POST['fund_code']
        
        fund_review = FundReviewModel.flush_fund_review(f_fund_id)
        
        t_content_heads = []
        t_content_rows = {}
        
        t_nav_list = fund_review.nav_list()
        for t_entry in t_nav_list:
            t_content_rows[t_entry[0].strftime('%Y%m%d')] = (t_entry[0].strftime('%Y/%m/%d'),)
            t_content_rows[t_entry[0].strftime('%Y%m%d')] += (t_entry[1],)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
        t_content_heads.append('Date')
        t_content_heads.append('NAV')
        
        t_yoy_1_list = fund_review.yoy_list(1)
        for t_entry in t_yoy_1_list:
            t_content_rows[t_entry[0].strftime('%Y%m%d')] += ('{:.2f}%'.format(t_entry[1]),)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
        t_content_heads.append('YoY_1')
        
        t_yoy_2_list = fund_review.yoy_list(2)
        for t_entry in t_yoy_2_list:
            t_content_rows[t_entry[0].strftime('%Y%m%d')] += ('{:.2f}%'.format(t_entry[1]),)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
        t_content_heads.append('YoY_2')
        
        t_data_str = ''
        t_data_str += '{data: ' + str(t_nav_list).replace('L', '') + ', label:"NAV", yaxis: 4},'
        t_data_str += '{data: ' + str(t_yoy_1_list).replace('L', '') + ', label:"YoY_1", yaxis: 5},'
        t_data_str += '{data: ' + str(t_yoy_2_list).replace('L', '') + ', label:"YoY_2", yaxis: 5},'
    
        plot = {
                'data' : t_data_str,
                }
        
        t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
        tbl_content = {
                       'heads': t_content_heads,
                       'rows': t_content_rows.values(),
                       }
    
        args = {
                'tpl_img_header' : _("HEAD_FUND_REVIEW") , 
                'tpl_section_title' : FundClearModel.get_by_key_name(f_fund_id).fund_name, #_("TITLE_NAV_REVIEW_DETAIL"), 
                'plot' : plot,
                'tbl_content' : tbl_content,
                'action_url': request.get_full_path(),
                'fund_info_list': t_fund_info_list,
                'fund_code': f_fund_id,
                }
        args.update(csrf(request))

        return render_to_response('mf_my_japan.tpl.html', args)
    
    else:
        args = {
                'tpl_img_header': _('HEAD_FUND_REVIEW'),
                'tpl_section_title' : ' ',
                'action_url': request.get_full_path(),
                'fund_info_list': t_fund_info_list,
                'fund_code': '',
                }
        args.update(csrf(request))
        return render_to_response('mf_fund_review_page.tpl.html', args)
       
def fund_review_view_3(request):
    t_fund_info_list = get_fundcode_dictlist()
    if request.POST:
        f_fund_id = request.POST['fund_code']
        
        fund_review = FundReviewModel.flush_fund_review(f_fund_id)
        
        t_nav_list = fund_review.nav_list()
        for t_entry in t_nav_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
        
        t_yoy_1_list = fund_review.yoy_list(1)
        for t_entry in t_yoy_1_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
        
        t_yoy_2_list = fund_review.yoy_list(2)
        for t_entry in t_yoy_2_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 

        t_data_str = ''
        t_data_str += '{data: ' + str(t_nav_list).replace('L', '') + ', label:"NAV", yaxis: 1},'
        t_data_str += '{data: ' + str(t_yoy_1_list).replace('L', '') + ', label:"YoY_1", yaxis: 2},'
        t_data_str += '{data: ' + str(t_yoy_2_list).replace('L', '') + ', label:"YoY_2", yaxis: 2},'
    
        t_tpl_args = {
                        'data' : t_data_str,
                        'page_title' : 'Fund Review - ' + FundClearModel.get_by_key_name(f_fund_id).fund_name, #get_name_with_fundcode_list(f_fund_id),
                        'action_url': request.get_full_path(),
                        'fund_info_list': t_fund_info_list,
                        'fund_code': f_fund_id,
                      }
        t_tpl_args.update(csrf(request))
        return render_to_response('mf_fund_review.html', t_tpl_args)
    else:
        args = {
                'page_title': 'Fund Review',
                'action_url': request.get_full_path(),
                'fund_info_list': t_fund_info_list,
                'fund_code': '',
                }
        args.update(csrf(request))
        return render_to_response('mf_fund_review_page.html', args)

def fund_review_view_2(request):
    t_fund_info_list = get_fundcode_dictlist()
    if request.POST:
        f_fund_id = request.POST['fund_code']
        
        t_years = 2
        fund_review = fundreview.FundReview(f_fund_id,t_years)
    
        for t_entry in fund_review.nav_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
        
        for t_entry in fund_review.yoy_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
        
        t_data_str = ''
        t_data_str += '{data: ' + str(fund_review.nav_list).replace('L', '') + ', label:"NAV", yaxis: 1},'
        t_data_str += '{data: ' + str(fund_review.yoy_list).replace('L', '') + ', label:"YoY", yaxis: 2},'
    
        t_tpl_args = {
                        'data' : t_data_str,
                        'page_title' : 'Fund Review - ' + fund_review.fund_name, #get_name_with_fundcode_list(f_fund_id),
                        'action_url': request.get_full_path(),
                        'fund_info_list': t_fund_info_list,
                        'fund_code': f_fund_id,
                      }
        t_tpl_args.update(csrf(request))
        return render_to_response('mf_fund_review.html', t_tpl_args)
    else:
        args = {
                'page_title': 'Fund Review',
                'action_url': request.get_full_path(),
                'fund_info_list': t_fund_info_list,
                'fund_code': '',
                }
        args.update(csrf(request))
        return render_to_response('mf_fund_review_page.html', args)
        
def fund_review_view(request, fund_id='LU0069970746', years=1):
    '''
    review NAV + YoY
    '''
    fund_review = fundreview.FundReview(fund_id,years)

    for t_entry in fund_review.nav_list:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
    
    for t_entry in fund_review.yoy_list:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
    
    t_data_str = ''
    t_data_str += '{data: ' + str(fund_review.nav_list).replace('L', '') + ', label:"NAV", yaxis: 1},'
    t_data_str += '{data: ' + str(fund_review.yoy_list).replace('L', '') + ', label:"YoY", yaxis: 2},'

    t_tpl_args = {
                  'data' : t_data_str,
                  'page_title' : fund_review.fund_name,
                  }
    return render_to_response('fund_review.html', t_tpl_args)

def japan_yoy_compare_view_2(request):
    years = 2
    fund_id_list = TARGET_FUND_ID_LIST

    #-> calculate total sample months needed
    TOTAL_SAMPLE_MONTHS_COUNT = 12 * int(years)
    fund_data_months = TOTAL_SAMPLE_MONTHS_COUNT*2+1
     
    #-> download fund data from FundClear
    t_fund_list = get_funds_dict(fund_id_list,fund_data_months)

    #-> sampling fund data 
    t_sample_date_list = util_date.get_sample_date_list(fund_data_months,False)
    t_fund_data_list = {}
    t_fund_yoy_dict = {}
    
    t_content_heads = []
    t_content_rows = {}

    for t_fund_id in t_fund_list:
        t_fund_data_list[t_fund_id] = t_fund_list[t_fund_id].get_sample_value_list(t_sample_date_list)
        t_fund_yoy_dict[t_fund_id] = []
        
        #-> compute YoY value for last 12 months
        t_check_date_1 = date.today()
        for i in range(TOTAL_SAMPLE_MONTHS_COUNT):
            t_check_date_1 = date(t_check_date_1.year, t_check_date_1.month, 1) - relativedelta(days=+1)
            t_check_date_2 = date(t_check_date_1.year-1,t_check_date_1.month,1) + relativedelta(months=+1) - relativedelta(days=+1)
            t_col_1_list = [row[0] for row in t_fund_data_list[t_fund_id]]
            nav1 = t_fund_data_list[t_fund_id][t_col_1_list.index(t_check_date_1)][1]
            nav2 = t_fund_data_list[t_fund_id][t_col_1_list.index(t_check_date_2)][1]
            #logging.debug('date ' + str(t_check_date_1) + ' nav ' + str(nav1))
            #logging.debug('date ' + str(t_check_date_2) + ' nav ' + str(nav2))
            yoy = 100 * (nav1-nav2)/nav2
            t_fund_yoy_dict[t_fund_id].append([t_check_date_1,yoy])
        t_fund_yoy_dict[t_fund_id].sort(key=lambda x: x[0])
    
    for t_entry in t_fund_yoy_dict.itervalues().next():
        t_content_rows[t_entry[0].strftime('%Y%m%d')] = (t_entry[0].strftime('%Y/%m/%d'),)
    t_content_heads.append('Date')

    #-> formating date column for FLOT
    for t_fund_id in t_fund_yoy_dict:
        logging.debug(__name__ + ': japan_yoy_compare_view ' + t_fund_id + ':\n' + str(t_fund_yoy_dict[t_fund_id]))
        for t_entry in t_fund_yoy_dict[t_fund_id]:
            t_content_rows[t_entry[0].strftime('%Y%m%d')] += ('{:.3}%'.format(t_entry[1]),)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 

    t_fundcode_list = get_fundcode_list()
    t_code_list = [row[1] for row in t_fundcode_list]
    t_data_str = ''
    t_fund_name = ''
    for t_fund_id in t_fund_yoy_dict:
        if t_fund_id in t_code_list:
            t_fund_name = t_fundcode_list[t_code_list.index(t_fund_id)][2]
        t_data_str += '{data: ' + str(t_fund_yoy_dict[t_fund_id]).replace('L', '') + ', label:"' + t_fund_id + ', ' + t_fund_name + '", yaxis: 5},'
        t_content_heads.append(t_fund_name)
    
    plot = {
            'data' : t_data_str,
            }
    
    t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
    tbl_content = {
                   'heads': t_content_heads,
                   'rows': t_content_rows.values(),
                   }

    args = {
            'tpl_img_header' : _("HEADER_JPY_TOP_FUND_YOY") , 
            'tpl_section_title' : _("YOY"), 
            'plot' : plot,
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_my_japan.tpl.html',args)
        
def japan_yoy_compare_view(request):
    years = 2
    fund_id_list = TARGET_FUND_ID_LIST
    #fund_id_list = ['AJSCY3']

    #-> calculate total sample months needed
    TOTAL_SAMPLE_MONTHS_COUNT = 12 * int(years)
    fund_data_months = TOTAL_SAMPLE_MONTHS_COUNT*2+1
     
    #-> download fund data from FundClear
    t_fund_list = get_funds_dict(fund_id_list,fund_data_months)

    #-> sampling fund data 
    t_sample_date_list = util_date.get_sample_date_list(fund_data_months,False)
    t_fund_data_list = {}
    t_fund_yoy_dict = {}

    for t_fund_id in t_fund_list:
        t_fund_data_list[t_fund_id] = t_fund_list[t_fund_id].get_sample_value_list(t_sample_date_list)
        t_fund_yoy_dict[t_fund_id] = []
        
        #-> compute YoY value for last 12 months
        t_check_date_1 = date.today()
        for i in range(TOTAL_SAMPLE_MONTHS_COUNT):
            t_check_date_1 = date(t_check_date_1.year, t_check_date_1.month, 1) - relativedelta(days=+1)
            t_check_date_2 = date(t_check_date_1.year-1,t_check_date_1.month,1) + relativedelta(months=+1) - relativedelta(days=+1)
            t_col_1_list = [row[0] for row in t_fund_data_list[t_fund_id]]
            nav1 = t_fund_data_list[t_fund_id][t_col_1_list.index(t_check_date_1)][1]
            nav2 = t_fund_data_list[t_fund_id][t_col_1_list.index(t_check_date_2)][1]
            #logging.debug('date ' + str(t_check_date_1) + ' nav ' + str(nav1))
            #logging.debug('date ' + str(t_check_date_2) + ' nav ' + str(nav2))
            yoy = (nav1-nav2)/nav2
            t_fund_yoy_dict[t_fund_id].append([t_check_date_1,yoy])
        t_fund_yoy_dict[t_fund_id].sort(key=lambda x: x[0])
    
    #-> formating date column for FLOT
    for t_fund_id in t_fund_yoy_dict:
        logging.debug(__name__ + ': japan_yoy_compare_view ' + t_fund_id + ':\n' + str(t_fund_yoy_dict[t_fund_id]))
        for t_entry in t_fund_yoy_dict[t_fund_id]:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 

    t_fundcode_list = get_fundcode_list()
    t_code_list = [row[1] for row in t_fundcode_list]
    t_data_str = ''
    t_fund_name = ''
    for t_fund_id in t_fund_yoy_dict:
        if t_fund_id in t_code_list:
            t_fund_name = t_fundcode_list[t_code_list.index(t_fund_id)][2]
        t_data_str += '{data: ' + str(t_fund_yoy_dict[t_fund_id]).replace('L', '') + ', label:"' + t_fund_id + ', ' + t_fund_name + '"},'


    t_tpl_args = {
                  'data' : t_data_str,
                  'page_title' : 'Fund_Japan_YoY_Compare_Year_' + str(years),
                  }
    #return render_to_response('fund_japans.html', t_tpl_args)
    return render_to_response('mf_japan_tops.html', t_tpl_args)
       
def japan_nav_compare_view_2(request):
    fund_data_months = 25
    fund_id_list = TARGET_FUND_ID_LIST
    #fund_id_list = ['AJSCY3','AJSCA3']
    
    #-> download fund data from FundClear
    t_fund_list = get_funds_dict(fund_id_list,fund_data_months)
    
    #-> sampling fund data & formating date column for FLOT
    t_sample_date_list = util_date.get_sample_date_list(25)
    
    t_content_heads = []
    t_content_rows = {}
    for t_date in t_sample_date_list:
        t_content_rows[t_date.strftime('%Y%m%d')] = (t_date.strftime('%Y/%m/%d'),)
    t_content_heads.append('Date')
    
    t_fund_data_list = {}
    for t_fund_id in t_fund_list:
        t_fund_data_list[t_fund_id] = t_fund_list[t_fund_id].get_sample_value_list(t_sample_date_list)
        t_content_heads.append(t_fund_id)
        for t_entry in t_fund_data_list[t_fund_id]:
            t_content_rows[t_entry[0].strftime('%Y%m%d')] += (t_entry[1],)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 

    t_data_str = ''
    for t_fund_id in t_fund_data_list:
        t_data_str += '{data: ' + str(t_fund_data_list[t_fund_id]).replace('L', '') + ', label:" ' + t_fund_id + '", yaxis: 2},'

    plot = {
            'data' : t_data_str,
            }
    
    t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
    tbl_content = {
                   'heads': t_content_heads,
                   'rows': t_content_rows.values(),
                   }

    args = {
            'tpl_img_header' : _("HEADER_JPY_TOP_FUND_NAV") , 
            'tpl_section_title' : _("NAV(CURRENCY_JPY)"), 
            'plot' : plot,
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_my_japan.tpl.html',args)
        
def japan_nav_compare_view(request):
    fund_data_months = 25
    fund_id_list = TARGET_FUND_ID_LIST
    #fund_id_list = ['AJSCY3','AJSCA3']
    
    #-> download fund data from FundClear
    t_fund_list = get_funds_dict(fund_id_list,fund_data_months)
    
    #-> sampling fund data & formating date column for FLOT
    t_sample_date_list = util_date.get_sample_date_list(25)
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
    #return render_to_response('fund_japans.html', t_tpl_args)
    return render_to_response('mf_japan_tops.html', t_tpl_args)

def mf_japan_view_2(request):
    t_fund_id = 'LU0069970746'
    t_currency_type = bot_ex.CURRENCY_JPY
    mf_report = MFReport.get_mfreport_by_id(t_fund_id, t_currency_type)
    args = {}
    if not mf_report is None:
        t_content_heads = []
        t_content_rows = {}
        
        exchange_report = list(mf_report.report_exchange)
        for t_entry in exchange_report:
            t_content_rows[t_entry[0].strftime("%Y%m%d")] = (t_entry[0].strftime("%Y/%m/%d"), t_entry[1],)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
        t_content_heads.append('Date')
        t_content_heads.append('JPY/TW')
        
        profit_report = list(mf_report.report_profit)
        for t_entry in profit_report:
            t_content_rows[t_entry[0].strftime("%Y%m%d")] += ('{:.2}%'.format(t_entry[1]),)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
        t_content_heads.append('Profit')
        
        nav_report = list(mf_report.report_nav)
        for t_entry in nav_report:
            t_content_rows[t_entry[0].strftime("%Y%m%d")] += (t_entry[1],)
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
        t_content_heads.append('NAV')
    
        cost_report = list(mf_report.report_cost)
        for t_entry in cost_report:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000        
        
        cost_report_2 = list(mf_report.report_cost2)
        for t_entry in cost_report_2:
            t_content_rows[t_entry[0].strftime("%Y%m%d")] += (t_entry[1],)
        t_content_heads.append('Cost')
        
        t_content_rows = collections.OrderedDict(sorted(t_content_rows.items()))
        
        #return HttpResponse(str(t_content_heads) + '<br/>' + str(t_content_rows.values()))
    
        plot = {
                'data': '{data: ' + str(cost_report).replace('L', '') + ', label: "Cost", lines: {show: true, steps: true}},' + \
                        '{data: ' + str(nav_report).replace('L', '') + ', label: "NAV", lines: {show: true}, yaxis: 2},' + \
                        '{data: ' + str(profit_report).replace('L', '') + ', label: "Profit (%)", lines: {show: true}, yaxis: 3},' + \
                        '{data: ' + str(exchange_report).replace('L', '') + ', label: "JPY/TWN", lines: {show: true}, yaxis: 4},'
                }
        
        tbl_content = {
                       'heads': t_content_heads,
                       'rows': t_content_rows.values(),
                       }
    
        args = {
                'tpl_img_header' : _("FUND_NAME_LU0069970746") , #u'法巴百利達日本小型股票基金 C',
                'tpl_section_title' : _("NAV(CURRENCY_JPY)"), #u'基金淨值 (日幣)',
                'plot' : plot,
                'tbl_content' : tbl_content,
                }
    
    return render_to_response('mf_my_japan.tpl.html',args)
        
def mf_japan_view(request):
    t_fund_id = 'LU0069970746'
    t_currency_type = bot_ex.CURRENCY_JPY
    mf_report = MFReport.get_mfreport_by_id(t_fund_id, t_currency_type)
    if mf_report is None:
        return HttpResponse('MFReport Fail')
    
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
    #return render_to_response('my_fund_japan.html', args)
    return render_to_response('mf_my_japan.html', args)
    
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
                      currency_type = bot_ex.CURRENCY_JPY, \
                      share = 49.144, \
                      fund_nav = 6872.0, \
                      exchange_rate = 0.2961
                      )
    return HttpResponse('add_my_trade done')

def add_my_trade_2(request):
    _add_trade_record(date_invest = date(2014,8,20), \
                      fund_id = 'LU0069970746', \
                      amount_trade = 100000.0, \
                      trade_fee = 1950.0, \
                      currency_type = bot_ex.CURRENCY_JPY, \
                      share = 48.601, \
                      fund_nav = 7061.0, \
                      exchange_rate = 0.2914
                      )
    return HttpResponse('add_my_trade done')
    
def add_my_trade_3(request):
    _add_trade_record(date_invest = date(2014,9,24), \
                      fund_id = 'LU0069970746', \
                      amount_trade = 100000.0, \
                      trade_fee = 1950.0, \
                      currency_type = bot_ex.CURRENCY_JPY, \
                      share = 48.866, \
                      fund_nav = 7319.0, \
                      exchange_rate = 0.2796, \
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
    currency_type = bot_ex.CURRENCY_JPY
    date_since = date.today() - relativedelta(months=+8) - relativedelta(days=+1)
    fund = FundClearModel.get_fund(fund_id)
    exchange = bot_ex.BotExchangeInfoModel.get_bot_exchange(currency_type) 
    
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
