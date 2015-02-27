
import os
import sys
import io
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher    import PKCS1_v1_5

librepoints = [
    'login',
    'logout',
    'getsalt',
]
IDEBUG                    = False
USE_SQL                   = True
MAX_CONTENT_LENGTH        = 128*1024*1024



print "IMPORTING FUNCTIONS"
from routes import *


bin_path = os.path.abspath( __file__ )
dir_path = os.path.dirname( bin_path )
#print "dir_path ", dir_path
#sys.path.insert(0, dir_path )
#sys.path.insert(0, os.path.join(dir_path, "venv/lib/python2.7/site-packages") )




"""
Decides the interface whether RAM or SQL
"""
print "importing vcf_walk"
sys.path.insert( 0, os.path.join( dir_path, 'vcfmerger' ) )

if USE_SQL:
    import vcf_walk_sql as interface
else:
    import vcf_walk_ram as interface




#TODO:
#      ADD OPTION FOR MAX_NUMBER_OF_COLUMNS




#    complete_path = os.path.join(root_dir(), "static", "login.html")
#    mimetype      = "text/html"
#    content       = get_file(complete_path)
#    return Response(content, mimetype=mimetype)


def add_default_users():
    if not check_user_exists("admin"):
        print "admin user does not exists. CREATING admin user with default password admin"

        noonce = gen_noonce()
        pwd    = generate_password_hash("admin" + "admin" + noonce)

        try:
            add_user("admin", pwd, noonce)

        except:
            print "failed to add default user ADMIN. cannont continue"
            raise


class encryption(object):
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.keylen_file = os.path.join( data_folder, "config.keylen" )

        if not os.path.exists( self.keylen_file ):
            print "keylen file %s does not exists. CREATING with default %d" % ( self.keylen_file, 2048 )
            open(self.keylen_file, 'w').write(str(2048))

        self.RSA_KEY_SIZE              = int(open(self.keylen_file     , 'r' ).read())
        print "RSA_KEY_SIZE", self.RSA_KEY_SIZE

        self.rsa_private_key_file_name = os.path.join( "templates", 'rsa_%d_priv.pem' % self.RSA_KEY_SIZE )
        self.rsa_public_key_file_name  = os.path.join( "templates", 'rsa_%d_pub.pem'  % self.RSA_KEY_SIZE )

        if ( not os.path.exists( self.rsa_private_key_file_name ) ) or ( not os.path.exists( self.rsa_public_key_file_name ) ):
            if ( os.path.exists( self.rsa_private_key_file_name ) ):
                os.remove(self.rsa_private_key_file_name)

            if ( os.path.exists( self.rsa_public_key_file_name ) ):
                os.remove(self.rsa_public_key_file_name)

            print "PUBLIC KEY %s OR PRIVATE KEY %s DOES NOT EXISTS. CREATING" % (self.rsa_private_key_file_name, self.rsa_public_key_file_name)
            #(pubkey, privkey) = rsa.newkeys(RSA_KEY_SIZE, accurate=True, poolsize=1)
            #open(rsa_public_key_file_name , 'w').write( pubkey.save_pkcs1()  )
            #open(rsa_private_key_file_name, 'w').write( privkey.save_pkcs1() )


            self.privkey = RSA.generate(self.RSA_KEY_SIZE)
            self.pubkey  = self.privkey.publickey()

            open(self.rsa_public_key_file_name , 'w').write( self.pubkey.exportKey('PEM')  )
            open(self.rsa_private_key_file_name, 'w').write( self.privkey.exportKey('PEM') )

            print "saved public and private keys"


        self.rsa_private_key      = RSA.importKey(open(self.rsa_private_key_file_name, 'r').read())
        self.rsa_public_key       = RSA.importKey(open(self.rsa_public_key_file_name , 'r').read())

        self.enc_cipher           = PKCS1_v1_5.new(self.rsa_public_key )
        self.dec_cipher           = PKCS1_v1_5.new(self.rsa_private_key)

        print "encryption test"
        message     = "test"
        encmess     = self.encrypter(message)
        decmess     = self.decrypter(encmess)

        print "message ", message
        print "encmess ", encmess
        print "decmess ", decmess

        assert message == decmess, "decrypted message %s does not match original message %s" % (decmess, message)


        #rsa_private_key      = rsa.PrivateKey.load_pkcs1( open(rsa_private_key_file_name, 'r').read() )
        #try:
        #    rsa_public_key       = rsa.PublicKey.load_pkcs1(  open(rsa_public_key_file_name , 'r').read() )
        #except:
        #    try:
        #        rsa_public_key       = rsa.PublicKey.load_pkcs1_openssl_pem( open(rsa_public_key_file_name , 'r').read() )
        #    except:
        #        raise

        #def encrypter(message):
        #    return base64.b64encode( rsa.encrypt(message, rsa_public_key ) )
        #
        #def decrypter(message):
        #    return rsa.decrypt(base64.b64decode( message ), rsa_private_key)

    def encrypter(self, message):
        ciphertext = self.enc_cipher.encrypt(message)
        return base64.b64encode( ciphertext )

    def decrypter(self, message):
        sentinel   = None
        ciphertext = base64.b64decode( message )
        dec        = self.dec_cipher.decrypt(ciphertext, sentinel)
        if dec is None:
            print "error decrypting message"
            sys.exit(1)
        return dec




##VARIABLES
#DEBUG                     = True
#MAX_NUMBER_OF_COLUMNS     = 300
#SERVER_PORT               = 10000
#MAX_CONTENT_LENGTH        = 128 * 1024 * 1024
#USE_SQL                   = True
#INFOLDER                  = None
#
#
#hasLogin                  = False
#SECRET_KEY                = None
#USER_DATABASE_FILE        = None
#SECRET_FILE               = None
#ENCRYPTION_INST           = None


