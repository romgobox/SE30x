#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import sqlite3
import json


from protocol import SE30X, Protocol
from tcp_channel import TCPChannel as TCP
from algorithm import Algorithm
from meter import Meter


DATABASE = 'se.db'

def getMetersByChannel(cur, ch_id, channel):
    meters_sql = '''
        SELECT wh.id, wh.wh_adr, wh.wh_num, wh.wh_pass, wh.wh_settings, wh.wh_protocol
        FROM meter as wh
        WHERE wh.channel_id=%s
        ''' % ch_id

    metersDB = cur.execute(meters_sql)
    metersMap = {}
    for meter in metersDB.fetchall():
        mid = meter['id']
        madr = meter['wh_adr']
        mnum = meter['wh_num']
        mpass = meter['wh_pass']
        params = json.loads(meter['wh_settings'])
        protocol = meter['wh_protocol']
        meterInst = Meter(mid, madr, mnum, mpass, protocol=Protocol.get_protocol(protocol), 
                                                        channel=channel, parameters=params)
        if metersMap.get(protocol):
            metersMap[protocol].append(meterInst)
        else:
            metersMap[protocol] = [meterInst]
    return metersMap

def main():   
    con = sqlite3.connect(DATABASE)
    con.row_factory=sqlite3.Row
    cur = con.cursor()
    channels_sql = '''
                SELECT ch.id, ch.ip_adr, ch.ip_port 
                FROM channels as ch 
                '''
    channelsDB = cur.execute(channels_sql)
    metersToSave = []
    for ch in channelsDB.fetchall():
        ch_id = ch['id']
        ip = ch['ip_adr']
        port = ch['ip_port']
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