from django.shortcuts import render_to_response
from django.http import HttpResponse

from datetime import date
from dateutil.relativedelta import relativedelta
import logging

from urlsrc.models import WebContentModel
from models import FundClearModel


URL_TEMPLATE = 'http://announce.fundclear.com.tw/MOPSFundWeb/D02_02P.jsp?fundId={fund_id}&beginDate={begin_date}&endDate={end_date}'

def flot_axes_time_view(request,fund_id):
    if (fund_id == ''):
        #fund_id = 'AJSCY3'
        logging.warn('PARAM [fund_id] ERROR')
        return HttpResponse('PARAM ERROR')

    end_date = date.today() - relativedelta(days=+1)
    begin_date = end_date - relativedelta(years=+1)
    url = URL_TEMPLATE.format(fund_id=fund_id,begin_date=begin_date.strftime("%Y/%m/%d"),end_date=end_date.strftime("%Y/%m/%d"))
    
    webHtml = FundClearModel.get_or_insert(fund_id)
    webHtml.url = url
    if ( (webHtml.expired_date == None) or (date.today() > webHtml.expired_date)):
        if (webHtml.do_urlfetch()):
            webHtml.expired_date = end_date
            webHtml.put()
        else:
            return HttpResponse('URL Fetch Fail!!!')
    else:
        logging.info('webHtml exist in datastore and not expired.')
    
    dataset = webHtml.get_dateset()
    html_table = webHtml.get_single_html_table()
    if dataset == None:
        return HttpResponse('Table Dataset Parsing Fail!!!')
    
    args = {
            #'fund_name' : fund_id,
            'fund_name' : webHtml.fund_name,
            'dataset': str(dataset).replace('L',''),
            'html_table': html_table
            }
    return render_to_response('flot_axes_time_view.html', args)

