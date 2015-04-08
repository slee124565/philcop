from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from datetime import date, datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

import csv,StringIO
import logging, httplib
import codecs

CURRENCY_JPY = 'JPY'
CURRENCY_USD = 'USD'
CURRENCY_CNY = 'CNY'
CURRENCY_TWD = 'TWD'
CURRENCY_AUD = 'AUD'
CURRENCY_LIST = [CURRENCY_JPY,
                 CURRENCY_USD,
                 CURRENCY_CNY,
                 CURRENCY_AUD,
                 ]

#'date,currency,buy,buy_cash,buy_ondemand,sell,sell_cash,sell_ondemand,'
CSV_COL_DATE = 'date'
CSV_COL_CURRENCY = 'currency'
CSV_COL_BUY = 'buy'
CSV_COL_BUY_CASH = 'buy_cash'
CSV_COL_BUY_ONDEMAND = 'buy_ondemand'
CSV_COL_SELL = 'sell'
CSV_COL_SELL_CASH = 'sell_cash'
CSV_COL_SELL_ONDEMAND = 'sell_ondemand'
CSV_COLS = '{},{},{},{},{},{},{},{},'.format(CSV_COL_DATE,
                                             CSV_COL_CURRENCY,
                                             CSV_COL_BUY,
                                             CSV_COL_BUY_CASH,
                                             CSV_COL_BUY_ONDEMAND,
                                             CSV_COL_SELL,
                                             CSV_COL_SELL_CASH,
                                             CSV_COL_SELL_ONDEMAND)

URL_EXCHANGE_TEMPLATE = 'http://rate.bot.com.tw/Pages/UIP004/Download0042.ashx?lang=zh-TW&fileType=1&afterOrNot=1&whom={currency_type}&date1={begin_date}&date2={end_date}'

#-> ex: 'http://rate.bot.com.tw/Pages/UIP005/Download.ashx?lang=zh-TW&fileType=1&whom=GB0030001000&date1=20140101&date2=20140925&afterOrNot=1&curcd=TWD'
#-> trigger csv file download
URL_GOLD_TW_TEMPLATE = 'http://rate.bot.com.tw/Pages/UIP005/Download.ashx?lang=zh-TW&fileType=1&whom=GB0030001000&date1={begin_date}&date2={end_date}&afterOrNot=1&curcd={currency_type}'

DICT_KEY_DATE_FORMAT = '%Y%m%d'

