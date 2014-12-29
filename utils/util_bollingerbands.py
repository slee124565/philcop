import numpy as np
import logging

def standard_deviation(p_list,p_tf=20):
    value_list = [t_entry[1] for t_entry in p_list]
    sd = []
    x = p_tf
    #logging.debug('length: ' + str(len(value_list)))
    while x <= len(value_list):
        array2consider = value_list[x-p_tf:x]
        standev = np.std(array2consider)
        #logging.debug(str(array2consider) + '\n' + str(standev) + '\n' + str(x))
        sd.append([p_list[x-1][0],standev])
        x += 1
        
    #logging.debug(__name__ + ',standard_deviation :\n' + str(sd))
    return sd
        

def movingaverage(p_list, p_window=20):
    date_list = [t_entry[0] for t_entry in p_list]
    value_list = [t_entry[1] for t_entry in p_list]
    weights = np.repeat(1.0, p_window)/p_window
    smas = np.convolve(value_list, weights, 'valid')
    #logging.debug('debug:\n' + str(smas))
    smas = [list(a) for a in zip(date_list[p_window-1:],smas)]

    #logging.debug(__name__ + ',movingaverage :\n' + str(smas))
    return smas
    
def get_bollingerbands(p_list, p_tff=20, p_sdw=1.0):
    topBand1 = []
    topBand2 = []
    botBand1 = []
    botBand2 = []
    #logging.debug('{}'.format(p_list))
    
    if len(p_list) > 0:
        sma = movingaverage(p_list, int(p_tff))
        sd_list = standard_deviation(p_list, int(p_tff))
        #logging.debug('sma:\n' + str(sma) + '\nsd:\n' + str(sd_list))
    
        x = 0
        while x < len(sma):
            curDate = sma[x][0]
            curSMA = sma[x][1]
            curSD = sd_list[x][1]
            TB1 = curSMA + curSD*float(p_sdw)
            TB2 = curSMA + curSD*2*float(p_sdw)
            BB1 = curSMA - curSD*float(p_sdw)
            BB2 = curSMA - curSD*2*float(p_sdw)
            
            topBand1.append([curDate,TB1])
            topBand2.append([curDate,TB2])
            botBand1.append([curDate,BB1])
            botBand2.append([curDate,BB2])
            x += 1
    else:
        sma = []
    return sma, topBand1, topBand2, botBand1, botBand2
        
        