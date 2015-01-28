from google.appengine.api import taskqueue

from django.http import HttpResponse
import httplib

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

import twse_gae
from twse_gae.models_stock import StockModel
from twse_gae.models_otc import OTCStockModel
from twse_gae.models import TWSEStockModel

import logging, os

'''
cron task for both TWSEStockModel and OTCStockModel
usage:
    def add_stk_update_task(p_stk_no):
        add a task for chain update stock data

    def cron_update_taskhandler(request):
        add chain update task for each id in twse_gae.models_stock.CONFIG_STOCK_LIST
    
    def reload_stk_task_handler(request):
        remove stock DB model entity with ID stk_no and add a chain update task
        
    def update_stk_taskhandler(request):
        add chain update task for stock ID stk_no from year month: get_stk_update_ym
    
    def cupdate_stk_taskhandler(request):
        add chain update task for stock ID stk_no from year month: year_month with type (all or else)
'''
def add_stk_update_task(p_stk_no):
    fname = '{} {}'.format(__name__,'add_stk_update_task')
    logging.info('{}: with stock {}'.format(fname,p_stk_no))
    taskqueue.add(method = 'GET', 
                      url = "/twse/task/stk_update/" ,
                      countdown = date.today().day % 5,
                      params = {
                                'stk_no': p_stk_no,
                                })

def cron_stk_update_taskhandler(request):
    '''
    design for cron schedule updating all stock in CONFIG_STOCK_LIST
    '''
    
    fname = '{} {}'.format(__name__,'cron_stk_update_taskhandler')
    response = HttpResponse(fname)
    t_stk_list = twse_gae.models_stock.CONFIG_STOCK_LIST
    logging.info('{}: CONFIG_STOCK_LIST {}'.format(fname,t_stk_list))
    
    for t_stk_no in t_stk_list:
        taskqueue.add(method = 'GET', 
                          url = os.path.dirname(os.path.dirname(request.get_full_path())) + "/stk_update/" ,
                          countdown = date.today().day % 5,
                          params = {
                                    'stk_no': t_stk_no,
                                    })

    response.status_code = httplib.OK
    return response

def reload_stk_task_handler(request):
    '''
    remove stock entity from db if exist
    start update task for stock
    '''
    fname = '{} {}'.format(__name__,'reload_stk_task_handler')
    response = HttpResponse(fname)
    t_stk_no = request.GET['stk_no']
    logging.info('{}: with stock {}'.format(fname,t_stk_no))

    #-> delete db entity if exist
    t_stk_type = StockModel.get_type_by_stk_no(t_stk_no)
    if t_stk_type == StockModel.STOCK_TYPE_TWSE:
        t_entity = TWSEStockModel.get_by_key_name(TWSEStockModel.compose_key_name(t_stk_no))
    elif t_stk_type == StockModel.STOCK_TYPE_OTC:
        t_entity = OTCStockModel.get_by_key_name(TWSEStockModel.compose_key_name(t_stk_no))
    else:
        response.content = 'stk_no {} ERROR'.format(t_stk_no)
        logging.warning('{}: stk_no {} ERROR'.format(fname,t_stk_no))
        return response
        
        
    if not t_entity is None:
        t_entity.delete()

    #-> start chain task
    taskqueue.add(method = 'GET', 
                      url = os.path.dirname(os.path.dirname(request.get_full_path())) + "/stk_update/" ,
                      countdown = date.today().day % 5,
                      params = {
                                'stk_no': t_stk_no,
                                })
        
    response.status_code = httplib.OK
    return response

def update_stk_taskhandler(request):
    '''
    start chain update task since last update date
    '''
    fname = '{} {}'.format(__name__,'update_stk_taskhandler')
    response = HttpResponse(fname)
    response.status_code = httplib.OK
    t_stk_no = request.GET['stk_no']

    logging.info('{}: with stock {}'.format(fname,t_stk_no))
    t_stk_type = StockModel.get_type_by_stk_no(t_stk_no)
    if t_stk_type == StockModel.STOCK_TYPE_TWSE:
        t_last_ym = TWSEStockModel.get_stk_update_ym(t_stk_no)
    elif t_stk_type == StockModel.STOCK_TYPE_OTC:
        t_last_ym = OTCStockModel.get_stk_update_ym(t_stk_no)
    else:
        response.content = 'stk_no {} ERROR'.format(t_stk_no)
        logging.warning('{}: stk_no {} ERROR'.format(fname,t_stk_no))
        return response
        

    #-> start chain update task
    if t_last_ym == date.today().strftime('%Y%m'):
        logging.info('{}: stock {} already updted, task skipped'.format(fname,t_stk_no))
    else:
        taskqueue.add(method = 'GET', 
                      url = os.path.dirname(os.path.dirname(request.get_full_path())) + "/stk_cupdate/" ,
                      countdown = date.today().day % 5,
                      params = {
                                'stk_no': t_stk_no,
                                'year_month': t_last_ym,
                                'type': 'all',
                                })

    response.status_code = httplib.OK
    return response

