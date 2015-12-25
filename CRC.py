#! /usr/bin/python
# -*- coding: utf-8 -*-


import logging

logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-4s [%(asctime)s] %(message)s', level = logging.DEBUG)


class CRC_SE3xx(object):

    def __init__(self):
        pass


    def calculate(self, bccString):

        if bccString == '':
            return ''
        else:
            sum = 0
            for i in bccString:
                sum = sum + ord(i)
            if int(hex(sum)[-2:], 16)>127:
                return chr(int(hex(sum)[-2:], 16) - 128)
            else:
                return chr(int(hex(sum)[-2:], 16))
    
    def check(self, cmd, check=True):
        #logging.debug(u'Проверяем CRC. Дана строка: %s' % str(cmd))
        if self.calculate(cmd[1:-1]) == cmd[-1:] or check==False:
            return True
        else:
            return False
