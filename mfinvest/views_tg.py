from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from treasury_gov.models import USTreasuryModel
from utils.util_date import get_sample_date_list
import treasury_gov.models as us_treasury
import calendar, logging, collections

def treasury_view(request,year_since=2000):
    
    tenor_list = [ \
                  us_treasury.TREASURY_TENOR_1M, \
                  #us_treasury.TREASURY_TENOR_3M, \
                  us_treasury.TREASURY_TENOR_1Y, \
                  us_treasury.TREASURY_TENOR_10Y, \
                  us_treasury.TREASURY_TENOR_30Y, \
                  ]

    content_head_list = ['Date']
    plot_data = ''
    for tenor in tenor_list:
        content_head_list.append(tenor)
        yield_list = USTreasuryModel.get_yield_list_since(year_since, tenor)
        for t_entry in yield_list:
            t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
        plot_data += '{data: ' + str(yield_list).replace('L', '') + \
                            ', label: "'+tenor+'", lines: {show: true}},\n'
    
    treasury_dict = {}
    content_rows = {}
    date_list = get_sample_date_list()
    for t_date in date_list:
        t_year = t_date.year
        if str(t_year) in treasury_dict.keys():
            t_treasury = treasury_dict[str(t_year)]
        else:
            t_treasury = USTreasuryModel.get_treasury(t_year)
            treasury_dict[str(t_year)] = t_treasury
        content_rows[str(t_date)] = [t_date.strftime('%Y/%m/%d')]
        for tenor in tenor_list:
            content_rows[str(t_date)].append(t_treasury.get_yield_by_date(t_date,tenor))
    #logging.debug('treasury_dict.keys:\n' + str(treasury_dict.keys()))
    #logging.debug('content_head_list:\n' + str(content_head_list))
    #logging.debug('content_rows:\n' + str(content_rows))
    content_rows = collections.OrderedDict(sorted(content_rows.items()))
    tbl_content = {
                   'heads': content_head_list,
                   'rows': content_rows.values(),
                   }
    
    plot = {
            'data': plot_data 
            }

    args = {
            'tpl_img_header' : 'US Treasury Yield',
            'plot' : plot,
            'tpl_section_title' : _('TITLE_BOT_CURRENCY_CASH_SELL'), 
            'tbl_content' : tbl_content,
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
