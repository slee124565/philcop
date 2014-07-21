from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError

import logging

class WebContentModel(db.Model):
    url = db.StringProperty()
    content = db.BlobProperty()
    expired_date = db.DateProperty()
    
    def do_urlfetch(self):
        if self.url == None:
            logging.warn('object attribute [url] is None!!!')
            return None
        try:
            result = urlfetch.fetch(self.url)
            if result.status_code == 200:
                self.content = db.Blob(result.content)
                return self
            else:
                logging.warn('do_urlfetch failed!!! fetch result code is ' + result.status_code + '!!!\nurl:' + self.url)
                return None
        except DownloadError:
            logging.warn('Internet Download Error')
            return None