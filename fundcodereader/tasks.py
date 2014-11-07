from django.http import HttpResponse

from fundcodereader.models import FundCodeModel
import fundcodereader.models as fr
import logging

def download_fundcode(request):
    response = HttpResponse('download_fundcode')
    if FundCodeModel._update_from_web():
        response.status_code = fr.HTTP_STATUS_CODE_OK
        logging.info('download_fundcode success')
    else:
        response.status_code = fr.HTTP_STATUS_CODE_SERVER_ERROR
        logging.warning('download_fundcode fail!')
    
    return response