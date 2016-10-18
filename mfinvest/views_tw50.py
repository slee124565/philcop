from google.appengine.api import taskqueue, mail

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from utils.util_bollingerbands import get_bollingerbands

from twse_gae.models_stock import StockModel
from twse_gae.models_tw50 import TW50Model
from mfinvest.models_mf import MFModle

import logging, httplib

def send_tw50_wk_bb_review_report():
    fname = '{} {}'.format(__name__,'send_tw50_wk_bb_review_report')
    logging.debug('{}: send report'.format(fname))
    user_address = 'lee.shiueh@gmail.com'
    sender_address = 'MyGAE <lee.shiueh@gmail.com>'
    subject = 'TW50 Weekly Review Notification'
    body = 'http://trusty-catbird-645.appspot.com/mf/tw50/'
    mail.send_mail(sender_address, user_address, subject, body)

def task_tw50_chain_update_bb_state(request):
    fname = '{} {}'.format(__name__,'task_tw50_chain_update_bb_state')
    if 'index' in request.GET:
        t_index = request.GET['index']
    else:
        t_index = 0
    logging.info('{}: with index {}'.format(fname,t_index))
    tw50_list = TW50Model.get_id_list()
    if int(t_index) >= len(tw50_list) or int(t_index) < 0:
        t_msg = '{}: param index {} exceed max length'.format(fname, t_index)
        logging.warning(t_msg)
    else:

        t_stk_no = tw50_list[int(t_index)]
    
        if StockModel.check_db_exist(t_stk_no) == False:
            t_msg = '{}: stock {} index model not exist'.format(fname, t_stk_no)
            logging.warning(t_msg)
        else:
            t_stock = StockModel.get_stock(t_stk_no)
            p_timeframe = 26
            p_sdw = 100
            t_date_since = date.today() + relativedelta(days=-(7*p_timeframe))
            t_offset = 2 - t_date_since.weekday()
            t_date_since += relativedelta(days=t_offset)
            t_date_list = []
            while t_date_since <= date.today():
                t_date_list.append(t_date_since)
                t_date_since += relativedelta(days=+7)
            t_value_list = t_stock.get_sample_index_list(t_date_list)
            t_current_nav = t_value_list[-1][1]
            sma,tb1,tb2,bb1,bb2 = get_bollingerbands(t_value_list,p_timeframe,float(p_sdw)/100)
            if t_current_nav < bb2[-1][1]:
                t_bb_state = 'BB3'
            elif t_current_nav < bb1[-1][1]:
                t_bb_state = 'BB2'
            elif t_current_nav < sma[-1][1]:
                t_bb_state = 'BB1'
            elif t_current_nav < tb1[-1][1]:
                t_bb_state = 'TB1'
            elif t_current_nav < tb2[-1][1]:
                t_bb_state = 'TB2'
            else:
                t_bb_state = 'TB3'
                
            t_model = MFModle.get_model()
            t_model.dict_data[t_stk_no] = {}
            t_model.dict_data[t_stk_no]['state'] = t_bb_state
            t_model.dict_data[t_stk_no]['closed'] = t_current_nav
            t_model.save_dict_data()
            t_msg = '{} {} with state {}'.format(fname,t_stk_no,str(t_model.dict_data))
            logging.info(t_msg)

        t_next_index = int(t_index)+1
        if t_next_index < len(tw50_list):
            logging.debug('{}: add next chain task with index {}'.format(fname,t_next_index))
            taskqueue.add(method = 'GET', 
                          url = "/mf/task/tw50_cupdate/" ,
                          countdown = datetime.now().second % 5,
                          params = {
                                    'index': t_next_index,
                                    })
        
        if t_next_index == len(tw50_list):
            send_tw50_wk_bb_review_report()

    response = HttpResponse(t_msg)
    response.status_code = httplib.OK
    return response

def default_view(request, p_bb_level=''):
    tw50_id_list = TW50Model.get_id_list()
    
    content_head_list = ['ID','Name','Price','Weekly BB Area','Weekly BB','Daily BB']
    content_rows = []
    t_model = MFModle.get_model()
    
    for t_stk_no in tw50_id_list:
        if t_stk_no in t_model.dict_data:
            t_bb_state = t_model.dict_data[t_stk_no]['state']
        else:
            t_bb_state = 'NA'
            
        if t_bb_state in ['TB3','TB2']:
            t_bb_state_html = '<p class="text-danger"><strong>{}</strong></p>'.format(t_bb_state)
        elif t_bb_state in ['BB2','BB3']:
            t_bb_state_html = '<p class="text-success"><strong>{}</strong></p>'.format(t_bb_state)
        else:
            t_bb_state_html = '<p class="text-muted"><strong>{}</strong></p>'.format(t_bb_state)
            
        if ((p_bb_level == '') or
            ((p_bb_level == 'BB2') and (t_bb_state in ['BB2','BB3'])) or
            ((p_bb_level == 'BB3') and (t_bb_state == 'BB3')) or
            ((p_bb_level == 'TP2') and (t_bb_state in ['TP2','TP3'])) or
            ((p_bb_level == 'TP3') and (t_bb_state == 'TP3')) ):
            content_rows.append([
                             t_stk_no,
                             StockModel.get_name_by_stk_no(t_stk_no),
                             t_model.dict_data[t_stk_no]['closed'],
                             t_bb_state_html,
                             '<a href="/mf/twse/bb/' + t_stk_no + '/weekly2/">BB Weekly View</a>',
                             '<a href="/mf/twse/bb/' + t_stk_no + '/daily/">BB Daily View</a>',
                             ])
    if p_bb_level == "":
        content_rows.sort(key=lambda x: (x[3],x[0]))
    else:
        content_rows.sort(key=lambda x: x[0])
    tbl_content = {
                   'heads': content_head_list,
                   'rows': content_rows,
                   }

    args = {
            'tpl_section_title': _("HEAD_TW50_BB_REVIEW"),
            'tbl_content' : tbl_content,
            }
    return render_to_response('mf_simple_table.tpl.html', args)
    