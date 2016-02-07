#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import json

from protocol import SE30X, Protocol
from tcp_channel import TCPChannel as TCP
from algorithm import Algorithm
from meter import Meter
from utils import get_db

import MySQLdb
import MySQLdb.cursors


def getMetersByChannel(cur, ch_id, channel):
    # import pudb; pu.db
    meters_sql = '''
        SELECT wh.id, wh.wh_adr, wh.wh_num, wh.wh_pass, wh.wh_settings, pr.pr_name
        FROM meters wh, protocols pr
        WHERE wh.channel_id={ch_id} AND wh.protocol_id=pr.id
        '''.format(ch_id=ch_id)

    cur, con = get_db()
    cur.execute(meters_sql)
    meters = cur.fetchall()
    metersMap = {}
    for meter in meters:
        mid = meter['id']
        madr = meter['wh_adr']
        mnum = meter['wh_num']
        mpass = meter['wh_pass']
        params = json.loads(meter['wh_settings'])
        protocol = meter['pr_name']
        meterInst = Meter(mid, madr, mnum, mpass, protocol=Protocol.get_protocol(protocol), 
                                                        channel=channel, parameters=params)
        if metersMap.get(protocol):
            metersMap[protocol].append(meterInst)
        else:
            metersMap[protocol] = [meterInst]
    return metersMap

def main():   
    channels_sql = '''
                SELECT id, ch_ip, ch_port 
                FROM channels
                WHERE is_activ=1
                '''
    cur, con = get_db()
    cur.execute(channels_sql)
    channels = cur.fetchall()
    metersToSave = []
    for ch in channels:
        ch_id = ch['id']
        ip = ch['ch_ip']
        port = ch['ch_port']
        channel = TCP(address=ip, port=port, attempt = 3,  whTimeout=15)
        metersMap = getMetersByChannel(cur, ch_id, channel)
        for protocol, meters in metersMap.items():
            metersToSave.extend(meters)
            algorithm = Algorithm(channel=channel, meters=meters)
            algorithm.runAlgorithm()

    for meter in metersToSave:
        meter.saveFixDayValues()
        meter.saveppValues()

if __name__ == '__main__':
    main()