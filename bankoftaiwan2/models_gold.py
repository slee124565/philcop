from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

import models_exchange as bot_ex

import csv,StringIO
import logging, httplib
import codecs

URL_GOLD_TW_TEMPLATE = 'http://rate.bot.com.tw/Pages/UIP005/Download.ashx?lang=zh-TW&fileType=1&whom=GB0030001000&date1={begin_date}&date2={end_date}&afterOrNot=1&curcd={currency_type}'

DICT_KEY_DATE_FORMAT = '%Y%m%d'

CSV_COL_DATE = 'date'
CSV_COL_CURRENCY = 'currency'
CSV_COL_UNIT = 'unit'
CSV_COL_BUY_ONDEMAND = 'buy_ondemand'
CSV_COL_SELL_ONDEMAND = 'sell_ondemand'
CSV_COLS = '{},{},{},{},{}'.format(CSV_COL_DATE,
                                   CSV_COL_CURRENCY,
                                   CSV_COL_UNIT,
                                   CSV_COL_BUY_ONDEMAND,
                                   CSV_COL_SELL_ONDEMAND
                                   )

class BotGoldInfoModel(db.Model):
    data_year_dict = {}
    
    @classmethod
    def compose_key_name(cls, p_currenc_type):
        return '{}'.format(p_currenc_type)
    
    @classmethod
    def get_bot_gold(cls, p_currency_type=bot_ex.CURRENCY_TWD):
        func = '{} {}'.format(__name__,'get_bot_gold')
        try:
            this_year = str(date.today().year)
            t_keyname = BotGoldInfoModel.compose_key_name(p_currency_type)
            t_gold = BotGoldInfoModel.get_by_key_name(t_keyname)
            if t_gold is None:
                if BotGoldDataModel._update_from_web(p_currency_type,this_year):
                    logging.info('{}: entity with key {} not exist, update from web...'.format(func,t_keyname))
                    t_gold = BotGoldInfoModel.get_by_key_name(t_keyname)
                else:
                    return None
            t_gold.data_year_dict = {}
            t_gold._load_year_data(this_year)
    
            #-> check if yesterday's data exist
            this_wkday = date.today().weekday()
            if this_wkday == 0:
                check_date = date.today() + relativedelta(days=-3)
            elif this_wkday in [1,2,3,4]:
                check_date = date.today() + relativedelta(days=-1)
            else:
                check_date = date.today() + relativedelta(days=(this_wkday-7))
            logging.debug('{}: check_date {}'.format(func,str(check_date)))
            if not check_date.strftime('%Y%m%d') in t_gold.data_year_dict[this_year].keys():
                logging.info('{}: update latest data from internet web.'.format(func))
                BotGoldDataModel._update_from_web(p_currency_type, this_year)
                t_gold._load_year_data(this_year)
    
            logging.debug('{}: with key {} success'.format(func,t_keyname))
            return t_gold
        
        except Exception, e:
            err_msg = '{}'.format(e)
            logging.error('{}: ERROR {}'.format(func,err_msg))
            return None

    def _load_year_data(self, p_year):
        func = '{} {}'.format(__name__,'_load_year_data')
        currency_type = self.key().name()
        t_keyname = BotGoldDataModel.compose_key_name(currency_type,p_year)
        t_data = BotGoldDataModel.get_by_key_name(t_keyname, parent=self)
        if t_data is None:
            logging.warning('{} with key {} return None'.format(func,t_keyname))
            self.data_year_dict[str(p_year)] = {}
            return False
        
        self.data_year_dict[str(p_year)] = t_data._get_data_dict()
        logging.debug('{}: with year {}'.format(func,p_year))
        return True

    def get_sample_value_list(self, p_date_list,p_csv_field=CSV_COL_SELL_ONDEMAND):
        t_list = []
        for t_date in p_date_list:
            t_list.append([t_date,self.get_value(t_date,p_csv_field)])
        return t_list
    
    def get_value(self,p_datetime,p_csv_field=CSV_COL_SELL_ONDEMAND):
        func = '{} {}'.format(__name__,'get_value')
        if not type(p_datetime) is date:
            logging.warning('{}: p_datetime type is not date!'.format(func))
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
            logging.debug('{}: {} rate not exist, check {} instead.'.format(func,t_key,str(t_prev_date)))
            t_key = t_prev_date.strftime(DICT_KEY_DATE_FORMAT)
            if str(t_prev_date.year) != t_year:
                return self.get_value(t_prev_date, p_csv_field)
            t_count += 1
            if t_count > 30: #-> protect
                return 0.0
        return float(t_year_dict[t_key][p_csv_field])

    def get_price_list(self, p_csv_field=CSV_COL_SELL_ONDEMAND):
        t_dataset = BotGoldDataModel.all().ancestor(self).order('year')
        t_list = []
        for t_data in t_dataset:
            if not t_data.year in self.data_year_dict.keys():
                if not self._load_year_data(t_data.year):
                    continue
            t_dict = self.data_year_dict[t_data.year]
            for t_key in t_dict:
                t_list.append([t_dict[t_key][CSV_COL_DATE],t_dict[t_key][p_csv_field]])
                
        t_list.sort(key=lambda x: x[0])    
        return t_list

class BotGoldDataModel(db.Model):
    content_csv = db.BlobProperty(default='')
    year = db.StringProperty()
    
    @classmethod
    def compose_key_name(cls, p_currency_type,p_year):
        return '{}_{}'.format(p_currency_type,p_year)
    
    @classmethod
    def _update_from_web(cls,p_currency_type,p_year):
        func = '{} {}'.format(__name__,'_update_from_web')
        try :
            model_parent = BotGoldInfoModel.get_or_insert(BotGoldInfoModel.compose_key_name(p_currency_type))
            t_model = BotGoldDataModel.get_or_insert(BotGoldDataModel.compose_key_name(p_currency_type, p_year),
                                                    parent=model_parent)
            t_model.year = str(p_year)
            begin_date = date(int(p_year),1,1).strftime(DICT_KEY_DATE_FORMAT)
            if int(p_year) == date.today().year:
                end_date = date.today() + relativedelta(days=-1)
                end_date = end_date.strftime(DICT_KEY_DATE_FORMAT)
            else:
                end_date = date(int(p_year),12,31).strftime(DICT_KEY_DATE_FORMAT)  
            t_url = URL_GOLD_TW_TEMPLATE.format(currency_type=p_currency_type,
                                               begin_date=begin_date,
                                               end_date=end_date)
    
            logging.info('{}: url:\n{}'.format(func,t_url))
        
            web_fetch = urlfetch.fetch(t_url)
            t_dwn_result = False
            if web_fetch.status_code == httplib.OK:
                t_model.content_csv = web_fetch.content
                logging.info('{}: get {} lines content'.format(func,len(t_model.content_csv.splitlines())))
                t_dwn_result = True
            t_model.put()
            
            return t_dwn_result
            
        except Exception, e:
            err_msg = '{}'.format(e)
            t_model.put()
            logging.warning('{} : ERROR {}'.format(func,err_msg))
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
