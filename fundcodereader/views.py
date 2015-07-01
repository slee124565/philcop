from django.http import HttpResponse

from models import FundCodeModel

def codename_list(self):
    response = HttpResponse(content_type='text/plain')
    t_content = ''
    t_list = FundCodeModel.get_codename_list()
    for t_entry in t_list:
        t_code,t_name = t_entry
        t_content += t_code + ',' + t_name + '\n'
        
    response.content = t_content
    return response