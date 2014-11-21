from django.http import HttpResponse
from google.appengine.api import taskqueue

from datetime import date

from fundclear2.models import FundClearDataModel, FundClearInfoModel
import fundclear2.models as fc2

from fundcodereader.models import FundCodeModel
#import indexreview.tasks as reviewtask

import logging, os
from fundclear.fcreader import FundInfo

def funddata_update(request):
    response = HttpResponse('funddata_update')
    taskhandler_url = os.path.dirname(os.path.dirname(request.get_full_path())) + '/cupdate/'
    taskqueue.add(method = 'GET', 
                  url = taskhandler_url,
                  countdown = 10,
                  params = {
                            'PARAM1': 0,
                            'PARAM2': '',
                            })
    logging.info('funddata_update: add chain update task')
    response.status_code = fc2.HTTP_STATUS_CODE_OK
    return response
    
def funddata_init(request):
    response = HttpResponse('funddata_init')
    taskhandler_url = os.path.dirname(os.path.dirname(request.get_full_path())) + '/cupdate/'
    taskqueue.add(method = 'GET', 
                  url = taskhandler_url,
                  countdown = 10,
                  params = {
                            'PARAM1': 0,
                            'PARAM2': 'all',
                            })
    response.status_code = fc2.HTTP_STATUS_CODE_OK
    logging.info('funddata_init: add chain update task')
    return response

def chain_update_taskhandler(request):
    '''
    function request 2 param: 
    code_index(mondatory): the start index of FundCodeModel.get_codename_list(),
    type(optional): fund data update type; <all> means update all years data
    '''
    
    p_code_index = int(request.REQUEST['PARAM1'])
    p_type = ''
    if 'PARAM2' in request.REQUEST.keys():
        p_type = str(request.REQUEST['PARAM2'])

    codename_list = FundCodeModel.get_codename_list()
    #codename_list = codename_list[:5]
    response = HttpResponse('update_funddata_taskhandler with code_index {code_index}'.format(code_index=p_code_index))
    if p_code_index < len(codename_list):
        #-> add update_funddata_task for p_code_index
        p_code = codename_list[p_code_index][0]
        taskhandler_url = os.path.dirname(os.path.dirname(request.get_full_path())) + '/dupdate/'
        taskqueue.add(method = 'GET', 
                      url = taskhandler_url,
                      countdown = 5,
                      params = {
                                'PARAM1': p_code,
                                'PARAM3': p_type,
                                })
        logging.info('chain_update_taskhandler: add update task for fund_id {fund_id}'.format(fund_id=p_code))
        #-> add chain_update_task for (p_code_index+1)
        p_next_index = p_code_index + 1
        if p_next_index < len(codename_list):
            taskqueue.add(method = 'GET', 
                          url = os.path.dirname(request.get_full_path()) + '/',
                          countdown = 50,
                          params = {
                                    'PARAM1': p_next_index,
                                    'PARAM2': p_type,
                                    })
            logging.info('chain_update_taskhandler: add chain_update task for index {index}'.format(index=p_next_index))        
        else:
            logging.info('chain_update_taskhandler: end chain_update task with index {index}'.format(index=p_next_index))        
            '''
            taskqueue.add(method = 'GET', 
                          url = reviewtask.get_fc_init_url(),
                          countdown = 10,
                          )
            logging.info('chain_update_taskhandler: review chain update task added.')
            '''
    else:
        logging.warning('chain_update_taskhandler: code index {code_index} param error'.format(code_index=p_code_index))
    pass

    response.status_code = fc2.HTTP_STATUS_CODE_OK
    return response

def update_funddata_taskhandler(request):
    '''
    function request 3 param: fund_id, download_year, update_type
    if update_type == 'all', it will update fund nav before download_year
    '''
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
    
        if p_type == 'all':
            funddata = FundClearDataModel._get_funddata(p_fund_id, p_year)
            nav_item_count = len(funddata._get_nav_dict())
            logging.info('update_funddata_taskhandler: nav item count {count}'.format(count=nav_item_count))
            
            if nav_item_count == 0:
                logging.info('update_funddata_taskhandler: year {year} nav_dict len 0, end update task.'.format(year=p_year))
            else:
                logging.info('update_funddata_taskhandler: continue update with year {year} by adding new update task'.format(year=str(int(p_year)-1)))
                taskqueue.add(method = 'GET', 
                              url = os.path.dirname(request.get_full_path()) + '/',
                              countdown = 5,
                              params = {
                                        'PARAM1': p_fund_id,
                                        'PARAM2': int(p_year)-1,
                                        'PARAM3': p_type,
                                        })
    
    else:
        response.status_code = fc2.HTTP_STATUS_CODE_SERVER_ERROR
        logging.warning('update_funddata_taskhandler fail!')

    return response

