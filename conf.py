#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (c) 2013 V zhang <dolphinzhang1987@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Created on 2013-6-9

@author: V
'''

import os

# from koala.core.config import Config
#
# base = os.path.dirname(os.path.abspath(__file__))
# user_conf = os.path.join(base, 'test.yaml')
# if not os.path.exists(user_conf):
#     user_conf = os.path.join(base, 'map_google.yaml')
# user_config = Config(user_conf)
#
# starts = [str(start.uid) for start in user_config.job.starts]
#
# mongo_host = user_config.job.mongo.host
# mongo_port = user_config.job.mongo.port
# db_name = user_config.job.db
#
# instances = user_config.job.instances

level1_types = ['food', 'restaurant',  'amusement_park', 'park']
level2_types = ['cafe', 'school', 'night_club', 'zoo']
level3_types = ['shopping_mall', 'hair_care', 'museum']
types = [level1_types, level2_types, level3_types]
app_keys = {'AIzaSyAw0jhkE1v890qEZ3AeS8nmliUr4sTG_5M':0, 'AIzaSyDZaHRpC3xQYFOBZlopW-awRSIKFKIjryM':0, 'AIzaSyDRs-fG8hhn0EtHalyX8mCV6Qap4JU4qHI':0,
             'AIzaSyAc40giECD9324cpB0ihinneVvM1zHZNvg':0, 'AIzaSyC_xY2TekE8KoCZ5Bd14YpqUhM8gUzSvmQ':0, 'AIzaSyBQXwKWudaPt5vbCUE3Q8_aYc7fDar_mRk':0,
             'AIzaSyAviH-KwdIOrHwT0tqQRR2YvcOk7MqD1S0':0, 'AIzaSyCGys4yeF2HwnNikMwiGxPHr68iaXscjF4':0, 'AIzaSyA5fWLW2FJCfjn7EUXS4IVm-lt3GtllKOw':0,
             'AIzaSyBsDoHtEtWlPn8XArrCjgN92n1szBe9zr0':0}

# mongo_server = {"host": "124.207.209.57", "port": 27010}