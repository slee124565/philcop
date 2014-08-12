from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

from datetime import date

import logging

class WebContentModel(db.Model):
    url = db.StringProperty()
    content = db.BlobProperty()
    expired_date = db.DateProperty()
    
    @classmethod
    def get_or_insert_webcontent(cls, p_key_name, p_url, p_expired_date=None):
        '''
        This function make used of function WebContentModel.do_urlfetch() to fetch web content
        and will check attribute 'expired_date' before do_urlfetch;
        if web content in datastore is not expired, it will return web content from datastore directly
        ex:
            webContent = WebContentModel.get_or_insert_webcontent(key_name,url,expired_date)
            if webContent:
                web_content_process()
            else:
                url_fetch_exception_handle()
        '''
        webContent = cls.get_or_insert(p_key_name)
        webContent.url = p_url
        if ( (webContent.expired_date == None) or \
             (date.today() > webContent.expired_date) or \
             (p_expired_date == None)):
            if (webContent.do_urlfetch()):
                webContent.expired_date = p_expired_date
                webContent.put()
            else:
                logging.warning(__name__ + ': WebContentModel urlfetch Fail!!!')
                return None
        else:
            logging.info(__name__ + ': web content exist in datastore and not expired.')
        
        return webContent
    
    def sample_value_list(self, p_sample_key_list, p_matrix):
        t_sample_list = []
        
        t_row1_list = [row[0] for row in p_matrix]
        for t_key in p_sample_key_list:
            if t_key in t_row1_list:
                t_index = t_row1_list.index(t_key)
                t_sample_list.append(p_matrix[t_index])
            else:
                t_sample_list.append([t_key, None])
        
        logging.debug(__name__ + ': sample_value_list for p_sample_key_list\n' + str(p_sample_key_list) + '\n' + str(t_sample_list))
        return t_sample_list
        
    def do_urlfetch(self):
        '''
        This function fetch Internet content according attribute 'url',
        store Internet content in attribute 'content'
        and return WebContentModel if success; return None if fail.
        ex:
            webContent = WebContentModel.get_or_insert(key_name)
            webContent.url = 'http://www.google.com'
            if webContent.do_urlfetch():
                webContent.put()
                process_web_conent()
            else
                url_fetch_exception_handle()
        '''
        if self.url == None:
            logging.warning(__name__ + ': Invalid Parameter url ' + self.url)
            return None
        try:
            logging.debug('fetch url resource: \n' + self.url)
            result = urlfetch.fetch(self.url)
            if result.status_code == 200:
                self.content = db.Blob(result.content)
                return self
            else:
                logging.warning(__name__ + ': do_urlfetch failed!!! fetch result code is ' + result.status_code + '!!!\nurl:' + self.url)
                return None
        except DownloadError:
            logging.warning(__name__ + ': Internet Download Error')
            return None