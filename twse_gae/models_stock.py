from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from lxml.html import document_fromstring
from lxml import etree

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

import csv,StringIO
import logging, httplib, pickle, codecs
from twse_gae.models import TWSEStockModel
from twse_gae.models_otc import OTCStockModel


CONFIG_STOCK_LIST = ['0050','2330','3293']


class StockModel(db.Model):
    STOCK_TYPE_TWSE = 'twse'
    STOCK_TYPE_OTC = 'otc'
    URL_CODE_LIST_TWSE = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
    URL_CODE_LIST_OTC = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=4'
    CSV_COL_ID = 'id'
    CSV_COL_NAME = 'name'
    CSV_COL_type = 'type'
    CSV_CONTENT_HEADER = 'id,name,type'

    '''
    csv_dict = {
                'twse': {code:name,...},
                'otc': {code:name,...},
                }
    '''
    
    csv_dict_pickle = db.BlobProperty()
    csv_dict = {}

    @classmethod
    def get_model(cls):
        fname = '{} {}'.format(__name__,'get_model')
        t_model = cls.get_or_insert('stock')
        if not t_model.csv_dict_pickle in [None, '']:
            t_model.csv_dict = pickle.loads(t_model.csv_dict_pickle)
        else:
            t_model.csv_dict = {}
        #logging.debug('{}: {}'.format(fname,str(t_model.csv_dict)))
        return t_model

    
    def get_stock_type(self, p_stk_no):
        fname = '{} {}'.format(__name__,'get_stock_type')
        #logging.debug('{}: check stock {} type'.format(fname,p_stk_no))

        if p_stk_no in self.csv_dict[self.STOCK_TYPE_TWSE].keys():
            t_type = self.STOCK_TYPE_TWSE
        elif p_stk_no in self.csv_dict[self.STOCK_TYPE_OTC].keys():
            t_type = self.STOCK_TYPE_OTC
        else:
            t_type = None
        logging.debug('{}: stock {} type is {}'.format(fname,p_stk_no,t_type))
        return t_type

    @classmethod
    def get_type_by_stk_no(cls, p_stk_no):
        t_model = cls.get_model()
        return t_model.get_stock_type(p_stk_no)
        
        
    @classmethod
    def get_stock(cls, p_stk_no):
        fname = '{} {}'.format(__name__,'get_stock')
        logging.debug('{}: with {}'.format(fname,p_stk_no))
        
        t_stk_type = cls.get_type_by_stk_no(p_stk_no)
        if t_stk_type == cls.STOCK_TYPE_TWSE:
            t_stock = TWSEStockModel.get_stock(p_stk_no)
        elif t_stk_type == cls.STOCK_TYPE_OTC:
            t_stock = OTCStockModel.get_stock(p_stk_no)
        else:
            t_stock = None
        logging.info('{}: with {}'.format(fname,t_stock))
        return t_stock
    
    @classmethod
    def parse_csv_dict(cls, p_type, p_csv_content):
        fname = '{} {}'.format(__name__,'update_csv_dict')
        csv_reader = csv.DictReader(StringIO.StringIO(p_csv_content))
        data_dict = {}
        for row in csv_reader:
            t_item = dict(row)
            t_item_id = cls.parse_csv_col_date(t_item[cls.CSV_COL_ID])
            data_dict[str(t_item_id)] = t_item
            
        logging.debug('{}:{}'.format(fname,str(data_dict)))
        return data_dict
            
    @classmethod
    def update_from_web(cls, p_type):
        fname = '{} {}'.format(__name__,'update_from_web')
        
        if p_type == cls.STOCK_TYPE_TWSE:
            web_fetch = urlfetch.fetch(cls.URL_CODE_LIST_TWSE)
        else:
            web_fetch = urlfetch.fetch(cls.URL_CODE_LIST_OTC)
            
        logging.debug('{}: fetch {} \n{}'.format(fname,p_type,cls.URL_CODE_LIST_TWSE))
        
        try :
            if web_fetch.status_code == httplib.OK:
                t_dict_data = {}
                
                #web_content = document_fromstring(codecs.decode(web_fetch.content,'big5','ignore'))
                web_content = document_fromstring(web_fetch.content)
                t_tables = web_content.xpath("/html/body/table[2]")
                t_table = t_tables[0]
                for t_row in t_table[2:]:
                    #logging.debug(etree.tostring(t_row))
                    if len(t_row) == 7:
                        #logging.debug(etree.tostring(t_row[0]))
                        t_stk_no = ''
                        t_stk_name = t_row[0].text
                        t_industry_type = t_row[4].text
                        for t_chr in t_stk_name:
                            if ord(t_chr) > 127:
                                break;
                            else:
                                t_stk_no += t_chr
                        t_dict_data[t_stk_no.strip()] = [t_stk_name,t_industry_type]
                    else:
                        pass
                        #logging.debug('{}: ignore rowdata with len {}'.format(fname,len(t_row)))
                t_model = cls.get_model()
                t_model.csv_dict[p_type] = t_dict_data
                t_model.csv_dict_pickle = pickle.dumps(t_model.csv_dict)
                t_model.put()
                return True
            else:
                logging.warning('{}: urlfetch status code {}'.format(fname,web_content.status_code))
                return False
        except urlfetch.DownloadError:
            logging.warning('{} : Internet Download Error'.format(fname))
            return False
                
                    
                    
            
            
            
            
            
        