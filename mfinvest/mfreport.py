
from mfinvest.models import MutualFundInvestModel
from fundclear.models import FundClearModel
from bankoftaiwan.models import BotExchangeModel, exchange

from datetime import date
from dateutil.relativedelta import relativedelta
import logging

def get_sample_date_list(p_count=12,p_inc_last_day=True):
    t_sample_date_list = []
    
    #-> date_begin: the end day of the month which 12 months ago
    t_date_sample_start = date.today() - relativedelta(months=p_count)
    t_date_begin = date(t_date_sample_start.year,t_date_sample_start.month+1,1) - relativedelta(days=+1)
    
    #-> date_end: yesterday
    t_date_end = date.today() - relativedelta(days=+1)
    #self.date_end = date(date.today().year,date.today().month,1) - relativedelta(days=+1)
    
    #-> _sample_date_list
    t_check_date = t_date_begin
    while (t_check_date <= t_date_end):
        t_sample_date_list.append(t_check_date)
        t_check_date = date(t_check_date.year,t_check_date.month,1) + relativedelta(months=+2) - relativedelta(days=+1)
    
    #-> add yesterday into sample list
    if p_inc_last_day:
        t_sample_date_list.append(date.today() - relativedelta(days=+1))
    
    return t_sample_date_list

def get_sample_date_list_2(p_date_begin, p_date_end):
    '''
    return a list of [date] for each month between p_date_begin and p_date_end
    '''
    t_sample_date_list = []
    
    #-> date_begin: the end day of the month for p_date_begin
    t_date_sample_start = p_date_begin
    t_date_begin = date(t_date_sample_start.year,t_date_sample_start.month+1,1) - relativedelta(days=+1)
    
    t_date_end =p_date_end
    
    #-> _sample_date_list
    t_check_date = t_date_begin
    while (t_check_date <= t_date_end):
        t_sample_date_list.append(t_check_date)
        t_check_date = date(t_check_date.year,t_check_date.month,1) + relativedelta(months=+2) - relativedelta(days=+1)
    
    return t_sample_date_list

