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
import subprocess


print "importing SSL"
#import ssl
from OpenSSL import crypto, SSL

SSL_KEY_LENGTH = 2048

print "IMPORTING BEHAVIOUR"
from behaviour import *



def init( args ):
    load_config( args )

def start():
    if app.config['HAS_LOGIN']:
        ssl_cert, ssl_key = create_self_signed_cert(cert_dir=dir_path, cert_name="server")
        print "SSL ENABLED: access by https://127.0.0.1:%d" % app.config["SERVER_PORT"       ]
        app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0', ssl_context=(ssl_cert, ssl_key))
    else:
        print "SSL DISABLED: access by http://127.0.0.1:%d" % app.config["SERVER_PORT"       ]
        app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0')

def create_self_signed_cert(cert_dir=".", cert_name="server"):
    print "generating self signed certificate"
    C_F = os.path.join(os.path.abspath(cert_dir), cert_name + ".crt")
    K_F = os.path.join(os.path.abspath(cert_dir), cert_name + ".key")

    if not os.path.exists(C_F) or not os.path.exists(K_F):
        print " certificates do not exists. creating"
        cmdline = "openssl req  -nodes -new -newkey rsa:%(key_length)d -x509 -batch -days 365 -extensions v3_req -keyout %(key_file)s -out %(cert_file)s" % {"key_length": SSL_KEY_LENGTH, "key_file": K_F, "cert_file": C_F }
        print "  running:", cmdline
        os.system(cmdline)
    else:
        print " certificates exists. skipping"

    return (C_F, K_F)






    #if os.path.exists( ssl_cert ) and os.path.exists( ssl_key ) :
    #    print "SSL ENABLED: access by https://127.0.0.1:%d" % app.config["SERVER_PORT"       ]
    #    app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0', ssl_context=(ssl_cert, ssl_key))
    #
    #else:
    #    print "SSL DISABLED: access by http://127.0.0.1:%d" % app.config["SERVER_PORT"       ]
    #    app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0')


    #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context = ssl.create_default_context( ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    #context.load_cert_chain('yourserver.crt', 'yourserver.key')
    #app.run(port=app.config["SERVER_PORT"       ], host='0.0.0.0', ssl_context=context)

    #http://kracekumar.com/post/54437887454/ssl-for-flask-local-development
    #Generate a private key
    #openssl genrsa -des3 -out server.key 1024
    #
    #Generate a CSR
    #openssl req -new -key server.key -out server.csr
    #
    #Remove Passphrase from key
    #cp server.key server.key.org
    #openssl rsa -in server.key.org -out server.key
    #
    #Generate self signed certificate
    #openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    #
    #
    #openssl req  -nodes -new -newkey rsa:2048 -x509 -batch -days 365 -keyout server.key -out server.crt

    #ssl_cert = os.path.join(dir_path, 'server.crt')
    #ssl_key  = os.path.join(dir_path, 'server.key')


#http://www.linux.org/threads/creating-a-self-signed-certificate-with-python.4591/
#def create_self_signed_cert(cert_dir=".", cert_name="server"):
#    print "generating self signed certificate"
#    C_F = os.path.join(os.path.abspath(cert_dir), cert_name + ".crt")
#    K_F = os.path.join(os.path.abspath(cert_dir), cert_name + ".key")
#
#    if not os.path.exists(C_F) or not os.path.exists(K_F):
#        print " certificates do not exists. creating"
#        # create a key pair
#        k = crypto.PKey()
#        k.generate_key(crypto.TYPE_RSA, SSL_KEY_LENGTH)
#        # create a self-signed cert
#        cert = crypto.X509()
#        cert.set_pubkey(k)
#        cert.sign(k, 'sha1')
#
#        print " saving certificates"
#        open(C_F, "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
#        open(K_F, "wt").write(crypto.dump_privatekey( crypto.FILETYPE_PEM, k   ))
#    return (C_F, K_F)

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
