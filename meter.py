#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import sqlite3


from protocol import SE30X
from tcp_channel import TCPChannel as TCP
from utils import dateList, dateListPP

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
        self.ppValueMap = []
        self.parameters = parameters or {
            'fixDay':{'depth': 5},
            'ppValue':{'depth':5},
        }

    def __repr__(self):
        return '<meter adr: %s, number: %s>' % (str(self.adr), self.number)

    def saveFixDayValues(self):
        con = sqlite3.connect(DATABASE)
        for date, value in self.fixDayValue.items():
            if value:
                dateP = datetime.strptime(date, '%d.%m.%y')
                dateval = datetime.strftime(dateP, '%d.%m.%Y %H:%M:%S')
                now = datetime.now()
                datercv = datetime.strftime(now, '%d.%m.%Y %H:%M:%S')
                sql = '''
                INSERT INTO meter_values VALUES(Null, {id}, 1, '{datercv}', '{dateval}', {value})
                '''.format(id=self.id, datercv=datercv, dateval=dateval, value=value['Sum'])
                cur = con.cursor()
                cur.execute(sql)
        con.commit()

    def saveppValues(self):
        con = sqlite3.connect(DATABASE)
        for date in self.ppValueMap:
            value = self.ppValue.get(date)
            if value:
                # dateP = datetime.strptime(date, '%d.%m.%y')
                # dateval = datetime.strftime(dateP, '%d.%m.%Y %H:%M:%S')
                dateval = date
                now = datetime.now()
                datercv = datetime.strftime(now, '%d.%m.%Y %H:%M:%S')
                sql = '''
                INSERT INTO meter_values VALUES(Null, {id}, 2, '{datercv}', '{dateval}', {value})
                '''.format(id=self.id, datercv=datercv, dateval=dateval, value=value)
                
                cur = con.cursor()
                cur.execute(sql)
        con.commit()

    def getppValueMap(self, depth):
        self.ppValueMap = dateListPP(depth)
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        for date in list(self.ppValueMap):
            sql = '''
            SELECT COUNT(datetime_value)
            FROM meter_values
            WHERE
                meter_id={id} AND
                datetime_value='{date}' AND
                param_num={param_num}
            '''.format(id=self.id, date=date, param_num=2)
            cur.execute(sql)
            con.commit()
            for row in cur.fetchall():
                if row[0] != 0:
                    self.ppValueMap.remove(date)

    def checkValInDB(self, depth):
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

