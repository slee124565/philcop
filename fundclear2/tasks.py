from django.http import HttpResponse
from google.appengine.api import taskqueue

from datetime import date

from fundclear2.models import FundClearDataModel, FundClearInfoModel
import fundclear2.models as fc2

import logging, os

def update_funddata_taskhandler(request):
    p_fund_id = str(request.REQUEST['PARAM1'])
    if 'PARAM2' in request.REQUEST.keys():
        p_year = str(request.REQUEST['PARAM2'])
    else:
        p_year=date.today().year
    if 'PARAM3' in request.REQUEST.keys():
        p_type = str(request.REQUEST['PARAM3'])
    else:
        p_type = ''
        
    logging.info('update_funddata_taskhandler: fund id:{fund_id}, year:{year}, type:{type}'.format(
                                                                                        fund_id=p_fund_id,
                                                                                        year=p_year,
                                                                                        type=p_type))
    response = HttpResponse('update_funddata_taskhandler')
    if FundClearDataModel._update_from_web(p_fund_id,p_year):
        response.status_code = fc2.HTTP_STATUS_CODE_OK
        logging.info('update_funddata_taskhandler success')
    else:
        response.status_code = fc2.HTTP_STATUS_CODE_SERVER_ERROR
        logging.warning('update_funddata_taskhandler fail!')
    
    if p_type == 'all':
        funddata = FundClearDataModel._get_funddata(p_fund_id, p_year)
        nav_item_count = len(funddata._get_nav_dict())
        logging.debug('update_funddata_taskhandler: nav item count {count}'.format(count=nav_item_count))
        if nav_item_count == 0:
            logging.info('update_funddata_taskhandler: year {year} nav_dict len 0, end update task.'.format(year=p_year))
        else:
            logging.info('update_funddata_taskhandler: continue update with year {year} by adding new update task'.format(year=str(int(p_year)-1)))
            taskqueue.add(method = 'GET', 
                          url = os.path.dirname(request.get_full_path()) + '/',
                          countdown = 15,
                          params = {
                                    'PARAM1': p_fund_id,
                                    'PARAM2': int(p_year)-1,
                                    'PARAM3': p_type,
                                    })
    
    return response




