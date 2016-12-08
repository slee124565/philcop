from django.http import HttpResponse

from datetime import date
from treasury_gov.models import USTreasuryModel

import treasury_gov.models as us_treasury
import logging

def update_treasury_taskhandler(request):
    '''
    update datastore for USTreasuryModel for the year request by Param p_year
    '''
    p_year = str(request.REQUEST['PARAM'])
    if p_year == '':
        p_year=date.today().year
        logging.info('update_treasury_taskhandler: no PARAM, set default (this year)')
        
    logging.info('update_treasury_taskhandler: with year {year} starting ...'.format(year=p_year))    
    response = HttpResponse('update_treasury_taskhandler')
    if USTreasuryModel._update_from_web(p_year):
        response.status_code = us_treasury.HTTP_STATUS_CODE_OK
        logging.info('update_treasury_taskhandler success')
    else:
        response.status_code = us_treasury.HTTP_STATUS_CODE_SERVER_ERROR
        logging.warning('update_treasury_taskhandler fail!')
        
    return response
    