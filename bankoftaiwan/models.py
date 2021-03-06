import logging

from google.appengine.ext import db

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

from urlsrc.models import WebContentModel
from bankoftaiwan import exchange, const_inc
import phicops.utils

URL_EXCHANGE_TEMPLATE = 'http://rate.bot.com.tw/Pages/UIP004/Download0042.ashx?lang=zh-TW&fileType=1&afterOrNot=1&whom={currency_type}&date1={date1}&date2={date2}'

#-> ex: 'http://rate.bot.com.tw/Pages/UIP005/Download.ashx?lang=zh-TW&fileType=1&whom=GB0030001000&date1=20140101&date2=20140925&afterOrNot=1&curcd=TWD'
#-> trigger csv file download
URL_GOLD_TW_TEMPLATE = 'http://rate.bot.com.tw/Pages/UIP005/Download.ashx?lang=zh-TW&fileType=1&whom=GB0030001000&date1={date1}&date2={date2}&afterOrNot=1&curcd={currency_type}'

DATE_INDEX = 0
VALUE_INDEX = 1

def _parsing_bot_date_str(p_date_str):
    if len(p_date_str) != 8:
        logging.error(__name__ + ': Invalid Date String Param: ' + p_date_str)
    return parser.parse(p_date_str[0:4] + '/' + p_date_str[4:6] + '/' + p_date_str[6:]).date()
    
class BotExchangeModel(WebContentModel):
    currency_name = db.StringProperty()
    
    @classmethod
    def get_bot_exchange(cls, p_currency_type, p_months=12, p_flush=False):
        if p_months < 0:
            logging.warning(__name__ + ': Invalid Parameter Value p_month ' + str(p_months))
            return None
        
        end_date = date.today() - relativedelta(days=+1)
        begin_date = end_date - relativedelta(months=p_months)
        t_url = URL_EXCHANGE_TEMPLATE.format(currency_type=p_currency_type,
                                           date1=begin_date.strftime("%Y%m%d"),
                                           date2=end_date.strftime("%Y%m%d"))
        if p_flush:
            t_expired_date = None
        else:
            t_expired_date = date.today()
        bot_model = BotExchangeModel.get_or_insert_webcontent(p_currency_type,t_url,t_expired_date,p_months)
        if bot_model == None:
            logging.warning(__name__ + ': BotExchangeMode get_bot_exchange fail')
        
        if bot_model.currency_name == None:
            bot_model.currency_name = p_currency_type
            bot_model.put()
            
        return bot_model
    
    def get_sample_value_list(self, p_date_list,p_exchange_field=exchange.FIELD_SELL_ON_DEMAND):
        '''
        return a list of [date, exchange_rate] according to date list p_date_list
        '''
        rate_list = self.get_exchange_list(p_exchange_field)
        return self.sample_value_list(p_date_list, rate_list)

    
    def get_rate(self, p_datetime, p_exchange_field=exchange.FIELD_SELL_ON_DEMAND):
        exchange_list = self.get_exchange_list(p_exchange_field)
        t_count = 0
        if (exchange_list[0][DATE_INDEX]).date() <= p_datetime:
            for t_entry in exchange_list:
                if p_datetime == t_entry[DATE_INDEX].date():
                    return exchange_list[t_count-1][VALUE_INDEX]
                t_count += 1
        logging.warning(__name__ + ': get_rate: no matched date value exist!')
        return 0
    
    
    def get_discrete_exchange_list(self, p_exchange_field=exchange.FIELD_SELL_ON_DEMAND, p_select_day=phicops.utils.MONTH_DAY_END):
        #data_list = []
        exchange_list = self.get_exchange_list(p_exchange_field)
        return phicops.utils.get_discrete_date_data_list(exchange_list, p_select_day)
        '''
        DATE_INDEX = 0
        if exchange_list:
            if p_select_day != exchange.MONTH_DAY_END:
                for t_entry in exchange_list:
                    if t_entry[DATE_INDEX].day == p_select_day:
                        data_list.append(t_entry)
            else: #-> end of month
                prev_entry_index = -1
                for t_entry in exchange_list:
                    if t_entry[DATE_INDEX].day == 1:
                        if prev_entry_index >= 0:
                            data_list.append(exchange_list[prev_entry_index])
                    prev_entry_index += 1
        logging.debug(__name__ + ': get_discrete_exchange_list\n' + str(data_list))
        return data_list
        '''
            
    def get_exchange_list(self, p_exchange_field):
        if p_exchange_field > exchange.FIELD_SELL_ON_DEMAND:
            logging.error(__name__ + ': Invalid p_exchange_field value ' + str(p_exchange_field))
            return None
        
        data_list = []
        t_csv_list = str(self.content).decode('big5').splitlines()
        #logging.debug(__name__ + ': csv_list lenght ' + str(len(t_csv_list)))
        for t_list in t_csv_list:
            t_entry_list = t_list.split(',')
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
                logging.debug(__name__ + ': skip csv list content: ' + t_list)
        
        data_list.sort(key=lambda x: x[0])
        #logging.debug('currency name: ' + str(self.currency_name) + '\n' + str(data_list))
        
        #-> add holiday entry with previous day's value
        t_end_date = date.today() - relativedelta(days=+1)

        t_date_check = data_list[0][DATE_INDEX] + relativedelta(days=+1)
        index = 1
        #while index < t_total:
        while t_date_check <= t_end_date:
            #logging.debug(__name__ + ': checking entry: ' + str(data_list[index]) + ' with index ' + str(index) + ' date ' + str(t_date_check))
            if data_list[index][DATE_INDEX] == t_date_check:
                #-> date_check entry exist; skip to check next entry
                index += 1
            else:
                #-> date_checck entry not exist; add with previous entry's value
                data_list.append([(t_date_check),data_list[index-1][VALUE_INDEX]])
                #logging.debug(__name__ + ': append entry ' + str([(t_date_check),data_list[index-1][VALUE_INDEX]]))
            t_date_check = t_date_check + relativedelta(days=+1)
        data_list.sort(key=lambda x: x[0])
        
        #-> append entries until to previous day
        
        #logging.debug(__name__ + ': get_exchange_list (' + str(len(data_list)) + '):\n' + str(data_list))
        return data_list

