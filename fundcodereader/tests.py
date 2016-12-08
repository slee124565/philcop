from django.http import HttpResponse

from models import FundCodeModel

def print_content(request):
    response = HttpResponse(content_type='text/plain')
    fundcode = FundCodeModel.get_or_insert('FundCodeModel')
    response.content = fundcode.change_content_csv_col_name()
    return response
    
def test_get_codename_list(request):
    response = HttpResponse(content_type='text/plain')
    t_content = 'test_get_codename_list\n'
    codename_list = FundCodeModel.get_codename_list()
    t_content += 'len: ' + str(len(codename_list)) + '\n'
    for t_entry in codename_list:
        #t_content = str(t_entry) + '\n'
        t_content += t_entry[0] + ',' + t_entry[1] + '\n'
    response.content = t_content
    return response

def test_get_fundname(request):
    response = HttpResponse(content_type='text/plain')
    t_content = 'test_get_fundname\n'
    codename_list = FundCodeModel.get_codename_list()
    for t_entry in codename_list[:10]:
        t_content += 'code ' + t_entry[0] + ' name is ' + FundCodeModel.get_fundname(t_entry[0]) + '\n'
    response.content = t_content
    return response
