from google.appengine.api import urlfetch

from models import TWSEStockModel

from datetime import date

import csv,StringIO
import logging, httplib

class OTCStockModel(TWSEStockModel):
    URL_TEMPLATE = 'http://www.otc.org.tw/web/stock/aftertrading/daily_trading_info/st43_download.php?l=zh-tw&d={yyym}&stkno={stk_no}&s=0,asc,0'
    
    @classmethod
    def parse_csv_content_dict(cls, p_csv_content):
        '''
        csv row data start from line 6 :: OFFSET = 5
        and skip last row data
        '''
        fname = '{} {}'.format(__name__,'parse_csv_content_dict')
        ROW_OFFSET = 5
        rows = p_csv_content.splitlines()
        rows = [','.join(cls.CSV_COLS)] + rows[ROW_OFFSET:-1]
        csv_content = '\n'.join(rows)

        csv_reader = csv.DictReader(StringIO.StringIO(csv_content))
        data_dict = {}
        for row in csv_reader:
            t_item = dict(row)
            t_item_date = cls.parse_csv_col_date(t_item[cls.CSV_COL_DATE])
            t_item[cls.CSV_COL_DATE] = t_item_date
            data_dict[str(t_item_date)] = t_item
            
        logging.debug('{}:{}'.format(fname,str(data_dict)))
        return data_dict

    @classmethod
    def get_yyym_format(cls, p_date):
        return '{}/{}'.format((p_date.year-1911),p_date.month)
    
    @classmethod
    def get_fetch_url(cls, p_stk_no, p_year_month):
        fname = '{} {}'.format(__name__,'get_fetch_url')
        t_yyy = int(p_year_month[:4])-1911
        t_m = p_year_month[-2:]
        t_yyym = '{}/{}'.format(t_yyy,t_m)
        t_fetch_url = cls.URL_TEMPLATE.format(yyym=t_yyym,stk_no=p_stk_no)
        logging.debug('{}: {}'.format(fname,t_fetch_url))
        return t_fetch_url

    @classmethod
    def test(cls):
        return cls.func_main()
        return cls.update_monthly_csv_from_web('3293', cls.get_yyym_format(date.today()))
        return cls.get_yyym_format(date.today())
        return cls.compose_key_name('3293')
        logging.debug('test: {}'.format(OTCStockModel.URL_TEMPLATE))
        return OTCStockModel.URL_TEMPLATE