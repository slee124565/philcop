from google.appengine.api import taskqueue
from django.http import HttpResponse

from fundclear2.models import FundClearInfoModel
from fundcodereader.models import FundCodeModel

from indexreview.models import IndexReviewModel

import logging, httplib

def get_fc_update_taskhandler_url():
    return '/ir/task/fc_update/'

def get_fc_cupdate_taskhandler_url():
    return '/ir/task/fc_cupdate/'

def get_fc_init_url():
    return '/ir/task/fc_init/'

def fc2_review_erase_taskhandler(reuqest):
    #TODO: erase all model object in datastore
    pass

def fc2_review_update(request):
    logging.info('fc2_review_update: start chain update all indexreview for fundclear2...')
    taskqueue.add(method = 'GET', 
          url = get_fc_cupdate_taskhandler_url(),
          countdown = 2,
          params = {
                    'PARAM1': '0',
                    })
        
def fc2_review_cupdate_taskhandler(request):
    response = HttpResponse('fc2_review_cupdate_taskhandler')

    UPDATE_SIZE = 5
    try:
        fundcode_list = FundCodeModel.get_codename_list()
        
        logging.debug('fc2_review_cupdate_taskhandler: debug mode!!!')
        fundcode_list = fundcode_list[:10]

        fund_index = int(request.REQUEST['PARAM1'])
        logging.info('fc2_review_cupdate_taskhandler: start with index {ind}'.format(ind=fund_index))
        
        for i in range(UPDATE_SIZE):
            next_index = fund_index + i
            if next_index < len(fundcode_list):
                fund_code = fundcode_list[next_index][0]
                logging.info('fc2_review_cupdate_taskhandler: index {ind} get fund code {fund_code}'.format(
                                                                                ind=next_index,
                                                                                fund_code=fund_code))
                taskqueue.add(method = 'GET', 
                      url = get_fc_update_taskhandler_url(),
                      countdown = 2,
                      params = {
                                'PARAM1': fund_code,
                                })
            else:
                logging.info('fc2_review_cupdate_taskhandler: end of chain update task.')
                break
        
            
        if (fund_index+UPDATE_SIZE) < len(fundcode_list):
            logging.debug('fc2_review_cupdate_taskhandler: add next chain update task with index {index}'.format(
                                                                                    index=fund_index+UPDATE_SIZE))
            taskqueue.add(method = 'GET', 
                  url = get_fc_cupdate_taskhandler_url(),
                  countdown = 5,
                  params = {
                            'PARAM1': str(fund_index+UPDATE_SIZE),
                            })
        response.status_code = httplib.OK
        return response
    except Exception, e:
        response.status_code = httplib.INTERNAL_SERVER_ERROR
        logging.error('fc2_review_update_taskhandler exception: {msg}'.format(msg=str(e)))
        
    return response

def fc2_review_update_taskhandler(request):
    response = HttpResponse('fc2_review_update_taskhandler')

    try:
        f_fund_id = request.REQUEST['PARAM1']
        t_fund = FundClearInfoModel.get_fund(f_fund_id)
        t_fund.load_all_nav()
        IndexReviewModel._update_review(t_fund)
        response.status_code = httplib.OK
    except Exception, e:
        response.status_code = httplib.INTERNAL_SERVER_ERROR
        logging.error('fc2_review_update_taskhandler exception: {msg}'.format(msg=str(e)))
        
    return response

