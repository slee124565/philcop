#from django.test import TestCase

from django.http import HttpResponse

from models import BisEersModel
from bis_org.models import EERS_DS_KEY_NARROW

import bis_org.models as bis

def test_get_indices(request):
    
    #t_basket = bis.EERS_DS_KEY_NARROW
    t_basket = bis.EERS_DS_KEY_BROAD
    
    bis_eers = BisEersModel._get_indices(t_basket)
    
    t_area_list = bis_eers.area_list
    return HttpResponse('<br/>\n'.join([str(area) for area in t_area_list])) 
       
    #t_area_eers = bis_eers.area_eers
    #return HttpResponse(str(t_area_eers))
    
    #t_areas = bis_eers.get_reference_area_list()
    #t_area = t_areas[1]

    t_areas = ['China','Chinese Taipei',]
    
    t_result = ''
    
    t_area_eers = bis_eers.get_area_real_bis_eers(t_areas)
    #t_area_eers = bis_eers.get_area_nominal_bis_eers('Chinese Taipei')
    #t_area_eers = bis_eers.get_area_nominal_bis_eers('China')
    
    return HttpResponse(str(t_area_eers))
    
    for date,indice in t_area_eers:
        t_result += str(date) + ' : ' + indice + '<br/>\n'
    return HttpResponse(t_result)
    
        