def get_db_err_fund_id_list():
    fund_id_list = []
    fundclear_id_list = FundCodeModel.get_code_list()
    fund_query = FundClearInfoModel.all()
    for t_fund in fund_query:
        t_id = t_fund.key().name()
        if not t_id in fundclear_id_list:
            fund_id_list.append(t_id)
    return fund_id_list
    
def get_analysis(p_fund_code):
    #TODO: return {key:value} dict
    '''
    not_in_fundclear_list
    year_nav_count
    has_discontinuous_year
    '''
    t_dict = {
              'not_in_fundclear_list': False,
              'year_nav_count': 0,
              'zero_year_nav': False,
              'has_discontinuous_year': False,
              'not_update_yet': False,
              'year_list': 'N/A'
              }
    #-> not_in_fundclear_list
    fundclear_code_list = FundCodeModel.get_code_list()
    if not p_fund_code in fundclear_code_list:
        t_dict['not_in_fundclear_list'] = True
        return t_dict

    #->year_nav_count & has_discontinuous_year & year_list
    t_fund = FundClearInfoModel.get_by_key_name(FundClearInfoModel.compose_key_name(p_fund_code))
    if t_fund is None:
        t_dict['not_update_yet'] = True
        return t_dict
    
    data_query = FundClearDataModel.all().ancestor(t_fund).order('-year')
    check_year = date.today().year
    this_year = str(check_year)
    t_year_list = ''
    for t_data in data_query:
        if t_data.year == this_year:
            nav_dict = t_data._get_nav_dict()
            t_dict['year_nav_count'] = len(nav_dict)
            if t_dict['year_nav_count'] == 0:
                t_dict['zero_year_nav'] = True
            
        t_year_list += t_data.year + ', '
        if str(check_year) != t_data.year:
            t_dict['has_discontinuous_year'] = True
        else:
            check_year -= 1 
        
    t_dict['year_list'] = t_year_list
    return t_dict
    
    
def get_year_nav_fund_list():
    #TODO: return a list of fund nav number for this year

    codename_all = FundCodeModel.get_codename_list()
    this_year = date.today().year
    
    fund_list = []
    for t_entry in codename_all[:10]:
        t_fund_id = t_entry[0]
        t_fundinfo = FundClearInfoModel.get_by_key_name(FundClearInfoModel.compose_key_name(t_fund_id))
        if t_fundinfo is None:
            fund_list.append(t_entry+[0]) 
        else:
            t_funddata = FundClearDataModel.all().ancestor(t_fundinfo).filter('year', str(this_year)).get()
            if t_funddata is None:
                fund_list.append(t_entry+[0])
            else:
                t_nav_dict = t_funddata._get_nav_dict()
                fund_list.append(t_entry+[len(t_nav_dict)])
    return fund_list
    
    
def get_zero_nav_fund_list():
    #TODO: return a list of fund which has no any nav for this year
    codename_all = FundCodeModel.get_codename_list()
    this_year = date.today().year
    
    zero_fund_list = []
    for t_entry in codename_all[:20]:
        t_fund_id = t_entry[0]
        t_fundinfo = FundClearInfoModel.get_by_key_name(FundClearInfoModel.compose_key_name(t_fund_id))
        if t_fundinfo is None:
            zero_fund_list.append(t_entry)
        else:
            t_funddata = FundClearDataModel.all().ancestor(t_fundinfo).filter('year', str(this_year)).get()
            if t_funddata is None:
                zero_fund_list.append(t_entry)
            else:
                t_nav_dict = t_funddata._get_nav_dict()
                if len(t_nav_dict) == 0:
                    zero_fund_list.append(t_entry)
            
    return zero_fund_list