class BotExchangeInfoModel(db.Model):
    data_year_dict = {}

    @classmethod
    def get_bot_exchange(cls, p_currency_type):    
        this_year = str(date.today().year)
        key_name = BotExchangeInfoModel.compose_key_name(p_currency_type)
        t_info = BotExchangeInfoModel.get_by_key_name(key_name)
        if t_info is None:
            logging.info('get_bot_exchange: entity with key {} not exist, update from web...'.format(key_name))

            if BotExchangeDataModel._update_from_web(p_currency_type, this_year):
                t_info = BotExchangeInfoModel.get_by_key_name(key_name)
            else:
                return None
        t_info.data_year_dict = {}
        t_info._load_year_data(this_year)

        #-> check if yesterday's data exist
        this_wkday = date.today().weekday()
        if this_wkday == 0:
            check_date = date.today() + relativedelta(days=-3)
        elif this_wkday in [1,2,3,4]:
            check_date = date.today() + relativedelta(days=-1)
        else:
            check_date = date.today() + relativedelta(days=(this_wkday-7))
        logging.debug('get_bot_exchange: check_date {}'.format(str(check_date)))
        if not check_date.strftime('%Y%m%d') in t_info.data_year_dict[this_year].keys():
            logging.info('get_bot_exchange: update latest data from internet web.')
            BotExchangeDataModel._update_from_web(p_currency_type, this_year)
            t_info._load_year_data(this_year)

        logging.debug('get_bot_exchange: with key {} success'.format(key_name))
        return t_info

    @classmethod
    def compose_key_name(cls, p_currency_type):
        return str(p_currency_type)
    
    def _load_year_data(self, p_year):
        currency_type = self.key().name()
        t_keyname = BotExchangeDataModel.compose_key_name(currency_type,p_year)
        t_data = BotExchangeDataModel.get_by_key_name(t_keyname, parent=self)
        if t_data is None:
            logging.warning('_load_year_data with key {} return None'.format(t_keyname))
            self.data_year_dict[str(p_year)] = {}
            return False
        
        self.data_year_dict[str(p_year)] = t_data._get_data_dict()
        logging.debug('_load_year_data: with year {}'.format(p_year))
        return True
    
    def get_sample_value_list(self, p_date_list,p_exchange_field=CSV_COL_SELL_ONDEMAND):
        t_list = []
        for t_date in p_date_list:
            t_list.append([t_date,self.get_rate(t_date,p_exchange_field)])
        return t_list
    
    def get_rate(self, p_datetime, p_exchange_field=CSV_COL_SELL_ONDEMAND):
        func = '{} {}'.format(__name__,'get_rate')
        if not type(p_datetime) is date:
            logging.warning('get_rate: p_datetime type is not date!')
            return 0.0
        
        t_year = str(p_datetime.year)
        if not t_year in self.data_year_dict.keys():
            if not self._load_year_data(t_year):
                return 0.0
        t_year_dict = self.data_year_dict[t_year]
        t_key = p_datetime.strftime(DICT_KEY_DATE_FORMAT)
        t_count = 0
        t_prev_date = p_datetime
        while not t_key in t_year_dict.keys():
            t_prev_date = t_prev_date + relativedelta(days=-1)
            logging.debug('get_rate: {} rate not exist, check {} instead.'.format(t_key,str(t_prev_date)))
            t_key = t_prev_date.strftime(DICT_KEY_DATE_FORMAT)
            if str(t_prev_date.year) != t_year:
                logging.debug('{}: year change'.format(func))
                return self.get_rate(t_prev_date, p_exchange_field)
            t_count += 1
            if t_count > 30: #-> protect
                logging.warning('{}: loop protect activate'.format(func))
                return 0.0

        return float(t_year_dict[t_key][p_exchange_field])
    
    def get_exchange_list(self,p_exchange_field=CSV_COL_SELL_ONDEMAND):
        t_dataset = BotExchangeDataModel.all().ancestor(self).order('year')
        t_list = []
        for t_data in t_dataset:
            if not t_data.year in self.data_year_dict.keys():
                if not self._load_year_data(t_data.year):
                    continue
            t_dict = self.data_year_dict[t_data.year]
            for t_key in t_dict:
                t_list.append([datetime.strptime(t_dict[t_key][CSV_COL_DATE],DICT_KEY_DATE_FORMAT).date(),
                               float(t_dict[t_key][p_exchange_field])])
                
        t_list.sort(key=lambda x: x[0])    
        return t_list
    
    def get_value_list(self, p_year_since=date.today().year, p_exchange_field=CSV_COL_SELL_ONDEMAND):
        t_list = []
        t_year = date.today().year
        while t_year >= p_year_since:
            if not str(t_year) in self.data_year_dict.keys():
                self._load_year_data(t_year)
            for t_key in self.data_year_dict[str(t_year)]:
                t_list.append([datetime.strptime(self.data_year_dict[str(t_year)][t_key][CSV_COL_DATE],DICT_KEY_DATE_FORMAT).date(),
                               float(self.data_year_dict[str(t_year)][t_key][p_exchange_field])])
            t_year = t_year -1
            
        t_list.sort(key=lambda x: x[0])    
        return t_list
   
class BotExchangeDataModel(db.Model):
    content_csv = db.BlobProperty(default='')
    year = db.StringProperty()
    
    @classmethod
    def compose_key_name(cls, p_currency_type, p_year):
        return '{}_{}'.format(p_currency_type,p_year)
    
    @classmethod
    def _update_from_web(cls, p_currency_type, p_year=date.today().year):
        func = '{} {}'.format(__name__,'_update_from_web')
        try :
            model_parent = BotExchangeInfoModel.get_or_insert(BotExchangeInfoModel.compose_key_name(p_currency_type))
            t_model = BotExchangeDataModel.get_or_insert(BotExchangeDataModel.compose_key_name(p_currency_type, p_year),
                                                    parent=model_parent)
            t_model.year = str(p_year)
            begin_date = date(int(p_year),1,1).strftime("%Y%m%d")
            if int(p_year) == date.today().year:
                end_date = date.today() + relativedelta(days=-1)
                end_date = end_date.strftime("%Y%m%d")
            else:
                end_date = date(int(p_year),12,31).strftime("%Y%m%d")  
            t_url = URL_EXCHANGE_TEMPLATE.format(currency_type=p_currency_type,
                                               begin_date=begin_date,
                                               end_date=end_date)
    
            logging.info('_update_from_web, url: ' + t_url)
        
            web_fetch = urlfetch.fetch(t_url)
            t_dwn_result = False
            if web_fetch.status_code == httplib.OK:
                t_model.content_csv = web_fetch.content
                logging.info('{}: get {} lines content'.format(func,len(t_model.content_csv.splitlines())))
                t_dwn_result = True
            t_model.put()
            
            return t_dwn_result
            
        except DownloadError:
            t_model.put()
            logging.warning('_update_from_web : Internet Download Error')
            return False

    def _get_data_dict(self):
        col_names = [CSV_COLS]
        rows = self.content_csv.splitlines()
        rows = col_names + rows[1:]
        csv_content = '\n'.join(rows)
        #logging.debug('csv_content:\n{}'.format(csv_content))
        csv_reader = csv.DictReader(StringIO.StringIO(csv_content))
        data_dict = {}
        for row in csv_reader:
            t_item = dict(row)
            data_dict[t_item['date']] = t_item
        return data_dict
