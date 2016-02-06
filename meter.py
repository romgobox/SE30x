#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import MySQLdb
import MySQLdb.cursors
from utils import dateList, dateListPP, get_db


class Meter(object):
    """Класс прибора учета"""

    def __init__(self, id, adr, number, password, protocol, channel, parameters):
        self.id = id
        self.adr = adr
        self.number = number
        self.password = password
        self.protocol = protocol
        self.channel = channel
        self.protocol.channel = self.channel
        self.fixDayValue = {}
        self.ppValue = {}
        self.ppValueMap = []
        self.parameters = parameters or {
            'fixDay':5,
            'ppValue':5,
        }

    def __repr__(self):
        return '<meter adr: %s, number: %s>' % (str(self.adr), self.number)

    def authCheckNum(self, ):
        check = False
        if self.protocol.whAuth(self.adr, self.password):
            if self.protocol.whNum(self.adr) == self.number:
                check = True
        else:
            check = False
        return check

    def logOut(self):
        self.protocol.whLogOut(self.adr)

    def getFixedValues(self, dates):
        for date in dates:
            value = self.protocol.whFixDay(self.adr, date=date)
            if value:
                self.fixDayValue[date] = value
            else:
                self.fixDayValue[date] = None
        # if meter.fixDayValue:
        #     meter.saveFixDayValues()

    def getPPValues(self, dates):
        # import pudb; pu.db
        for date in dates:
            value = self.protocol.whPPValue(self.adr, date=date)
            if value:
                self.ppValue.update(value)
            else:
                self.ppValue[date] = None

    def saveFixDayValues(self):
        cur, con = get_db()
        for date, value in self.fixDayValue.items():
            if value:
                dateP = datetime.strptime(date, '%d.%m.%y')
                dateval = datetime.strftime(dateP, '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                datercv = datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
                sql = '''
                INSERT INTO webse.values 
                VALUES(
                    Null, 
                    {id}, 
                    1, 
                    '{datercv}', 
                    '{dateval}', 
                    {value})
                '''.format(id=self.id, datercv=datercv, dateval=dateval, value=value['Sum'])
                cur.execute(sql)
        con.commit()

    def saveppValues(self):
        cur, con = get_db()
        for date in self.ppValueMap:
            value = self.ppValue.get(date)
            if value:
                # dateP = datetime.strptime(date, '%d.%m.%y')
                # dateval = datetime.strftime(dateP, '%d.%m.%Y %H:%M:%S')
                dateval = date
                now = datetime.now()
                datercv = datetime.strftime(now, '%Y-%m-%d %H:%M:%S')
                sql = '''
                INSERT INTO webse.values 
                VALUES(
                    Null, 
                    {id}, 
                    2, 
                    '{datercv}', 
                    '{dateval}', 
                    {value})
                '''.format(id=self.id, datercv=datercv, dateval=dateval, value=value)
                cur.execute(sql)
        con.commit()

    def getppValueMap(self, depth):
        cur, con = get_db()
        self.ppValueMap = dateListPP(depth)
        for date in list(self.ppValueMap):
            sql = '''
            SELECT COUNT(datetime_value) count
            FROM webse.values
            WHERE
                meter_id={id} AND
                datetime_value='{date}' AND
                param_num={param_num}
            '''.format(id=self.id, date=date, param_num=2)
            cur.execute(sql)
            for row in cur.fetchall():
                if row['count'] != 0:
                    self.ppValueMap.remove(date)

    def checkValInDB(self, depth):
        # import pudb; pu.db
        cur, con = get_db()
        datesList = []
        datesList = dateList(depth)
        dates = []
        for date in datesList:
            dateP = datetime.strptime(date, '%d.%m.%y')
            dateval = datetime.strftime(dateP, '%Y-%m-%d %H:%M:%S')
            sql = '''
            SELECT COUNT(datetime_value) count
            FROM webse.values
            WHERE
                meter_id={id} AND
                datetime_value='{date}' AND
                param_num={param_num}
            '''.format(id=self.id, date=dateval, param_num=1)
            cur.execute(sql)
            for row in cur.fetchall():
                if row['count'] == 0:
                    dates.append(date)
        return dates

