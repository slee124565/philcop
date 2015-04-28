from google.appengine.ext import db

import logging, pickle


class MFModle(db.Model):
    dict_data_pickle = db.BlobProperty(default='')
    dict_data = {}
    
    @classmethod
    def get_model(cls, p_keyname='mf_tw50'):
        func = '{} {}'.format(__name__,'get_model')
        
        logging.info('{}: get model with keyname {}'.format(func,p_keyname))
        
        t_model = cls.get_or_insert(p_keyname)
        
        if t_model.dict_data_pickle in [None,'']:
            t_model.dict_data_pickle = ''
            t_model.dict_data = {}
        else:    
            t_model.dict_data = pickle.loads(t_model.dict_data_pickle)
        return t_model
        
        
    def save_dict_data(self):
        self.dict_data_pickle = pickle.dumps(self.dict_data)
        self.put()