#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime


from protocol import SE30X
from tcp_channel import TCPChannel as TCP
# from meter import Meter
from utils import dateList, dateListPP

# whs = [
    
#     ([665], '37.28.182.115', 55555),
#     #([275, 193], '37.28.182.119', 55555),
#     #([75], '37.28.179.220', 55555),
    
#     ]
'''
wh_adrs = {
    275: {'num':'00927', 'pass':'777777'}
    193: {'num':'00927', 'pass':'777777'}
}
conn = {
    'ip_adr':'37.28.182.119',
    'port': 55555
}
['009217067001275', '009217067001193']

'''
# meters = []
# meters.append(Meter(275, '009217067001275', 777777, '37.28.182.119', 55555))
# meters.append(Meter(193, '009217067001193', 777777, '37.28.182.119', 55555))

class Algorithm(object):
    """Класс прибора учета"""

    def __init__(self, protocol, channel, meters):
        self.channel = channel
        self.protocol = protocol
        self.protocol.channel = self.channel
        self.meters = meters
        self.connection = self.channel.connect()

    def runAlgorithm(self):
        for meter in self.meters:
            params = meter.parameters
            if self.authCheckNum(meter.adr, meter.password, meter.number):
                if params.get('fixDay'):
                    depth = params['fixDay']['depth']
                    dates = meter.checkValInDB(depth)
                    self.getFixedValues(meter, dates)
                if params.get('ppValue'):
                    depth = params['ppValue']['depth']
                    meter.getppValueMap(depth)
                    dates = dateList(depth)
                    self.getPPValues(meter, dates)
            self.protocol.whLogOut(meter.adr)
        self.channel.terminate()


    def authCheckNum(self, wh_adr, wh_pass, wh_num):
        check = False
        if self.connection:
            if self.protocol.whAuth(wh_adr, wh_pass):
                if self.protocol.whNum(wh_adr) == wh_num:
                    check = True
        else:
            check = False
        return check

    def getFixedValues(self, meter, dates):
        for date in dates:
            value = self.protocol.whFixDay(meter.adr, date=date)
            if value:
                meter.fixDayValue[date] = value 
            else:
                meter.fixDayValue[date] = None
        # if meter.fixDayValue:
        #     meter.saveFixDayValues()

    def getPPValues(self, meter, dates):
        for date in dates:
            value = self.protocol.whPPValue(meter.adr, date=date)
            if value:
                meter.ppValue.update(value)
            else:
                meter.ppValue[date] = None
        # if meter.ppValue:
        #     meter.saveppValues()

                