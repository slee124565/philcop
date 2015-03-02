from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from datetime import date
from dateutil.relativedelta import relativedelta

from utils.util_bollingerbands import get_bollingerbands

from twse_gae.models_stock import StockModel
from twse_gae.models_tw50 import TW50Model

import logging, calendar, collections


def get_stk_wk_bb_area(p_stk_no):
    fname = '{} {}'.format(__name__,'t_stock = StockModel.get_stock(p_stk_no)')
    if StockModel.check_db_exist(p_stk_no) == False:
        return 'Need Update'
    t_stock = StockModel.get_stock(p_stk_no)
    p_timeframe = 26
    p_sdw = 100
    t_date_since = date.today() + relativedelta(days=-(7*p_timeframe))
    t_offset = 2 - t_date_since.weekday()
    t_date_since += relativedelta(days=t_offset)
    t_date_list = []
    while t_date_since <= date.today():
        t_date_list.append(t_date_since)
        t_date_since += relativedelta(days=+7)
    t_value_list = t_stock.get_sample_index_list(t_date_list)
    t_current_nav = t_value_list[-1][1]
    sma,tb1,tb2,bb1,bb2 = get_bollingerbands(t_value_list,p_timeframe,float(p_sdw)/100)
    logging.debug('{}: curr {}, sma {}, tb1 {} ,tb2 {} , bb1 {}, bb2 {}'.format(fname,
                                                                                t_current_nav,
                                                                                sma[-1],
                                                                                tb1[-1],
                                                                                tb2[-1],
                                                                                bb1[-1],
                                                                                bb2[-1]))
    if t_current_nav < bb2[-1][1]:
        return 'BB3'
    elif t_current_nav < bb1[-1][1]:
        return 'BB2'
    elif t_current_nav < sma[-1][1]:
        return 'BB1'
    elif t_current_nav < tb1[-1][1]:
        return 'TB1'
    elif t_current_nav < tb2[-1][1]:
        return 'TB2'
    else:
        return 'TB3'
    
    
def list_view(request):
    tw50_id_list = TW50Model.get_id_list()
    
    content_head_list = ['ID', 'Name', 'Weekly BB Area', 'Weekly BB', 'Daily BB']
    content_rows = []
    
    for t_stk_no in tw50_id_list:
        #t_entry[2] = '<a href="/mf/bb/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        #t_entry[2] = '<a href="/fc/flot/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        content_rows.append([
                             t_stk_no,
                             StockModel.get_name_by_stk_no(t_stk_no),
                             get_stk_wk_bb_area(t_stk_no),
                             '<a href="/mf/twse/bb/' + t_stk_no + '/weekly/">BB Weekly View</a>',
                             '<a href="/mf/twse/bb/' + t_stk_no + '/daily/">BB Daily View</a>',
                             ])
    
    tbl_content = {
                   'heads': content_head_list,
                   'rows': content_rows,
                   }

    args = {
            'tpl_section_title': _("HEAD_TW50_BB_REVIEW"),
            'tbl_content' : tbl_content,
            }
    return render_to_response('mf_simple_table.tpl.html', args)
    