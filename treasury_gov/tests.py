#from django.test import TestCase
from django.http import HttpResponse

from models import USTreasuryModel
import treasury_gov.models as us_treasury
from dateutil import parser

def test_get_yield_list_since(request):
    t_list = USTreasuryModel.get_yield_list_since(2008)
    t_result = ''
    
    for t_entry in t_list:
        t_result += str(t_entry) + "<br/>"
        
    return HttpResponse(t_result)
    
def test_get_tenor_list(request):
    return HttpResponse(str(USTreasuryModel.get_tenor_list()))
    
    
def test_get_yield_by_date(request):
    treasury = USTreasuryModel.get_treasury()

    t_date_str = '1/1/14'
    t_date = parser.parse(t_date_str)
    t_result = t_date_str + ':' + str(treasury.get_yield_by_date(t_date)) + '<br/>'
    
    t_date_str = '10/13/14'
    t_date = parser.parse(t_date_str)
    t_result += t_date_str + ':' + str(treasury.get_yield_by_date(t_date)) + '<br/>'
    return HttpResponse(t_result)
    
    
    
def test_get_yield_list_by_tenor(request):
    treasury = USTreasuryModel.get_treasury()
    t_result = ''
    for t_entry in treasury.get_yield_list_by_tenor(us_treasury.TREASURY_TENOR_10Y):
        t_result += str(t_entry) + '<br/>'
    return HttpResponse(t_result)
    
def test_get_treasury(request):
    treasury = USTreasuryModel.get_treasury('2013')
    t_result = ''
    for row in treasury.treasury_dict:
        t_result += str(row[us_treasury.TREASURY_ITEM_KEY_DATE]) + ' : ' + str(row[us_treasury.TREASURY_TENOR_10Y]) + '<br/>'
    
    return HttpResponse(t_result)

def test_update_from_web(request):
    t_test = USTreasuryModel._update_from_web()
    return HttpResponse(t_test)