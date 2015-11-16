import sys
import os
import cPickle
import gzip
import zlib
import base64

def getSuffix(colnamessh):
    minname = min([ len(x) for x in colnamessh])
    #print "minname", minname

    for l in xrange(minname, 1, -1):
        #print " l", l
        shorts = set()

        for n in colnamessh:
            shorts.add(n[len(n)-l:])

        #print " shorts", shorts
        if len(shorts) == 1:
            return shorts.pop()

        if len(shorts) == 0:
            return None

    return None

def compress(data, compresslevel=9):
    """
    Compress and b64encode
    """
    res = zlib.compress(data, compresslevel)
    res = base64.b64encode(res).replace("\n", '')
    return res

def decompress(data):
    """
    b64decode  and uncompress
    """
    res = base64.b64decode(data)
    res = zlib.decompress(res)
    return res

def dumps(fn, data, compresslevel=9):
    """
    Dump pickle in a compressed file
    """
    db_fhd    = gzip.open( fn+'.tmp', 'wb', compresslevel )
    cPickle.dump( data, db_fhd, cPickle.HIGHEST_PROTOCOL )
    db_fhd.close()
    os.rename(fn+'.tmp', fn)

def loads(fn, sdata=None):
    """
    Load compressed pickle
    """
    print "  loading", fn
    fhd  = gzip.open(fn, 'rb')
    print "  loading", fn, 'opened'
    data = cPickle.load( fhd )
    print "  loading", fn, 'loaded'
    fhd.close()
    #print "  loading", fn, 'closed', len(data), data.keys()
    if sdata is not None:
        print "  saving", fn,"in shared memory"
        sdata[fn] = data
        print "  saved", fn,"in shared memory"
    else:
        print "  returning", fn
        return data
    print "  returning", fn
    return 0

def dumps_data(data, compresslevel=9):
    """
    Returns pickled and compressed data
    """
    pdata = cPickle.dumps( data, cPickle.HIGHEST_PROTOCOL )
    cdata = zlib.compress( pdata, compresslevel )
    return cdata

def loads_data(cdata):
    """
    Decompress and unpickle data
    """
    pdata = zlib.decompress( cdata )
    data  = cPickle.loads( pdata )
    return data



def checkfile(infile):
    """
    Checks whether file exists
    """
    if infile is None:
        print "no input file given"
        sys.exit(1)

    if isinstance(infile, list):
        if len(infile) > 1:
            print "more than one file given"
            print infile
            sys.exit(1)

        infile = infile[0]

    if not os.path.exists(infile):
        print "input file %s does not exists" % infile
        sys.exit(1)

    if os.path.isdir( infile ):
        print "input file %s is a folder" % infile
        sys.exit(1)
    
    return infile


def openfile(infile, method, compresslevel=1):
    """
    Open file handling if compressed or not
    """
    fhd = None

    if infile.endswith('.gz'):
        fhd = gzip.open(infile, method+'b', compresslevel)

    else:
        fhd = open(infile, method)

    return fhd


def openvcffile(infile, method, **kwargs):
    """
    Open vcf file checking for extension and handling compression
    """

    fhd = openfile(infile, method, **kwargs)

    if infile.endswith('.vcf.gz'):
        pass

    elif infile.endswith('.vcf'):
        pass

    else:
        print "unknown file type"
        sys.exit(1)
    
    return fhd


def getFh(infile):
    """
    Returns file handler. Handles compression given the .gz extension
    """
    ifh = None
    if infile.endswith('gz'):
        ifh = gzip.open(infile, 'rb')
    else:
        ifh = open(infile, 'r')
    return ifh


def makeIndexFile( indexFile, infile ):
    """
    Indexes the start position of each chromosome and creates a index file
    """
    print "creating index"
    chroms  = {}

    ifh     = getFh(infile)

    for line in iter(ifh.readline, ''):
        if line[0] == "#":
            continue

        line = line.strip()
        if len(line) == 0: continue

        chro = line.split("\t")[0]

        if chro not in chroms:
            beginPos     = ifh.tell() - len(line)
            chroms[chro] = beginPos
            print "creating index :: chrom %s curr pos %15d begin pos %15d" % (chro, ifh.tell(), beginPos)

    for chro in sorted(chroms):
        pos = chroms[chro]
        ifh.seek(pos)
        print ifh.readline(),

    ifh.close()

    with open(indexFile, 'w') as ofh:
        for chrom in sorted(chroms):
            ofh.write( "%s\t%d\n" % ( chrom, chroms[chrom] ) )


def readIndex(indexFile):
    """
    Reads VCF index file
    """
    print "reading index",indexFile
    chroms = {}
    with open(indexFile, 'r') as ifh:
        for line in ifh:
            line = line.strip()
            if len(line) == 0: continue
            print "INDEX LINE", line,
            chrom, pos = line.strip().split("\t")
            pos = int(pos)
            if pos > 0:
                pos -= 1
            chroms[chrom] = pos
            print "reading index :: chrom %s pos %15d" % ( chrom, pos )
    return chroms

import multiprocessing
from multiprocessing import Pool, Queue, Manager
import time


def parallel_loads(infiles, ddata=None):
    data = {}
    for infile in infiles:
        data[ infile ] = [ (infile,), {} ]

    parallel( loads, data )

    for k in data:
        if ddata is not None:
            ddata[k] = data[k][2]
        else:
            data[k]  = data[k][2]

    if ddata is not None:
        return
    else:
        return data

def parallel(func, data):
    m     = Manager()
    d     = m.dict()
    p     = Pool(len(data))
    procs = []

    for idd in data:
        args, kwargs = data[ idd ]
        kwargs[ 'sdata' ] = d
        res = [ idd, p.apply_async( func, args, kwargs ) ]
        procs.append( res )
    p.close()


    done = []
    while True:
        sys.stdout.write( 'w' )
        sys.stdout.flush()
        for res in procs:
            idd   = res[0]
            proc  = res[1]
            if proc.ready() and idd not in done:
                if not proc.successful():
                    proc.get()
                print
                print "  getting sync data from idd", idd, (len(done)+1),'/',len(data)

                proc.wait()
                print "  getting sync data from idd %s LOADING"  % idd, proc.ready(), proc.successful()
                #db = proc.get()
                done.append( idd )
            else:
                time.sleep(5)

        if len(done) == len(data):
            print "  finished looping"
            break

    print "  leaving"

    #print d
    #pp( d )
    #for k in d.keys():
        #print k
        #for v in d[k]:
            #print v
    #p.join()

    for idd in done:
        print idd
        print "  getting sync data from idd %s SAVING"   % idd, d.keys()
        while True:
            if idd in d:
                break
            print d.keys()
            #sys.stdout.write( 's' )
            #sys.stdout.flush()
            time.sleep(10)


    for idd in done:
        print idd
        print "  getting sync data from idd %s PRESENT"  % idd, d.keys()
        data[ idd ].append( d[ idd ] )
        print "  getting sync data from idd %s DELETING" % idd
        #del d[ idd ]
        del data[idd][1]['sdata']
        print "  getting sync data from idd %s DONE"     % idd
    p.join()
