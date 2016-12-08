from google.appengine.api import taskqueue

from django.http import HttpResponse
import logging, os

from models import FundClearModel
from fcreader import get_fundcode_list

NUM_INDEX =0
CODE_INDEX = 1
NAME_INDEX = 2

def get_erase_model_all_url():
    return '/fc/task/erase_all/'

def erase_model_all(request):
    func = '{} {}'.format(__name__,'erase_model_all')
    entities = FundClearModel.all().fetch(limit=20)
    for t_entity in entities:
        t_entity.delete()
    if len(entities) == 20:
        taskqueue.add(method = 'GET', \
                      url = get_erase_model_all_url(), \
                      countdown = 3, \
                      )
    else:
        logging.info('{}: end of erase model all task'.format(func))
    
    return HttpResponse(func)
    
def update_all_taskhandler(request):
    logging.debug(__name__ + ', update_all_taskhandler activated')
    t_full_path = request.get_full_path()
    t_taskhandler_path = os.path.dirname(os.path.dirname(t_full_path)) + '/chain_update/'
    t_url = t_taskhandler_path
    taskqueue.add(method = 'GET', \
                  url = t_url, \
                  params = {
                            'index': 0
                            })
    t_msg = 'add task with handler url:\n' + t_taskhandler_path
    return HttpResponse(t_msg)
    
def chain_update_taskhandler(request):

    #-> get index
    t_index = int(request.REQUEST['index'])
    logging.info(__name__ + ', chain_update_taskhandler ' + request.method + ' with index ' + str(t_index))
    
    #-> update fund with t_index
    t_fund_info_list = get_fundcode_list()[:]
    #t_fund_info_list = [[0,'a','a1'],[1,'b','b1'],[2,'c','c1']]
    if t_index < len(t_fund_info_list):
        
        #-> udpate FundClearModel
        t_fundinfo = t_fund_info_list[t_index]
        logging.debug(__name__ + ', chain_update_taskhandler: fund code ' + t_fundinfo[CODE_INDEX])
        t_fund = FundClearModel.get_fund(t_fundinfo[CODE_INDEX])
        if t_fund is None:
            logging.info(__name__ + ', chain_update_taskhandler add update_task for fund_id ' + t_fundinfo[CODE_INDEX])
            t_taskhandler_path = os.path.dirname(os.path.dirname(request.get_full_path())) + '/update/' + t_fundinfo[CODE_INDEX] + '/'
            taskqueue.add(method = 'GET', \
                          url = t_taskhandler_path, \
                          countdown = 5, \
                          )
            

        #-> add next chain_task
        t_index += 1
        if t_index < len(t_fund_info_list):
            logging.debug(__name__ + ', chain_update_taskhandler add chain_task with index ' + str(t_index))
            #logging.debug(request.get_full_path())
            t_taskhandler_path = os.path.dirname(request.get_full_path()) + '/'
            t_url = t_taskhandler_path
            taskqueue.add(method = 'GET', \
                          url = t_url, \
                          countdown = 5, \
                          params = {
                                    'index': t_index
                                    })
        else:
            logging.debug(__name__ + ', chain_update_taskhandler: stop')
    else:
        logging.warning(__name__ + ', chain_update_taskhandler: index PARAM ERROR')
            
    t_response = HttpResponse()
    t_response.status_code = 200
    return t_response
    
def chain_update_test(request):
    logging.debug('chain_update_test enter')
    t_full_path = request.get_full_path()
    t_taskhandler_path = os.path.dirname(os.path.dirname(t_full_path)) + '/chain_update/'
    t_url = t_taskhandler_path
    taskqueue.add(method = 'GET', \
                  url = t_url, \
                  params = {
                            'index': 0
                            })
    t_msg = 'add task with handler url:\n' + t_taskhandler_path
    return HttpResponse(t_msg)
    
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