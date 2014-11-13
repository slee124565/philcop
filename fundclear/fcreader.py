
'''
utility for parsing fund_code.xml
Get FundClear Fund code and Fund name
'''

from lxml import etree
import logging, pickle

from fundclear.models import dFundCodeModel

FUND_CODE_FILE = 'fundclear/fund_code.xml'

def get_name_with_fundcode_list(p_code,p_fundcode_list=None):
    t_fundcode_list = p_fundcode_list
    if t_fundcode_list is None:
        t_fundcode_list = get_fundcode_list()
    t_code_list = [row[1] for row in t_fundcode_list]
    if p_code in t_code_list:
        return t_fundcode_list[t_code_list.index(p_code)][2]
    else:
        return ''
    
def get_fundcode_dictlist():
    t_fundcode_list = get_fundcode_list()
    t_fundcode_dictlist = []
    for t_fundcode in t_fundcode_list:
        t_fundcode_dictlist.append({
                                    'index': t_fundcode[0],
                                    'code': t_fundcode[1],
                                    'name': t_fundcode[2],
                                    })
    return t_fundcode_dictlist

def get_fundcode_list():
    t_keyname = FUND_CODE_FILE
    t_model = dFundCodeModel.get_or_insert(t_keyname)
    return pickle.loads(t_model.content)
    
def save_fundcode_config():
    t_fundinfo_list = get_fund_info_list()
    t_keyname = FUND_CODE_FILE
    t_fundcode = dFundCodeModel.get_or_insert(t_keyname)
    t_fundcode.content = pickle.dumps(t_fundinfo_list)
    t_fundcode.put()
    return 'save_fundcode_config done'

class FundInfo():
    code = ''
    name = ''
    index = ''
    
    def __init__(self, code, name, index):
        self.code = code
        self.name = name
        self.index = index
    
    def __str__(self):
        return self.__unicode__()
    
    def __unicode__(self):
        return '[' + self.code + ',' + unicode(self.name) + ',' + self.index + ']'
    
def get_fund_info_list():
    '''
    return dict for {code : FundInfo} object
    '''
    t_root = etree.parse(FUND_CODE_FILE)
    t_qdata = t_root.find('qData')
    if t_qdata == None:
        logging.warning(__name__ + ', get_fund_info_list: Can not find qData element')
        return None
    
    t_fund_info_list = []
    logging.debug(__name__ + ', get_fund_info_list: check total row ' + str(len(t_qdata)))
    for t_row in t_qdata[:]:
        t_code = t_name = None
        t_attrib = t_row.attrib
        if 'index' in t_attrib.keys():
            t_index = int(t_row.attrib['index'])
        else:
            logging.debug(__name__ + ', get_fund_info_list: no index attribute')
        for t_element in t_row:
            #logging.debug('check tag ' + t_element.tag)
            if t_element.tag == 'fundCode':
                #logging.debug('find fundCode')
                t_code = t_element
            if t_element.tag == 'fundName':
                #logging.debug('find fundName: ' + t_element.text)
                t_name = t_element
        if t_code is not None and t_name is not None:
            t_fund_code = t_code.text
            t_fund_name = t_name.text
            t_fund_info_list.append([t_index,t_fund_code,t_fund_name])
            logging.debug(__name__ + ', get_fund_info_list: add entry for code ' + t_fund_code + ' index ' + str(t_index))
        else:
            logging.warning(__name__ + ', get_fund_info_list: Can not find fundCode or fundName for element content:\n' + etree.tostring(t_row))
    
    t_fund_info_list.sort(key=lambda x: x[0])
    logging.debug(__name__ + ', get_fund_info_list result total ' + str(len(t_fund_info_list)))
    return t_fund_info_list
    
def get_fund_code_name():
    '''
    return dict for {code, name}
    '''
    t_root = etree.parse(FUND_CODE_FILE)
    t_qdata = t_root.find('qData')
    if t_qdata == None:
        logging.warning(__name__ + ', get_fund_code_name: Can not find qData element')
        return None
    
    t_fund_code_name = {}
    logging.debug(__name__ + ', get_fund_code_name: check total row ' + str(len(t_qdata)))
    for t_row in t_qdata[:]:
        t_code = t_name = None
        for t_element in t_row:
            #logging.debug('check tag ' + t_element.tag)
            if t_element.tag == 'fundCode':
                #logging.debug('find fundCode')
                t_code = t_element
            if t_element.tag == 'fundName':
                #logging.debug('find fundName: ' + t_element.text)
                t_name = t_element
                if t_name is None:
                    logging.debug('t_name is None')
        if t_code is not None and t_name is not None:
            t_fund_code = t_code.text
            t_fund_name = t_name.text
            t_fund_code_name[t_fund_code] = t_fund_name
            logging.debug(__name__ + ', get_fund_code_name: add entry (' + t_fund_code + ',' + unicode(t_fund_name).encode('utf8') + ')')
        else:
            logging.warning(__name__ + ', get_fund_code_name: Can not find fundCode or fundName for element content:\n' + etree.tostring(t_row))
    
    logging.debug(__name__ + ', get_fund_code_name result total ' + str(len(t_fund_code_name)))
    return t_fund_code_name
