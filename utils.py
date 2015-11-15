#! /usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime

def chSim(sim):
    sim = sim
    if len(sim)==1: sim = "0" + sim
    return sim
    
def udate():
    return datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S.%f")

def HexToChr(hexList=[]):
    chrList = [chr(int(x, 16)) for x in hexList]
    chrString = ''.join(chrList)
    return chrString