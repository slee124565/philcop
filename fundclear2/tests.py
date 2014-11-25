#from django.test import TestCase
from django.http import HttpResponse
from models import FundClearDataModel, FundClearInfoModel
from datetime import date

import logging

def test_get_fund_with_err_id(request):
    fund_id = '0'
    fund = FundClearInfoModel.get_fund(fund_id)
    response = HttpResponse(content_type='text/plain')
    if fund is None:
        response.content = 'no fund for id {fund_id}'.format(fund_id=fund_id)
    else:
        response.content = 'get fund:\n' + str(fund.nav_year_dict.items())
    return response
    
def test_load_all_nav(request):
    fund_id = 'LU0069970746'
    t_fund = FundClearInfoModel.get_fund(fund_id)
    t_fund.load_all_nav()
    return HttpResponse('test_load_all_nav: check log')
    
    
def test_get_nav_by_date(request):
    fund_id = '618344' #'CIFGHIOT'
    fund = FundClearInfoModel.get_fund(fund_id)
    
    t_date = date(2014,1,1)
    t_date = date(2014,11,4)
    t_content = 'date {t_date} nav is {nav}\n'.format(
                                                    t_date=str(t_date),
                                                    nav=fund.get_nav_by_date(t_date))

    value_list = fund.get_value_list(t_date.year)
    for t_entry in value_list:
        t_content += str(t_entry) + '\n'

    response = HttpResponse(content_type='text/plain')
    response.content = t_content
    return response
    
    
    
def test_get_value_list(request):
    fund_id = '618344' #'CIFGHIOT'
    fund_id = request.REQUEST['id']
    fund = FundClearInfoModel.get_fund(fund_id)
    year_since = date.today().year - 5
    value_list = fund.get_value_list(year_since)
    t_content = ''
    for t_entry in value_list:
        t_content += str(t_entry) + '\n'
    
    response = HttpResponse(content_type='text/plain')
    response.content = t_content
    return response
    
    
def test_load_year_nav(reqeust):
    fund_id = '618344' #'CIFGHIOT'
    fund = FundClearInfoModel.get_fund(fund_id)
    t_content = ''
    t_year = 2013
    if fund._load_year_nav(t_year):
        t_content += 'load year nav {year} success\n'.format(year=t_year)
    else:
        t_content += 'load year nav {year} fail\n'.format(year=t_year)
        
    t_year = 2012
    if fund._load_year_nav(t_year):
        t_content += 'load year nav {year} success\n'.format(year=t_year)
    else:
        t_content += 'load year nav {year} fail\n'.format(year=t_year)

    t_content += str(str(fund.nav_year_dict['2013'].values()))
    response = HttpResponse(content_type='text/plain')
    #response.content = str(fund.nav_year_dict.items())
    response.content = t_content
    return response
    
    
def test_update_from_web(request):
    fund_id = '618344'
    year = date.today().year
    
    response = HttpResponse(content_type='text/plain')
    
    #fundinfo = FundClearInfoModel.get_by_key_name(FundClearInfoModel.compose_key_name(fund_id))
    #if fundinfo.title != '':
    #    response.content = fundinfo.title.encode('utf-8')
    #return response
    
    result = FundClearDataModel._update_from_web(fund_id,year)
    if result :
        fundinfo = FundClearInfoModel.get_by_key_name(FundClearInfoModel.compose_key_name(fund_id))
        fund = FundClearDataModel.get_by_key_name(FundClearDataModel.compose_key_name(fund_id, year),
                                                  parent=fundinfo)
        response.content = fund.content_csv
    else:
        response.content = 'FundClearModel.get_by_key_name() Fail'
        
    return response

def test_get_fund(request):
    fund_id = 'CIFGHIOT'
    fund = FundClearInfoModel.get_fund(fund_id)
    response = HttpResponse(content_type='text/plain')
    #response.content = str(fund.nav_year_dict.items())
    response.content = str(fund.nav_year_dict.items())
    return response
    
    