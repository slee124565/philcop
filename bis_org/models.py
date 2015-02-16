from google.appengine.ext import db
from google.appengine.api import urlfetch, mail
from google.appengine.api.urlfetch import DownloadError

from lxml.html import document_fromstring
from lxml import etree

from dateutil.relativedelta import relativedelta
from dateutil import parser

import logging
import bis_org
import csv,StringIO

EERS_TYPE_NOMINAL = 1
EERS_TYPE_REAL = 2

EERS_KEY_NOMIMAL = 'nomial'
EERS_KEY_REAL = 'real'

EERS_AREA_CODE_INDEX = 0
EERS_AREA_NAME_INDEX = 1


EERS_DS_KEY_BROAD = 'eers_broad'
EERS_DS_KEY_NARROW = 'eers_narrow'

class BisEersModel(db.Model):
    '''
    BIS EERs Model
    '''
    update_date_info = db.BlobProperty(default='')
    content_csv = db.BlobProperty(default='')
    key_name = ''
    area_eers = None #-> csv.DictReader object
    area_list = [] #-> [[code,name],[code,name], ... ]
    
    @classmethod
    def get_broad_indices(cls):
        '''
        get BIS EERs data from datastore  
        '''
        return cls._get_indices(EERS_DS_KEY_BROAD)
    
    @classmethod
    def get_narrow_indices(cls):
        '''
        get BIS EERs data from datastore  
        '''
        return cls._get_indices(EERS_DS_KEY_NARROW)
    
    @classmethod
    def _get_indices(cls, p_key_name=EERS_DS_KEY_BROAD):
        eers = BisEersModel.get_or_insert(p_key_name)
        if eers is None:
            logging.warning('_get_indices: fail to get object from datastore with key_name: ' + p_key_name)

        if str(eers.update_date_info) == '':
            logging.warning('_get_indices: bis_eers object has no update_date_info, need to update from web first!!!')
            cls._update_from_web(p_key_name)
            eers = BisEersModel.get_or_insert(p_key_name)
        eers.key_name = p_key_name
        eers.area_list = []
        eers._parse_area_eers()
        return eers
        
    @classmethod
    def update_from_web(cls):
        return cls._update_from_web(EERS_DS_KEY_BROAD) and \
                    cls._update_from_web(EERS_DS_KEY_NARROW)
    
    @classmethod
    def _update_from_web(cls,p_key_name=EERS_DS_KEY_BROAD):
        '''
        update datastore with BIS EERs Web Content if updated
        '''
        logging.debug('update_from_web start with keyname:' + p_key_name + ' ...')
        try:
            #-> get eers object from datastore
            eers = BisEersModel.get_or_insert(p_key_name)
            if eers is None:
                logging.warning('fail to get eers object from datastore, key_name: ' + p_key_name)
                return False
            
            #-> update BIS EERs Index
            t_url = 'http://www.bis.org/statistics/eer/index.htm'
            web_fetch = urlfetch.fetch(t_url)
            if web_fetch.status_code == bis_org.HTTP_STATUS_CODE_OK:
                web_content = document_fromstring(web_fetch.content)
                web_update_info = web_content.xpath('//*[@id="center"]')
                #logging.debug('web_update_info len: ' + str(len(web_update_info)))
                web_update_text = etree.tostring(web_update_info[0])
                #logging.debug('web_update_text:\n' + str(web_update_text))
            else:
                logging.warning('update_from_web: index page urlfetch fail')
                return False
            
            if eers.update_date_info is None:
                eers.update_date_info = ''
                
            if eers.update_date_info == web_update_text:
                logging.debug('update_from_web: index page has not been changed; update cancel')
                return True
            else:
                logging.debug('web_update_text changed:\n[prev]:\n' + eers.update_date_info + '\n[next]:\n' + web_update_text)
                eers.update_date_info = web_update_text
                logging.debug('update_from_web: index page has been changed; start csv updating ...')

            
            if p_key_name == EERS_DS_KEY_BROAD:
                #-> update Board BIS EERs
                t_url = 'http://stats.bis.org/eer?basket=B&obs=all&format=csv'
            else:
                #-> update Narrow BIS EERs
                t_url = 'http://stats.bis.org/eer?basket=N&obs=all&format=csv'
            web_fetch = urlfetch.fetch(t_url)
            if web_fetch.status_code == bis_org.HTTP_STATUS_CODE_OK:
                web_csv = web_fetch.content
                eers.content_csv = web_csv
                eers.put()
                cls.mail_notify_admin('update_from_web: update success.')
                logging.debug('update_from_web: update success.')
                return True
            else:
                cls.mail_notify_admin('update_from_web: csv content urlfetch fail.')
                logging.warning('update_from_web: csv content urlfetch fail.')
                return False

        except DownloadError:
            cls.mail_notify_admin('update_from_web : Internet Download Error')
            logging.warning('update_from_web : Internet Download Error')
            return False
    
    @classmethod
    def mail_notify_admin(cls, p_msg):
        user_address = 'lee.shiueh@gmail.com'
        sender_address = 'MyGAE <lee.shiueh@gmail.com>'
        subject = 'BisEersModel._update_from_web'
        body = p_msg
        mail.send_mail(sender_address, user_address, subject, body)
        
        
    def _parse_area_eers(self):
        '''
        area_list = [[code,name],[code,name], ... ]
        area_eers = csv.DictReader object
        '''
        t_lines = str(self.content_csv).splitlines()
        #-> check headers not changed and parse area list
        AREAS_ROW_INDEX = 8
        AREAS_HEAD_TEXT = 'Reference area,'
        if str(t_lines[AREAS_ROW_INDEX]).find(AREAS_HEAD_TEXT) != 0:
            logging.warning('_parse_area_eers: fail to parse area list data')
            return
        area_list = str(t_lines[AREAS_ROW_INDEX]).split(',')
        for t_area in area_list[1:]:
            area_code = t_area.split(':')
            if not area_code in self.area_list:
                self.area_list.append(area_code)

        #-> parse date_value set
        EERS_START_ROW_INDEX = 9
        eers_csv_data = '\n'.join(t_lines[EERS_START_ROW_INDEX:])
        self.area_eers = eers_csv_data
        
        self.area_eers = csv.DictReader(StringIO.StringIO(eers_csv_data))
        return
                            
    def get_reference_area_list(self):
        return [area[EERS_AREA_NAME_INDEX] for area in self.area_list]
    
    def get_reference_code_list(self):
        return [area[EERS_AREA_CODE_INDEX] for area in self.area_list]
    
    def _get_area_code(self, p_area):
        return self.area_list[self.get_reference_area_list().index(p_area, )][EERS_AREA_CODE_INDEX]
    
    def _get_area_name(self, p_code):
        return self.area_list[self.get_reference_code_list().index(p_code, )][EERS_AREA_NAME_INDEX]        
    
    def _get_area_eers_dict_key(self, p_area, p_type=EERS_TYPE_REAL):
        if self.key_name == EERS_DS_KEY_BROAD:
            t_basket = 'B'
        else:
            t_basket = 'N'
        
        if p_type == EERS_TYPE_NOMINAL:
            return 'M:N:' + t_basket +':' + self._get_area_code(p_area)
        else:
            return 'M:R:' + t_basket +':' + self._get_area_code(p_area)
            
    def _get_areas_bis_eers(self, p_areas, p_type=EERS_TYPE_REAL):
        t_result = {}
        area_all = self.get_reference_area_list()
        if type(p_areas) is list:
            for t_area in p_areas:
                if t_area in area_all:
                    t_result[t_area] = self._get_area_bis_eers(t_area, p_type)
                else:
                    logging.warning('_get_areas_bis_eers: area ' + t_area + ' is not in reference area list.')
        else:
            if p_areas in area_all:
                t_result[p_areas] = self._get_area_bis_eers(p_areas, p_type)
            else:
                logging.warning('_get_areas_bis_eers: area ' + p_areas + ' is not in reference area list.')
        return t_result
        
    def _get_area_bis_eers(self, p_area, p_type=EERS_TYPE_REAL):
        area_dict_key = self._get_area_eers_dict_key(p_area,p_type)
        #logging.debug('_get_area_bis_eers with area: ' + p_area + ', dict_key: ' + area_dict_key)
        date_dict_key = 'Month'
        t_list = []
        self._parse_area_eers()
        for row in self.area_eers:
            t_date = parser.parse(row[date_dict_key]+'-01').date() + relativedelta(months=+1, days=-1)
            t_list.append([t_date, float(row[area_dict_key])])
        return t_list
    
    def get_area_nominal_bis_eers(self, p_areas):
        return self._get_areas_bis_eers(p_areas,EERS_TYPE_NOMINAL)
    
    def get_area_real_bis_eers(self, p_areas):
        return self._get_areas_bis_eers(p_areas,EERS_TYPE_REAL)
    
    
    