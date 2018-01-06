from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View

from fundclear2.models import FundClearInfoModel, FundClearDataModel
import fundclear2.tasks as fundtask
from fundcodereader.models import FundCodeModel

import logging
import collections
import json

def current_nav(request,p_fund_id):
    '''
    get func latest NAV with id p_fund_id
    '''
    t_fund = FundClearInfoModel.get_fund(p_fund_id)
    t_list = t_fund.get_value_list()
    return HttpResponse(t_list[-1][1])
    
    
def datamodel_statistic_report_view(request):
    #response = HttpResponse(content_type='text/plain')
    response = HttpResponse()
    content = '<table border="1px solid black">'
    codename_list = FundCodeModel.get_codename_list()
    for t_code, t_name in codename_list[:]:
        ancestor = FundClearInfoModel.get_by_key_name(FundClearInfoModel.compose_key_name(t_code))
        if ancestor is None:
            t_count = 0
            t_years = ''
        else:
            t_funddata_query = FundClearDataModel.all().ancestor(ancestor).order('year')
            t_count = 0
            t_years = ''
            for t_funddata in t_funddata_query:
                t_count += 1
                if t_funddata.year is None:
                    t_years += '?,'
                else:
                    t_years += t_funddata.year + ', '
        t_report = '<tr><td width="10%" align="right">{}</td><td width="5%" align="right">{}</td><td width="50%">{}</td><td>{}</td></tr>\n'.format(
                                                                         t_code,
                                                                         t_count,
                                                                         t_name,
                                                                         t_years,
                                                                         )
        content += t_report
    
    content += '</table>'
    response.content = content
    return response

def fund_analysis_view(request, p_key=None):
    response = HttpResponse()
    codename_all = FundCodeModel.get_codename_list()
    t_count = 1
    t_table = '<table border="1px solid black">{}{}</table>\n'
    t_thead = ''
    t_tbody = ''
    t_keys = []
    for (t_code,t_name) in codename_all[:]:
        t_reviews = fundtask.get_analysis(t_code)
        if t_thead == '':
            t_thead = '<tr><td>No</td><td>ID</td><td>Name</td>\n'
            if p_key is None:
                for t_key in sorted(t_reviews.keys()):
                    t_thead += '<td>{}</td>'.format(t_key)
                    t_keys.append(t_key)
            else:
                if p_key in t_reviews.keys():
                    t_thead += '<td>{}</td>'.format(p_key)
                    t_keys.append(p_key)
                else:
                    response.content = 'key {} not exist!!!'.format(p_key)
                    return response
            t_thead += '</tr>\n'
        
        
        if p_key is None:
            t_row = '<tr><td>{}</td><td>{}</td><td>{}</td>'.format(t_count,t_code,t_name)
            for t_key in t_keys:
                t_row += '<td>{}</td>'.format(t_reviews[t_key])
            t_row += '</tr>\n'
            t_tbody += t_row
        else:
            if t_reviews[p_key]:
                t_row = '<tr><td>{}</td><td>{}</td><td>{}</td>'.format(t_count,t_code,t_name)
                for t_key in t_keys:
                    t_row += '<td>{}</td>'.format(t_reviews[t_key])
                t_row += '</tr>\n'
                t_tbody += t_row
        t_count += 1
    
    response.content = t_table.format(t_thead,t_tbody)
    return response

def datastore_fund_code_check_view(request):
    #TODO: object has fund code not in fundclear code list
    pass

    
def zero_nav_fund_list_view(request):
    response = HttpResponse(content_type='text/plain')
    fund_list = fundtask.get_zero_nav_fund_list()
    t_content = ''
    count = 1
    for t_entry in fund_list:
        t_content += str(count) + ', ' + t_entry[0] + ', ' + t_entry[1] + '\n'
        count += 1
    response.content = t_content
    return response

def year_nav_fund_list_view(request):
    response = HttpResponse(content_type='text/plain')
    fund_list = fundtask.get_year_nav_fund_list()
    t_content = ''
    for t_entry in fund_list:
        for t_cell in t_entry:
            t_content += '{}, '.format(t_cell) 
        t_content += '\n'
    response.content = t_content
    return response
    

def year_discontinuous_fund_list_view(request):
    response = HttpResponse(context_type='text/plain')
    fund_list = _get_year_discontinuous_fund_list()
    response.content = str(fund_list)
    return response
    
def _get_year_discontinuous_fund_list():
    #TODO: return a list of fund which has discontinuous year data
    fund_list = []
    
    return fund_list

def fund_id_not_in_list_view(request):
    response = HttpResponse(context_type='text/plain')
    fund_list = _get_fund_id_not_in_list()
    response.content = str(fund_list)
    return response
    
    
def _get_fund_id_not_in_list():
    #TODO: return a list of fund id which is in datastore but not in fundcodereader list
    code_list = []
    
    return code_list

class FundJsonView(View):
    
    def get(self, request, p_fund_id, p_year, *args, **kwargs):
        
        t_fund = FundClearInfoModel.get_fund(p_fund_id)
        t_fdata = FundClearDataModel.get_by_key_name(
                                                    FundClearDataModel.compose_key_name(p_fund_id, p_year),
                                                    t_fund)
        nav_dict = t_fdata._get_nav_dict()
        nav_dict = collections.OrderedDict(sorted(nav_dict.items()))
        json_nav = [ [key, nav_dict[key][1]] for key in nav_dict]
        
        return HttpResponse(json.dumps(json_nav,indent=2))

    def post(self, request, p_fund_id, p_year, *args, **kwargs):
        
        csv_content = request.POST.get('csv_content','').encode('utf-8')
        fund_title = request.POST.get('fund_title','')
        
        if csv_content == '' or fund_title == '':
            return HttpResponseBadRequest('Param Error\nfund_title length%d' %
                                          (len(fund_title)))
        
        FundClearDataModel.save_fund_csv_data(p_fund_id, p_year, fund_title, csv_content)
        
        return HttpResponse('OK')
    
    
    
    
    
    