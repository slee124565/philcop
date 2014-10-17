from django.http import HttpResponse

from models import BisEersModel
import logging
import bis_org

def update_bis_eers_taskhandler(request):
    '''
    task: check and update BIS EERs datastore from BIS website
    schedule: per week
    '''
    logging.info('update_bis_eers_task: starting ...')
    t_response = HttpResponse('update_bis_eers_taskhandler')    

    if BisEersModel.update_from_web():
        logging.info('update_bis_eers_task success.')
        t_response.status_code = bis_org.HTTP_STATUS_CODE_OK
    else:
        logging.warning('update_bis_eers_task fail.')
        t_response.status_code = bis_org.HTTP_STATUS_CODE_SERVER_ERROR

    return t_response
    