class BotGoldModel(WebContentModel):
    
    @classmethod
    def get_bot_gold(cls, p_currency_type=exchange.CURRENCY_TWD, p_months=12, p_flush=False):
        
        end_date = date.today() - relativedelta(days=+1)
        begin_date = end_date - relativedelta(months=p_months)
        t_url = URL_GOLD_TW_TEMPLATE.format(currency_type=p_currency_type,
                                           date1=begin_date.strftime("%Y%m%d"),
                                           date2=end_date.strftime("%Y%m%d"))
        if p_flush:
            t_expired_date = None
        else:
            t_expired_date = date.today()
        t_model = BotGoldModel.get_or_insert_webcontent(p_currency_type,t_url,t_expired_date,p_months)
        if t_model == None:
            logging.warning(__name__ + ': BotGoldModel get_bot_gold fail')
        
            if t_model.currency_name == None:
                t_model.currency_name = p_currency_type
                t_model.put()
            
        return t_model
    
    def get_sample_value_list(self, p_date_list, p_gold_field=const_inc.FIELD_GOLD_SELL):
        '''
        return a list of [date, exchange_rate] according to date list p_date_list
        '''
        gold_price_list = self.get_price_list(p_gold_field)
        return self.sample_value_list(p_date_list, gold_price_list)

    def get_price_list(self, p_gold_field=const_inc.FIELD_GOLD_SELL):
        '''
        p_gold_file: const_inc.FIELD_GOLD_BUY or const_inc.FIELD_GOLD_SELL
        '''
        data_list = []
        t_csv_list = str(self.content).decode('big5').splitlines()
        logging.debug(__name__ + ': csv_list lenght ' + str(len(t_csv_list)))
        #-> skip first field name row data  
        for t_list in t_csv_list[1:]:
            t_entry_list = t_list.split(',')
            t_date = _parsing_bot_date_str(t_entry_list[const_inc.FIELD_GOLD_DATE])
            t_value = float(t_entry_list[p_gold_field])
            data_list.append([t_date,t_value])
        
        data_list.sort(key=lambda x: x[0])
        
        #-> add holiday entry with previous day's value
        t_end_date = date.today() - relativedelta(days=+1)

        t_date_check = data_list[0][DATE_INDEX] + relativedelta(days=+1)
        index = 1
        while t_date_check <= t_end_date:
            if data_list[index][DATE_INDEX] == t_date_check:
                #-> date_check entry exist; skip to check next entry
                index += 1
            else:
                #-> date_checck entry not exist; add with previous entry's value
                data_list.append([(t_date_check),data_list[index-1][VALUE_INDEX]])
                #logging.debug(__name__ + ': append entry ' + str([(t_date_check),data_list[index-1][VALUE_INDEX]]))
            t_date_check = t_date_check + relativedelta(days=+1)
        data_list.sort(key=lambda x: x[0])
        
        logging.debug(__name__ + ': get_price_list (' + str(len(data_list)) + '):\n' + str(data_list))
        return data_list
        