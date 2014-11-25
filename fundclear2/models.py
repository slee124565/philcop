from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from lxml.html import document_fromstring
from lxml import etree

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta
from indexreview.models import IndexReviewModel
from fundcodereader.models import FundCodeModel

import csv,StringIO
import logging,calendar,copy

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_SERVER_ERROR = 500

CSV_ITEM_KEY_DATE = 'Date'
CSV_ITEM_KEY_NAV = 'NAV'

NAV_INDEX_DATE = 0
NAV_INDEX_VALUE = 1

URL_TEMPLATE = 'http://announce.fundclear.com.tw/MOPSFundWeb/D02_02P.jsp?fundId={fund_id}&beginDate={begin_date}&endDate={end_date}'

class FundClearInfoModel(db.Model):
    title = db.StringProperty(default='')
    currency = db.StringProperty()
    nav_year_dict = {}

    @classmethod
    def compose_key_name(cls,p_fund_id):
        return p_fund_id
    
    @classmethod
    def get_fund(cls,p_fund_id):
        fund_id_list = FundCodeModel.get_code_list()
        if not p_fund_id in fund_id_list:
            logging.warning('get_fund: id {fund_id} not in fund id list!'.format(fund_id=p_fund_id))
            return None
        p_year = str(date.today().year)
        key_name = FundClearInfoModel.compose_key_name(p_fund_id)
        fundinfo = FundClearInfoModel.get_by_key_name(key_name)
        if fundinfo is None:
            logging.info('FundClearInfoModel({fund_id}) not exist, update from web...'.format(fund_id=p_fund_id))
            if FundClearDataModel._update_from_web(p_fund_id, p_year):
                fundinfo = FundClearInfoModel.get_by_key_name(key_name)
            else:
                return None

        fundinfo._load_year_nav(p_year)

        #-> check if today's nav exist
        if not date.today().strftime('%Y/%m/%d') in fundinfo.nav_year_dict[p_year].keys():
            logging.info('get_fund: update fund latest NAV from internet web.')
            FundClearDataModel._update_from_web(p_fund_id, p_year)
            fundinfo._load_year_nav(p_year)
        
        logging.debug('get_fund: with id {} success'.format(p_fund_id))
        return fundinfo
    
    def get_sample_value_list(self, p_date_list):
        '''
        return a list of [date, nav] according to date list p_date_list
        '''
        t_list = []
        for t_date in p_date_list:
            t_nav = self.get_nav_by_date(t_date)
            t_list.append([t_date,t_nav])
        return t_list

    def load_all_nav(self):
        for t_funddata in FundClearDataModel.all().ancestor(self):
            nav_dict = t_funddata._get_nav_dict()
            t_keyname_split = t_funddata.key().name().split('_')
            t_year = t_keyname_split[-1]
            #logging.debug('load_all_nav for year ' + t_year)
            self.nav_year_dict[t_year] = nav_dict
    
    def _load_year_nav(self, p_year):
        t_year = str(p_year)
        fund_id = self.key().name()
        funddata = FundClearDataModel.get_by_key_name(FundClearDataModel.compose_key_name(fund_id,t_year), 
                                                      parent=self)
        if funddata is None:
            logging.warning('_load_year_nav with fund id {fund_id} and year {year} return None'.format(
                                                                                                       fund_id=fund_id,
                                                                                                       year=t_year))
            self.nav_year_dict[t_year] = {}
            return False
        
        nav_dict = funddata._get_nav_dict()
        self.nav_year_dict[t_year] = nav_dict
        logging.debug('_load_year_nav: with year {}'.format(t_year))
        return True
    
    def get_year_nav_dict(self, p_year):
        t_year = str(p_year)
        if not t_year in self.nav_year_dict.keys():
            self._load_year_nav(t_year)
            #logging.debug('get_year_nav_dict for year {p_year}'.format(p_year=p_year))
        return self.nav_year_dict[t_year]
        
    def get_value_list_for_year(self, p_year):
        t_year_nav = self.get_year_nav_dict(p_year)
        value_list = t_year_nav.values()
        value_list.sort(key=lambda x: x[0])
        #logging.debug('get_value_list_for_year {year}\n{value_list}'.format(year=p_year,value_list=str(value_list)))
        return list(value_list)
    
    def get_index_list(self):
        '''
        return current exists [date,nav] list 
        '''
        value_list = []
        for t_key in self.nav_year_dict.keys():
            value_list += self.nav_year_dict[t_key].values()
        value_list.sort(key=lambda x: x[0])
        return value_list
            
    def get_value_list(self, p_year_since=date.today().year):
        t_year = p_year_since
        this_year = date.today().year
        value_list = []
        while t_year <= this_year:
            self._load_year_nav(t_year)
            '''
            if not str(t_year) in self.nav_year_dict.keys():
                self._load_year_nav(t_year)
                logging.debug('get_value_list: load year nav {}'.format(t_year))
            '''
            if str(t_year) in self.nav_year_dict.keys():
                t_year_list = self.nav_year_dict[str(t_year)].values()
                value_list += t_year_list
                logging.debug('get_value_list: add year nav {}'.format(t_year))
            t_year += 1
                
        value_list.sort(key=lambda x: x[0])
        return list(value_list)

    def get_nav_by_date(self, p_date):
        t_date = p_date        
        t_year = str(t_date.year)
        year_value_list = self.get_value_list_for_year(t_year)
        if len(year_value_list) == 0:
            return 0.0
        if t_date < year_value_list[0][NAV_INDEX_DATE]:
            t_date = date(t_date.year-1,12,31)
            logging.info('get_nav_by_date: get NAV for date {t_date} instead of {p_date}'.format(t_date=str(t_date),
                                                                                p_date=str(p_date)))
            return self.get_nav_by_date(t_date)
        if t_date > year_value_list[-1][NAV_INDEX_DATE]: 
            logging.info('get_nav_by_date: date {p_date} exceed year nav max date {max_date}'.format(p_date=str(p_date),
                                                                                    max_date=str(year_value_list[-1][NAV_INDEX_DATE])))
            return 0.0      
        t_key = t_date.strftime('%Y/%m/%d')
        while not t_key in self.nav_year_dict[t_year].keys():
            t_date = t_date + relativedelta(days=-1)
            t_key = t_date.strftime('%Y/%m/%d')
            if t_date.day == 1 and t_date.month == 1:
                logging.warning('get_nav_by_date fail: get NAV for {p_date}'.format(str(p_date)))
                return 0.0
        return self.nav_year_dict[t_year][t_key][NAV_INDEX_VALUE]
        
