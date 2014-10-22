from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from lxml.html import document_fromstring
from lxml import etree

from dateutil.relativedelta import relativedelta
from dateutil import parser
from datetime import date

import logging,os
import csv,StringIO

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_SERVER_ERROR = 500

TREASURY_TENOR_1M   = '1 mo'
TREASURY_TENOR_3M   = '3 mo'
TREASURY_TENOR_6M   = '6 mo'
TREASURY_TENOR_1Y   = '1 yr'
TREASURY_TENOR_2Y   = '2 yr'
TREASURY_TENOR_3Y   = '3 yr'
TREASURY_TENOR_5Y   = '5 yr'
TREASURY_TENOR_7Y   = '7 yr'
TREASURY_TENOR_10Y  = '10 yr'
TREASURY_TENOR_20Y  = '20 yr'
TREASURY_TENOR_30Y  = '30 yr'

TREASURY_ITEM_KEY_DATE = 'Date'

KEY_DATE_FORMAT = '%m/%d/%y'

TREASURY_YEAR_SINCE = '1990'

# Create your models here.
#-> http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year=2014
#-> xpath: //*[@id="t-content-main-content"]/table/tr/td/div/table

TREASURY_URL = 'http://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year={year}'
    
class USTreasuryModel(db.Model):
    '''
    Model key format = yyyy
    '''
    content_csv = db.BlobProperty(default='')
    treasury_year = ''
    treasury_dict = None
    
    @classmethod
    def get_yield_list_since(cls, p_year=(date.today().year-1), p_tenor=TREASURY_TENOR_10Y):
        '''
        return list of yield since p_year
        '''
        t_yield_list = []

        this_year = int(date.today().year)
        if not str(p_year).isdigit() or int(p_year) > this_year:
            logging.warning('get_yield_list_since: Param Error, p_year:{p_year},p_tenor={p_tenor}'.format(p_year=p_year,p_tenor=p_tenor))
            return None
        
        year_add = int(p_year)
        while year_add <= this_year:
            t_treasury = USTreasuryModel.get_treasury(year_add)
            if t_treasury is None:
                logging.warning('get_yield_list_since: get treasury for year {year} fail!'.format(year=year_add))
            else:
                t_year_yeild_list = t_treasury.get_yield_list_by_tenor(p_tenor)
                #logging.debug(str(t_year_yeild_list))
                t_yield_list += t_year_yeild_list
            year_add += 1
            
        t_yield_list.sort(key=lambda x: x[0])
        return t_yield_list
    
    @classmethod
    def _update_from_web(cls,p_year):
        model_key = str(p_year)
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
    
    @classmethod
    def get_treasury(cls, p_year=date.today().strftime('%Y')):
        treasury = USTreasuryModel.get_or_insert(str(p_year))
        
        if treasury.content_csv == '':
            logging.info('get_treasury: empty content datastore object, update from web with key name: ' + str(p_year))
            cls._update_from_web(p_year)
            treasury = USTreasuryModel.get_or_insert(str(p_year))
        
        yesterday = date.today() + relativedelta(days=-1)
        if str(date.today().year)==str(p_year) and \
                str(treasury.content_csv).find(yesterday.strftime(KEY_DATE_FORMAT))==-1:
            logging.info('update latest treasury from web')
            cls._update_from_web(p_year)
            treasury = USTreasuryModel.get_or_insert(str(p_year))
                
        csv_reader = csv.DictReader(StringIO.StringIO(treasury.content_csv))
        treasury_dict = {}
        for row in csv_reader:
            treasury_dict[row[TREASURY_ITEM_KEY_DATE]] = dict(row)
        
        treasury.treasury_dict = treasury_dict
        treasury.treasury_year = p_year
        return treasury
    
    @classmethod
    def get_tenor_list(cls):
        treasury = cls.get_treasury()
        #return str(treasury.treasury_dict)
        for key, entry in treasury.treasury_dict.items():
            #return str(entry)
            t_list = entry.keys()
            del t_list[t_list.index(TREASURY_ITEM_KEY_DATE)]
            del t_list[t_list.index('')]
            return t_list
                
    def get_yield_list_by_tenor(self, p_tenor=TREASURY_TENOR_10Y):
        t_list = []
        for key, row in self.treasury_dict.items():
            try:
                if str(row[TREASURY_ITEM_KEY_DATE]).strip() != '':
                    t_date = parser.parse(row[TREASURY_ITEM_KEY_DATE]).date()
                    t_yield = float(row[p_tenor])
                    t_list.append([t_date,t_yield])
            except:
                #logging.debug('get_yield_list_by_tenor: entry skip year {year}, tenor {tenor} and date {date} with value {value}'.format(
                #                            year=self.treasury_year,tenor=p_tenor, date=key,value=row[p_tenor]))
                continue
        t_list.sort(key=lambda x: x[0])
        #logging.debug(str(t_list))
        return t_list
            
    def get_yield_by_date(self, p_date=date.today(), p_tenor=TREASURY_TENOR_10Y):
        p_year = p_date.strftime('%Y')
        if self.treasury_year != p_year:
            logging.warning('get_yield_by_date: param error; obj year : {obj_year}, param year: {param_year}'.format(obj_year=self.treasury_year, param_year=p_year))
            return False
        date_keys = self.treasury_dict.keys()
        date_prev = p_date
        while not date_prev.strftime(KEY_DATE_FORMAT) in date_keys:
            logging.debug('get_yield_by_date: {p_date} not in keys, check previous value.'.format(p_date=date_prev.strftime(KEY_DATE_FORMAT)))
            if p_date.day == 1 and p_date.month == 1:
                treasury = USTreasuryModel.get_treasury(str(date_prev.year-1))
                return treasury.get_yield_by_date(date_prev+relativedelta(days=-1))
            else:
                date_prev = date_prev + relativedelta(days=-1)

        return self.treasury_dict[date_prev.strftime(KEY_DATE_FORMAT)][p_tenor]
        
 
 
 
 
 
        