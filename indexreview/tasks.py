from django.http import HttpResponse

from fundclear2.models import FundClearInfoModel
import fundclear2.models as fc2
from indexreview.models import IndexReviewModel

def get_fc_update_taskhandler_url():
    return '/ir/task/update/'
    
def indexreview_fc_update_taskhandler(request):
    
    response = HttpResponse('indexreview_fc_update_taskhandler')

    f_fund_id = request.REQUEST['PARAM1']
    t_fund = FundClearInfoModel.get_fund(f_fund_id)
    t_fund.load_all_nav()
    IndexReviewModel._update_review(t_fund)
    response.status_code = fc2.HTTP_STATUS_CODE_OK
    return response
    