from django.http import HttpResponse
from django.shortcuts import render_to_response
from datetime import date
from dateutil.relativedelta import relativedelta

from fundclear.models import FundClearModel
from utils import util_bollingerbands

import calendar, logging


def bollinger_band_view(request, p_fund_id):
    
    t_fund = FundClearModel.get_fund(p_fund_id)
    if t_fund is None:
        return HttpResponse('FundClearModel.get_fund fail; fund id: ' + p_fund_id)

    t_value_list = t_fund.get_value_list()
    sma,tb1,tb2,bb1,bb2 = util_bollingerbands.get_bollingerbands(t_value_list)
    
    t_view_date_since = date.today() + relativedelta(months=-2)
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
            'page_title' : 'Bollinger Band Review',
            'fund_title' : FundClearModel.get_by_key_name(p_fund_id).fund_name,
            'fund_id' : p_fund_id,
            'plot' : plot,
            }
    
    return render_to_response('bollinger_band.html',args)
    