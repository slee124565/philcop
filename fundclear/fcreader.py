
'''
utility for parsing fund_code.xml
Get FundClear Fund code and Fund name
'''

from lxml import etree
import logging

FUND_CODE_FILE = 'fundclear/fund_code.xml'
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