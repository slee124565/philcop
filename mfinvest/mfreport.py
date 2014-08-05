
from mfinvest.models import MutualFundInvestModel
from fundclear.models import FundClearModel
from bankoftaiwan.models import BotExchangeModel, exchange

from datetime import date
from dateutil.relativedelta import relativedelta
import logging

class MFReport():
    fund_id = None
    currency_type = None
    date_begin = None
    date_end = None
    m_fund = None       #-> FundClearModel
    #m_invest = None     #-> MutualFundInvestModel
    m_exchange = None   #-> BotExchangeModel
    report_cost = []
    report_cost2 = []
    report_share = []
    report_market_value = []
    report_nav = []
    report_exchange = []
    report_profit = []
    
    @classmethod
    def get_mfreport_by_id(cls, p_fund_id, p_currency_type):
        report = MFReport(fund_id=p_fund_id, currency_type=p_currency_type )
        #report.m_invest = MutualFundInvestModel.all().filter('id =', report.fund_id).order('date_invest')
        report.m_fund = FundClearModel.get_fund(report.fund_id)
        report.report_nav = report.m_fund.get_discrete_value_list()
        report.m_exchange = BotExchangeModel.get_bot_exchange(exchange.CURRENCY_JPY)
        report.report_exchange = report.m_exchange.get_discrete_exchange_list()
        report._get_history_cost_n_share_report()
        report._get_history_market_value_report()
        return report
    
    def __init__(self, fund_id, currency_type):
        self.fund_id = fund_id
        self.currency_type = currency_type
        t_date_sample_start = date.today() - relativedelta(months=+12)
        self.date_begin = date(t_date_sample_start.year,t_date_sample_start.month+1,1) - relativedelta(days=+1)
        self.date_end = date(date.today().year,date.today().month,1) - relativedelta(days=+1)
        
    def _get_history_cost_n_share_report(self):
        '''
        cost = amount_trade + trade_fee
        return list of [date, cost] 
        '''
        history = MutualFundInvestModel.all().filter('id =', self.fund_id).order('date_invest')
        if self.date_begin < history[0].date_invest:
            self.report_cost.append([self.date_begin, 0.0, 0.0])
        
        #-> create invest cost report
        cost = 0.0
        share = 0.0
        t_dict_share = {}
        t_dict_cost = {}
        for t_entry in history:
            if self.date_end >= t_entry.date_invest:
                cost += (t_entry.amount_trade + t_entry.trade_fee)
                self.report_cost.append([t_entry.date_invest, cost])
                share += t_entry.share
                t_key = t_entry.date_invest.strftime("%Y-%m")
                t_dict_share[t_key] = share
                t_dict_cost[t_key] = cost
        
        if self.date_end > history[history.count()-1].date_invest:
            self.report_cost.append([self.date_end, cost])
        logging.debug(__name__ + ': invest cost report \n' + str(self.report_cost))
        
        #-> create invest share report
        t_check_date = self.date_begin
        t_last_share = 0.0
        t_last_cost = 0.0
        while (t_check_date <= self.date_end):
            t_key = t_check_date.strftime('%Y-%m')
            if t_key in t_dict_share:
                self.report_share.append([t_check_date, t_dict_share[t_key]])
                self.report_cost2.append([t_check_date, t_dict_cost[t_key]])
                t_last_share = t_dict_share[t_key]
                t_last_cost = t_dict_cost[t_key]
            else:
                self.report_share.append([t_check_date, t_last_share])
                self.report_cost2.append([t_check_date, t_last_cost])
            t_check_date = date(t_check_date.year,t_check_date.month,1) + relativedelta(months=+2) - relativedelta(days=+1)
        logging.debug(__name__ + ': invest share report \n' + str(self.report_share))
        logging.debug(__name__ + ': invest 2nd cost report \n' + str(self.report_cost2))

    def _get_history_market_value_report(self):
        '''
        return a list of [date, market_value] according to report_share list
        '''
        t_fund_nav_list = self.report_nav
        t_exchange_list = self.report_exchange
        for i in range (len(self.report_share)):
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
            
