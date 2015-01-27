from django.http import HttpResponse
from twse_gae.models import TWSEStockModel
import twse_gae.models as twse
from datetime import date
from dateutil.relativedelta import relativedelta 
import pickle


def get_stk_content(p_stock):
    t_content = ''
    t_content += 'csv_dick.keys: {}<br/>\n'.format(sorted(p_stock.csv_dict.keys()))
    for t_entry in p_stock.get_index_list():
        t_content += '{}<br/>\n'.format(t_entry)
    return t_content

def test_get_stk_update_ym(request, p_stk_no):
    return HttpResponse('get_stk_update_ym is {}'.format(TWSEStockModel.get_stk_update_ym(p_stk_no)))
    
def test_update_month(request,p_stk_no,p_year_month):
    t_stock = TWSEStockModel.update_monthly_csv_from_web(p_stk_no,p_year_month,True)
    if t_stock is None:
        return HttpResponse('TWSEStockModel.update_monthly_csv_from_web({},{}) faile'.format(p_stk_no,p_year_month))
    else:
        return HttpResponse(get_stk_content(t_stock))

def test_get_index_by_date(request):
    t_stock = TWSEStockModel.get_stock('0050')
    t_content = ''
    t_date = date.today()
    t_end_ate = date.today() + relativedelta(years=-1)
    while t_date > t_end_ate:
        t_content += '{} get index {}<br/>\n'.format(t_date,t_stock.get_index_by_date(t_date))
        t_date += relativedelta(days=-1)
    return HttpResponse(t_content)
    
    
    
def test_get_last_ym(request, p_stk_no='0050'):
    return HttpResponse(TWSEStockModel.get_last_ym(p_stk_no))
    
    
def test_get_index_list(request,p_col=twse.TWSEStockModel.CSV_COL_CLOSE):
    t_stock = TWSEStockModel.get_stock('0050')
    t_content = ''
    for t_entry in t_stock.get_index_list(p_col):
        t_content += '{}<br/>\n'.format(str(t_entry)) 
    
    return HttpResponse(t_content)

def test_parse_csv_col_date(request):
    t_date = '104/01/05'
    return HttpResponse(TWSEStockModel.parse_csv_col_date(t_date))
    
def test_get_stock(request, p_stk_no='0050'):
    t_stock = TWSEStockModel.get_by_key_name(TWSEStockModel.compose_key_name(p_stk_no))
    if t_stock is None:
        return HttpResponse('get_stock {} fail'.format(p_stk_no))
    
    if t_stock.csv_dict_pickle in [None,'']:
        return HttpResponse('get_stock {} with empty content'.format(p_stk_no))
    
    t_stock.csv_dict = pickle.loads(t_stock.csv_dict_pickle)
    t_content = ''
    t_content += 'csv_dick.keys: {}<br/>\n'.format(sorted(t_stock.csv_dict.keys()))
    for t_entry in t_stock.get_index_list():
        t_content += '{}<br/>\n'.format(t_entry)
    return HttpResponse(t_content)







