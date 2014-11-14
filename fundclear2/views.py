from django.http import HttpResponse
from fundclear2.models import FundClearInfoModel, FundClearDataModel
from fundcodereader.models import FundCodeModel

def datamodel_statistic_report_view(request):
    #response = HttpResponse(content_type='text/plain')
    response = HttpResponse()
    content = '<table border="1px solid black">'
    codename_list = FundCodeModel.get_codename_list()
    for t_code, t_name in codename_list[:]:
        ancestor = FundClearInfoModel.get_by_key_name(FundClearInfoModel.compose_key_name(t_code))
        if ancestor is None:
            t_count = 0
            t_years = ''
        else:
            t_funddata_query = FundClearDataModel.all().ancestor(ancestor).order('year')
            t_count = 0
            t_years = ''
            for t_funddata in t_funddata_query:
                t_count += 1
                if t_funddata.year is None:
                    t_years += '?,'
                else:
                    t_years += t_funddata.year + ', '
        t_report = '<tr><td width="10%" align="right">{}</td><td width="5%" align="right">{}</td><td width="50%">{}</td><td>{}</td></tr>\n'.format(
                                                                         t_code,
                                                                         t_count,
                                                                         t_name,
                                                                         t_years,
                                                                         )
        content += t_report
    
    content += '</table>'
    response.content = content
    return response