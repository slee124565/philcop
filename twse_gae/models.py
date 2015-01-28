from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

import csv,StringIO
import logging, httplib, pickle

CONFIG_WEB_FETCH_MAX_MONTH = 12*2

def get_list_update_handler_url():
    return '/twse/task/list_update/'
    
def get_chain_update_handler_url():
    return '/twse/task/cupdate/'

def get_stk_update_handler_url():
    return '/twse/task/update/'

def get_stk_reload_handler_url():
    return '/twse/task/reload/'

class TWSEStockModel(db.Model):
    
    URL_TEMPLATE = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAY_print.php?genpage=genpage/Report{Ym}/{Ym}_F3_1_8_{stk_no}.php&type=csv'
    CSV_COL_DATE = 'date'
    CSV_COL_SHARE = 'share'
    CSV_COL_AMOUNT = 'amount'
    CSV_COL_HIGH = 'high'
    CSV_COL_LOW = 'low'
    CSV_COL_OPEN = 'open'
    CSV_COL_CLOSE = 'close'
    CSV_COL_DIFF = 'diff'
    CSV_COL_DEAL = 'deal'
    CSV_COLS = [CSV_COL_DATE,
               CSV_COL_SHARE,
               CSV_COL_AMOUNT,
               CSV_COL_HIGH,
               CSV_COL_LOW,
               CSV_COL_OPEN,
               CSV_COL_CLOSE,
               CSV_COL_DIFF,
               CSV_COL_DEAL]
    
    '''
    content_csv = {
                    'Ym' : {},
                    ... 
                    }
    '''
    
    #stk_no = db.StringProperty() #-> stk_no as model key
    csv_dict_pickle = db.BlobProperty(default='')
    #update_list = db.StringProperty() #-> update_list is same with content_csv.keys()
    csv_dict = {}
    
    def get_index_by_date(self, p_date):
        func = '{} {}'.format(__name__,'get_index_by_date')
        t_date = str(p_date)        
        t_ym = p_date.strftime('%Y%m')
        t_count = 1
        if t_ym in self.csv_dict.keys():
            if t_date in self.csv_dict[t_ym].keys():
                return float(self.csv_dict[t_ym][t_date][TWSEStockModel.CSV_COL_CLOSE])
            else:
                return self.get_index_by_date(p_date + relativedelta(days=-1))
        else:
            return 0.0
            
    def get_sample_index_list(self, p_date_list):
        func = '{} {}'.format(__name__,'get_sample_index_list')
        t_list = []
        for t_date in p_date_list:
            t_nav = self.get_index_by_date(t_date)
            t_list.append([t_date,t_nav])
        return t_list
        
    def get_index_list(self):
        func = '{} {}'.format(__name__,'get_index_list')
        t_index_list = []
        for t_ym_dict in self.csv_dict.values():
            for t_entry in t_ym_dict.values():
                t_index_list.append([t_entry[TWSEStockModel.CSV_COL_DATE],float(t_entry[TWSEStockModel.CSV_COL_CLOSE])])
        
        t_index_list.sort(key=lambda x:x[0])
        #logging.debug('{}:{}'.format(func,str(t_index_list)))
        return t_index_list
    
    @classmethod
    def compose_key_name(cls, stk_no):
        return stk_no
    
    @classmethod 
    def remove_csv_dict_deprecated_data(cls, p_csv_dict):
        fname = '{} {}'.format(__name__,'remove_csv_dict_deprecated_data')
        t_yearmonth_since = date.today() + relativedelta(months=-CONFIG_WEB_FETCH_MAX_MONTH)
        t_ym_since = t_yearmonth_since.strftime('%Y%m')
        t_dict_ym_list = sorted(p_csv_dict.keys())
        for t_ym in t_dict_ym_list:
            if t_ym < t_ym_since:
                logging.debug('{}: remove key {} element'.format(fname,t_ym))
                del p_csv_dict[t_ym]
            else:
                break
            
        return p_csv_dict
        
    @classmethod
    def update_monthly_dict(cls, p_stk_no, p_monthly_dict, p_saved=True):
        func = '{} {}'.format(__name__,'update_monthly_dict')
        t_stock = cls.get_or_insert(cls.compose_key_name(p_stk_no))
        if not t_stock.csv_dict_pickle in [None, '']:
            t_stock.csv_dict = pickle.loads(t_stock.csv_dict_pickle)
        else:
            t_stock.csv_dict = {}
        t_entry = p_monthly_dict.itervalues().next()
        t_ym = t_entry[cls.CSV_COL_DATE].strftime('%Y%m')
        t_stock.csv_dict[t_ym] = p_monthly_dict
        t_stock.csv_dict = cls.remove_csv_dict_deprecated_data(t_stock.csv_dict)
        t_stock.csv_dict_pickle = pickle.dumps(t_stock.csv_dict)
        if p_saved:
            t_stock.put()
        logging.info('{}: stock {} month {} updated with saved {}'.format(func,p_stk_no,t_ym,p_saved))
        return t_stock
            
    @classmethod
    def parse_csv_col_date(cls, p_col_date):
        t_arr = p_col_date.split('/')
        return date(1911+int(t_arr[0]),int(t_arr[1]),int(t_arr[2]))
        
    @classmethod
    def parse_csv_content_dict(cls, p_csv_content):
        '''
        csv row data start from line 3 :: OFFSET = 2
        '''
        func = '{} {}'.format(__name__,'parse_csv_content_dict')
        ROW_OFFSET = 2
        rows = p_csv_content.splitlines()
        rows = [','.join(cls.CSV_COLS)] + rows[ROW_OFFSET:]
        csv_content = '\n'.join(rows)
        #logging.debug('{}: csv_content:\n{}'.format(func,csv_content))
        csv_reader = csv.DictReader(StringIO.StringIO(csv_content))
        data_dict = {}
        for row in csv_reader:
            t_item = dict(row)
            t_item_date = cls.parse_csv_col_date(t_item[cls.CSV_COL_DATE])
            t_item[cls.CSV_COL_DATE] = t_item_date
            data_dict[str(t_item_date)] = t_item
            
        logging.debug('{}:{}'.format(func,str(data_dict)))
        return data_dict

    @classmethod
    def get_fetch_url(cls, p_stk_no, p_year_month):
        fname = '{} {}'.format(__name__,'get_fetch_url')
        t_fetch_url = cls.URL_TEMPLATE.format(Ym=p_year_month,stk_no=p_stk_no)
        logging.debug('{}: {}'.format(fname,t_fetch_url))
        return t_fetch_url
        
    @classmethod
    def update_monthly_csv_from_web(cls, p_stk_no, p_year_month, p_saved=False):
        '''
        return model entity
        '''
        func = '{} {}'.format(__name__,'update_monthly_csv_from_web')
        #t_url = cls.URL_TEMPLATE.format(Ym=p_year_month,stk_no=p_stk_no)
        t_url = cls.get_fetch_url(p_stk_no, p_year_month)
        
        try :
            web_fetch = urlfetch.fetch(t_url)
            if web_fetch.status_code == httplib.OK:
                web_content = web_fetch.content
                t_monthly_dict = cls.parse_csv_content_dict(web_content)
                if len(t_monthly_dict) == 0:
                    return None
                t_stock = cls.update_monthly_dict(p_stk_no,t_monthly_dict,p_saved)
                return t_stock
            else:
                logging.warning('{}: urlfetch fail status code {}'.format(func,web_fetch.status_code))
                return None
        except urlfetch.DownloadError, err:
            logging.warning('{} : Internet Download Error: {}'.format(func, str(err)))
            return None
        '''
        except Exception, e:
            logging.error('{} : Exception {}'.format(func, str(e)))
            return None
        '''
    
    
    @classmethod
    def add_stk_update_task(cls, p_stk_no):
        func = '{} {}'.format(__name__,'add_stk_update_task')
        logging.info('{}: with stock {}'.format(func,p_stk_no))
        taskqueue.add(method = 'GET', 
                          url = get_stk_update_handler_url() ,
                          countdown = 2,
                          params = {
                                    'stk_no': p_stk_no,
                                    })
        
    @classmethod
    def get_stock(cls, p_stk_no):
        func = '{} {}'.format(__name__,'get_stock')
        
        logging.info('{}: query stock {}'.format(func,p_stk_no))
        
        t_stock = cls.get_by_key_name(cls.compose_key_name(p_stk_no))
        
        if t_stock is None or t_stock.csv_dict_pickle in [None,'']:
            logging.warning('{}: stock is first loaded, needs to update.'.format(func))
            #t_date = date.today() + relativedelta(months=-CONFIG_WEB_FETCH_MAX_MONTH)
            #t_stock = cls.update_monthly_csv_from_web(p_stk_no, t_date.strftime('%Y%m'))
            t_stock = cls.update_monthly_csv_from_web(p_stk_no, date.today().strftime('%Y%m'))
        else:
            t_stock.csv_dict = pickle.loads(t_stock.csv_dict_pickle)
            #-> update from web if today's index not exist
            t_ym = date.today().strftime('%Y%m')
            if (not t_ym in t_stock.csv_dict.keys()) or (not str(date.today()) in t_stock.csv_dict[t_ym].keys()):
                t_stock_new = cls.update_monthly_csv_from_web(p_stk_no, date.today().strftime('%Y%m'))
                if not t_stock_new is None:
                    t_stock = t_stock_new
            else:
                logging.info('{}: load stock data from DB.'.format(func))
        return t_stock
    
    @classmethod
    def get_last_ym(cls, p_stk_no):
        func = '{} {}'.format(__name__,'get_last_ym')
        t_stock = cls.get_stock(p_stk_no)
        t_ym_list = sorted(t_stock.csv_dict.keys())
        logging.debug('{}: {}'.format(func,t_ym_list))
        return t_ym_list[-1]
    
    @classmethod
    def get_stk_update_ym(cls, p_stk_no):
        func = '{} {}'.format(__name__,'get_stk_update_ym')
        t_yearmonth_since = date.today() + relativedelta(months=-CONFIG_WEB_FETCH_MAX_MONTH)
        t_init_ym = t_yearmonth_since.strftime('%Y%m')
        t_stock = cls.get_stock(p_stk_no)

        t_dict_ym_list = sorted(t_stock.csv_dict.keys())
        t_check_date = date(t_yearmonth_since.year,t_yearmonth_since.month,1) + relativedelta(months=1)
        if t_init_ym in t_dict_ym_list:
            #-> update stock
            t_last_ym = t_init_ym
            while t_check_date.strftime('%Y%m') in t_dict_ym_list:
                t_last_ym = t_check_date.strftime('%Y%m')
                t_check_date += relativedelta(months=1)
            logging.debug('{}: stock {} update from last modified month {}'.format(func,p_stk_no,t_last_ym))
        else:
            #-> init stock
            t_last_ym = t_init_ym
            logging.debug('{}: stock {} has no history data, update from month {}'.format(func,p_stk_no,t_init_ym))
        return t_last_ym
            
        