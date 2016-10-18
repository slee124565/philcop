from django.http import HttpResponse
from models import URLFetchModel

from lxml.html import document_fromstring
from lxml import etree
url = 'http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/genpage/Report201502/201502_F3_1_8_2330.php?STK_NO=2330&myear=2015&mmon=02'
xpath = '//*[@id="contentblock"]/td/table[3]'


def read_twse_web_content(request):
    #t_tables = URLFetchModel.get_web_content(url=url, xpath=xpath)
    #return HttpResponse(len(t_tables))
    #return HttpResponse(parse_twse_web_content(t_tables[0]))

    #return HttpResponse(URLFetchModel.get_content())

    web_content = document_fromstring(URLFetchModel.get_content())
    t_tables = web_content.xpath("//table")
    response = HttpResponse(content_type='text/plain')
    response.content = parse_twse_web_content(t_tables[0])

    return response

def parse_twse_web_content(p_table):
    
    t_content = ''
    t_tr_count = 0
    for t_element in p_table:
        t_line = ''
        if t_element.tag == 'table':
            break
        if t_element.tag == 'tr' and len(t_element) == 9:
            if t_tr_count > 0:
                for t_col in t_element:
                    if len(t_col) == 0:
                        t_line += t_col.text.replace(',','') + ','
                    else:
                        t_line += t_col[0].text + ','
                t_content += t_line[:-1] + '\n'
            t_tr_count += 1
        
        
    return t_content
    
    
def save_twse_web_content(request):
    if not URLFetchModel.get_web_content(url=url, xpath=xpath) is None:
        return HttpResponse('save_twse_web_content')
    else:
        return HttpResponse('save_twse_web_content failed')