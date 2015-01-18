from google.appengine.api import taskqueue

from django.http import HttpResponse
import httplib

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

from twse_gae.models import TWSEStockModel
import twse_gae.models as twse

import logging, os

def add_stk_update_task(p_stk_no):
    func = '{} {}'.format(__name__,'add_stk_update_task')
    logging.info('{}: with stock {}'.format(func,p_stk_no))
    taskqueue.add(method = 'GET', 
                      url = twse.get_stk_update_handler_url() ,
                      countdown = 2,
                      params = {
                                'stk_no': p_stk_no,
                                })
    

def list_update_taskhandler(request):
    '''
    design for cron schedule updating all stock in CONFIG_STOCK_LIST
    '''
    
    func = '{} {}'.format(__name__,'update_taskhandler')
    response = HttpResponse(func)
    logging.info('{}: CONFIG_STOCK_LIST {}'.format(func,twse.CONFIG_STOCK_LIST))
    
    t_count = 2
    for t_stk_no in twse.CONFIG_STOCK_LIST:
        taskqueue.add(method = 'GET', 
                          url = twse.get_stk_update_handler_url() ,
                          countdown = t_count,
                          params = {
                                    'stk_no': t_stk_no,
                                    })
        t_count = (t_count+2) % 5

    response.status_code = httplib.OK
    return response

def reload_stk_task_handler(request):
    '''
    remove stock entity from db if exist
    start update task for stock
    '''
    func = '{} {}'.format(__name__,'reload_stk_task_handler')
    response = HttpResponse(func)
    t_stk_no = request.GET['stk_no']
    logging.info('{}: with stock {}'.format(func,t_stk_no))

    #-> delete db entity if exist
    t_entity = TWSEStockModel.get_by_key_name(TWSEStockModel.compose_key_name(t_stk_no))
    if not t_entity is None:
        t_entity.delete()

    #-> start chain task
    taskqueue.add(method = 'GET', 
                      url = twse.get_stk_update_handler_url() ,
                      countdown = 2,
                      params = {
                                'stk_no': t_stk_no,
                                })
        
    response.status_code = httplib.OK
    return response
    
            
def update_stk_taskhandler(request):
    '''
    start chain update task since last update date
    '''
    func = '{} {}'.format(__name__,'update_stk_taskhandler')
    response = HttpResponse(func)
    t_stk_no = request.GET['stk_no']

    logging.info('{}: with stock {}'.format(func,t_stk_no))
    t_last_ym = TWSEStockModel.get_stk_update_ym(t_stk_no)

    #-> start chain update task
    if t_last_ym == date.today().strftime('%Y%m'):
        logging.info('{}: stock {} already updted, task skipped'.format(func,t_stk_no))
    else:
        taskqueue.add(method = 'GET', 
                      url = twse.get_chain_update_handler_url() ,
                      countdown = 2,
                      params = {
                                'stk_no': t_stk_no,
                                'year_month': t_last_ym,
                                'type': 'all',
                                })

    response.status_code = httplib.OK
    return response
        

def cupdate_stk_taskhandler(request):
    '''
    fetch single month data and create next task for fetching next month data
    param: stk_no
    param: year_month, default = this_month
    param: type, default = None, if type == 'all', chain update all data
    '''
    func = '{} {}'.format(__name__,'cupdate_stk_taskhandler')
    response = HttpResponse('{}'.format(func))
    logging.debug(func)
    try:
        t_stk_no = request.GET['stk_no']
        t_year_month = request.GET['year_month']
        t_type = ''
        if 'type' in request.GET.keys():
            t_type = request.GET['type']
        
        logging.info('{}: start updating task for stock {} with month {} and type {}'.format(func,t_stk_no,t_year_month,t_type))
        
        if not TWSEStockModel.update_monthly_csv_from_web(t_stk_no,t_year_month,True) is None:
            logging.info('{}: update success.'.format(func))
            response.status_code = httplib.OK
            #-> add next chain task for next month
            if t_type == 'all':
                t_update_date = parser.parse(t_year_month[0:4]+'/'+t_year_month[4:]+'/01')
                t_next_month = t_update_date.date() + relativedelta(months=1)
                t_next_yearmonth = t_next_month.strftime('%Y%m')
                if t_next_yearmonth <= date.today().strftime('%Y%m'):
                    taskqueue.add(method = 'GET', 
                          url = os.path.dirname(request.get_full_path()) + "/",
                          countdown = 5,
                          params = {
                                    'stk_no': t_stk_no,
                                    'year_month': t_next_yearmonth,
                                    'type': t_type,
                                    })
                    logging.info('{}: add next chain update task; stock {}, month {}, type {}'.format(func,
                                                                                                    t_stk_no,
                                                                                                    t_next_yearmonth,
                                                                                                    t_type))
                else:
                    logging.info('{}: chain update complete for stock {}'.format(func,t_stk_no))
        else:
            logging.warning('{}: chain upate fail!'.format(func))
            response.status_code = httplib.INTERNAL_SERVER_ERROR
        
        return response
    except Exception, e:
        err_msg = str(e)
        logging.warning('{}: ERR {}'.format(func,err_msg))
        response.status_code = httplib.OK
        return response
    