from google.appengine.ext import db

class GoldInvestModel(db.Model):
    currency_type = db.StringProperty()
    exchange_rate = db.FloatProperty()
    date_invest = db.DateProperty()
    weight_purchase = db.FloatProperty()
    trade_fee = db.FloatProperty()
    amount_trade = db.FloatProperty()
    bid_price = db.FloatProperty()
    