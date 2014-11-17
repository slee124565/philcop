from django.shortcuts import render_to_response
#from django.http import HttpResponse
from bis_org.models import BisEersModel
from utils import util_bollingerbands
from django.utils.translation import ugettext as _
import calendar

def eers_view(request, p_code='TW'):
    bis_eers = BisEersModel.get_broad_indices()
    p_area = bis_eers._get_area_name(p_code)
    area_eers = bis_eers.get_area_real_bis_eers(p_area)

    t_value_list = area_eers[p_area]
    #return HttpResponse(str(t_value_list[-24:]))
    
    #-> indices table content
    content_head_list = ['Date', 'Indices']
    content_rows = []
    for t_entry in t_value_list[-24:]:
        content_rows.append([t_entry[0].strftime('%Y/%m/%d'), t_entry[1]])
    tbl_content = {
                   'heads': content_head_list,
                   'rows': content_rows,
                   }

    #-> indices BB content
    sma,tb1,tb2,bb1,bb2 = util_bollingerbands.get_bollingerbands(t_value_list)

    for ndx2, t_list in enumerate([t_value_list,sma,tb1,tb2,bb1,bb2]):
        for ndx,t_entry in enumerate(t_list):
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000

    plot = {
            'data': '{data: ' + str(sma).replace('L', '') + \
                            ', label: "SMA", color: "black", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(t_value_list).replace('L', '') + \
                            ', label: "Indices", color: "blue", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(tb1).replace('L', '') + \
                            ', label: "TB1", color: "yellow", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(tb2).replace('L', '') + \
                            ', label: "TB2", color: "red", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(bb1).replace('L', '') + \
                            ', label: "BB1", color: "yellow", lines: {show: true}, yaxis: 4},' + \
                    '{data: ' + str(bb2).replace('L', '') + \
                            ', label: "BB2", color: "red", lines: {show: true}, yaxis: 4},' 
            }
    
    args = {
            'tpl_img_header' :  p_area + ' BIS EERs Indices Bollinger Band Review',
            'plot' : plot,
            'tpl_section_title' : _('BIS EERs Indices'), 
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
