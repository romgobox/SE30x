#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import logging
from datetime import datetime
from protocol import SE30X, ProtocolFactory
from tcp_channel import ChannelFactory
from meter import Meter
from utils import dateList, dateListPP, get_db
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG)


class Algorithm(object):
    """Класс алгоритма опроса"""

    def __init__(self, channels_id=[], meters_id=[], alg_type='full'):
        self.metersMap = {}
        self.channels = []
        self.channels_id = channels_id or []
        self.meters_id = meters_id or []
        self.alg_type = alg_type or 'full'
        self.requestResult = self.runAlgorithm(self.alg_type)

    def runAlgorithm(self, alg_type):
        result = None
        if alg_type == 'full':
            if self.channels_id:
                for channel in self.channels_id:
                    self.getMetersByChannel(ch_id=channel)
                self.fullAlgorithm()
                self.saveValues('full')
                result = self.serializeValues('full')

        return result

    def fullAlgorithm(self):
        for channel, meters in self.metersMap.items():
            try:
                channel.connect()
            except:
                break
            for meter in meters:
                params = meter.parameters
                if meter.authCheckNum():
                    if params.get('fixDay'):
                        depth = int(params['fixDay'])
                        dates = meter.checkFixDayValInDB(depth)
                        meter.getFixedValues(dates)
                    if params.get('ppValue'):
                        depth = int(params['ppValue'])
                        meter.getppValueMap(depth)
                        dates = meter.checkPPValueValInDB(depth)
                        meter.getPPValues(dates)
                meter.logOut()
            channel.terminate()

    def getMetersByChannel(self, ch_id=None, channel=None):
        channel = channel or self.getChannel(ch_id)
        ch_id = ch_id or channel.id
        meters_sql = '''
            SELECT wh.id, wh.wh_adr, wh.wh_num, wh.wh_pass, wh.wh_settings, pr.pr_name
            FROM meters wh, protocols pr
            WHERE wh.channel_id={ch_id} AND wh.protocol_id=pr.id
            '''.format(ch_id=ch_id)

        cur, con = get_db()
        cur.execute(meters_sql)
        meters = cur.fetchall()
        for meter in meters:
            mid = meter['id']
            madr = meter['wh_adr']
            mnum = meter['wh_num']
            mpass = meter['wh_pass']
            params = json.loads(meter['wh_settings'])
            protocol = meter['pr_name']
            meter = Meter(mid, madr, mnum, mpass, protocol=ProtocolFactory.get_protocol(protocol), 
                                                            channel=channel, parameters=params)
            if self.metersMap.get(channel):
                self.metersMap[channel].append(meter)
            else:
                self.metersMap[channel] = [meter]

    def getChannel(self, ch_id):
        channel_sql = '''
            SELECT id, ch_ip, ch_port 
            FROM channels
            WHERE id={ch_id} AND is_activ=1
            '''.format(ch_id=ch_id)
        cur, con = get_db()
        cur.execute(channel_sql)
        result = cur.fetchone()
        id = result['id']
        ch_ip = result['ch_ip']
        ch_port = result['ch_port']
        ch_type = 'TCPClient'
        channelFactory = ChannelFactory(id=id, ch_ip=ch_ip, ch_port=ch_port, ch_type=ch_type)
        channel = channelFactory.getChannel()
        self.channels.append(channel)
        return channel

    def saveValues(self, alg_type):
        if alg_type == 'full':
            for meters in self.metersMap.values():
                for meter in meters:
                    meter.saveFixDayValues()
                    meter.saveppValues()


    def serializeValues(self, alg_type):
        if alg_type == 'full':
            result = []
            for meters in self.metersMap.values():
                for meter in meters:
                    row = {
                        'id':meter.id,
                        'fixDay':meter.fixDayValue,
                        'ppValue':meter.ppValue
                    }
                    result.append(row)

        return result
