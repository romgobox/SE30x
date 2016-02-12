#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import json

from algorithm import Algorithm


def main():   
    import pudb; pu.db
    algorithm = Algorithm(channels_id=[12, 9], alg_type='full')
    result = algorithm.requestResult

if __name__ == '__main__':
    main()