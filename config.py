import os
bin_path = os.path.abspath( __file__ )
dir_path = os.path.dirname( bin_path )

#decide whether to have user control or not
hasLogin    = True

#add credentials
#
#default credentials. Admin is compulsory
#login: admin pass: admin
#
#to add users in the command line run:
#ibrowser adduser <USERNAME> <PASSWORD>
#
#to create default users in the command line, run:
#ibrowser genuser <USERNAME> <PASSWORD>
# then, copy the information in credentials
# eg: ./ibrowser.py genuser admin admin
#     username admin pass 5fa21eab20861e9f01f0f577bee378cf31b5b933090df492dbf0b05870096459cd2cb270ce0ca25ddb2ebfed7828a7b1 salt 6086e5c03e6e7cdb0899419b5653b485903d50d5cf14cd346e2036c510884df028c257eecc543908c35d83e6c6858c3f
#password and salt will change with each run
credentials = {
        #USERNAME  PASSWORD                                                                                            SALT
        'admin': ( '7757602374ab397a75f728d6dad7516fe464fc2d6a39135febb2863a412b0a1b1b513a20e6c3e9f97554602bba9aa3d3', 'f9b74f3d07e2879449e5541372e47f17aeb724017dbe00426a8d54a6a330c1ad0abfb898a0eec98ad3e66ae027609795' )
}

#to add users in the command line run:
#ibrowser adduser <USERNAME> <PASSWORD>
#to create default users in the command line, run:
#ibrowser genuser <USERNAME> <PASSWORD>
# then, copy the information in credentials


#define port to server webpage
SERVER_PORT               = 10000


#define if uses SQL or RAM database
USE_SQL                   = True


#CHANGE ME
#define cookie security key. if not changed anyone who knows this code can login
SECRET_KEY                = '91\xba\xf0+R\xbd\x14_\xcb\xa9\xd9\xd7\xdb\xb4\xbcTK \x9d(PL\xb0'

#to create a new security key, in the command line, run python in interactive mode and type:
#import os
#os.urandom(24)
#'91\xba\xf0+R\xbd\x14_\xcb\xa9\xd9\xd7\xdb\xb4\xbcTK \x9d(PL\xb0'
#copy the output text in config.py


INFOLDER                  = os.path.join( dir_path, "data" )

DEBUG                     = False
MAX_NUMBER_OF_COLUMNS     = 300
MAX_CONTENT_LENGTH        = 128 * 1024 * 1024
RSA_KEY_SIZE              = 2048
