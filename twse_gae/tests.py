from django.http import HttpResponse
from twse_gae.models import TWSEStockModel
import twse_gae.models as twse

def test_get_last_ym(request):
    return HttpResponse(TWSEStockModel.get_last_ym('0050'))
    
    
def test_get_index_list(request,p_col=twse.CSV_COL_CLOSE):
    t_stock = TWSEStockModel.get_stock('0050')
    t_content = ''
    for t_entry in t_stock.get_index_list(p_col):
        t_content += '{}<br/>\n'.format(str(t_entry)) 
    
    return HttpResponse(t_content)

def test_parse_csv_col_date(request):
    t_date = '104/01/05'
    return HttpResponse(TWSEStockModel.parse_csv_col_date(t_date))
    
def test_get_stock(request, p_stk_no='0050'):
    t_stock = TWSEStockModel.get_stock(p_stk_no)
    return HttpResponse(str(t_stock.csv_dict))