# -*- coding: utf-8 -*-

server = {'host': 'localhost',
          'port': 8080,
          'debug': True,
          'reloader': True}

git = {'enabled': False,
       'author': 'Spoonbill <spoonbill@nasa.com>'}

pelican = {'content_path': '../content',
           'file_extension': '.md',
           'deploy': False,
           'command': 'pelican content -s publishconf.py -t'}

auth = {'enabled': True,
        'username': 'username',
        'password': 'password'}
