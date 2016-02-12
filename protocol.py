#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
release-0.1:
    инициализация
"""
import subprocess
import time
from datetime import datetime, timedelta
import re
import logging
#logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'communications.log')
#logging.basicConfig(format = u'# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG)
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG)

from utils import chSim, udate, HexToChr

class ProtocolFactory(object):
    """Protocol Factory"""
    @staticmethod
    def get_protocol(protocol):
        if protocol == 'SE30X': return SE30X()

class SE30X(object):
    """ Класс реализующий протокол приборов учета (ПУ) Энергомера СЕ301(303)
    
    Args:
    
        channel (object): объект канала передачи данных
                            прямой serial, GSM, TCP/IP
    """
    def __init__(self, channel=None):
        self.channel = channel
        self.SOH='\x01'
        self.STX='\x02'
        self.ETX='\x03'
        self.ACK= 6
        self.NAK='15'

    def cmdWR(self, cmd, crcString='', crcCheck=True, getRX=True, ansChLine=''):
        return self.channel.TXRX(cmd, crcString, crcCheck, getRX, ansChLine)

    def whAuth(self, whAdr=0, whPass='777777'):
        """ Метод предназначен для авторизации в ПУ
        
        Args:        
            whAdr (int): сетевой адрес ПУ
            whPass (int): пароль ПУ (по-умолчанию: 777777).
        Returns:
            bool: True, если авторизация успешна, False, в любом другом случае.
        Examples:
            >>> SE30X.whAuth (whAdr = 145, whPass = 777777)
            True
            >>> SE30X.whAuth (whAdr = 145, whPass = 777776)
            False
        """
        
        auth = False
        whAuthCmd = '/?'+str(whAdr)+'!\x0D\x0A'
        logging.debug(u'Соединение со счетчиком %s и паролем %s:' % (str(whAdr), str(whPass)))
        ans = self.cmdWR(whAuthCmd, crcString='', crcCheck=False, getRX=True, ansChLine='/EK')
        
        if ans:
            ack = '\x06\x30\x35\x31\x0D\x0A'
            ans = self.cmdWR(ack, crcString='', crcCheck=False, getRX=True, ansChLine=str(whAdr))
            if ans:
                whPasAuth = self.SOH+'P1'+self.STX+'('+str(whPass)+')'+self.ETX
                ans = self.cmdWR(whPasAuth, 'P1'+self.STX+'('+str(whPass)+')'+self.ETX, crcCheck=False, getRX=True, ansChLine=chr(self.ACK))
                if ans:
                    logging.debug(u'Соединение со счетчиком %s и паролем %s установлено!' % (str(whAdr), str(whPass)))
                    auth = True
                else:
                    auth = False
            else:
                auth = False
        else:
            auth = False
            
        if not auth:
            logging.error(u'Не удалось установить соединение со счетчиком %s' % str(whAdr))
        return auth
    
    def whLogOut(self, whAdr):
        """ Метод предназначен для разрыва сессии с ПУ
        
        Args:
            whAdr (int): сетевой адрес ПУ.        
        Returns:
            Метод ничего не возвращает.
        Examples:
            >>>SE30X.whLogOut(whAdr = 145)
        """
        
        logOutCmd = '\x01\x42\x30\x03\x75'
        logging.info(u'Разрываем соединение с прибром учета: %s' % str(whAdr))
        ans = self.cmdWR(logOutCmd, '', crcCheck=False, getRX=False)
        
    def _whAnsCheck(self, whAdr=0, ansCmd=[]):
        whAnsDict = {
        '00':u'Все нормально',
        '01':u'Недопустимая команда или параметр',
        '02':u'Внутренняя ошибка счетчика',
        '03':u'Не достаточен уровень доступа для удовлетворения запроса',
        '04':u'Внутренние часы счетчика уже корректировались в течение текущих су¬ток',
        '05':u'Не открыт канал связи',
        }
        if not ansCmd:
            logging.error(u'Для анализа ответа дана пустая строка!')
            return False
        else:
            if (ansCmd[0]==chSim(hex(whAdr)[2:]) and len(ansCmd)>4) or ansCmd[0:2] == [chSim(hex(whAdr)[2:]), '00']:
                return True
            else:
                logging.error(whAnsDict[ansCmd[1]])
                return False
    
    def valueDict(self, date='', dictType=0):
        Dict = False
        if dictType==0:
            try:
                # datenextday = (datetime.strptime(date, '%d.%m.%y') + timedelta(days=1)).strftime('%d.%m.%y')
                datenextday = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                Dict = {
                        1: [date+' 00:30:00', 0.00],
                        2: [date+' 01:00:00', 0.00],
                        3: [date+' 01:30:00', 0.00],
                        4: [date+' 02:00:00', 0.00],
                        5: [date+' 02:30:00', 0.00],
                        6: [date+' 03:00:00', 0.00],
                        7: [date+' 03:30:00', 0.00],
                        8: [date+' 04:00:00', 0.00],
                        9: [date+' 04:30:00', 0.00],
                        10: [date+' 05:00:00', 0.00],
                        11: [date+' 05:30:00', 0.00],
                        12: [date+' 06:00:00', 0.00],
                        13: [date+' 06:30:00', 0.00],
                        14: [date+' 07:00:00', 0.00],
                        15: [date+' 07:30:00', 0.00],
                        16: [date+' 08:00:00', 0.00],
                        17: [date+' 08:30:00', 0.00],
                        18: [date+' 09:00:00', 0.00],
                        19: [date+' 09:30:00', 0.00],
                        20: [date+' 10:00:00', 0.00],
                        21: [date+' 10:30:00', 0.00],
                        22: [date+' 11:00:00', 0.00],
                        23: [date+' 11:30:00', 0.00],
                        24: [date+' 12:00:00', 0.00],
                        25: [date+' 12:30:00', 0.00],
                        26: [date+' 13:00:00', 0.00],
                        27: [date+' 13:30:00', 0.00],
                        28: [date+' 14:00:00', 0.00],
                        29: [date+' 14:30:00', 0.00],
                        30: [date+' 15:00:00', 0.00],
                        31: [date+' 15:30:00', 0.00],
                        32: [date+' 16:00:00', 0.00],
                        33: [date+' 16:30:00', 0.00],
                        34: [date+' 17:00:00', 0.00],
                        35: [date+' 17:30:00', 0.00],
                        36: [date+' 18:00:00', 0.00],
                        37: [date+' 18:30:00', 0.00],
                        38: [date+' 19:00:00', 0.00],
                        39: [date+' 19:30:00', 0.00],
                        40: [date+' 20:00:00', 0.00],
                        41: [date+' 20:30:00', 0.00],
                        42: [date+' 21:00:00', 0.00],
                        43: [date+' 21:30:00', 0.00],
                        44: [date+' 22:00:00', 0.00],
                        45: [date+' 22:30:00', 0.00],
                        46: [date+' 23:00:00', 0.00],
                        47: [date+' 23:30:00', 0.00],
                        48: [datenextday+' 00:00:00', 0.00],
                }
            except Exception, e:
                logging.error(u'Неверно задана дата %s! Причина: %s' % (date, e))
                Dict = False
        elif dictType==1:
            try:
                Dict = {
                        0: ['Sum', 0.00],
                        1: ['T1', 0.00],
                        2: ['T2', 0.00],
                        3: ['T3', 0.00],
                        4: ['T4', 0.00],
                        5: ['T5', 0.00],
                        
                }
            except Exception, e:
                logging.error(u'Не удалось сформировать словарь! Причина: %s' % (e))
                Dict = False
        elif dictType==3:
            try:
                Dict = {
                        0: ['A', 0.00],
                        1: ['B', 0.00],
                        2: ['C', 0.00],
                }
            except Exception, e:
                logging.error(u'Не удалось сформировать словарь! Причина: %s' % (e))
                Dict = False
        elif dictType==4:
            try:
                Dict = {
                        0: ['AB', 0.00],
                        1: ['BC', 0.00],
                        2: ['CA', 0.00],
                }
            except Exception, e:
                logging.error(u'Не удалось сформировать словарь! Причина: %s' % (e))
                Dict = False
        elif dictType==5:
            try:
                Dict = {
                        0: ['Sum', 0.00],
                        1: ['A', 0.00],
                        2: ['B', 0.00],
                        3: ['C', 0.00],
                }
            except Exception, e:
                logging.error(u'Не удалось сформировать словарь! Причина: %s' % (e))
                Dict = False
        return Dict
    
    def _HexToChr(self, hexList=[]):
        chrList = [chr(int(x, 16)) for x in hexList]
        chrString = ''.join(chrList)
        return chrString
    
    def whNum(self, whAdr=0):
        """ Метод предназначен для чтения серийного номера ПУ
        Args:
            whAdr (int): сетевой адрес ПУ.
        Returns:
            str: серийный номер ПУ в виде строки.
        Examples:
            >>> SE30X.whNum (whAdr = 137)
            009217067001137
        """
        whNum = False
        whNumCmd = self.SOH+'R1'+self.STX+'SNUMB()'+self.ETX
        logging.info(u'Чтение серийного номера прибора учета: %s' % str(whAdr))
        ans = self.cmdWR(whNumCmd, 'R1'+self.STX+'SNUMB()'+self.ETX, ansChLine='SNUMB')
        if ans:
            try:
                whNum = re.findall(u'\((.*?)\)', self._HexToChr(ans))[0]
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение серийного номера прибора учета! Причина: %s' % e)
                whNum = False
        else:
            logging.error(u'Не удалось выполнить чтение серийного номера прибора учета %s!' % str(whAdr))
            whNum = False
        return whNum
        
   
    def whTime(self, whAdr=0, datetimefrmt='%d.%m.%y %H:%M:%S'):
        """Method is intended for reading the date, time and indication of the season
        
        Sends command to read the date, time and indication of the season
        Args:
            whAdr (int): the metering device address, for Mercury 230 from 1 to 240, 0 corresponds to the address of any device on the bus
            datetimefrmt (str): datetime format as a string
        
        Returns:
            dict: with key: (type) value
                DateTime :(str) a string representation of a datetime, depending on the `datetimefrmt`
                TimeDiff :(int) time difference between device and server, in seconds
                Season :(int) indicates the season, 1 - winter time, 0 - summer time (`su-a-amer ti-a-ame...`)
        
        Examples:
        
            >>> whTime = m230.whTime(whAdr=145, datetimefrmt='%Y-%m-%d %H:%M:%S')
            >>> print 'Device datetime: %s, Season: %d, Time difference: %d' % (whTime['DateTime'], whTime['Season'], whTime['TimeDiff'])
            Device datetime: 2015-06-16 10:00:44, Season: 1, Time difference: 3523
        """
        
        whDateTime = False
        whDateCmd = self.SOH+'R1'+self.STX+'DATE_()'+self.ETX
        whTimeCmd = self.SOH+'R1'+self.STX+'TIME_()'+self.ETX
        logging.info(u'Чтение текущей даты и времени прибора учета: %s' % str(whAdr))
        ansDate = self.cmdWR(whDateCmd, 'R1'+self.STX+'DATE_()'+self.ETX, ansChLine='DATE_')
        
        if ansDate:
            ansTime = self.cmdWR(whTimeCmd, 'R1'+self.STX+'TIME_()'+self.ETX, ansChLine='TIME_')
            if ansTime:
                try:
                    
                    whDate = re.findall(u'\((.*?)\)', self._HexToChr(ansDate))[0].split('.') # ['01', '06', '07', '15']
                    whTime = re.findall(u'\((.*?)\)', self._HexToChr(ansTime))[0].split(':') # ['14', '57', '26']
                    
                    time_tuple = (int(whDate[3]), int(whDate[2]), int(whDate[1]), int(whTime[0]), int(whTime[1]), int(whTime[2]), int(whDate[0]), 1, 0)
                    #time_tuple = [int(x) for x in ans[5:8]][::-1] + [int(x) for x in ans[1:4]][::-1] + [0,1] + [int(ans[-3])]
                    whDateForm = time.strftime(datetimefrmt, time_tuple)
                    whSeason = 0
                    whTimeDelta = datetime.now() - datetime.strptime(whDateForm, datetimefrmt)
                    whDateTime = {'DateTime': whDateForm, 'Season': whSeason, 'TimeDiff':whTimeDelta.seconds}
                except Exception, e:
                    logging.error(u'Не удалось выполнить чтение времени прибора учета! Причина: %s' % e)
                    whDateTime = False
            else:
                logging.error(u'Не удалось выполнить чтение времени прибора учета %s!' % str(whAdr))
                whDateTime = False
        else:
            logging.error(u'Не удалось выполнить чтение даты прибора учета %s!' % str(whAdr))
            whDateTime = False
        return whDateTime
    
    def whCurVal(self, whAdr=0, EnergyType='PE'):
        """Method is intended for reading current values of energy (total and by tariffs)
        
        Sends command to read the current values of energy (total and by tariffs)
        
        Args:
        
            whAdr (int): the metering device address.
            EnergyType (str): type of energy,PE(default value) - active, QE - reactive.
        
        Returns:
        
            list:  (type) value.
                0 :(float) Total energy value.
                1 :(float) Tariff 1 energy value.
                2 :(float) Tariff 2 energy value.
                3 :(float) Tariff 3 energy value.
                4 :(float) Tariff 4 energy value.
                5 :(float) Tariff 5 energy value.
                
        Examples:
        
            >>> PE = SE30X.whCurVal(whAdr=229, EnergyType='PE')
            >>> print 'Total energy: %.2f, T1: %.2f, T2: f.2f' % (PE[0], PE[1], PE[2])
            Total energy: 5492.40, T1: 3719.09, T2: 1773.31
            
            >>> QE = SE30X.whCurVal(whAdr=229, EnergyType='QE')
            >>> print 'Total energy: %.2f, T1: %.2f, T2: f.2f' % (QE[0], QE[1], QE[2])
            Total energy: 5492.40, T1: 3719.09, T2: 1773.31
            
        """
        whCur = False
        whCurDict = self.valueDict(dictType=1)
        if whCurDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение текущих показаний прибора учета %s!' % str(whAdr))
            return False
        
        whCurValCmd = self.SOH+'R1'+self.STX+'ET0' + EnergyType + '()'+self.ETX
        logging.info(u'Чтение текущих показаний прибора учета: %s' % str(whAdr))
        ans = self.cmdWR(whCurValCmd, 'R1'+self.STX+'ET0'+EnergyType+'()'+self.ETX, ansChLine='ET0')
        if ans:
            try:
                whCur = {}
                whCurList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(whCurDict)):
                    whCurDict[i][1] = whCurList[i]
                    whCur[whCurDict[i][0]] = whCurDict[i][1]
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение текущих показаний прибора учета! Причина: %s' % e)
                whCur = False
        else:
            logging.error(u'Не удалось выполнить чтение текущих показаний прибора учета %s!' % str(whAdr))
            whCur = False
        return whCur
    
    
    def whFixDay(self, whAdr=0, EnergyType='PE', date=''):
        """Method is intended for reading fixed values of the day (total or by tariffs)
        
        Sends command to read the fixed values of the day (total or by tariffs)
        
        Args:
        
            whAdr (int): the metering device address
            EnergyType (str): type of energy,PE(default value) - active, QE - reactive.
            date (str): date request, format '1.1.15'
        
        Returns:
        
            dict:  (type) value.
                Sum :(float) Total energy value.
                T1 :(float) Tariff 1 energy value.
                T2 :(float) Tariff 2 energy value.
                T3 :(float) Tariff 3 energy value.
                T4 :(float) Tariff 4 energy value.
                T5 :(float) Tariff 5 energy value.
                
        Examples:
            
            >>> PE = SE30X.whFixDay(whAdr=229, EnergyType='PE', date='1.1.15')
            >>> print 'Total energy: %.2f, T1: %.2f, T2: f.2f' % (PE['Sum'], PE['T1'], PE['T2'])
            Total energy: 5492.40, T1: 3719.09, T2: 1773.31
            
            >>> QE = SE30X.whFixDay(whAdr=229, EnergyType='QE', date='12.03.15')
            >>> print 'Total energy: %.2f, T1: %.2f, T2: f.2f' % (QE['Sum'], QE['T1'], QE['T2'])
            Total energy: 5492.40, T1: 3719.09, T2: 1773.31
        """
        
        logging.info(u'Чтение показаний прибора учета на начало суток: %s' % str(whAdr))
        #dateStrf = datetime.strptime(date, '%d.%m.%y').strftime('%-d.%-m.%y') for Linux only

        whFixDict = self.valueDict(dictType=1)
        if whFixDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета %s на начало суток!' % str(whAdr))
            return False
        
        try:
            #Получаем значение не на конец, а на начало суток
            
            dateStrp = datetime.strptime(date, '%d.%m.%y') - timedelta(days=1)
            dateStrf = '%d.%d.%s' % (dateStrp.day, dateStrp.month, str(dateStrp.year)[-2:])
        except Exception, e:
            logging.error(u'Неверный формат даты! Причина: %s' % e)
            logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета %s на начало суток!' % str(whAdr))
            return False
        whFix = False
        whFixDayCmd = self.SOH+'R1'+self.STX+'END' + EnergyType + '('+dateStrf+')'+self.ETX
        ans = self.cmdWR(whFixDayCmd, 'R1'+self.STX+'END'+EnergyType+'('+dateStrf+')'+self.ETX, ansChLine='END')
        if ans:
            try:
                whFix = {}
                whFixList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(whFixDict)):
                    whFixDict[i][1] = whFixList[i]
                    whFix[whFixDict[i][0]] = whFixDict[i][1]    
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета на начало суток! Причина: %s' % e)
                whFix = False
        else:
            logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета %s на начало суток!' % str(whAdr))
            whFix = False
        return whFix
    
    def whFixMonth(self, whAdr=0, EnergyType='PE', date=''):
        """Method is intended for reading fixed values of the month (total or by tariffs)
        
        Sends command to read the fixed values of the month (total or by tariffs)
        
        Args:
        
            whAdr (int): the metering device address
            EnergyType (str): type of energy,PE(default value) - active, QE - reactive.
            date (str): date request, format '1.15'
        
        Returns:
        
            dict:  (type) value.
                Sum :(float) Total energy value.
                T1 :(float) Tariff 1 energy value.
                T2 :(float) Tariff 2 energy value.
                T3 :(float) Tariff 3 energy value.
                T4 :(float) Tariff 4 energy value.
                T5 :(float) Tariff 5 energy value.
                
        Examples:
            
            >>> PE = SE30X.whFixMonth(whAdr=229, EnergyType='PE', date='01.15')
            >>> print 'Total energy: %.2f, T1: %.2f, T2: f.2f' % (PE['Sum'], PE['T1'], PE['T2'])
            Total energy: 5492.40, T1: 3719.09, T2: 1773.31
            
            >>> QE = SE30X.whFixMonth(whAdr=229, EnergyType='QE', date='03.15')
            >>> print 'Total energy: %.2f, T1: %.2f, T2: f.2f' % (QE['Sum'], QE['T1'], QE['T2'])
            Total energy: 5492.40, T1: 3719.09, T2: 1773.31
        """
        logging.info(u'Чтение показаний прибора учета на начало месяца: %s' % str(whAdr))
        #dateStrf = datetime.strptime(date, '%d.%m.%y').strftime('%-d.%-m.%y') for Linux only
        
        whFixDict = self.valueDict(dictType=1)
        if whFixDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета %s на начало месяца!' % str(whAdr))
            return False
        
        try:
            dateCheck = datetime.strptime(date, '%m.%y') #Проверяем, что формат верен месяц.год
            dateStrp = datetime.strptime('01.'+date, '%d.%m.%y') - timedelta(days=1) #Получаем предыдущий месяц, для запроса показания на начало месяца
            dateStrf = '%d.%s' % (dateStrp.month, str(dateStrp.year)[-2:])
        except Exception, e:
            logging.error(u'Неверный формат даты! Причина: %s' % e)
            logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета %s на начало месяца!' % str(whAdr))
            return False
        whFixM = False
        whFixMonthCmd = self.SOH+'R1'+self.STX+'ENM' + EnergyType + '('+dateStrf+')'+self.ETX
        ans = self.cmdWR(whFixMonthCmd, 'R1'+self.STX+'ENM'+EnergyType+'('+dateStrf+')'+self.ETX, ansChLine='ENM')
        
        print re.findall(u'\((.*?)\)', self._HexToChr(ans))
        
        if ans:
            try:
                whFixM = {}
                whFixMList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(whFixDict)):
                    whFixDict[i][1] = whFixMList[i]
                    whFixM[whFixDict[i][0]] = whFixDict[i][1]
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета на начало месяца! Причина: %s' % e)
                whFixM = False
        else:
            logging.error(u'Не удалось выполнить чтение зафиксированных показаний прибора учета %s на начало месяца!' % str(whAdr))
            whFixM = False
        return whFixM
    
    def whPPValue(self, whAdr=0, EnergyType='PE', date='', fromRec=1, count=48):
        """Method is intended for reading value of power profile by given date
        
        Sends command to read the value of power profile by given date
        
        Args:
        
            whAdr (int): the metering device address
            EnergyType (str): type of energy,PE(default value) - active, QE - reactive.
            date (str): date request, format '01.01.15'.
            fromto (str): count of power profile records in given date, format '.1.10' (first 10 records)
        
        Returns:
        
            
            dict:  (type) value.
                'DATETIME' :(float) Power profile in period DATETIME value.
                
        
        Examples:
            
            >>> En = se.whPPValue(665, date='01.07.15', fromRec=1, count=1)
            >>> print 'print '%s: %.6f' % ('01.07.1500:30:00', En['01.07.1500:30:00'])
            01.07.15 00:30:00: 0.000331
        """
        
        logging.info(u'Чтение профиля мощности прибора: %s' % str(whAdr))
        
        #dateStrf = datetime.strptime(date, '%d.%m.%y').strftime('%-d.%-m.%y') for Linux only
        #try:
        #   dateStrp = datetime.strptime(date, '%d.%m.%y')
        #   dateStrf = '%d.%d.%s' % (dateStrp.day, dateStrp.month, str(dateStrp.year)[-2:])
        #except Exception, e:
        #   logging.error(u'Неверный формат даты! Причина: %s' % e)
        #   logging.error(u'Не удалось выполнить чтение профиля мощности прибора учета %s!' % str(whAdr))
        #   return False
        #whPPValCmd = self.SOH+'R1'+self.STX+'GRA' + EnergyType + '('+dateStrf+fromto+')'+self.ETX
        #ans = self.cmdWR(whPPValCmd, 'R1'+self.STX+'GRA'+EnergyType+'('+dateStrf+fromto+')'+self.ETX, ansChLine='GRA')
        
        PPV = False
        dateForDict = datetime.strptime(date, '%d.%m.%y').strftime('%Y-%m-%d')
        PPDict = self.valueDict(dateForDict, dictType=0)
        if PPDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение профиля мощности прибора учета %s!' % str(whAdr))
            return False
        fromto = '.%d.%d' % (fromRec, count)
        whPPValCmd = self.SOH+'R1'+self.STX+'GRA' + EnergyType + '('+date+fromto+')'+self.ETX
        ans = self.cmdWR(whPPValCmd, 'R1'+self.STX+'GRA'+EnergyType+'('+date+fromto+')'+self.ETX, ansChLine='GRA')
        if ans:
            try:
                PPV = {}
                PPVList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                k=0
                for i in range(fromRec, fromRec+count):
                    PPDict[i][1] = PPVList[k]
                    PPV[PPDict[i][0]] = PPDict[i][1]    
                    k+=1
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение профиля мощности прибора учета! Причина: %s' % e)
                PPV = False
        else:
            logging.error(u'Не удалось выполнить чтение профиля мощности прибора учета %s!' % str(whAdr))
            PPV = False
        return PPV

    def whU(self, whAdr):
        """Method is intended for reading instantaneous values of Voltage (V)
        
        Sends command to read the instantaneous values of Voltage (V)
        
        Args:
        
            whAdr (int): the metering device address.
        
        Returns:
        
            dict: with key: (type) value.
                A :(float) phase 1 voltage.
                B :(float) phase 2 voltage.
                C :(float) phase 3 voltage.
                
        Examples:
        
            >>> U = SE30X.whU(whAdr=145)
            >>> print 'A: %.3f, B: %.3 C: %.3f' % (U['A'],U['B'],U['C'],)
            A: 227.371 B: 217.371 C: 237.371
        """
        
        logging.info(u'Чтение мгновенных значений напряжения прибора учета: %s' % str(whAdr))
        U = False
        UDict = self.valueDict(dictType=3)
        if UDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение значений напряжения прибора учета %s!' % str(whAdr))
            return False
        whUCmd = self.SOH+'R1'+self.STX+'VOLTA()'+self.ETX
        ans = self.cmdWR(whUCmd, 'R1'+self.STX+'VOLTA()'+self.ETX, ansChLine='VOLTA')
        if ans:
            try:
                U = {}
                whUList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(UDict)):
                    UDict[i][1] = whUList[i]
                    U[UDict[i][0]] = UDict[i][1]    
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение значений напряжения прибора учета! Причина: %s' % e)
                U = False
        else:
            logging.error(u'Не удалось выполнить чтение значений напряжения прибора учета %s!' % str(whAdr))
            U = False
        return U
    
    def whUAngle(self, whAdr):
        """Method is intended for reading angles between the voltages
        
        Sends command to read the angles between the voltages
        
        Args:
        
            whAdr (int): the metering device address.
        
        Returns:
        
            dict: with key: (type) value.
                AB :(float) angle between phase 1 and 2 voltages.
                BC :(float) angle between phase 2 and 3 voltages.
                CA :(float) angle between phase 3 and 1 voltages.
                
        Examples:
        
            >>> A = merc.whUAngle(whAdr=145)
            >>> print 'A12: %s, A13: %s A23: %s' % (A['AB'],A['BC'],A['CA'],)
            A12: 120, A13: 240 A23: 120
        """
        logging.info(u'Чтение мгновенных значений углов между фазными напряжениями прибора учета: %s' % str(whAdr))
        UAn = False
        UAnDict = self.valueDict(dictType=4)
        if UAnDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение значений углов между фазными напряжениями прибора учета %s!' % str(whAdr))
            return False
        whUAnCmd = self.SOH+'R1'+self.STX+'CORUU()'+self.ETX
        ans = self.cmdWR(whUAnCmd, 'R1'+self.STX+'CORUU()'+self.ETX, ansChLine='CORUU')
        if ans:
            try:
                UAn = {}
                whUAnList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(UAnDict)):
                    UAnDict[i][1] = whUAnList[i]
                    UAn[UAnDict[i][0]] = UAnDict[i][1]  
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение значений углов между фазными напряжениями прибора учета! Причина: %s' % e)
                UAn = False
        else:
            logging.error(u'Не удалось выполнить чтение значений углов между фазными напряжениями прибора учета %s!' % str(whAdr))
            UAn = False
        return UAn
    
    def whIUAngle(self, whAdr):
        """Method is intended for reading angles between the voltages an I
        
        Sends command to read the angles between the voltages and I
        
        Args:
        
            whAdr (int): the metering device address.
        
        Returns:
        
            dict: with key: (type) value.
                A :(float) angle phase 1
                B :(float) angle phase 2
                C :(float) angle phase 3
                
        Examples:
        
            >>> A = merc.whIUAngle(whAdr=145)
            >>> print 'A: %s, B: %s C: %s' % (A['A'],A['B'],A['C'],)
            A: 120, B: 240 C: 120
        """
        logging.info(u'Чтение мгновенных значений углов между фазными векторами токов и напряжений прибора учета: %s' % str(whAdr))
        IUAn = False
        IUAnDict = self.valueDict(dictType=3)
        if IUAnDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение значений углов между фазными векторами токов и напряжений прибора учета %s!' % str(whAdr))
            return False
        whIUAnCmd = self.SOH+'R1'+self.STX+'CORIU()'+self.ETX
        ans = self.cmdWR(whIUAnCmd, 'R1'+self.STX+'CORIU()'+self.ETX, ansChLine='CORIU')
        if ans:
            try:
                IUAn = {}
                whIUAnList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(IUAnDict)):
                    IUAnDict[i][1] = whIUAnList[i]
                    IUAn[IUAnDict[i][0]] = IUAnDict[i][1]   
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение значений углов между фазными векторами токов и напряжений прибора учета! Причина: %s' % e)
                IUAn = False
        else:
            logging.error(u'Не удалось выполнить чтение значений углов между фазными векторами токов и напряжений прибора учета %s!' % str(whAdr))
            IUAn = False
        return IUAn

    
    def whI(self, whAdr):
        """Method is intended for reading instantaneous values of amperage (A)
        
        Sends command to read the instantaneous values of amperage (A)
        
        Args:
        
            whAdr (int): the metering device address.
        
        Returns:
        
            dict: with key: (type) value.
                A :(float) phase 1 voltage.
                B :(float) phase 2 voltage.
                C :(float) phase 3 voltage.
                
        Examples:
        
            >>> I = SE30X.whI(whAdr=145)
            >>> print 'A: %.3f, B: %.3 C: %.3f' % (I['A'],I['B'],I['C'],)
            A: 227.371 B: 217.371 C: 237.371
        """
        logging.info(u'Чтение мгновенных значений тока прибора учета: %s' % str(whAdr))
        I = False
        IDict = self.valueDict(dictType=3)
        if IDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение значений тока прибора учета %s!' % str(whAdr))
            return False
        whICmd = self.SOH+'R1'+self.STX+'CURRE()'+self.ETX
        ans = self.cmdWR(whICmd, 'R1'+self.STX+'CURRE()'+self.ETX, ansChLine='CURRE')
        if ans:
            try:
                I = {}
                whIList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(IDict)):
                    IDict[i][1] = whIList[i]
                    I[IDict[i][0]] = IDict[i][1]    
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение значений тока прибора учета! Причина: %s' % e)
                I = False
        else:
            logging.error(u'Не удалось выполнить чтение значений тока прибора учета %s!' % str(whAdr))
            I = False
        return I
    
    def whP(self, whAdr, EnergyType='P'):
        """Method is intended for reading instantaneous values of power
        
        Sends command to read the instantaneous values of power

        Args:
        
            whAdr (int): the metering device address.
            EnergyType (str): type energy. P - active, Q - reactive
        
        Returns:
        
            dict: with key: (type) value.
                A :(float) phase 1 power.
                B :(float) phase 2 power.
                C :(float) phase 3 power.
                
        Examples:
        
            >>> I = merc.whP(whAdr=145, en='P')
            >>> print 'P1: %.2f, P2: %.2f P3: %.2f' % (P[1],P[2],P[3],)
            P1: 0.00, P2: 0.00 P3: 0.00
        """
        logging.info(u'Чтение мгновенных значений фазной мощности прибора учета: %s' % str(whAdr))
        P = False
        PDict = self.valueDict(dictType=3)
        if PDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение значений фазной мощности прибора учета %s!' % str(whAdr))
            return False
        whPCmd = self.SOH+'R1'+self.STX+'POWP'+EnergyType+'()'+self.ETX
        ans = self.cmdWR(whPCmd, 'R1'+self.STX+'POWP'+EnergyType+'()'+self.ETX, ansChLine='POWP')
        if ans:
            try:
                P = {}
                whPList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(PDict)):
                    PDict[i][1] = whPList[i]
                    P[PDict[i][0]] = PDict[i][1]    
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение значений фазной мощности прибора учета! Причина: %s' % e)
                P = False
        else:
            logging.error(u'Не удалось выполнить чтение значений фазной мощности прибора учета %s!' % str(whAdr))
            P = False
        return P
    
    def whCosf(self, whAdr):
        """Method is intended for reading instantaneous values of power factor
        
        Sends command to read the instantaneous values of power factor
        !!! Not tested on real device !!!
        
        Args:
        
            whAdr (int): the metering device address, for Mercury 230 from 1 to 240, 0 corresponds to the address of any device on the bus.
            en (str): type energy. P - active, Q - reactive, S - full 
            
        Returns:
        
            dict: with key: (type) value.
                Sum :(float) total power.
                A :(float) phase 1 power.
                B :(float) phase 2 power.
                C :(float) phase 3 power.
                
        Examples:
        
            >>> C = merc.whCosf(wh_adr_set)
            >>> print 'C1: %.2f, C2: %.2f C3: %.2f' % (C[1],C[2],C[3],)
            C1: 0.97 C2: 0.89 C3: 0.76
        """
        logging.info(u'Чтение мгновенных значений коэффициента мощности прибора учета: %s' % str(whAdr))
        Cosf = False
        CosfDict = self.valueDict(dictType=5)
        if CosfDict:
            pass
        else:
            logging.error(u'Не удалось выполнить чтение значений коэффициента мощности прибора учета %s!' % str(whAdr))
            return False
        whCosfCmd = self.SOH+'R1'+self.STX+'COS_f()'+self.ETX
        ans = self.cmdWR(whCosfCmd, 'R1'+self.STX+'COS_f()'+self.ETX, ansChLine='COS_f')
        if ans:
            try:
                Cosf = {}
                whCosfList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                for i in range(len(CosfDict)):
                    CosfDict[i][1] = whCosfList[i]
                    Cosf[CosfDict[i][0]] = CosfDict[i][1]   
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение значений коэффициента мощности прибора учета! Причина: %s' % e)
                Cosf = False
        else:
            logging.error(u'Не удалось выполнить чтение значений коэффициента мощности прибора учета %s!' % str(whAdr))
            Cosf = False
        return Cosf
    
    def whFreq(self, whAdr):
        """Method is intended for reading instantaneous values of frequency
        
        Sends command to read the instantaneous values of frequency
        !!! Not tested on real device !!!
        
        Args:
        
            whAdr (int): the metering device address, for Mercury 230 from 1 to 240, 0 corresponds to the address of any device on the bus.
             
            
        Returns:
        
            float: frequency.
                
        Examples:
        
            >>> F = merc.whFreq(wh_adr_set)
            >>> print 'Frequency: %.2f' % F
            Frequency: 50.01
        """
        logging.info(u'Чтение мгновенных значений частоты прибора учета: %s' % str(whAdr))
        whFreqCmd = self.SOH+'R1'+self.STX+'FREQU()'+self.ETX
        ans = self.cmdWR(whFreqCmd, 'R1'+self.STX+'FREQU()'+self.ETX, ansChLine='FREQU')
        if ans:
            try:
                Freq = {}
                whFreqList = [float(x) for x in re.findall(u'\((.*?)\)', self._HexToChr(ans))]
                Freq['freq'] = whFreqList[0]    
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение значений частоты мощности прибора учета! Причина: %s' % e)
                Freq = False
        else:
            logging.error(u'Не удалось выполнить чтение значений частоты мощности прибора учета %s!' % str(whAdr))
            Freq = False
        return Freq
        
    def whFastRead(self, whAdr=0, whAct='R1', whParam='SNUMB()', ChLine='SNUMB'):
        
        whFastResponse = False
        whFastResponseCmd = '/?'+str(whAdr)+'!'+self.SOH+str(whAct)+self.STX+str(whParam)+self.ETX
        logging.info(u'Быстрое чтение параметра %s прибора учета: %s' % (str(whParam), str(whAdr)))
        ans = self.cmdWR(whFastResponseCmd, str(whAct)+self.STX+str(whParam)+self.ETX, ansChLine=ChLine)
        whFastResponse = self._HexToChr(ans)
        '''
        if ans:
            try:
                whNum = re.findall(u'\((.*?)\)', self._HexToChr(ans))[0]
            except Exception, e:
                logging.error(u'Не удалось выполнить чтение серийного номера прибора учета! Причина: %s' % e)
                whNum = False
        else:
            logging.error(u'Не удалось выполнить чтение серийного номера прибора учета %s!' % str(whAdr))
            whNum = False
        '''
        return whFastResponse
    
      





