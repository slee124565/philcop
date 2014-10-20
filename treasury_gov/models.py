from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from lxml.html import document_fromstring
from lxml import etree

from dateutil.relativedelta import relativedelta
from dateutil import parser

import logging

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_SERVER_ERROR = 500

# Create your models here.
#-> http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year=2014
#-> xpath: //*[@id="t-content-main-content"]/table/tr/td/div/table

TREASURY_URL = 'http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year={year}'

class USTreasuryModel(db.Model):
    '''
    Model key format = yyyy
    '''
    content_csv = db.BlobProperty(default='')
    
    @classmethod
    def _update_from_web(cls,p_year):
        model_key = p_year
        treasury = USTreasuryModel.get_or_insert(model_key)
        URL = TREASURY_URL.format(year=p_year)
        try :
            web_fetch = urlfetch.fetch(URL)
            if web_fetch.status_code == HTTP_STATUS_CODE_OK:
                web_content = document_fromstring(web_fetch.content)
                #logging.debug(etree.tostring(web_content))
                t_xpath = '//*[@id="t-content-main-content"]/table/tr/td/div/table'
                treasury_table = web_content.xpath(t_xpath)
                if len(treasury_table) > 0:
                    #logging.debug('len: ' + str(len(treasury_table)))
                    #treasury_html = etree.tostring(treasury_table[0])
                    #return(treasury_html)
                    treasury_csv = ''
                    for t_row in treasury_table[0]:
                        for t_col in t_row:
                            treasury_csv += t_col.text + ','
                        treasury_csv += '\n'
                    treasury.content_csv = treasury_csv
                    treasury.put()
                    logging.info('_update_from_web success.')
                    return True
                else:
                    logging.warning('_update_from_web web structure changed, parsing fail!')
                    return False
            else:
                logging.warning('_update_from_web fail, HTTP STATUS CODE: ' + str(web_fetch.status_code))
                return False
                #logging.debug('treasury_html:\n' + treasury_html)
        except DownloadError:
            logging.warning('_update_from_web : Internet Download Error')
            return False
        
        
        