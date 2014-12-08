
from utils.util_date import get_sample_date_list_2
from bankoftaiwan2.models_gold import BotGoldInfoModel
import bankoftaiwan2.models_exchange as bot_ex
from models import GoldInvestModel
from dateutil.relativedelta import relativedelta
from datetime import date
import logging

TOTAL_MONTH_TRACK = 12


class GoldReport(object):
    '''
    classdocs
    '''
    date_begin = None
    date_end = None
    m_exchange = None 
    m_bot_gold = None
    _sample_date_list = []
    _report_cost = []
    report_cost = []
    report_exchange = []
    report_market_value = []
    report_sell_price = []
    report_share = []
    report_profit = []

    @classmethod
    def get_report(cls, p_currency_type=bot_ex.CURRENCY_TWD):
        report = GoldReport(p_currency_type)
        if report is not None:
            report._get_history_cost_n_share_report(p_currency_type)
            report._get_history_market_value_report()

        return report
        
        
    def __init__(self, p_currency_type=bot_ex.CURRENCY_TWD):
        '''
        Constructor
        '''
        self._report_cost = []
        self.report_cost = []
        self.report_exchange = []
        self.report_market_value = []
        self.report_sell_price = []
        self.report_share = []
        self.report_profit = []
        
        #-> get BOT Gold Model
        self.m_bot_gold = BotGoldInfoModel.get_bot_gold(p_currency_type)
        if self.m_bot_gold is None:
            logging.warning(__name__ + ', __init__: gold data download fail!!!')
            return None
        
        #-> get BOT Exchange Model
        if (p_currency_type != bot_ex.CURRENCY_TWD):
            self.m_exchange = bot_ex.BotExchangeInfoModel.get_bot_exchange(bot_ex.CURRENCY_USD) 
            
            if self.m_exchange is None:
                logging.warning(__name__ + ',__init__: exchange data download fail!')
                return None


        #-> date_begin: the end day of the month which 12 months ago
        t_date_sample_start = date.today() - relativedelta(months=TOTAL_MONTH_TRACK)
        self.date_begin = date(t_date_sample_start.year,t_date_sample_start.month,1) - relativedelta(months=+1,days=+1)
        
        #-> date_end: yesterday
        self.date_end = date.today() - relativedelta(days=+1)

        #-> _sample_date_list
        self._sample_date_list = get_sample_date_list_2(self.date_begin, self.date_end, True)
        
        #-> get BOT gold sell price sample data
        self.report_sell_price = self.m_bot_gold.get_sample_value_list(self._sample_date_list)
        
        #-> get BOT exchange sample data
        if (p_currency_type != bot_ex.CURRENCY_TWD):
            self.report_exchange = self.m_exchange.get_sample_value_list(self._sample_date_list)
        else:
            for t_date in self._sample_date_list:
                self.report_exchange.append([t_date,1.0])        

    def _get_history_cost_n_share_report(self, p_currency_type):
        '''
        cost = amount_trade + trade_fee
        return list of [date, cost] 
        '''
        history = GoldInvestModel.all().filter('currency_type =', p_currency_type).order('date_invest')
        if self.date_begin < history[0].date_invest:
            self._report_cost.append([self.date_begin, 0.0])
        
        #-> create invest cost report
        cost = 0.0
        share = 0.0
        DATE_KEY_FORMAT = '%Y-%m'
        t_dict_share = {}
        t_dict_cost = {}
        for t_entry in history:
            if self.date_end >= t_entry.date_invest:
                cost += (t_entry.amount_trade + t_entry.trade_fee)
                self._report_cost.append([t_entry.date_invest, cost])
                share += t_entry.weight_purchase
                t_key = t_entry.date_invest.strftime(DATE_KEY_FORMAT)
                t_dict_share[t_key] = share
                t_dict_cost[t_key] = cost
        
        if self.date_end > history[history.count()-1].date_invest:
            self._report_cost.append([self.date_end, cost])
            
        logging.debug(__name__ + ': invest cost report \n' + str(self._report_cost))
        
        #-> create invest cost2 & share reports
        t_last_share = 0.0
        t_last_cost = 0.0
        for t_date in self._sample_date_list:
            t_key = t_date.strftime(DATE_KEY_FORMAT)
            if t_key in t_dict_share:
                self.report_cost.append([t_date,t_dict_cost[t_key]])
                self.report_share.append([t_date, t_dict_share[t_key]])
                t_last_share = t_dict_share[t_key]
                t_last_cost = t_dict_cost[t_key]
            else:
                self.report_share.append([t_date, t_last_share])
                self.report_cost.append([t_date, t_last_cost])
        logging.debug(__name__ + ': invest share report \n' + str(self.report_share))
        logging.debug(__name__ + ': invest 2nd cost report \n' + str(self.report_cost))

    def _get_history_market_value_report(self):
        '''
        return a list of [date, market_value] according to report_share list
        '''
        t_price_list = self.report_sell_price
        t_exchange_list = self.report_exchange
        #logging.debug('report_nav len:' + str(len(self.report_nav)))
        #logging.debug('report_exchange len:' + str(len(self.report_exchange)))
        #logging.debug('report_share len:' + str(len(self.report_share)))
        for i in range (len(self._sample_date_list)):
            t_date = self.report_share[i][0]
            self.report_market_value.append([t_date, \
                                             self.report_share[i][1]*t_price_list[i][1]*t_exchange_list[i][1]])
            if (self.report_cost[i][1] != 0):
                t_profit = 100*(self.report_market_value[i][1] - self.report_cost[i][1])/self.report_cost[i][1]
            else:
                t_profit = 0.0
            self.report_profit.append([t_date,t_profit])
        logging.debug(__name__ + ': sell price \n' + str(self.report_sell_price))
        logging.debug(__name__ + ': exchange \n' + str(self.report_exchange))
        logging.debug(__name__ + ': invest market value report \n' + str(self.report_market_value))
        logging.debug(__name__ + ': invest profit report \n' + str(self.report_profit))
        