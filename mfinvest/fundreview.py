from django.http import HttpResponse
from datetime import date
from dateutil.relativedelta import relativedelta

from fundclear.models import FundClearModel
from mfinvest.mfreport import get_sample_date_list

import logging

class FundReview():
    fund_id = ''
    fund_name = ''
    review_year = 1
    nav_list= []
    yoy_list = []
    
    def __init__(self, fund_id, review_year=1):
        logging.info(__name__ + ', init object for fund_id ' + fund_id + ', review_year ' + str(review_year))
        self.fund_id = fund_id
        self.review_year = review_year

        #-> calculate total sample months needed
        TOTAL_SAMPLE_MONTHS_COUNT = 12 * int(review_year)
        fund_data_months = TOTAL_SAMPLE_MONTHS_COUNT*2+1
        
        #-> download fund data from FundClear
        t_fund = FundClearModel.get_fund(fund_id, fund_data_months)
        if t_fund == None:
            return HttpResponse('FundClearModel ERROR')
        
        #-> sampling fund data 
        t_sample_date_list = get_sample_date_list(fund_data_months,False)
        
        #-> nav_report
        self.nav_list = t_fund.get_sample_value_list(t_sample_date_list)
        #logging.debug(__name__ + ', 1st nav_list:\n' + str(self.nav_list))
        self.fund_name = t_fund.fund_name
        if self.fund_name != None:
            logging.debug(__name__ + ', fund_name ' + self.fund_name)
    

        #-> yoy_report
        self.yoy_list = []
        t_check_date_1 = date.today()
        for i in range(TOTAL_SAMPLE_MONTHS_COUNT):
            t_check_date_1 = date(t_check_date_1.year, t_check_date_1.month, 1) - relativedelta(days=+1)
            t_check_date_2 = date(t_check_date_1.year-1,t_check_date_1.month,1) + relativedelta(months=+1) - relativedelta(days=+1)
            t_col_1_list = [row[0] for row in self.nav_list]
            nav1 = self.nav_list[t_col_1_list.index(t_check_date_1)][1]
            nav2 = self.nav_list[t_col_1_list.index(t_check_date_2)][1]
            #logging.debug(__name__ + ', date ' + str(t_check_date_1) + ' nav ' + str(nav1))
            #logging.debug(__name__ + ', date ' + str(t_check_date_2) + ' nav ' + str(nav2))
            if nav1 is not None and nav2 is not None:
                yoy = (nav1-nav2)/nav2
            else:
                logging.warning(__name__ + ', __init__: Can not compute YoY for NAV ' + str(nav1) + ',' + str(nav2))
                yoy = None
            self.yoy_list.append([t_check_date_1,yoy])
        
        #logging.debug(__name__ + ', yoy_list befor sorting:\n' + str(self.yoy_list))
        self.yoy_list.sort(key=lambda x: x[0])
        self.nav_list = self.nav_list[-TOTAL_SAMPLE_MONTHS_COUNT:]
        logging.debug(__name__ + ', __init__ fund_id ' + fund_id + ' for year ' + str(review_year) + '\n' + \
                      'nav_list:\n' + str(self.nav_list) + '\n' + \
                      'yoy_list:\n' + str(self.yoy_list))
        