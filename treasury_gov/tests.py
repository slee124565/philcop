#from django.test import TestCase
from django.http import HttpResponse

from models import USTreasuryModel

def test_update_from_web(request):
    t_test = USTreasuryModel._update_from_web()
    return HttpResponse(t_test)