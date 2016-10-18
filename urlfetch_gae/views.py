from django.http import HttpResponse

from lxml.html import document_fromstring
from lxml import etree

from models import URLFetchModel
import os, logging

def fetch_stock_content(request):
    t_url = 'http://mops.twse.com.tw/mops/web/ajax_quickpgm?encodeURIComponent=1&firstin=true&step=4&checkbtn=1&queryName=co_id&TYPEK2=&code1=&keyword4='
    t_xpath = '//*[@id="zoom"]'
    t_xpath = '//*[@id="zoom"]/tbody'
    #t_table = URLFetchModel.get_web_content(url=t_url,xpath=t_xpath,saved=False)
    t_file = open(os.path.dirname(__file__) +'/stk_info.html')
    web_content = document_fromstring(t_file.read())
    t_file.close()
    t_elements = web_content.xpath(t_xpath)
    t_stk_info = parse_content(t_elements[0])
    t_content = ''
    for t_key in t_stk_info:
        t_content += u'{}:{}<br/>\n'.format(t_key,t_stk_info[t_key][0])
        #t_content += t_key + ',' + t_stk_info[t_key][0] + '<br/>'
    return HttpResponse(t_content)

    

def parse_content(p_htmltable):
    t_dict_data = {}
    for t_row in p_htmltable[1:]:
        if len(t_row) == 6:
            t_id = t_row[0][0].text
            t_abbr_name = t_row[1][0].text
            t_full_name = t_row[2][0].text
            t_market = t_row[3][0].text
            t_industry = t_row[4][0].text
            t_memo = t_row[5][0].text
            t_dict_data[t_id] = [t_abbr_name,t_full_name,t_market,t_industry,t_memo]
    return t_dict_data
        
    
            
    
    