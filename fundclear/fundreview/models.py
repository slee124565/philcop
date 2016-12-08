from google.appengine.ext import db
from datetime import date
from utils.util_date import get_sample_date_list
from dateutil.relativedelta import relativedelta
from fundclear.models import FundClearModel

import logging, pickle

CONFIG_REVIEW_MONTH_COUNT = 37

class FundReviewModel(db.Model):
    #fund_name = db.StringProperty()
    #fund_id = db.StringProperty()
    _nav_list_dump = db.BlobProperty()
    _yoy_1_list_dump = db.BlobProperty()
    _yoy_2_list_dump = db.BlobProperty()
    _date_nav_list = None
    
    #-> attribute method
    def nav_list(self):
        if self._nav_list_dump is not None:
            return pickle.loads(self._nav_list_dump)
        else:
            return None
        
    #-> attribute method
    def yoy_list(self, years=1):
        if years == 1 and self._yoy_1_list_dump is not None:
            return pickle.loads(self._yoy_1_list_dump)
        elif years == 2 and self._yoy_2_list_dump is not None:
            return pickle.loads(self._yoy_2_list_dump)
        else:
            logging.warning(__name__ + ', trying get yoy_list for not supported year ' + str(years))
            return None
     
    
    @classmethod
    def flush_fund_review(cls,fund_id):
        
        t_fund = FundClearModel.get_fund(fund_id,CONFIG_REVIEW_MONTH_COUNT)
        if t_fund is None:
            logging.warning(__name__ + ', flush_fund_review failed!')
            return None
                
        #-> get model object
        t_fundreview = FundReviewModel.get_or_insert(fund_id)
        
        #-> get sample date list
        t_date_list = get_sample_date_list(CONFIG_REVIEW_MONTH_COUNT, False)
        
        #-> get nav list
        t_fundreview._date_nav_list = t_fund.get_sample_value_list(t_date_list)

        #-> get 1 year YoY list
        t_fundreview._yoy_1_list_dump = pickle.dumps(t_fundreview._get_12_yoy_list(1))
        
        #-> get 2 year YoY list
        t_fundreview._yoy_2_list_dump = pickle.dumps(t_fundreview._get_12_yoy_list(2))
        
        t_fundreview._nav_list_dump = pickle.dumps(t_fundreview._date_nav_list)    
        t_fundreview.put()
        #logging.debug(__name__ + ', FundReview flushed for fund id ' + fund_id)

        return t_fundreview
        
    def _get_12_yoy_list(self,p_year):
        t_yoy_list = []
        t_check_date_1 = date.today()
        for i in range(12):
            t_check_date_1 = date(t_check_date_1.year, t_check_date_1.month, 1) - relativedelta(days=+1)
            t_check_date_2 = date(t_check_date_1.year-p_year,t_check_date_1.month,1) + relativedelta(months=+1) - relativedelta(days=+1)
            #logging.debug(__name__ + ', compute yoy for date between ' + str(t_check_date_1) + ',' + str(t_check_date_2))
            t_col_1_list = [row[0] for row in self._date_nav_list]
            if t_check_date_1 in t_col_1_list and t_check_date_2 in t_col_1_list:
                nav1 = self._date_nav_list[t_col_1_list.index(t_check_date_1)][1]
                nav2 = self._date_nav_list[t_col_1_list.index(t_check_date_2)][1]
                #logging.debug(__name__ + ', date ' + str(t_check_date_1) + ' nav ' + str(nav1))
                #logging.debug(__name__ + ', date ' + str(t_check_date_2) + ' nav ' + str(nav2))
                if (nav1 is not None) and (nav2 is not None) and (nav2 != 0):
                    yoy = 100 * (nav1-nav2)/nav2
                else:
                    logging.warning(__name__ + ', can not compute YoY for date between ' + str(t_check_date_1) + ',' + str(t_check_date_2))
                    yoy = 0
                t_yoy_list.append([t_check_date_1,yoy])
        
        #logging.debug(__name__ + ', yoy_list befor sorting:\n' + str(t_yoy_list))
        t_yoy_list.sort(key=lambda x: x[0])
        #logging.debug(__name__ + ', _get_12_yoy_list with year ' + str(p_year) + ':\n' + str(t_yoy_list))
        return t_yoy_list
        