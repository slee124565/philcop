from django.shortcuts import render_to_response
#from django.http import HttpResponse
from bis_org.models import BisEersModel
from indexreview.models import IndexReviewModel
from utils import util_bollingerbands
from django.utils.translation import ugettext as _
import calendar, collections

def eers_area_list_view(request):
    bis_eers = BisEersModel.get_broad_indices()
    
    content_head_list = ['Code', 'Name', 'BB View']
    content_rows = []
    
    for t_entry in bis_eers.area_list:
        #t_entry[2] = '<a href="/mf/bb/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        #t_entry[2] = '<a href="/fc/flot/'+t_entry[1]+'/">' + t_entry[2] + "</a>"
        content_rows.append([
                             t_entry[0],
                             t_entry[1],
                             '<a href="/mf/bis/'+t_entry[0]+'/">BB View</a>',
                             ])
    
    tbl_content = {
                   'heads': content_head_list,
                   'rows': content_rows,
                   }

    args = {
            'tpl_section_title': _("HEAD_BIS_EERS_REVIEW"),
            'tbl_content' : tbl_content,
            }
    return render_to_response('mf_simple_table.tpl.html', args)
    
    
def eers_view(request, p_code='TW'):
    bis_eers = BisEersModel.get_broad_indices()
    p_area = bis_eers._get_area_name(p_code)
    area_eers = bis_eers.get_area_real_bis_eers(p_area)

    t_value_list = area_eers[p_area]
    #return HttpResponse(str(t_value_list[-24:]))
    
    #-> indices table content
    content_head_list = ['Date', 'Indices', 'YoY']
    content_rows = {}
    yoy_list = IndexReviewModel.get_12_yoy_list(t_value_list,p_total_sample_count=25)
    for t_entry in t_value_list[-24:]:
        content_rows[t_entry[0].strftime('%Y%m%d')] = [t_entry[0].strftime('%Y/%m/%d'), t_entry[1],'N/A']
    for t_entry in yoy_list:
        content_rows[t_entry[0].strftime('%Y%m%d')][2] = '{:.2f}%'.format(t_entry[1])

    t_content_rows = collections.OrderedDict(sorted(content_rows.items()))
    tbl_content = {
                   'heads': content_head_list,
                   'rows': t_content_rows.values(),
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
