#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import json
import gevent.monkey
gevent.monkey.patch_socket()

from algorithm import Algorithm

def alg_run(channel):
    algorithm = Algorithm(channels_id=[channel], alg_type='full')
    return algorithm.requestResult

def main():   
    channels = [11,9]
    result = []
    requests = [gevent.spawn(alg_run, channel) for channel in channels]
    gevent.joinall(requests)
    for greenlet in requests:
        result.append(greenlet.value)
    return result

if __name__ == '__main__':
    result = main()
    import pudb; pu.db