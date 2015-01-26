from google.appengine.api import taskqueue

from django.http import HttpResponse
import httplib

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

from twse_gae.models_stock import StockModel
import logging, os

def update_model(request):
    fname = '{} {}'.format(__name__,'update_model')
    response = HttpResponse(fname)

    taskqueue.add(method = 'GET', 
          url = os.path.dirname(os.path.dirname(request.get_full_path())) + "/update_task/",
          countdown = date.today().day % 5)
    
    response.status_code = httplib.OK 
    return response

def update_model_taskhandler(request):
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
                  url = os.path.dirname(os.path.dirname(request.get_full_path())) + "/update_task/",
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