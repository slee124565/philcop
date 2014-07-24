import logging
import calendar

from google.appengine.ext import db

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

from urlsrc.models import WebContentModel
from bankoftaiwan import exchange

URL_EXCHANGE_TEMPLATE = 'http://rate.bot.com.tw/Pages/UIP004/Download0042.ashx?lang=zh-TW&fileType=1&afterOrNot=1&whom={currency_type}&date1={date1}&date2={date2}'

def _parsing_bot_date_str(p_date_str):
    if len(p_date_str) != 8:
        logging.error('Invalid Date String Param: ' + p_date_str)
    return parser.parse(p_date_str[0:4] + '/' + p_date_str[4:6] + '/' + p_date_str[6:])
    
class BotExchangeModel(WebContentModel):
    currency_name = db.StringProperty()
    
    @classmethod
    def get_bot_exchange(cls, p_currency_type, p_months=12):
        if p_months < 0:
            logging.warning('Invalid Parameter Value p_month ' + str(p_months))
            return None
        
        end_date = date.today() - relativedelta(days=+1)
        begin_date = end_date - relativedelta(months=p_months)
        t_url = URL_EXCHANGE_TEMPLATE.format(currency_type=p_currency_type,
                                           date1=begin_date.strftime("%Y%m%d"),
                                           date2=end_date.strftime("%Y%m%d"))
        bot_model = BotExchangeModel.get_or_insert_webcontent(p_currency_type, t_url, date.today())
        if bot_model == None:
            logging.warning('BotExchangeMode get_bot_exchange fail')
        
        return bot_model
        
    def get_exchange_list(self, p_exchange_field):
        if p_exchange_field > exchange.FIELD_SELL_ON_DEMAND:
            logging.error('Invalid p_exchange_field value ' + str(p_exchange_field))
            return None
        
        data_list = []
        t_csv_list = str(self.content).decode('big5').splitlines()
        logging.debug('csv_list lenght ' + str(len(t_csv_list)))
        for t_list in t_csv_list:
            t_entry_list = t_list.split(',')
            #logging.debug(t_entry_list)
            if t_entry_list[exchange.FIELD_CURRENCY_NAME].strip() == self.currency_name:
                #logging.debug([t_entry_list[exchange.FIELD_DATE],t_entry_list[p_exchange_field]])
                t_date = _parsing_bot_date_str(t_entry_list[exchange.FIELD_DATE])
                t_value = t_entry_list[p_exchange_field]
                if (p_exchange_field == exchange.FIELD_BUY_CASH) or \
                    (p_exchange_field == exchange.FIELD_BUY_ON_DEMAND) or \
                    (p_exchange_field == exchange.FIELD_SELL_CASH) or \
                    (p_exchange_field == exchange.FIELD_SELL_ON_DEMAND):
                    t_value = float(t_value)
                data_list.append([t_date,t_value])
            else:
                logging.debug('skip csv list content: ' + t_list)
        
        data_list.sort(key=lambda x: x[0])
        logging.debug('get_exchange_list (' + str(len(data_list)) + '):\n' + str(data_list))
        return data_list
