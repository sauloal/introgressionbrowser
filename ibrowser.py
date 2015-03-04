#!/usr/bin/python
"""
Web server for the Introgression browser.
Reads config.py to setup.
Uses vcf_walk as shared library and either vcf_walk_ram or vcf_walk_sql as database.


#to add users in the command line run:
#ibrowser adduser <USERNAME> <PASSWORD>


NFO FILE:
title=
custom_order=
custom_order=
custom_order=

CUSTOM ORDER FILE:
#ROWNUM=0 (-1 or nothing to ignore)
#COLNUM=1 (-1 or nothing to ignore)
#NAME=
#CHROMOSOME= (__global__ or empty for all chromosomes)
row order\tcol order\n
"""
#TODO
#https://exploreflask.com/users.html

import sys

print "IMPORTING BEHAVIOUR"
from behaviour import *



def init( args ):
    load_config( args )

def start():
    if app.config['HAS_LOGIN']:
        print "SSL ENABLED: access by https://127.0.0.1:%d" % app.config["SERVER_PORT"       ]

        app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0', ssl_context=(app.config["SSL_CERT"], app.config["SSL_KEY"]))
        #app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0', ssl_context=app.config["SSL_CONTEXT"])
    else:
        print "SSL DISABLED: access by http://127.0.0.1:%d" % app.config["SERVER_PORT"       ]
        app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0')


if __name__ == '__main__':
    init(sys.argv[1:])

    if len(sys.argv) > 2:
        run_action(sys.argv[2:])

    else:
        if app.config['HAS_LOGIN'         ]:
            add_default_users()

        load_database()
        start()

else:
    load_database()
    application = app
