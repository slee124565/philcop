from google.appengine.ext import db
from google.appengine.api import urlfetch

from lxml.html import document_fromstring
from lxml import etree

import logging, httplib, pickle, codecs


class URLFetchModel(db.Model):
    fetch_content = db.BlobProperty()
    

    def save_content(self,p_content):
        self.fetch_content = p_content
        self.put()
    
    @classmethod
    def get_content(cls,p_keyname=None):
        t_model = cls.get_model(p_keyname)
        return t_model.fetch_content
    
    @classmethod
    def get_model(cls,p_keyname=None):
        t_model = URLFetchModel.get_or_insert(str(p_keyname))
        return t_model
    
    
    @classmethod
    def get_web_content(cls, url, xpath='', saved=True, keyname=None):
        fname = '{} {}'.format(__name__,'get_web_content')
        logging.debug('{}: fetch with xpath {} and url: \n{}'.format(fname,xpath,url))
        
        try :
            web_fetch = urlfetch.fetch(url)
            if web_fetch.status_code == httplib.OK:
                web_content = document_fromstring(web_fetch.content)
                if xpath == '':
                    t_html = web_fetch.content
                else:
                    t_elements = web_content.xpath(xpath)
                    #return t_elements
                    t_html = etree.tostring(t_elements[0])
                if saved:
                    t_model = cls.get_model(keyname)
                    t_model.save_content(t_html)
                return t_html
            else:
                logging.warning('{}: urlfetch status code {}'.format(fname,web_fetch.status_code))
                return None
        except urlfetch.DownloadError, e:
            logging.warning('{} : Internet Download Error {}'.format(fname,e))
            return None
        