class MFReport():
    fund_id = None
    currency_type = None
    date_begin = None
    date_end = None
    m_fund = None               #-> FundClearModel
    m_exchange = None           #-> BotExchangeModel
    _sample_date_list = []
    report_cost = []            #-> only contain date that change
    report_cost2 = []           #-> sync with _sample_date_list
    report_share = []           #-> sync with _sample_date_list
    report_market_value = []    #-> sync with _sample_date_list
    report_nav = []             #-> sync with _sample_date_list
    report_exchange = []        #-> sync with _sample_date_list
    report_profit = []          #-> sync with _sample_date_list
    
    @classmethod
    def get_mfreport_by_id(cls, p_fund_id, p_currency_type):
        report = MFReport(fund_id=p_fund_id, currency_type=p_currency_type)
        report.m_fund = FundClearModel.get_fund(report.fund_id)
        report.m_exchange = BotExchangeModel.get_bot_exchange(exchange.CURRENCY_JPY)
        
        if report.m_fund is None or report.m_exchange is None:
            logging.warning(__name__ + ', get_mfreport_by_id: fund or exchange data download fail!!!')
            return None

        #report.report_nav = report.m_fund.get_discrete_value_list()
        report.report_nav = report.m_fund.get_sample_value_list(report._sample_date_list)
        
        #report.report_exchange = report.m_exchange.get_discrete_exchange_list()
        report.report_exchange = report.m_exchange.get_sample_value_list(report._sample_date_list)

        report._get_history_cost_n_share_report()

        report._get_history_market_value_report()

        return report
    
    def __init__(self, fund_id, currency_type):
        '''
        date_begin: the end day of the month which 12 months ago
        date_end: yesterday
        _sample_date_list: each end day of month between date_begin and date_end + date_end
        '''
        self.fund_id = fund_id
        self.currency_type = currency_type
        
        #-> date_begin: the end day of the month which 12 months ago
        t_date_sample_start = date.today() - relativedelta(months=+12)
        self.date_begin = date(t_date_sample_start.year,t_date_sample_start.month+1,1) - relativedelta(days=+1)
        
        #-> date_end: yesterday
        self.date_end = date.today() - relativedelta(days=+1)
        #self.date_end = date(date.today().year,date.today().month,1) - relativedelta(days=+1)
        
        #-> _sample_date_list
        self._sample_date_list = []
        t_check_date = self.date_begin
        while (t_check_date <= self.date_end):
            self._sample_date_list.append(t_check_date)
            t_check_date = date(t_check_date.year,t_check_date.month,1) + relativedelta(months=+2) - relativedelta(days=+1)
        self._sample_date_list.append(date.today() - relativedelta(days=+1))
        
        self.report_cost = []
        self.report_cost2 = []
        self.report_exchange = []
        self.report_market_value = []
        self.report_nav = []
        self.report_profit = []
        self.report_share = []
        
    def _get_history_cost_n_share_report(self):
        '''
        cost = amount_trade + trade_fee
        return list of [date, cost] 
        '''
        history = MutualFundInvestModel.all().filter('id =', self.fund_id).order('date_invest')
        if self.date_begin < history[0].date_invest:
            self.report_cost.append([self.date_begin, 0.0])
        
        #-> create invest cost report
        cost = 0.0
        share = 0.0
        DATE_KEY_FORMAT = '%Y-%m'
        t_dict_share = {}
        t_dict_cost = {}
        for t_entry in history:
            if self.date_end >= t_entry.date_invest:
                cost += (t_entry.amount_trade + t_entry.trade_fee)
                self.report_cost.append([t_entry.date_invest, cost])
                share += t_entry.share
                t_key = t_entry.date_invest.strftime(DATE_KEY_FORMAT)
                t_dict_share[t_key] = share
                t_dict_cost[t_key] = cost
        
        if self.date_end > history[history.count()-1].date_invest:
            self.report_cost.append([self.date_end, cost])
            
        logging.debug(__name__ + ': invest cost report \n' + str(self.report_cost))
        
        #-> create invest cost2 & share reports
        t_last_share = 0.0
        t_last_cost = 0.0
        for t_date in self._sample_date_list:
            t_key = t_date.strftime(DATE_KEY_FORMAT)
            if t_key in t_dict_share:
                self.report_cost2.append([t_date,t_dict_cost[t_key]])
                self.report_share.append([t_date, t_dict_share[t_key]])
                t_last_share = t_dict_share[t_key]
                t_last_cost = t_dict_cost[t_key]
            else:
                self.report_share.append([t_date, t_last_share])
                self.report_cost2.append([t_date, t_last_cost])
        logging.debug(__name__ + ': invest share report \n' + str(self.report_share))
        logging.debug(__name__ + ': invest 2nd cost report \n' + str(self.report_cost2))

    def _get_history_market_value_report(self):
        '''
        return a list of [date, market_value] according to report_share list
        '''
        t_fund_nav_list = self.report_nav
        t_exchange_list = self.report_exchange
        #logging.debug('report_nav len:' + str(len(self.report_nav)))
        #logging.debug('report_exchange len:' + str(len(self.report_exchange)))
        #logging.debug('report_share len:' + str(len(self.report_share)))
        for i in range (len(self._sample_date_list)):
            t_date = self.report_share[i][0]
            self.report_market_value.append([t_date, \
                                             self.report_share[i][1]*t_fund_nav_list[i][1]*t_exchange_list[i][1]])
            if (self.report_cost2[i][1] != 0):
                t_profit = 100*(self.report_market_value[i][1] - self.report_cost2[i][1])/self.report_cost2[i][1]
            else:
                t_profit = 0.0
            self.report_profit.append([t_date,t_profit])
        logging.debug(__name__ + ': nav \n' + str(self.report_nav))
        logging.debug(__name__ + ': exchange \n' + str(self.report_exchange))
        logging.debug(__name__ + ': invest market value report \n' + str(self.report_market_value))
        logging.debug(__name__ + ': invest profit report \n' + str(self.report_profit))
            
