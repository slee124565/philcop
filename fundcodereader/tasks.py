from google.appengine.api import taskqueue

from django.http import HttpResponse

from fundcodereader.models import FundCodeModel
import fundcodereader.models as fr
import logging, httplib

def update_codelist(request):
    fname = '{} {}'.format(__name__,'update_codelist')
    logging.info('{}: add download task'.format(fname))
    
    response = HttpResponse(fname)
    taskqueue.add(method = 'GET', 
                      url = fr.get_update_handler_url() ,
                      countdown = 2,
                      )
    response.status_code = httplib.OK
    return response

def update_fundcode_taskhandler(request):
    fname = '{} {}'.format(__name__,'download_fundcode_taskhandler')
    logging.info('{}: task start'.format(fname))
    
    response = HttpResponse('download_fundcode_taskhandler')

    if FundCodeModel._update_from_web():
        response.status_code = httplib.OK
        logging.info('download_fundcode success')
    else:
        response.status_code = httplib.INTERNAL_SERVER_ERROR
        logging.warning('download_fundcode fail!')
    
    return response

    