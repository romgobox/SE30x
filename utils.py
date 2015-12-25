#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta

def chSim(sim):
    sim = sim
    if len(sim)==1: sim = "0" + sim
    return sim
    
def udate():
    return datetime.now().strftime("%d.%m.%y %H:%M:%S.%f")

def HexToChr(hexList=[]):
    chrList = [chr(int(x, 16)) for x in hexList]
    chrString = ''.join(chrList)
    return chrString

def dateList(depth):
    ''' Метод возвращает список дат на заданную глубину.
        Используется при опросе профиля мощности и 
        зафиксированных показаний на начало суток
    '''
    dateList = []
    nextDay = datetime.now()
    dateList.append(nextDay.strftime('%d.%m.%y'))
    for i in xrange(depth):
        nextDay = (nextDay - timedelta(days=1))
        dateList.append(nextDay.strftime('%d.%m.%y'))
    return dateList

def dateListPP(depth):
    dateList = []
    Now = datetime.now()
    if Now.minute > 30:
        firstVal = Now.strftime('%d.%m.%y %H:')+'30:00'
        dateList.append(firstVal)
        nextVal = datetime.strptime(firstVal, '%d.%m.%y %H:%M:%S')
    else:
        firstVal = Now.strftime('%d.%m.%y %H:')+'00:00'
        dateList.append(firstVal)
        nextVal = datetime.strptime(firstVal, '%d.%m.%y %H:%M:%S')
    for i in xrange(depth):
        nextVal = nextVal - timedelta(minutes=30)
        dateList.append(nextVal.strftime('%d.%m.%y %H:%M:%S'))
    return dateList

def monthList(depth):
    ''' Метод возвращает список месяцев на заданную глубину.
        Используется при опросе зафиксированных показаний на начало месяца
    '''
    monthList = []
    nextMonth = datetime.now()
    month = '%d.%s' % (nextMonth.month, str(nextMonth.year)[-2:])
    monthList.append(month)
    for i in xrange(depth):
        nextMonth = datetime.strptime('01.'+nextMonth.strftime('%m.%y'), '%d.%m.%y') - timedelta(days=1) 
        month = '%d.%s' % (nextMonth.month, str(nextMonth.year)[-2:])
        monthList.append(month)
    return monthList