#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime


from protocol import SE30X
from tcp_channel import TCPChannel as TCP
from utils import dateList

whs = [
    
    ([665], '37.28.182.115', 55555),
    #([275, 193], '37.28.182.119', 55555),
    #([75], '37.28.179.220', 55555),
    
    ]
'''
wh_adrs = {
    275: {'num':'00927', 'pass':'777777'}
    193: {'num':'00927', 'pass':'777777'}
}
conn = {
    'ip_adr':'37.28.182.119',
    'port': 55555
}
'''

class Meter(object):
        """Класс прибора учета"""

        def __init__(self, id, adr, number, password, parameters):
            self.id = id
            self.adr = adr
            self.number = number
            self.password = password
            self.fixDayValue = {}
            self.ppValue = {}
            self.parameters = parameters or {
                'fixDay':{'depth': 5},
                'ppValue':{'depth':5},
            }

        def __repr__(self):
            return '<meter adr: %s, number: %s>' % (str(self.adr), self.number)