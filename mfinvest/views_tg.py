from django.shortcuts import render_to_response

from treasury_gov.models import USTreasuryModel

import treasury_gov.models as us_treasury
import calendar

def treasury_view(request,year_since=2000):
    
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
            'tpl_img_header' : 'US Treasury Yield',
            'plot' : plot,
            'tpl_section_title' : 'Developed by lee.shiueh@gmail.com',
            }
    
    return render_to_response('mf_simple_flot.tpl.html',args)
