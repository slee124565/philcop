from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from datetime import date

import csv,StringIO
import logging,codecs
from django.template.defaultfilters import join

WEB_URL = 'http://announce.fundclear.com.tw/MOPSFundWeb/INQ41SERVLET3?dlType=2&xagentId=all'
MODEL_KEY_NAME = 'FundCodeModel'

HTTP_STATUS_CODE_OK = 200
HTTP_STATUS_CODE_SERVER_ERROR = 500

def get_update_handler_url():
    return '/fr/task/download/'

class FundCodeModel(db.Model):
    content_csv = db.BlobProperty(default='')
    lastupdated = db.DateProperty()
    
    @classmethod
    def _update_from_web(cls):
        fundcode = FundCodeModel.get_or_insert(MODEL_KEY_NAME)
        logging.info('_update_from_web starting with url:\n' + WEB_URL)
        try:
            web_fetch = urlfetch.fetch(WEB_URL)
            if web_fetch.status_code == HTTP_STATUS_CODE_OK:
                fundcode.content_csv = web_fetch.content
                fundcode.lastupdated = date.today()
                fundcode.put()
                logging.info('_update_from_web success')
                return True
            else:
                logging.warning('_update_from_web fail, HTTP STATUS CODE: ' + str(web_fetch.status_code))
                return False
        except DownloadError:
            logging.warning('_update_from_web : Internet Download Error')
            return False

    @classmethod
    def get_code_list(cls):
        codename_list = cls.get_codename_list()
        return [row[0] for row in codename_list]
    
    def change_content_csv_col_name(self):
        t_lines = self.content_csv.split('\n')
        t_lines[0] = 'code,name,'
        t_content = '\n'.join(t_lines)
        return t_content
         
    @classmethod
    def get_codename_list(cls):
        codename_dict = FundCodeModel.get_codename_dict()
        codename_list = codename_dict.items()
        codename_list.sort(key=lambda x: x[0])
        return codename_list
    
    @classmethod
    def get_codename_dict(cls):
        codemodel = FundCodeModel.get_by_key_name(MODEL_KEY_NAME)
        csv_reader = csv.DictReader(StringIO.StringIO(codemodel.change_content_csv_col_name()))
        codename_dict = {}
        for row in csv_reader:
            t_set = dict(row)
            #logging.debug('%s' % t_set)
            t_name = codecs.decode(t_set['name'],'big5').encode('utf-8')
            t_code = str(t_set['code']).replace('=','').replace('"','')
            #logging.debug(t_item)
            codename_dict[t_code] = t_name
        return codename_dict
        
    @classmethod
    def get_fundname(cls, p_fundcode):
        codename_dict = cls.get_codename_dict()
        if p_fundcode in codename_dict.keys():
            return codename_dict[p_fundcode]
        else:
            logging.warning('get_fundname: code {code} not in list'.format(code=p_fundcode))
            return ''
    
    