#decide whether to have user control or not
hasLogin                  = False

#define port to server webpage
SERVER_PORT               = 10000

#define if uses SQL or RAM database
USE_SQL                   = True

#define data folder
INFOLDER                  = os.path.join( dir_path, "data" )

# pages which can be seen without login
librepaths = [
    '/api',
    '/favicon.ico'
]


DEBUG                     = False
MAX_CONTENT_LENGTH        = 128 * 1024 * 1024

