from django.http import HttpResponse
from django.shortcuts import render_to_response
from datetime import date
from dateutil.relativedelta import relativedelta

from fundclear.models import FundClearModel
from utils import util_bollingerbands

from bis_org.models import BisEersModel

from treasury_gov.models import USTreasuryModel
import treasury_gov.models as us_treasury

import calendar, logging

def treasury_view(request,year_since=date.today().year):
    
    tenor_list = [ \
                  us_treasury.TREASURY_TENOR_1M, \
                  #us_treasury.TREASURY_TENOR_3M, \
                  us_treasury.TREASURY_TENOR_1Y, \
                  us_treasury.TREASURY_TENOR_10Y, \
                  us_treasury.TREASURY_TENOR_30Y, \
                  ]
    plot_data = ''
    for tenor in tenor_list:
        yield_list = USTreasuryModel.get_yield_list_since(year_since, tenor)
        for t_entry in yield_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
        plot_data += '{data: ' + str(yield_list).replace('L', '') + \
                            ', label: "'+tenor+'", lines: {show: true}},\n'
    plot = {
            'data': plot_data 
            }

    args = {
            'flot_title' : 'US Treasury Yield',
            'plot' : plot,
            }
    
    return render_to_response('bis_org.html',args)

def bis_bb_view(request, p_code):
    bis_eers = BisEersModel.get_broad_indices()
    p_area = bis_eers._get_area_name(p_code)
    area_eers = bis_eers.get_area_real_bis_eers(p_area)

    t_value_list = area_eers[p_area]
    #return HttpResponse(str(t_value_list))
    sma,tb1,tb2,bb1,bb2 = util_bollingerbands.get_bollingerbands(t_value_list)

    for ndx2, t_list in enumerate([t_value_list,sma,tb1,tb2,bb1,bb2]):
        for ndx,t_entry in enumerate(t_list):
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000

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
            'page_title' : 'BIS EERs Indices Bollinger Band Review',
            'fund_title' : p_area + ' BIS EERs Indices Bollinger Band Review',
            'plot' : plot,
            }
    
    return render_to_response('bollinger_band.html',args)

    
def bis_org_view(request):
    area_list = ['Chinese Taipei','China','Japan','United States','Korea','Euro area', 'United Kingdom',]
    bis_eers = BisEersModel.get_broad_indices()
    area_eers = bis_eers.get_area_real_bis_eers(area_list)
    
    t_view_date_since = date.today() + relativedelta(years=-2)
    t_ndx = 0

    t_data = ''
    for t_area in area_list:
        for ndx, t_entry in enumerate(area_eers[t_area]):
            if t_entry[0] < t_view_date_since:
                t_ndx = ndx
            else:
                t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
        area_eers[t_area]
        del area_eers[t_area][:(t_ndx+1)]
        t_data += '{data: ' + str(area_eers[t_area]).replace('L', '') + \
                            ', label: "'+t_area+'", lines: {show: true},},'
    plot = {
            'data': t_data 
            }

    args = {
            'flot_title' : 'BIS Real EERs',
            'plot' : plot,
            }
    
    return render_to_response('bis_org.html',args)

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
    