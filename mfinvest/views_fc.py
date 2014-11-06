from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from datetime import date
from dateutil.relativedelta import relativedelta

from fundclear.fcreader import get_fundcode_list, get_fundcode_dictlist
from fundclear.models import FundClearModel
from fundclear.fundreview.models import FundReviewModel
from utils.util_bollingerbands import get_bollingerbands
from utils.util_date import get_sample_date_list_2

import logging, calendar, collections

BB_VIEW_MONTHS = 12

def list_all_fund_view(request):
    t_fundcode_list = get_fundcode_list()
    
    content_head_list = ['Code', 'Name', 'BB View', 'NAV View']
    content_rows = []
    
    for t_entry in t_fundcode_list:
        #t_entry[2] = '<a href="/mf/bb/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        #t_entry[2] = '<a href="/fc/flot/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        content_rows.append([
                             t_entry[1],
                             t_entry[2],
                             '<a href="/mf/fc/bb/'+t_entry[1]+'/">BB View</a>',
                             '<a href="/mf/fc/nav/'+t_entry[1]+'/">NAV View</a>',
                             ])
    
    tbl_content = {
                   'heads': content_head_list,
                   'rows': content_rows,
                   }

    args = {
            'tpl_section_title': _("HEAD_FUND_REVIEW"),
            'tbl_content' : tbl_content,
            }
    return render_to_response('mf_simple_table.tpl.html', args)


def nav_view(request,p_fund_id):
    
    f_fund_id = p_fund_id
    
    fund_review = FundReviewModel.flush_fund_review(f_fund_id)
    if fund_review is None:
        args = {
                'tpl_img_header' : FundClearModel.get_by_key_name(f_fund_id).fund_name, 
                }
        return render_to_response('mf_my_japan.tpl.html', args)
    
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
            'tpl_img_header' : FundClearModel.get_by_key_name(f_fund_id).fund_name, 
            'tpl_section_title' : _("HEAD_FUND_REVIEW"), #_("TITLE_NAV_REVIEW_DETAIL"), 
            'plot' : plot,
            'tbl_content' : tbl_content,
            }

    return render_to_response('mf_my_japan.tpl.html', args)
    
    
def bb_view(request,p_fund_id):
    t_fund = FundClearModel.get_fund(p_fund_id)
    if t_fund is None:
        args = {
                'tpl_img_header' : FundClearModel.get_by_key_name(p_fund_id).fund_name,
                }
        return render_to_response('mf_simple_flot.tpl.html',args)
    else:
        t_value_list = t_fund.get_value_list()
        sma,tb1,tb2,bb1,bb2 = get_bollingerbands(t_value_list)
        
        t_view_date_since = date.today() + relativedelta(months=-BB_VIEW_MONTHS)
        t_ndx = 0
    
        for ndx2, t_list in enumerate([t_value_list,sma,tb1,tb2,bb1,bb2]):
            for ndx,t_entry in enumerate(t_list):
                if t_entry[0] < t_view_date_since:
                    t_ndx = ndx
                else:
                    t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
            del t_list[:(t_ndx+1)]
        
            
        plot = {
                'data': '{data: ' + str(sma).replace('L', '') + \
                                ', label: "SMA", color: "black", lines: {show: true}, yaxis: 4},' + \
                        '{data: ' + str(t_value_list).replace('L', '') + \
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
                'tpl_img_header' : FundClearModel.get_by_key_name(p_fund_id).fund_name,
                'tpl_section_title' : ' ',
                'plot' : plot,
                }
        
        return render_to_response('mf_simple_flot.tpl.html',args)
    
    

