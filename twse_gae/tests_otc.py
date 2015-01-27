from django.http import HttpResponse

from models_otc import OTCStockModel
from models_stock import TWSEStockModel


def func_get_stock(request, p_stk_no):
    t_stock = OTCStockModel.get_stock(p_stk_no)
    if t_stock is None:
        return HttpResponse('func_get_stock {} fail'.format(p_stk_no))
    else:
        return HttpResponse(str(t_stock.get_index_list()))
    
    
def test(request):
    return HttpResponse(OTCStockModel.func_main())
    return HttpResponse(OTCStockModel.get_stk_update_ym('3293'))
    return HttpResponse(OTCStockModel.test())