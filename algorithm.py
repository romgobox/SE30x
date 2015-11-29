#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime


from protocol import SE30X
from tcp_channel import TCPChannel as TCP
# from meter import Meter
from utils import dateList

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

        def authCheckNum(self, wh_adr, wh_pass, wh_num):
            check = False
            if self.connection:
                if self.protocol.whAuth(wh_adr, wh_pass):
                    if self.protocol.whNum(wh_adr) == wh_num:
                        check = True
            else:
                check = False
            return check

        def getFixedValues(self, depth):
            fixedValuesDict = {}
            for meter in self.meters:
                fixedValuesDict[meter.adr] = []
                if self.authCheckNum(meter.adr, meter.password, meter.number):
                    dates = dateList(depth)
                    for date in dates:
                        value = self.protocol.whFixDay(meter.adr, date=date)
                        if value:
                            valueDict = {date:value}
                            fixedValuesDict[meter.adr].append(valueDict)
                        else:
                            valueDict = {date:None}
                            fixedValuesDict[meter.adr].append(valueDict)
                else:
                    fixedValuesDict[meter.adr] = None
            self.channel.terminate()

            return fixedValuesDict
                    

                