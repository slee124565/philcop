from google.appengine.ext import db

from datetime import date
from dateutil.relativedelta import relativedelta

from utils.util_date import get_sample_date_list

import logging, pickle

CONFIG_REVIEW_MONTH_COUNT = 37

class IndexReviewModel(db.Model):
    _index_list_dump = db.BlobProperty()
    _yoy_1_list_dump = db.BlobProperty()
    _yoy_2_list_dump = db.BlobProperty()

    #-> attribute method
    def index_list(self):
        if self._index_list_dump is not None:
            return pickle.loads(self._index_list_dump)
        else:
            logging.warning('index_list is empty!')
            return []
        
    #-> attribute method
    def yoy_list(self, p_ycount=1):
        if p_ycount == 1 and self._yoy_1_list_dump is not None:
            return pickle.loads(self._yoy_1_list_dump)
        elif p_ycount == 2 and self._yoy_2_list_dump is not None:
            return pickle.loads(self._yoy_2_list_dump)
        else:
            logging.warning('yoy_list for ycount {ycount} is empty'.format(ycount=p_ycount))
            return []

    @classmethod
    def get_index_review(cls,p_index_src_model):
        t_keyname = p_index_src_model.__class__.__name__ + '_' + p_index_src_model.key().name()
        #logging.debug('t_keyname: ' + t_keyname)
        t_review = cls.get_by_key_name(t_keyname, p_index_src_model)
        
        if t_review is None:
            t_index_list = p_index_src_model.get_index_list()
            t_review = IndexReviewModel.save_index_review(t_index_list, t_keyname, p_index_src_model)
            logging.info('get_index_review: initial IndexReviewModel saved with key {key}'.format(key=t_keyname))

        return t_review
        
    @classmethod
    def save_index_review(cls,p_index_list,p_keyname,p_db_parent):
        #-> get model object
        t_indexreview = IndexReviewModel.get_or_insert(p_keyname,parent=p_db_parent)
        
        #-> get sample date list
        t_date_list = get_sample_date_list(CONFIG_REVIEW_MONTH_COUNT, False)
        
        #-> get sample index list
        t_sample_index_list = cls.get_sample_index_list(p_index_list, t_date_list)
        t_indexreview._index_list_dump = pickle.dumps(t_sample_index_list)
        t_indexreview._yoy_1_list_dump = pickle.dumps(cls.get_12_yoy_list(t_sample_index_list, 1))
        t_indexreview._yoy_2_list_dump = pickle.dumps(cls.get_12_yoy_list(t_sample_index_list, 2))
        t_indexreview.put()
        '''
        logging.debug('save_index_review:\nnav_list:{nav_list}\nyoy_1:\n{yoy_1}\nyoy_2:\n{yoy_2}'.format(
                                                        nav_list=str(t_indexreview.index_list()),
                                                        yoy_1=str(t_indexreview.yoy_list(1)),
                                                        yoy_2=str(t_indexreview.yoy_list(2))))

        '''
        return t_indexreview
        
    @classmethod
    def get_sample_index_list(cls,p_index_list,p_date_list):
        t_list = []
        t_date_list = [row[0] for row in p_index_list]
        for t_date in p_date_list:
            try:
                t_index = p_index_list[t_date_list.index(t_date)][1]
            except:
                logging.warning('get_sample_index_list index error for date {date}'.format(date=str(t_date)))
                t_index = 0.0
            t_list.append([t_date,t_index])
        return t_list

    
    @classmethod
    def get_12_yoy_list(cls,p_index_list,p_ycount=1):
        '''
        p_index_list = [[date,index],[date,index],...]
        p_ycount = 1 means 1 year to year calculation
        return [[date,yoy_1],[date,yoy_2],...]
        '''
        TOTAL_SAMPLE_COUNT = 12
        t_yoy_list = []
        t_check_date_1 = date.today()
        for i in range(TOTAL_SAMPLE_COUNT):
            t_check_date_1 = date(t_check_date_1.year, t_check_date_1.month, 1) - relativedelta(days=+1)
            t_check_date_2 = date(t_check_date_1.year-p_ycount,t_check_date_1.month,1) + \
                                    relativedelta(months=+1) - relativedelta(days=+1)
            #logging.debug(__name__ + ', compute yoy for date between ' + str(t_check_date_1) + ',' + str(t_check_date_2))
            t_col_1_list = [row[0] for row in p_index_list]
            if t_check_date_1 in t_col_1_list and t_check_date_2 in t_col_1_list:
                try:
                    nav1 = p_index_list[t_col_1_list.index(t_check_date_1)][1]
                    nav2 = p_index_list[t_col_1_list.index(t_check_date_2)][1]
                except:
                    logging.warning('get_12_yoy_list index error for date {date1} or {date2}'.format(
                                                                            date1=str(t_check_date_1),
                                                                            date2=str(t_check_date_2)))
                    nav1 = 0
                    nav2 = 0
                #logging.debug(__name__ + ', date ' + str(t_check_date_1) + ' nav ' + str(nav1))
                #logging.debug(__name__ + ', date ' + str(t_check_date_2) + ' nav ' + str(nav2))
                if (nav1 is not None) and (nav2 is not None) and (nav2 != 0):
                    yoy = 100 * (nav1-nav2)/nav2
                else:
                    logging.warning('get_12_yoy_list: can not compute YoY for date between {date1} and {date2}'.format(
                                                            date1=str(t_check_date_1),
                                                            date2=str(t_check_date_2)))
                    yoy = 0
                t_yoy_list.append([t_check_date_1,yoy])
        
        #logging.debug(__name__ + ', yoy_list befor sorting:\n' + str(t_yoy_list))
        t_yoy_list.sort(key=lambda x: x[0])
        #logging.debug(__name__ + ', _get_12_yoy_list with year ' + str(p_year) + ':\n' + str(t_yoy_list))
        return t_yoy_list
    