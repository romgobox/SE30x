#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import sqlite3


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

DATABASE = 'se.db'

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

    def saveFixDayValues(self):
        for date, value in self.fixDayValue.items():
            if value:
                dateP = datetime.strptime(date, '%d.%m.%y')
                dateval = datetime.strftime(dateP, '%d.%m.%Y %H:%M:%S')
                now = datetime.now()
                datercv = datetime.strftime(now, '%d.%m.%Y %H:%M:%S')
                sql = '''
                INSERT INTO meter_values VALUES(Null, {id}, 1, '{datercv}', '{dateval}', {value})
                '''.format(id=self.id, datercv=datercv, dateval=dateval, value=value['Sum'])
                con = sqlite3.connect(DATABASE)
                cur = con.cursor()
                cur.execute(sql)
        con.commit()

    def saveppValues(self):
        for date, value in self.ppValue.items():
            if value:
                # dateP = datetime.strptime(date, '%d.%m.%y')
                # dateval = datetime.strftime(dateP, '%d.%m.%Y %H:%M:%S')
                dateval = date
                now = datetime.now()
                datercv = datetime.strftime(now, '%d.%m.%Y %H:%M:%S')
                sql = '''
                INSERT INTO meter_values VALUES(Null, {id}, 2, '{datercv}', '{dateval}', {value})
                '''.format(id=self.id, datercv=datercv, dateval=dateval, value=value)
                con = sqlite3.connect(DATABASE)
                cur = con.cursor()
                cur.execute(sql)
        con.commit()

    def checkValInDB(self, depth, param_num):
        datesList = []
        datesList = dateList(depth)
        dates = []
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        for date in datesList:
            dateP = datetime.strptime(date, '%d.%m.%y')
            dateval = datetime.strftime(dateP, '%d.%m.%Y %H:%M:%S')
            sql = '''
            SELECT COUNT(datetime_value)
            FROM meter_values
            WHERE
                meter_id={id} AND
                datetime_value='{date}' AND
                param_num={param_num}
            '''.format(id=self.id, date=dateval, param_num=param_num)
            cur.execute(sql)
            con.commit()
            for row in cur.fetchall():
                if row[0] == 0:
                    dates.append(date)
        return dates

