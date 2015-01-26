from django.http import HttpResponse
from twse_gae.models_stock import StockModel
import codecs

def test_stock_update_from_web(request,p_type=StockModel.STOCK_TYPE_TWSE):
    if (StockModel.update_from_web(p_type)):
        return HttpResponse('test_stock_update_from_web {}'.format(p_type))
    else:
        return HttpResponse('test_stock_update_from_web {} fail'.format(p_type))



