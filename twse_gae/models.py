from google.appengine.ext import db
from google.appengine.api import urlfetch

from lxml.html import document_fromstring
from lxml import etree

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

import csv,StringIO
import logging, httplib, pickle
from __builtin__ import classmethod

CONFIG_WEB_FETCH_MAX_MONTH = 12*3 # 3 years
CONFIG_STOCK_LIST = ['0050']
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


class TWSEStockModel(db.Model):
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
        
    def get_index_list(self, p_col_name=CSV_COL_CLOSE):
        func = '{} {}'.format(__name__,'get_index_list')
        t_index_list = []
        for t_ym_dict in self.csv_dict.values():
            for t_entry in t_ym_dict.values():
                t_index_list.append([t_entry[CSV_COL_DATE],t_entry[p_col_name]])
        
        t_index_list.sort(key=lambda x:x[0])
        logging.debug('{}:{}'.format(func,str(t_index_list)))
        return t_index_list
    
    @classmethod
    def compose_key_name(cls, stk_no):
        return stk_no
    
    @classmethod
    def update_monthly_dict(cls, p_stk_no, p_monthly_dict):
        func = '{} {}'.format(__name__,'update_monthly_dict')
        t_stock = TWSEStockModel.get_or_insert(TWSEStockModel.compose_key_name(p_stk_no))
        if not t_stock.csv_dict_pickle in [None, '']:
            t_stock.csv_dict = pickle.loads(t_stock.csv_dict_pickle)
        else:
            t_stock.csv_dict = {}
        t_entry = p_monthly_dict.itervalues().next()
        t_ym = t_entry[CSV_COL_DATE].strftime('%Y%m')
        t_stock.csv_dict[t_ym] = p_monthly_dict
        t_stock.csv_dict_pickle = pickle.dumps(t_stock.csv_dict)
        t_stock.put()
        logging.info('{}: stock {} month {} updated'.format(func,p_stk_no,t_ym))
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
        rows = [','.join(CSV_COLS)] + rows[ROW_OFFSET:]
        csv_content = '\n'.join(rows)
        #logging.debug('{}: csv_content:\n{}'.format(func,csv_content))
        csv_reader = csv.DictReader(StringIO.StringIO(csv_content))
        data_dict = {}
        for row in csv_reader:
            t_item = dict(row)
            t_item_date = cls.parse_csv_col_date(t_item[CSV_COL_DATE])
            t_item[CSV_COL_DATE] = t_item_date
            data_dict[str(t_item_date)] = t_item
            
        logging.debug('{}:{}'.format(func,str(data_dict)))
        return data_dict

    @classmethod
    def update_monthly_csv_from_web(cls, p_stk_no, p_year_month):
        '''
        return model entity
        '''
        func = '{} {}'.format(__name__,'update_monthly_csv_from_web')
        t_url = URL_TEMPLATE.format(Ym=p_year_month,stk_no=p_stk_no)
        logging.info('{}: fetch url:\n{}'.format(func,t_url))
        
        try :
            web_fetch = urlfetch.fetch(t_url)
            if web_fetch.status_code == httplib.OK:
                web_content = web_fetch.content
                t_monthly_dict = cls.parse_csv_content_dict(web_content)
                t_stock = cls.update_monthly_dict(p_stk_no,t_monthly_dict)
                return t_stock
            else:
                logging.warning('{}: urlfetch fail status code {}'.format(func,web_fetch.status_code))
                return None
        except urlfetch.DownloadError:
            logging.warning('{} : Internet Download Error'.format(func))
            return None
        '''
        except Exception, e:
            logging.error('{} : Exception {}'.format(func, str(e)))
            return None
        '''
       
    @classmethod
    def get_stock(cls, p_stk_no):
        func = '{} {}'.format(__name__,'get_stock')
        
        logging.info('{}: query stock {}'.format(func,p_stk_no))
        t_stock = TWSEStockModel.get_by_key_name(cls.compose_key_name(p_stk_no))
        if t_stock is None or t_stock.csv_dict_pickle in [None,'']:
            t_stock = cls.update_monthly_csv_from_web(p_stk_no, date.today().strftime('%Y%m'))
        else:
            t_stock.csv_dict = pickle.loads(t_stock.csv_dict_pickle)
            #-> update from web if today's index not exist
            t_ym = date.today().strftime('%Y%m')
            if (not t_ym in t_stock.csv_dict.keys()) or (not str(date.today()) in t_stock.csv_dict[t_ym].keys()):
                t_stock = cls.update_monthly_csv_from_web(p_stk_no, date.today().strftime('%Y%m'))
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
    
            
        
    
        