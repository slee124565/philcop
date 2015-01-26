from django.http import HttpResponse
from models_stock import StockModel
import codecs

def code_list_view(request):
    t_model = StockModel.get_model()
    t_content = ''
    
    for t_type in t_model.csv_dict:
        t_content += t_type + '<br/>\n'
        t_count = 1
        for t_stk_no in t_model.csv_dict[t_type]:
            t_content += t_stk_no + ','
            if t_count % 20 == 0:
                t_content += '<br/>\n'
            t_count += 1
        t_content += '<br/><br/>\n'
        
    return HttpResponse(t_content)