class FundClearDataModel(db.Model):
    content_csv = db.BlobProperty(default='')
    year = db.StringProperty()
    
    @classmethod
    def _get_funddata(cls,p_fund_id,p_year):
        model_parent = FundClearInfoModel.get_or_insert(FundClearInfoModel.compose_key_name(p_fund_id))
        return FundClearDataModel.get_or_insert(
                                    FundClearDataModel.compose_key_name(p_fund_id, p_year),
                                    parent=model_parent)
        
    @classmethod
    def compose_key_name(cls, p_fund_id, p_year):
        return str(p_fund_id) + '_' + str(p_year)

    @classmethod
    def _update_from_web(cls,p_fund_id,p_year=date.today().year):
        model_parent = FundClearInfoModel.get_or_insert(FundClearInfoModel.compose_key_name(p_fund_id))
        fund = FundClearDataModel.get_or_insert(FundClearDataModel.compose_key_name(p_fund_id, p_year),
                                                parent=model_parent)
        
        begin_date = date(int(p_year),1,1).strftime("%Y/%m/%d")
        if int(p_year) == date.today().year:
            end_date = date.today().strftime("%Y/%m/%d")
        else:
            end_date = date(int(p_year),12,31).strftime("%Y/%m/%d")  
        url = URL_TEMPLATE.format(fund_id=p_fund_id,
                                  begin_date=begin_date,
                                  end_date=end_date)
        logging.info('_update_from_web, url: ' + url)

        try :
            web_fetch = urlfetch.fetch(url)
            if web_fetch.status_code == HTTP_STATUS_CODE_OK:
                web_content = document_fromstring(str(web_fetch.content).decode('big5'))
                
                #xpath: /html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td/table[2]/tbody
                #t_tables = web_content.xpath("/html/body/table/tr[1]/td/table/tr[2]/td/table[2]")
                #return etree.tostring(t_tables[0])
                
                t_tables = web_content.xpath("//table")
                TABLE_TITLE_INDEX = 4
                TABLE_NAV_INDEX_START = 5
                
                fund_title = t_tables[TABLE_TITLE_INDEX][0][0].text.replace('\r\n','')
                #logging.debug('get fund title: ' + fund_title)
                if model_parent.title == '':
                    model_parent.title = fund_title
                    model_parent.put()
                    logging.info('Fund title saved.')
                
                dataset = []
                t_total = len(t_tables)
                #logging.debug('t_total: ' + str(t_total))
                t_count = TABLE_NAV_INDEX_START
                while (t_count <= (t_total-1)):
                    if len(t_tables[t_count]) == 2:
                        t_date_list = [t_child.text for t_child in t_tables[t_count][0]]
                        t_value_list = [t_child.text for t_child in t_tables[t_count][1]]
                        for i in range(0,len(t_date_list)):
                            if i != 0:
                                if (t_date_list[i].strip() != ''):
                                    dataset.append([t_date_list[i],t_value_list[i]])
                                #else:
                                #    logging.debug('remove element ('+ str(t_count) + '#' + str(i) + '): ' + str([t_date_list[i],t_value_list[i]]))
                    #else:
                    #    logging.debug('skip table:\n' + etree.tostring(t_tables[t_count]))
                    t_count += 1
                
                t_count = 0
                t_added = 0
                csv_content = CSV_ITEM_KEY_DATE + ',' + CSV_ITEM_KEY_NAV + '\n'
                while (t_count < len(dataset)):
                    #logging.info('t_count ' + str(t_count))
                    (t_date,t_value) = dataset[t_count]
                    #logging.debug(str(t_count) + ' ' + str(dataset[t_count]))
                    if (t_value == '--') or (t_value == 'N/A'):
                        if (t_count == 0):
                            #logging.warning('removeing dataset element ' + str(dataset[t_count]))
                            del dataset[t_count]
                            continue
                        else:
                            #logging.warning('replace value with previous one, date ' + str(dataset[t_count]))
                            dataset[t_count][1] = dataset[t_count-1][1]
                    #if (t_count > 192):
                    #    logging.info('DEBUG:' + str([t_date,t_value]))
                    csv_content += dataset[t_count][0] + ',' + str(float(dataset[t_count][1])) + '\n'
                    t_added += 1
                    #dataset[t_count][0] = calendar.timegm((parser.parse(t_date)).timetuple()) * 1000
                    #dataset[t_count][1] = float(dataset[t_count][1])
                    t_count += 1
                #return csv_content
                fund.year = str(p_year)
                fund.content_csv = csv_content
                fund.put()
                logging.info('Fund {id} with year {year} with item {item} saved.'.format(
                                                                        id=str(p_fund_id),
                                                                        year=str(p_year),
                                                                            item=t_added))
                return True
            else:
                logging.warning('_update_from_web fail, HTTP STATUS CODE: ' + str(web_fetch.status_code))
                return False
        except DownloadError:
            logging.warning('_update_from_web : Internet Download Error')
            return False

    def _get_nav_dict(self):
        csv_reader = csv.DictReader(StringIO.StringIO(self.content_csv))
        nav_dict = {}
        for row in csv_reader:
            nav_dict[row[CSV_ITEM_KEY_DATE]] = [parser.parse(row[CSV_ITEM_KEY_DATE]).date(),
                                                float(row[CSV_ITEM_KEY_NAV])]
        
        return nav_dict
        
        
        
