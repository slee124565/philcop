from django.http import HttpResponse

from models import FundClearModel
from utils import util_bollingerbands

def test_movingaverage(request):
    t_fund = FundClearModel.get_fund('LU0069970746')
    if t_fund is None:
        return HttpResponse('FundClearModel.get_fund fail')
    t_value_list = t_fund.get_value_list()
    length = 30
    t_value_list = t_value_list[:length]
    t_str = ''
    
    for t_entry in t_value_list:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','

    t_str += '<br/>\n'
    for t_entry in t_value_list:
        t_str += str(t_entry[1]) + ','
    
    t_sma = util_bollingerbands.movingaverage(t_value_list)

    t_str += '<br/>\n'
    for t_entry in t_sma:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','
        
    t_str += '<br/>\n'
    for t_entry in t_sma:
        t_str += str(t_entry[1]) + ','
    
    return HttpResponse(t_str)

def test_standard_deviation(request):
    t_fund = FundClearModel.get_fund('LU0069970746')
    t_value_list = t_fund.get_value_list()
    length = 30
    t_value_list = t_value_list[:(length+1)]
    t_str = ''
    
    for t_entry in t_value_list:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','

    t_str += '<br/>\n'
    for t_entry in t_value_list:
        t_str += str(t_entry[1]) + ','
    
    t_standev = util_bollingerbands.standard_deviation(t_value_list)

    t_str += '<br/>\n'
    for t_entry in t_standev:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','
        
    t_str += '<br/>\n'
    for t_entry in t_standev:
        t_str += str(t_entry[1]) + ','
    
    return HttpResponse(t_str)

def test_bollinger_band(request):
    t_fund = FundClearModel.get_fund('LU0069970746')
    t_value_list = t_fund.get_value_list()
    length = 30
    t_value_list = t_value_list[:(length+1)]
    
    sma,tb1,tb2,bb1,bb2 = util_bollingerbands.get_bollingerbands(t_value_list)
    t_str = ''
    
    for t_entry in t_value_list:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','

    t_str += '<br/>\n'
    for t_entry in t_value_list:
        t_str += str(t_entry[1]) + ','

    t_str += '<br/>\n'
    for t_entry in tb2:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','

    t_str += '<br/>\n'
    for t_entry in tb2:
        t_str += str(t_entry[1]) + ','

    t_str += '<br/>\n'
    for t_entry in tb1:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','

    t_str += '<br/>\n'
    for t_entry in tb1:
        t_str += str(t_entry[1]) + ','

    t_str += '<br/>\n'
    for t_entry in sma:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','

    t_str += '<br/>\n'
    for t_entry in sma:
        t_str += str(t_entry[1]) + ','

    t_str += '<br/>\n'
    for t_entry in bb1:
        t_str += t_entry[0].strftime('%Y/%m/%d') + ','

    t_str += '<br/>\n'
    for t_entry in bb2:
        t_str += str(t_entry[1]) + ','

    return HttpResponse(t_str)
