#! /usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import socket
import sys
import time
import datetime
import logging
#logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'communications.log')
#logging.basicConfig(format = u'# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG)
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG)


from utils import chSim, udate
from CRC import CRC_SE3xx

class ChannelFactory(object):
    """ Фабрика каналов опроса"""

    def __init__(self, id, ch_ip, ch_port, ch_type):
        self.id = id
        self.ch_ip = ch_ip
        self.ch_port = ch_port
        self.type = ch_type 
        
    def getChannel(self):
        if self.type == 'TCPClient':
            return TCPClient(id=self.id, address=self.ch_ip, port=self.ch_port, attempt = 3,  whTimeout=15)

    def __repr__(self):
        return '<channel ip: %s, port: %s>' % (str(self.ch_ip), self.ch_port)
    
    
class TCPClient(object):
    
    def __init__(self, id, address, port, whTimeout = 5, attempt = 3, whRXTimeout=0.5):
        
        self.id = id
        self.whTimeout = whTimeout
        self.attempt = attempt
        self.whRXTimeout = whRXTimeout
        self.address = address
        self.port = port
        
        self.CRC = CRC_SE3xx()


    def connect(self):
        connect_attempt = self.attempt
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.sock.settimeout(self.whTimeout)
        except socket.error, e:
            logging.error(u'Не удалось создать сокет! %s' % e)
            self.terminate()
        while connect_attempt>0:
            logging.debug(u'Устанавливаем соединение: %s:%s' % (self.address, self.port))
            try:
                connection = self.sock.connect((self.address, int(self.port)))
                connect_attempt = 0
                logging.debug(u'Соединение установлено!')
                return True
            except Exception, e:
                connect_attempt -= 1
                logging.error(u'Соединение не установлено. Причина: ' % e)
                time.sleep(1)
                if connect_attempt == 0:
                    return False

    def terminate(self):
        try:
            self.sock.close()
            logging.debug(u'Разрываем соединение!')
            return True
        except socket.error, e:
            logging.error(u'Соединение не разорвано. Причина: ' % e)
            return False
    
    def TXRX(self, cmd, crcString, crcCheck, getRX, ansChLine):
        answer = []
        ansHex = []
        ansHex1 = []
        ansChr=''
        ansBuf = ''
        attempts = self.attempt
        cmdTX = self.TX(cmd + self.CRC.calculate(crcString))
        logging.debug(u'TX >>> %s <<<>>> %s [%d]' % (" ".join(cmdTX[0]), cmdTX[1], cmdTX[2]))
        if getRX:
            while True and attempts>0:
                time.sleep(self.whRXTimeout)
                ansChr = self.RX()
                ansBuf += ansChr
                if self.RX_check(ansBuf, crcCheck, ansChLine):
                    attempts = 0
                    ansHex += [chSim(hex(ord(x))[2:]) for x in ansBuf]  #
                    answer = ansHex #!
                    cmdRX = [ansHex, ansBuf, len(ansHex)]  #
                    logging.debug(u'RX <<< %s <<<>>> %s [%s]' % (" ".join(cmdRX[0]), cmdRX[1], str(cmdRX[2])))
                    break
                else:
                    attempts -= 1
                    if attempts>0:
                        logging.error(u'Осталось попыток запроса: %d' % attempts)
                    else:
                        logging.error(u'Количество попыток запроса исчерпано!')
                        break
        else:
            attempts = 0
            answer = True
        return answer
    
    def RX_check(self, ansChr, crcCheck, ansChLine=''):
        if crcCheck:
            ans_check = self.CRC.check(ansChr, crcCheck)
        else:
            if ansChLine in ansChr:
                ans_check = True
            else:
                ans_check = False
        return ans_check
    
    def TX(self, cmd):
        
        totalsent = 0
        while totalsent < len(cmd):
            sent = self.sock.send(cmd[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
        cmdsend = [chSim(hex(ord(x))[2:]) for x in cmd]
        cmdTX = [cmdsend, cmd, len(cmdsend)]
        return cmdTX

    def RX(self, ):
        chunk = ''
        try:
            self.sock.settimeout(self.whTimeout)
            chunk = self.sock.recv(1024)
        except socket.error, e:
            logging.error(u'Нет ответа на запрос! Причина: %s' % e)
        return chunk
