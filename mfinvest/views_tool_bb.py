from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from datetime import date
from dateutil.relativedelta import relativedelta

from utils.util_bollingerbands import get_bollingerbands
from utils.util_date import get_sample_date_list_2

import logging, calendar, collections

BB_VIEW_MONTHS = 12
BB_TYPE_DAILY = 'daily'
BB_TYPE_WEEKLY = 'weekly'

def _bb_view(p_model,p_title,p_b_type,p_timeframe,p_sdw):
    func = '{} {}'.format(__name__,'_bb_view')

    if p_b_type == BB_TYPE_DAILY:
        BB_VIEW_MONTHS = 7
        t_date_since = date.today() + relativedelta(months=-(BB_VIEW_MONTHS*2))
        year_since = t_date_since.year
        t_value_list = p_model.get_value_list(year_since)
    else: #-> BB_TYPE_WEEKLY
        BB_VIEW_MONTHS = 14
        t_date_since = date.today() + relativedelta(months=-(2*BB_VIEW_MONTHS))
        t_offset = 2 - t_date_since.weekday()
        t_date_since += relativedelta(days=t_offset)
        t_date_list = []
        while t_date_since <= date.today():
            t_date_list.append(t_date_since)
            t_date_since += relativedelta(days=+7)
        t_value_list = p_model.get_sample_value_list(t_date_list)

    sma,tb1,tb2,bb1,bb2 = get_bollingerbands(t_value_list,p_timeframe,float(p_sdw)/100)

    t_content_heads = ['Date','NAV','BB2','BB1','SMA','TB1','TB2']
    t_content_rows = {}
    t_lastdate = t_value_list[-1][0]

    t_view_date_since = date.today() + relativedelta(months=-BB_VIEW_MONTHS)
    t_ndx = 0

    for ndx2, t_list in enumerate([t_value_list,bb2,bb1,sma,tb1,tb2]):
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
        del t_list[:(t_ndx+1)]
    
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
        
    t_label = ' lastDate:{}, {},TF:{},SDW:{}'.format(str(t_lastdate),p_b_type,p_timeframe,p_sdw)    
    plot = {
            'data': '{data: ' + str(sma).replace('L', '') + \
                            ', label: "' + t_label + '", color: "black", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(t_value_list).replace('L', '') + \
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
            'tpl_img_header' : p_title, # FundCodeModel.get_fundname(p_fund_id),
            'plot' : plot,
            'tpl_section_title' :  '{} View ; TF:{}; SD_W: {}'.format(p_b_type,p_timeframe,p_sdw),
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
