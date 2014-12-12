import os
bin_path = os.path.abspath( __file__ )
dir_path = os.path.dirname( bin_path )

#decide whether to have user control or not
hasLogin    = False

#add credentials
credentials = {
	'xxx'   : 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy',
}


#to create passwords, in the command line, run python in interactive mode and type:
#import hashlib
#hashlib.sha256("<LOGIN><PASSWORD>").hexdigest()



#define port. cluster server and svg server will use this port +1 and +2, respectively
SERVER_PORT               = 10000


#define if uses SQL or RAM database
USE_SQL                   = True


#define cookie security key. if not changed anyone who knows this code can login
SECRET_KEY                = "development key"
SECRET_KEY                = '91\xba\xf0+R\xbd\x14_\xcb\xa9\xd9\xd7\xdb\xb4\xbcTK \x9d(PL\xb0'

#to create a new security key, in the command line, run python in interactive mode and type:
#import os
#os.urandom(24)
#'\xe1:\xbf\xc2\xaa\x0b\x04\xb8\xac\xc1\xff;Z-W\xfcRE\xadY"K\xa1v'


#define available databases
#DATABASES = [
#    [ 'Solanum 60 RIL Moneymaker vs pimpinellifolium'                    , 'data/walk_out_ril'       ],
#    [ 'Solanum 60 RIL Moneymaker vs pimpinellifolium w parents'          , 'data/walk_ril_parent'    ],
#    [ 'Solanum 60 RIL Moneymaker vs pimpinellifolium w parents no gaps 1', 'data/walk_ril_3_nogaps'  ],
#    [ 'Solanum 60 RIL Moneymaker vs pimpinellifolium w parents no gaps 3', 'data/walk_ril_4_nogaps_3'],
#    [ 'Solanum 84 Genes'                                                 , 'data/walk_out_genes'     ],
#    [ 'Solanum 84 50 Kbp window'                                         , 'data/walk_out_50k'       ],
#    [ 'Solanum 84 10 Kbp window'                                         , 'data/walk_out_10k'       ]
#]

INFOLDER                  = os.path.join( dir_path, "data" )

DEBUG                     = False
MAX_NUMBER_OF_COLUMNS     = 300
MAX_CONTENT_LENGTH        = 128 * 1024 * 1024
