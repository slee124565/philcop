from google.appengine.api import taskqueue

from django.http import HttpResponse
from datetime import date

from models import USTreasuryModel
import treasury_gov.models as us_treasury

import os,logging

def datastore_check_view(request):
    #TODO:
    t_html = ''
    t_list = []
    t_year = int(us_treasury.TREASURY_YEAR_SINCE)
    this_year = date.today().year
    while t_year <= this_year:
        t_treasury = USTreasuryModel.get_treasury(t_year)
        if str(t_treasury.content_csv) == '':
            t_list.append([str(t_year),False])
        else:
            t_list.append([str(t_year),True])
        t_year += 1
        
    t_list.sort(key=lambda x: x[0])
    #logging.debug(str(t_list))
    for t_entry in t_list:
        if t_entry[1]:
            t_html += 'treasury year {year} update success.'.format(year=t_entry[0]) + '<br/>\n'
        else:
            t_html += 'treasury year {year} update fail.'.format(year=t_entry[0]) + '<br/>\n'
            
    return HttpResponse(t_html)
    
def treasury_init_view(request):
    '''
    update datastore from year TREASURY_YEAR_SINCE by task queue
    '''
    TASK_HANDLER_URL =  os.path.dirname(os.path.dirname(request.get_full_path())) + '/task/update/'
    
    t_html = 'update_datastore_all_by_taskqueue since {year}'.format(year=us_treasury.TREASURY_YEAR_SINCE) + '<br/>\n'
    t_year = int(us_treasury.TREASURY_YEAR_SINCE)
    this_year = date.today().year
    while t_year <= this_year:
        taskqueue.add(method = 'GET', \
              url = TASK_HANDLER_URL, \
              countdown = 5, \
              params = {
                        'PARAM': t_year
                        })
        t_html += 'add update task into queue for US treasury year {year}'.format(year=t_year) + '<br/>\n'
        t_year +=1
    
    return HttpResponse(t_html)