from datetime import date
MONTH_DAY_BEGIN = 1
MONTH_DAY_MIDDLE = 15
MONTH_DAY_END = -1
MONTH_DAY_TODAY = date.today().day

import logging

def get_discrete_date_data_list(p_date_list,p_select_day):
    '''
    param [p_date_list] is a list of order by date [date, value] entry
    param [p_select_day] is one value in [MONTH_DAY_BEGIN, MONTH_DAY_MIDDLE, MONTH_DAY_END , MONTH_DAY_TODAY]
    return a list of [date, value] entry selected by p_select_day
    '''
    data_list = []
    DATE_INDEX = 0
    if p_date_list:
        if p_select_day != MONTH_DAY_END:
            for t_entry in p_date_list:
                if t_entry[DATE_INDEX].day == p_select_day:
                    data_list.append(t_entry)
        else: #-> end of month
            prev_entry_index = -1
            for t_entry in p_date_list:
                if t_entry[DATE_INDEX].day == 1:
                    if prev_entry_index >= 0:
                        data_list.append(p_date_list[prev_entry_index])
                prev_entry_index += 1
    logging.debug(__name__ + ': get_discrete_date_data_list:\n' + str(data_list))
    return data_list
            
