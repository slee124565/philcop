from django.shortcuts import render_to_response
from django.http import HttpResponse

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging

from models import FundClearModel
from fcreader import get_fund_code_name, get_fund_info_list, save_fundcode_config, get_fundcode_list
import phicops.utils
import calendar

URL_TEMPLATE = 'http://announce.fundclear.com.tw/MOPSFundWeb/D02_02P.jsp?fundId={fund_id}&beginDate={begin_date}&endDate={end_date}'

def _test_get_fundcode_list(request):
    t_fundcode_list = get_fundcode_list()
    t_str = ''
    for t_fundcode in t_fundcode_list:
        t_str += t_fundcode[1] + ', ' + t_fundcode[2] + '<br/>' 
    return HttpResponse(t_str)

def _test_save_fundcode_config(request):
    return HttpResponse(save_fundcode_config())
    
def _test_get_fund_info_list(request):
    t_fund_info_list = get_fund_info_list()
    t_str = ''
    for t_fundinfo in t_fund_info_list:
        t_str += str(t_fundinfo) + '<br/>'
    return HttpResponse(t_str)
    
        
def _test_get_fund_code_name(request):
    codeName = get_fund_code_name()
    t_str = ''
    for code in codeName:
        t_str += code + ': ' + codeName[code] + '<br/>'
    return HttpResponse(t_str)

def _test_get_sample_value_list(request):
    #fund_id = 'AJSCY3'
    fund_id = 'LU0069970746'
    fund = FundClearModel.get_fund(fund_id)
    
    t_date_sample_start = datetime.now()- relativedelta(months=+12)
    date_begin = date(t_date_sample_start.year,t_date_sample_start.month+1,1) - relativedelta(days=+1)
    date_end = date(datetime.now().year,datetime.now().month,1) - relativedelta(days=+1)
    t_check_date = date_begin
    _sample_date_list = []
    while (t_check_date <= date_end):
        _sample_date_list.append(t_check_date)
        t_check_date = date(t_check_date.year,t_check_date.month,1) + relativedelta(months=+2) - relativedelta(days=+1)
    _sample_date_list.append(date.today() - relativedelta(days=+1))
    
    sample_value_list = fund.get_sample_value_list(_sample_date_list)
    return HttpResponse(str(sample_value_list))
    
def flot_axes_time_view(request,fund_id):
    if (fund_id == ''):
        #fund_id = 'AJSCY3'
        logging.warning('PARAM [fund_id] ERROR')
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
    
    #dataset = webHtml.get_dateset()
    dataset = webHtml.get_discrete_value_list(phicops.utils.MONTH_DAY_END)
    for t_entry in dataset:
        t_entry[0] = calendar.timegm((t_entry[0]).timetuple()) * 1000
    
    html_table = webHtml.get_single_html_table()
    if dataset == None:
        return HttpResponse('Table Dataset Parsing Fail!!!')
    
    args = {
            'page_title' : 'FundClear-' + fund_id,
            #'fund_name' : fund_id,
            'fund_name' : webHtml.fund_name,
            'dataset': str(dataset).replace('L',''),
            'html_table': html_table
            }
    return render_to_response('flot_axes_time_view.html', args)