def cupdate_stk_taskhandler(request):
    fname = '{} {}'.format(__name__,'cupdate_stk_taskhandler')
    response = HttpResponse(fname)
    logging.debug('{} active'.format(fname))
    try:
        t_stk_no = request.GET['stk_no']
        t_year_month = request.GET['year_month']
        t_type = ''
        if 'type' in request.GET.keys():
            t_type = request.GET['type']
        
        logging.info('{}: chain update task for stock {} with month {} and type {}'.format(fname,
                                                                                           t_stk_no,
                                                                                           t_year_month,
                                                                                           t_type))
        t_stk_type = StockModel.get_type_by_stk_no(t_stk_no)
        if t_stk_type is None:
            t_msg = '{}: stock {} type unknown'.format(fname,t_stk_no)
            logging.warning(t_msg)
            response.content = t_msg
            return response
        
        if t_stk_type == StockModel.STOCK_TYPE_TWSE:
            t_update_result = TWSEStockModel.update_monthly_csv_from_web(t_stk_no,t_year_month,True)
        else: #->StockModel.STOCK_TYPE_OTC
            t_update_result = OTCStockModel.update_monthly_csv_from_web(t_stk_no,t_year_month,True)
        
        if t_update_result is None:
            logging.warning('{}: chain update task fail!'.format(fname))
            response.status_code = httplib.INTERNAL_SERVER_ERROR
        else:
            logging.info('{}: chain update success.'.format(fname))
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
                    logging.info('{}: add next chain update task; stock {}, month {}, type {}'.format(fname,
                                                                                                    t_stk_no,
                                                                                                    t_next_yearmonth,
                                                                                                    t_type))
                else:
                    logging.info('{}: chain update complete for stock {}'.format(fname,t_stk_no))
        
        return response
    except Exception, e:
        err_msg = str(e)
        logging.warning('{}: ERR {}'.format(fname,err_msg))
        response.status_code = httplib.OK
        return response


#-> task for StockModel
def update_model(request):
    '''
    designed for GAE cron schedule activated
    '''
    fname = '{} {}'.format(__name__,'update_model')
    response = HttpResponse(fname)

    taskqueue.add(method = 'GET', 
          url = os.path.dirname(os.path.dirname(request.get_full_path())) + "/id_update/",
          countdown = date.today().day % 5)
    
    response.status_code = httplib.OK 
    return response

def update_model_taskhandler(request):
    '''
    designed for TWSE and OTC stock id update 
    '''
    fname = '{} {}'.format(__name__,'update_model_taskhandler')
    response = HttpResponse(fname)
    
    if 'type' in request.REQUEST.keys():
        t_type = request.REQUEST['type']
    else:
        t_type = StockModel.STOCK_TYPE_TWSE

    logging.info('{} with type {}'.format(fname,t_type))
    
    if not t_type in [StockModel.STOCK_TYPE_TWSE,StockModel.STOCK_TYPE_OTC]:
        logging.warning('{}: param type error')
        response.status_code = httplib.OK
        return response
    
    
    if (StockModel.update_from_web(t_type)):
        logging.info('{}: success'.format(fname))
        response.status_code = httplib.OK
        
        if t_type == StockModel.STOCK_TYPE_TWSE:
            taskqueue.add(method = 'GET', 
                  url = os.path.dirname(os.path.dirname(request.get_full_path())) + "/id_update/",
                  countdown = date.today().day % 5,
                  params = {
                            'type': StockModel.STOCK_TYPE_OTC,
                            })
        else:
            logging.info('{}: end of chain update.'.format(fname))
    else:
        logging.warning('{}: failed'.format(fname))
        response.status_code = httplib.INTERNAL_SERVER_ERROR
    
    
    return response    