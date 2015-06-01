#!/usr/bin/python
import os
import sys
import time
import multiprocessing
from pprint import pprint as pp
from multiprocessing import Pool, Queue, Manager

from pprint import pprint as pp
sys.path.insert(0, os.path.abspath( os.path.join( os.path.dirname( os.path.realpath(__file__) ), '..' ) ) )
print sys.path[0]
from filemanager import loads, parallel, parallel_loads



def main(args):
    print "main", args

    infiles = args
    infiles.sort()

    for infile in infiles:
        if not os.path.exists( infile ):
            print "infile", infile, 'does not exists'
            sys.exit(1)

    data = {}
    parallel_loads( infiles, ddata=data )

    for k in data:
        print k, len(data[k])
        pp( data[k] )


def main4(args):
    print "main", args

    infiles = args
    infiles.sort()

    for infile in infiles:
        if not os.path.exists( infile ):
            print "infile", infile, 'does not exists'
            sys.exit(1)

    data = parallel_loads( infiles )

    for k in data:
        print k, len(data[k])


def main3(args):
    print "main", args

    infiles = args
    infiles.sort()

    for infile in infiles:
        if not os.path.exists( infile ):
            print "infile", infile, 'does not exists'
            sys.exit(1)

    data = {}
    for infile in infiles:
        data[ infile ] = [ (infile,), {} ]

    parallel( loads, data )

    for k in data:
        print k, data[k][0], data[k][1], len(data[k][2])


def main2(args):
    print "main", args

    infiles = args
    infiles.sort()

    for infile in infiles:
        if not os.path.exists( infile ):
            print "infile", infile, 'does not exists'
            sys.exit(1)

    m     = Manager()
    d     = m.dict()
    p     = Pool(len(infiles))
    procs = []

    for infile in infiles:
        res = [ infile, p.apply_async( loads, (infile,), {'sdata': d} ) ]
        procs.append( res )
    p.close()


    data = []
    done = []
    while True:
        sys.stdout.write( 'w' )
        sys.stdout.flush()
        for res in procs:
            fn    = res[0]
            proc  = res[1]
            if proc.ready() and fn not in done:
                print
                print "  getting sync data from file", fn
                done.append( fn )

                proc.wait()
                print "  getting sync data from file %s LOADING" % fn, proc.ready(), proc.successful()
                #db = proc.get()
                print "  getting sync data from file %s SAVING"  % fn
                #data.append( db )
                print "  getting sync data from file %s DONE"    % fn
            else:
                time.sleep(5)

        if len(done) == len(infiles):
            print "  finished looping"
            break

    print "  leaving"

    #print d
    #pp( d )
    for k in d.keys():
        print k
        for v in d[k]:
            print v
    p.join()


if __name__ == '__main__':
    main(sys.argv[1:])
