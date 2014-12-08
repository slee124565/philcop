from google.appengine.api import taskqueue

from django.http import HttpResponse
from datetime import date

import bankoftaiwan2.models_exchange as bot_ex
import bankoftaiwan2.models_gold as bot_gold
import logging, httplib

def get_gold_chain_update_taskhandler_url():
    return '/bot2/task/g_cupdate/'

def get_ex_chain_update_taskhandler_url():
    return '/bot2/task/ex_cupdate/'

def init_gold_taskhandler(request):
    '''
    datastore initialization
    start chain task for each currency
    '''
    func = '{} {}'.format(__name__,'init_gold_taskhandler')
    t_cdown = 3
    for t_currency in bot_gold.BOT_GOLD_TRADE_CURRENCY_LIST:
        logging.info('{}: add chain task for {}'.format(func,t_currency))
        taskqueue.add(method='GET',
                      url=get_gold_chain_update_taskhandler_url(),
                      countdown=t_cdown,
                      params={
                              'PARAM1':t_currency,
                              })
        t_cdown += 11
    return HttpResponse(func)

def update_gold_taskhandler(request):
    '''
    TODO: schedule update all currency for this year
    update period : per month
    '''
    func = '{} {}'.format(__name__,'update_gold_taskhandler')
    for t_currency in bot_gold.BOT_GOLD_TRADE_CURRENCY_LIST:
        logging.info('{}: add chain task for {}'.format(func,t_currency))
        taskqueue.add(method='GET',
                      url=get_gold_chain_update_taskhandler_url(),
                      countdown=7,
                      params={
                              'PARAM1':t_currency,
                              'PARAM2':date.today().year
                              })
    return HttpResponse(func)

def gold_chain_update_taskhandler(request):
    '''
    update year gold price and add next chain_update task for next year until this year 
    '''
    func = '{} {}'.format(__name__,'gold_chain_update_taskhandler')
    YEAR_SINCE = 2009
    response = HttpResponse('{}'.format(func))
    response.status_code = httplib.OK
    try:
        p_currency = request.REQUEST['PARAM1']
        p_yr_since = YEAR_SINCE #date.today().year
        if 'PARAM2' in request.REQUEST.keys():
            p_yr_since = int(request.REQUEST['PARAM2'])

        logging.info('{}: for {} {}'.format(func,p_currency,p_yr_since))
        if not bot_gold.BotGoldDataModel._update_from_web(p_currency,p_yr_since):
            #TODO: send alert for admin
            response.status_code = httplib.INTERNAL_SERVER_ERROR
        
        if p_yr_since < date.today().year:
            logging.info('{}: add next chain update task for year {}'.format(func,p_yr_since+1))
            taskqueue.add(method = 'GET', 
                      url = get_gold_chain_update_taskhandler_url(),
                      countdown = 5,
                      params = {
                                'PARAM1': p_currency,
                                'PARAM2': (p_yr_since+1),
                                })
        else:
            logging.info('{}: end of chain task'.format(func))
        return response
    except Exception, e:
        err_msg = str(e)
        logging.error('{}: ERROR {}'.format(func,err_msg))
        return response


def init_ex_taskhandler(request):
    '''
    datastore initialization
    start chain task for each currency
    '''
    func = '{} {}'.format(__name__,'init_ex_taskhandler')
    t_cdown = 3
    for t_currency in bot_ex.CURRENCY_LIST:
        logging.info('{}: add chain task for {}'.format(func,t_currency))
        taskqueue.add(method='GET',
                      url=get_ex_chain_update_taskhandler_url(),
                      countdown=t_cdown,
                      params={
                              'PARAM1':t_currency,
                              })
        t_cdown += 11
    return HttpResponse(func)

def update_ex_taskhandler(request):
    '''
    TODO: schedule update all currency for this year
    update period : per month
    '''
    func = '{} {}'.format(__name__,'update_ex_taskhandler')
    for t_currency in bot_ex.CURRENCY_LIST:
        logging.info('{}: add chain task for {}'.format(func,t_currency))
        taskqueue.add(method='GET',
                      url=get_ex_chain_update_taskhandler_url(),
                      countdown=7,
                      params={
                              'PARAM1':t_currency,
                              'PARAM2':date.today().year
                              })
    return HttpResponse(func)

def ex_chain_update_taskhandler(request):
    '''
    update year exchange rate and add next chain_update task for next year until this year 
    '''
    func = 'chain_update_taskhandler'
    YEAR_SINCE = 2000
    response = HttpResponse('{} {}'.format(__name__,func))
    response.status_code = httplib.OK
    try:
        p_currency = request.REQUEST['PARAM1']
        p_yr_since = YEAR_SINCE #date.today().year
        if 'PARAM2' in request.REQUEST.keys():
            p_yr_since = int(request.REQUEST['PARAM2'])

        logging.info('{} {}: for {} {}'.format(__name__,func,p_currency,p_yr_since))
        if not bot_ex.BotExchangeDataModel._update_from_web(p_currency,p_yr_since):
            #TODO: send alert for admin
            response.status_code = httplib.INTERNAL_SERVER_ERROR
        
        if p_yr_since < date.today().year:
            logging.info('{}: add next chain update task for year {}'.format(func,p_yr_since+1))
            taskqueue.add(method = 'GET', 
                      url = get_ex_chain_update_taskhandler_url(),
                      countdown = 5,
                      params = {
                                'PARAM1': p_currency,
                                'PARAM2': (p_yr_since+1),
                                })
        else:
            logging.info('{} {}: end of chain task'.format(__name__,func))
        return response
    except Exception, e:
        err_msg = str(e)
        logging.error('{} {}: ERROR {}'.format(__name__,func,err_msg))
        return response

