from google.appengine.ext import db
import logging

#from fundclear.models import FundClearModel
#from bankoftaiwan.models import BotExchangeModel
#import bankoftaiwan.exchange

class MutualFundInvestModel(db.Model):
    id = db.StringProperty()
    currency = db.StringProperty()
    share = db.FloatProperty()
    date_invest = db.DateProperty()
    exchange_rate = db.FloatProperty()
    trade_fee = db.FloatProperty()
    amount_trade = db.FloatProperty()
    nav = db.FloatProperty()
    
    def __str__(self):
        return self.__unicode__()
        
    def __unicode__(self):
        return self.key().id_or_name()