def load_config( args ):
    if len(args) == 0:
        print "no config file or command given"
        sys.exit(1)


    global SERVER_PORT
    global USE_SQL
    global SECRET_FILE
    global SECRET_KEY
    global ENCRYPTION_INST
    global USER_DATABASE_FILE

    INFOLDER = os.path.abspath( args[0] )
    if not os.path.exists( INFOLDER ):
        print "data folder %s does not exists" % INFOLDER
        sys.exit(1)

    if not os.path.isdir( INFOLDER ):
        print "data folder %s is not a folder" % INFOLDER
        sys.exit(1)

    config_file      = os.path.join( INFOLDER, 'config.py'     )

    if not os.path.exists( config_file ):
        print "config file %s does not exists" % config_file
        sys.exit( 1 )


    print "loading config", config_file
    lcls = {}
    execfile(config_file, globals(), lcls)
    for lcl in lcls:
        globals()[lcl] = lcls[lcl]


    SECRET_FILE        = os.path.join( INFOLDER, "config.secret" )

    if not os.path.exists( SECRET_FILE ):
        print "secret file %s does not exists. CREATING" % SECRET_FILE
        secret = os.urandom(24)
        open(SECRET_FILE, 'wb').write(secret)

    SECRET_KEY                =     open(SECRET_FILE     , 'rb').read().strip()
    print "SECRET KEY  ", repr(SECRET_KEY)

    app.before_first_request(init_db)

    app.secret_key                   = SECRET_KEY
    app.debug                        = DEBUG
    app.config["getManager"        ] = getManager
    app.config['HAS_LOGIN'         ] = hasLogin
    app.config['LIBRE_PATHS'       ] = librepaths
    app.config['LIBRE_POINTS'      ] = librepoints
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config["INFOLDER"          ] = INFOLDER
    app.config["IDEBUG"            ] = IDEBUG
    app.config["INTERFACE"         ] = interface
    app.config["SERVER_PORT"       ] = SERVER_PORT

    interface.DEBUG = IDEBUG

    if hasLogin:
        print "LOGIN ENABLED"
        print "INITIALIZING DB"
        USER_DATABASE_FILE = os.path.join( INFOLDER, 'users.sqlite' )


        app.config['DATABASE_FILE'          ] = USER_DATABASE_FILE
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
        app.config['SQLALCHEMY_ECHO'        ] = False

        if not os.path.exists(USER_DATABASE_FILE):
            user_db.drop_all()
            user_db.create_all()



        print "INITIALIZING ENCRYPTION"
        app.config["ENCRYPTION_INST"] = encryption( INFOLDER )

        print "ENCRYPTION KEY SIZE", app.config["ENCRYPTION_INST"].RSA_KEY_SIZE
        #jsonpickle.set_preferred_backend('simplejson')
        #jsonpickle.set_encoder_options('simplejson', ensure_ascii=True, sort_keys=True, indent=1)

        app.jinja_env.globals['encbitsize'            ] = str( app.config["ENCRYPTION_INST"].RSA_KEY_SIZE )

        #http://stackoverflow.com/questions/9767585/insert-static-files-literally-into-jinja-templates-without-parsing-them
        def include_file(name):
            return Markup(app.jinja_loader.get_source(app.jinja_env, name)[0])

        def include_file_multiline(name):
            lines     = app.jinja_loader.get_source(app.jinja_env, name)[0]
            #lines.replace("RSA PUBLIC KEY", "PUBLIC KEY")
            lines     = lines.split("\n")
            lines     = [ "'" + l + "\\n' +" for l in lines ]
            lines[-1] = lines[-1].strip(" +")
            return Markup("\n".join( lines ))

        app.jinja_env.globals['include_file'          ] = include_file
        app.jinja_env.globals['include_file_multiline'] = include_file_multiline


def run_action(args):
    actions = ("adduser", "deluser", "listusers", "clean", "init")

    try:
        action   = args[0]
        if action in ["adduser", "deluser"]:
            username = args[1]
            if action in ["adduser"]:
                password = args[2]

    except:
        print "not enought arguments"
        sys.exit(1)



    if action not in actions:
        print "invalid action %s" % action
        sys.exit(1)



    if ( action not in ("init") ) and ( not hasLogin ):
        print "no login, no add/gen user"
        sys.exit(1)


    if   action == "init":
        print "inited"

    if action == "clean":
        print "cleaning"
        files_to_del = [ SECRET_FILE, USER_DATABASE_FILE ]

        if hasLogin:
            if ENCRYPTION_INST is not None:
                files_to_del.extend( [ ENCRYPTION_INST.keylen_file, ENCRYPTION_INST.rsa_private_key_file_name, ENCRYPTION_INST.rsa_public_key_file_name ] )

        for filename in files_to_del:
            if filename is None:
                continue

            print " deleting %s" % filename,
            if os.path.exists( filename ):
                os.remove( filename )
                print "... delete ...",
            else:
                print "... skip ...",
            print "DONE"

    elif action == "adduser":
        noonce = gen_noonce()
        pwd    = generate_password_hash(username + password + noonce)

        if check_user_exists(username):
            print "user %s already exists" % username
            sys.exit(1)

        try:
            add_user(username, pwd, noonce)

        except KeyError:
            print "user %s already exists" % username
            sys.exit(1)

    elif action == "deluser":
        print "deleting user %s" % username
        if check_user_exists(username):
            del_user(username)

        else:
            print "user %s does not exists" % username
            sys.exit(1)

    elif action == "listusers":
        print "listing users"
        print "\n".join(get_users())




