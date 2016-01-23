#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime


from utils import dateList, dateListPP


class Algorithm(object):
    """Класс прибора учета"""

    def __init__(self, channel, meters):
        self.channel = channel
        self.meters = meters
        self.connection = self.channel.connect()

    def runAlgorithm(self):
        for meter in self.meters:
            params = meter.parameters
            if meter.authCheckNum():
                if params.get('fixDay'):
                    depth = params['fixDay']['depth']
                    dates = meter.checkValInDB(depth)
                    meter.getFixedValues(dates)
                if params.get('ppValue'):
                    depth = params['ppValue']['depth']
                    meter.getppValueMap(depth)
                    dates = dateList(depth)
                    meter.getPPValues(dates)
            meter.logOut()
        self.channel.terminate()
