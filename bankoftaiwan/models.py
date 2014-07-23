import logging
import calendar

from google.appengine.ext import db

from dateutil import parser

from urlsrc.models import WebContentModel
from bankoftaiwan import exchange

def _parsing_bot_date_str(p_date_str):
    if len(p_date_str) != 8:
        logging.error('Invalid Date String Param: ' + p_date_str)
    return parser.parse(p_date_str[0:4] + '/' + p_date_str[4:6] + '/' + p_date_str[6:])
    
class BotExchangeModel(WebContentModel):
    currency_name = db.StringProperty()
    
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
                
        logging.debug('get_exchange_list (' + str(len(data_list)) + '):\n' + str(data_list))
        return data_list
