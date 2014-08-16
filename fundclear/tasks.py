from google.appengine.api import taskqueue

from django.http import HttpResponse
import logging, os

from models import FundClearModel

def update_taskhandler(request,fund_id):
    '''
    update FundClearModel for fund_id
    wity url = fc/task/update/[fund_id]
    '''
    logging.info(__name__ + ', update_taskhandler with fund_id ' + fund_id)
    t_fund = FundClearModel.get_fund(fund_id)
    t_response = HttpResponse()
    if (t_fund) is not None:
        t_response.status_code = 200
        logging.info(__name__ + ', update_taskhandler done')
    else:
        t_response.status_code = 500
        logging.warning(__name__ + ', update_taskhandler fail')
    
    return t_response
        
def update_test(request,fund_id):
    '''
    test update_taskhandler function
    '''
    logging.debug(__name__ + ', update_test with fund_id ' + fund_id)
    t_full_path = request.get_full_path()
    t_taskhandler_path = os.path.dirname(os.path.dirname(os.path.dirname(t_full_path))) + '/update/' + fund_id + '/'
    t_url = t_taskhandler_path
    taskqueue.add(url = t_url,method='GET')
    t_msg = 'add task with name ' + fund_id  + ' and handler url:\n' + t_taskhandler_path
    logging.info(__name__ + ', update_test ' + t_msg)
    return HttpResponse(t_msg)