import calendar
import logging

from google.appengine.ext import db

from lxml.html import document_fromstring
from lxml import etree

from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta

from urlsrc.models import WebContentModel

import phicops.utils

URL_TEMPLATE = 'http://announce.fundclear.com.tw/MOPSFundWeb/D02_02P.jsp?fundId={fund_id}&beginDate={begin_date}&endDate={end_date}'
DATE_INDEX = 0
VALUE_INDEX = 1

class FundClearModel(WebContentModel):
    fund_name = db.StringProperty()
    
    @classmethod
    def get_fund(cls, p_fund_id, p_months=12):
        if (p_fund_id == ''):
            logging.warn('Invalid Parameter Value p_fund_id ' + p_fund_id)
            return None

        if p_months < 0:
            logging.warning('Invalid Parameter Value p_month ' + str(p_months))
            return None

        end_date = date.today() - relativedelta(days=+1)
        begin_date = end_date - relativedelta(months=p_months)
        t_url = URL_TEMPLATE.format(fund_id=p_fund_id,begin_date=begin_date.strftime("%Y/%m/%d"),end_date=end_date.strftime("%Y/%m/%d"))
        
        fund_model = FundClearModel.get_or_insert_webcontent(p_fund_id, t_url, date.today())
        if fund_model == None:
            logging.warning('FundClearModel get_fund fail')

        return fund_model
    
    def get_nav_by_date(self, p_date):
        nav_list = self.get_value_list()
        t_count = 0
        if (nav_list[0][DATE_INDEX]).date() <= p_date:
            for t_entry in nav_list:
                if p_date == t_entry[DATE_INDEX].date():
                    logging.debug(__name__ + ': get_nav_by_date: matched entry ' + str(nav_list[t_count]))
                    return nav_list[t_count-1][VALUE_INDEX]
                t_count += 1
        logging.warning(__name__ + ': get_nav_by_date: no matched date value exist!')
        return False
    
    def get_single_html_table(self):
        stk_data = str(self.content).decode('big5')
        t_page = document_fromstring(stk_data)
        t_tables = t_page.xpath("//table")
        t_total = len(t_tables)
        #logging.info('total table count: ' + str(t_total))
        if t_total < 4:
            #return 'TABLE ERROR'
            logging.warning('Source HTML TABLE Count ERROR')
            return None
        
        html = '<table width="100%" border="1" cellpadding="1" cellspacing="1">'
        html += etree.tostring(t_tables[4][0])
        for t_table in t_tables[5:-1]:
            for t_child in t_table:
                if (t_child.tag == 'tr'):
                    if t_child != None:
                        html += etree.tostring(t_child)
        html += '</table>'
        return html
        
    def get_discrete_value_list(self, p_select_day=phicops.utils.MONTH_DAY_END):
        value_list = self.get_value_list()
        return phicops.utils.get_discrete_date_data_list(value_list, p_select_day)
        
    def get_value_list(self):
        '''
        return list of [datetime.datetime, float]
        '''
        dataset = []
        
        stk_data = str(self.content).decode('big5')
        t_page = document_fromstring(stk_data)
        t_tables = t_page.xpath("//table")
        t_total = len(t_tables)
        logging.info('total table count: ' + str(t_total))
        if t_total < 4:
            logging.warning(__name__ + 'Source HTML TABLE ERROR, count ' + str(t_total))
            return None
        
        #logging.info('fund title:' + etree.tostring(t_tables[4][0][0]))
        t_fund_name = t_tables[4][0][0].text
        t_fund_name = t_fund_name.replace('\r\n','')
        #t_fund_name = str(t_fund_name).encode('big5').splitlines()
        #t_fund_name = t_fund_name[0]
        logging.info('fund_name: ' + t_fund_name)
        self.fund_name = t_fund_name
        t_count = 5
        while (t_count <= (t_total-1)):
            #logging.info('table child len ' + str(len(t_tables[t_count])))
            if len(t_tables[t_count]) == 2:
                t_date_list = [t_child.text for t_child in t_tables[t_count][0]]
                t_value_list = [t_child.text for t_child in t_tables[t_count][1]]
                #logging.info(t_date_list)
                #logging.info(t_value_list)
                #logging.info('t_count:' + str(t_count) + '/' + str(t_total))
                for i in range(0,len(t_date_list)):
                    #logging.info('t_count:' + str(i) + '/' + str(len(t_date_list)))
                    #logging.info([t_date_list[i],t_value_list[i]])
                    if i != 0:
                        if (t_date_list[i].strip() != ''):
                            #logging.info([t_date_list[i],t_value_list[i]])
                            #dataset.append([calendar.timegm((parser.parse(t_date_list[i])).timetuple()) * 1000,t_value_list[i]])
                            dataset.append([t_date_list[i],t_value_list[i]])
                        else:
                            logging.debug('remove element ('+ str(t_count) + '#' + str(i) + '): ' + str([t_date_list[i],t_value_list[i]]))
            else:
                logging.debug('skip table:\n' + etree.tostring(t_tables[t_count]))
            t_count += 1
            #break
        t_count = 0
        while (t_count < len(dataset)):
            #logging.info('t_count ' + str(t_count))
            (t_date,t_value) = dataset[t_count]
            if (t_value == '--') or (t_value == 'N/A'):
                if (t_count ==0):
                    logging.debug('removeing dataset element ' + str(dataset[t_count]))
                    del dataset[t_count]
                    continue
                else:
                    logging.debug('replace value with previous one, date ' + str(dataset[t_count]))
                    dataset[t_count][1] = dataset[t_count-1][1]
            #if (t_count > 192):
            #    logging.info('DEBUG:' + str([t_date,t_value]))
            dataset[t_count][0] = parser.parse(t_date)
            dataset[t_count][1] = float(dataset[t_count][1])
            t_count += 1
            
        logging.debug(dataset)

        return dataset
        
        
    def get_dateset(self):
        '''
        return Flow diagram data list
        '''
        dataset = []
        
        stk_data = str(self.content).decode('big5')
        t_page = document_fromstring(stk_data)
        t_tables = t_page.xpath("//table")
        t_total = len(t_tables)
        logging.info('total table count: ' + str(t_total))
        if t_total < 4:
            logging.warning('Source HTML TABLE Count ERROR')
            return None
        
        #logging.info('fund title:' + etree.tostring(t_tables[4][0][0]))
        t_fund_name = t_tables[4][0][0].text
        t_fund_name = t_fund_name.replace('\r\n','')
        #t_fund_name = str(t_fund_name).encode('big5').splitlines()
        #t_fund_name = t_fund_name[0]
        logging.info('fund_name: ' + t_fund_name)
        if self.fund_name == None:
            self.fund_name = t_fund_name
            self.put()
        t_count = 5
        while (t_count <= (t_total-1)):
            #logging.info('table child len ' + str(len(t_tables[t_count])))
            if len(t_tables[t_count]) == 2:
                t_date_list = [t_child.text for t_child in t_tables[t_count][0]]
                t_value_list = [t_child.text for t_child in t_tables[t_count][1]]
                #logging.info(t_date_list)
                #logging.info(t_value_list)
                #logging.info('t_count:' + str(t_count) + '/' + str(t_total))
                for i in range(0,len(t_date_list)):
                    #logging.info('t_count:' + str(i) + '/' + str(len(t_date_list)))
                    #logging.info([t_date_list[i],t_value_list[i]])
                    if i != 0:
                        if (t_date_list[i].strip() != ''):
                            #logging.info([t_date_list[i],t_value_list[i]])
                            #dataset.append([calendar.timegm((parser.parse(t_date_list[i])).timetuple()) * 1000,t_value_list[i]])
                            dataset.append([t_date_list[i],t_value_list[i]])
                        else:
                            logging.info('remove element ('+ str(t_count) + '#' + str(i) + '): ' + str([t_date_list[i],t_value_list[i]]))
            else:
                logging.info('skip table:\n' + etree.tostring(t_tables[t_count]))
            t_count += 1
            #break
        t_count = 0
        while (t_count < len(dataset)):
            #logging.info('t_count ' + str(t_count))
            (t_date,t_value) = dataset[t_count]
            if (t_value == '--') or (t_value == 'N/A'):
                if (t_count ==0):
                    logging.warning('removeing dataset element ' + str(dataset[t_count]))
                    del dataset[t_count]
                    continue
                else:
                    logging.warning('replace value with previous one, date ' + str(dataset[t_count]))
                    dataset[t_count][1] = dataset[t_count-1][1]
            #if (t_count > 192):
            #    logging.info('DEBUG:' + str([t_date,t_value]))
            dataset[t_count][0] = calendar.timegm((parser.parse(t_date)).timetuple()) * 1000
            dataset[t_count][1] = float(dataset[t_count][1])
            t_count += 1
            
        logging.info(dataset)

        return dataset
    
