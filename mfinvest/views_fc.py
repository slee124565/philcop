from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from datetime import date
from dateutil.relativedelta import relativedelta

from fundclear.fcreader import get_fundcode_list, get_fundcode_dictlist
from fundclear.models import FundClearModel
#from fundclear.fundreview.models import FundReviewModel
#from fundreview2.models import FundReviewModel
from utils.util_bollingerbands import get_bollingerbands
from utils.util_date import get_sample_date_list_2

from fundclear2.models import FundClearInfoModel,FundClearDataModel
import fundclear2.models as fc2
import fundclear2.tasks as fc2task
from fundcodereader.models import FundCodeModel
from indexreview.models import IndexReviewModel

import logging, calendar, collections

BB_VIEW_MONTHS = 12
BB_TYPE_DAILY = 'daily'
BB_TYPE_WEEKLY = 'weekly'

def list_all_fund_view(request):
    t_fundcode_list = FundCodeModel.get_codename_list()
    
    content_head_list = ['Code', 'Name', 'BB View', 'NAV View', 'Update', 'Year Detail','SRC View']
    content_rows = []
    this_year = date.today().year
    t_begin_date = date(this_year-2,1,1).strftime("%Y/%m/%d")
    t_end_date = date.today().strftime("%Y/%m/%d")
    
    for t_entry in t_fundcode_list:
        #t_entry[2] = '<a href="/mf/bb/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        #t_entry[2] = '<a href="/fc/flot/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        src_url = fc2.URL_TEMPLATE.format(fund_id=t_entry[0],
                                          begin_date=t_begin_date,
                                          end_date=t_end_date)
        content_rows.append([
                             t_entry[0],
                             t_entry[1],
                             '<a href="/mf/fc/bb/'+t_entry[0]+'/">BB View</a>',
                             '<a href="/mf/fc/nav/'+t_entry[0]+'/">NAV View</a>',
                             '<a target="_blank" href="{}">Reload</a>'.format(
                                                        fc2task.get_reload_funddata_taskhandler_url(
                                                                    p_fund_id=t_entry[0]
                                                                    )
                                                        ),
                             '<a href="/mf/fc/nav_str/{}/{}/">{}</a>'.format(t_entry[0],
                                                                             date.today().year,
                                                                             date.today().year),
                             '<a target="_blank" href="{}">View</a>'.format(src_url),
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

def fund_nav_str_view(request,p_fund_id,p_year):
    try:
        t_fund = FundClearInfoModel.get_fund(p_fund_id)
        t_fdata = FundClearDataModel.get_by_key_name(
                                                    FundClearDataModel.compose_key_name(p_fund_id, p_year),
                                                    t_fund)
        nav_dict = t_fdata._get_nav_dict()
        nav_dict = collections.OrderedDict(sorted(nav_dict.items()))
        nav_info = ''
        for t_key, t_entry in nav_dict.items():
            nav_info += '{}:{}<br>\n'.format(t_key,t_entry)
        next_year = int(p_year) - 1
        t_fdata = FundClearDataModel.get_by_key_name(
                                                    FundClearDataModel.compose_key_name(p_fund_id, next_year),
                                                    t_fund)
        if t_fdata is None or len(t_fdata._get_nav_dict())==0:
            next_year_link = 'NAV End'
        else:
            next_year_link = '<a href="/mf/fc/nav_str/{}/{}/">{}</a>'.format(p_fund_id,
                                                                         next_year,
                                                                         'next')
        args = {
                'tpl_section_title': 'fund {} year {}, {}'.format(p_fund_id
                                                                ,p_year,
                                                                next_year_link),
                'tpl_info': nav_info,
                }
        return render_to_response('mf_simple_info.tpl.html',args)
        
    except Exception, e:
        err_msg = 'fund_nav_str_view ERROR: {}'.format(e)
        logging.error(err_msg)
        args = {
                'tpl_info': err_msg,
                }
        return render_to_response('mf_simple_info.tpl.html',args)
    
def nav_view(request,p_fund_id):
    
    f_fund_id = p_fund_id
    
    t_fund = FundClearInfoModel.get_fund(f_fund_id)
    year_since = date.today().year - 3
    t_fund.get_value_list(year_since)
    t_review = IndexReviewModel.get_index_review(t_fund)
    
    if t_review is None:
        args = {
                'tpl_img_header' : FundCodeModel.get_fundname(f_fund_id),
                }
        return render_to_response('mf_my_japan.tpl.html', args)
    
    t_content_heads = []
    t_content_rows = {}
    
    t_nav_list = list(t_review.index_list())
    for t_entry in t_nav_list:
        t_content_rows[t_entry[0].strftime('%Y%m%d')] = (t_entry[0].strftime('%Y/%m/%d'),)
        t_content_rows[t_entry[0].strftime('%Y%m%d')] += (t_entry[1],)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
    t_content_heads.append('Date')
    t_content_heads.append('NAV')
    
    t_yoy_1_list = list(t_review.yoy_list(1))
    for t_entry in t_yoy_1_list:
        t_content_rows[t_entry[0].strftime('%Y%m%d')] += ('{:.2f}%'.format(t_entry[1]),)
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000 
    t_content_heads.append('YoY_1')
    
    t_yoy_2_list = list(t_review.yoy_list(2))
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
            'tpl_img_header' : FundCodeModel.get_fundname(f_fund_id),
            'tpl_section_title' : _("HEAD_FUND_REVIEW"), #_("TITLE_NAV_REVIEW_DETAIL"), 
            'plot' : plot,
            'tbl_content' : tbl_content,
            }

    return render_to_response('mf_my_japan.tpl.html', args)
    
    
def bb_view(request,p_fund_id,p_b_type=BB_TYPE_DAILY,p_timeframe=None,p_sdw=None):
    if p_b_type == BB_TYPE_DAILY:
        if p_timeframe is None:
            p_timeframe = 18
            p_sdw = 100
        return _bb_view(p_fund_id, p_b_type, p_timeframe, p_sdw)
    else:
        if p_timeframe is None:
            p_timeframe = 5
            p_sdw = 85
        return _bb_view(p_fund_id, p_b_type, p_timeframe, p_sdw)
    
def _bb_view(p_fund_id,p_b_type,p_timeframe,p_sdw):
    func = '{} {}'.format(__name__,'_bb_view')
    t_fund = FundClearInfoModel.get_fund(p_fund_id)

    if p_b_type == BB_TYPE_DAILY:
        BB_VIEW_MONTHS = 7
        t_date_since = date.today() + relativedelta(months=-(BB_VIEW_MONTHS*2))
        year_since = t_date_since.year
        t_value_list = t_fund.get_value_list(year_since)
        t_index = [row[0] for row in t_value_list].index(t_date_since)
        t_value_list = t_value_list[t_index:]
    else: #-> BB_TYPE_WEEKLY
        BB_VIEW_MONTHS = 14
        t_date_since = date.today() + relativedelta(months=-(2*BB_VIEW_MONTHS))
        t_offset = 2 - t_date_since.weekday()
        t_date_since += relativedelta(days=t_offset)
        t_date_list = []
        while t_date_since <= date.today():
            t_date_list.append(t_date_since)
            t_date_since += relativedelta(days=+7)
        t_value_list = t_fund.get_sample_value_list(t_date_list)

    sma,tb1,tb2,bb1,bb2 = get_bollingerbands(t_value_list,p_timeframe,float(p_sdw)/100)

    t_content_heads = ['Date','NAV','BB2','BB1','SMA','TB1','TB2']
    t_content_rows = {}

    t_view_date_since = date.today() + relativedelta(months=-BB_VIEW_MONTHS)
    t_ndx = 0

    for ndx2, t_list in enumerate([t_value_list,bb2,bb1,sma,tb1,tb2]):
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
            'tpl_img_header' : t_fund.title, # FundCodeModel.get_fundname(p_fund_id),
            'plot' : plot,
            'tpl_section_title' :  'Fund {} View ;{}; TF:{}; SD_W: {}'.format(
                                                                    p_b_type,
                                                                    p_fund_id,
                                                                    p_timeframe,
                                                                    p_sdw),
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
