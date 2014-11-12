from google.appengine.api import taskqueue

from django.http import HttpResponse
import indexreview.tasks as reviewtask

import os

def test_update_task(request):
    
    t_fund_index = 'LU0069970746'
    taskqueue.add(method = 'GET', 
                  url = reviewtask.get_fc_update_taskhandler_url(),
                  params = {
                            'PARAM1': t_fund_index,
                            })
    return HttpResponse('test_update_task')