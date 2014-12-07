from datetime import date
from dateutil.relativedelta import relativedelta
import logging

def get_sample_date_list(p_count=12,p_inc_last_day=True):
    '''
    return a list of end day of each Month and yesterday if need
    '''
    t_sample_date_list = []
    
    #-> date_begin: the end day of the month which 12 months ago
    t_date_sample_start = date.today() - relativedelta(months=p_count)
    t_date_begin = date(t_date_sample_start.year,t_date_sample_start.month,1) + relativedelta(months=+1,days=-1)
    
    #-> date_end: yesterday
    t_date_end = date.today() - relativedelta(days=+1)
    #self.date_end = date(date.today().year,date.today().month,1) - relativedelta(days=+1)
    
    #-> _sample_date_list
    t_check_date = t_date_begin
    while (t_check_date <= t_date_end):
        t_sample_date_list.append(t_check_date)
        t_check_date = date(t_check_date.year,t_check_date.month,1) + relativedelta(months=+2) - relativedelta(days=+1)
    
    #-> add yesterday into sample list
    if p_inc_last_day:
        t_sample_date_list.append(date.today() - relativedelta(days=+1))
    
    return t_sample_date_list

def get_sample_date_list_2(p_date_begin, p_date_end, p_inc_everyday_of_last_month=False):
    '''
    return a list of [end date] for each month between p_date_begin and p_date_end
    '''
    t_sample_date_list = []
    
    #-> date_begin: the end day of the month for p_date_begin
    t_date_sample_start = p_date_begin
    t_date_begin = date(t_date_sample_start.year,t_date_sample_start.month,1) + relativedelta(months=+1, days=-1)
    
    t_date_end =p_date_end
    
    #-> _sample_date_list
    t_check_date = t_date_begin
    while (t_check_date <= t_date_end):
        t_sample_date_list.append(t_check_date)
        t_check_date = date(t_check_date.year,t_check_date.month,1) + relativedelta(months=+2) - relativedelta(days=+1)
    
    if p_inc_everyday_of_last_month and (t_sample_date_list[-1] < p_date_end):
        #-> first day of last month
        t_check_date = date(p_date_end.year,p_date_end.month,1)
        while (t_check_date <= p_date_end): 
            t_sample_date_list.append(t_check_date)
            t_check_date = t_check_date + relativedelta(days=+1)
        
    #logging.debug(__name__ + ', get_sample_date_list_2 result:\n' + str(t_sample_date_list))
    return t_sample_date_list
