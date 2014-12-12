#!/usr/bin/python
import os
import sys
import argparse
import fnmatch
import array
import copy
from multiprocessing import Pool
import tempfile
import signal

sys.path.insert(0, '.')
from filemanager import dumps, getSuffix
import newick_to_png

#rm test.pickle.gz; ./cluster.py -o test.pickle.gz ../data/src/RIL/walk_out_ril/SL2.40ch12/list.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.SL2.40ch12.000000*.matrix
#rm test.pickle.gz; ./cluster.py -o test.pickle.gz -d ../data/src/RIL/walk_out_ril/SL2.40ch12


ROWS    = 0
COLS    = 1
TMP_DIR = '/var/run/shm'


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def main(args):
    parser = argparse.ArgumentParser(description='Create makefile to convert files.')

    parser.add_argument('-o' , '--out'   , '--output'   , dest='output'   , default=None     , nargs='?'               ,                      type=str,  help='output file')
    parser.add_argument('-d' , '--dir'   , '--indir'    , dest='indir'    , default=None     , nargs='?'               ,                      type=str,  help='input dir. alternative to giving file names')
    parser.add_argument('-t' , '--thr'   , '--threads'  , dest='threads'  , default=2        , nargs='?'               ,                      type=int,  help='[optional] number of threads. [default: 5]')
    parser.add_argument('-e' , '--ext'   , '--extension', dest='extension', default='.matrix', nargs='?'               ,                      type=str,  help='[optional] extension to search. [default: .matrix]')

    parser.add_argument('-p' , '--nopng' ,                dest='dopng'                       ,                          action='store_false',            help='do not export png')
    parser.add_argument('-s' , '--nosvg' ,                dest='dosvg'                       ,                          action='store_false',            help='do not export svg')
    parser.add_argument('-n' , '--notree',                dest='dotree'                      ,                          action='store_false',            help='do not export tree. precludes no png and no svg')
    parser.add_argument('-r' , '--norows',                dest='dorows'                      ,                          action='store_false',            help='do not export rows')
    parser.add_argument('-c' , '--nocols',                dest='docols'                      ,                          action='store_false',            help='do not export cols')

    parser.add_argument('infiles'                                                            , nargs=argparse.REMAINDER,                                 help='[optional] input files')

    options  = parser.parse_args(args)

    outfile  = options.output
    indir    = options.indir
    threads  = options.threads
    ext      = options.extension
    infiles  = options.infiles
    dopng    = options.dopng
    dosvg    = options.dosvg
    dotree   = options.dotree
    dorows   = options.dorows
    docols   = options.docols



    numfiles = len(infiles)

    print options


    if numfiles == 0:
        if not indir:
            print "either filenames or input folder must be given"
            sys.exit(1)

        if not os.path.exists(indir):
            print "input folder %s does not exists" % indir
            sys.exit(1)

        infiles = []
        for root, dirnames, filenames in os.walk(indir):
            for filename in fnmatch.filter(filenames, '*'+ext):
                infiles.append(os.path.join(root, filename))

        numfiles = len(infiles)
        if numfiles == 0:
            print "no input files found having extension %s in folder %s" % (ext. indir)
            sys.exit(1)

        else:
            print "found %d files" % numfiles


    if outfile is None:
        print "no output file defined"
        sys.exit(1)


    for infile in infiles:
        if not os.path.exists(infile):
            print "infile %s does not exists" % infile
            sys.exit(1)


    if os.path.exists( outfile ):
        print "output file %s already exists. not overwriting. quitting" % outfile
        #sys.exit(1)
        os.remove( outfile )
        pass


    #sys.exit(0)

    colnames = infiles
    #print "colnames       ", colnames
    colnamesprf = os.path.commonprefix(colnames)
    #print "colnames prefix", colnamesprf
    colnamessh  = [ x.replace(colnamesprf, '') for x in colnames ]
    #print "colnames short1", colnamessh
    colnamessuf = getSuffix(colnamessh)
    #print "colnames suffix", colnamessuf
    colnamesshs = colnamessh
    if colnamessuf:
        colnamesshs = [ x[:len(x)-len(colnamessuf)] for x in colnamessh ]
        #print "colnames short2", colnamesshs



    data     = [[], []]
    filenum  = 0
    rnum     = 0
    numrowsG = 0
    rownames = []
    pool1    = Pool(threads, init_worker)
    results1 = []

    sys.setrecursionlimit(1500 + numfiles)

    for infile in infiles:
        rnum += 1
        print "ADDING %d/%d %s" % ( rnum, numfiles, infile )

        #numRows, rownamesl, matrix = read_file(infile)
        p = [ rnum, pool1.apply_async(read_file, (infile,) ) ]
        results1.append( p )
    pool1.close()

    print "MERGING FILES"
    try:
        for filei, r in results1:
            filenum    += 1
            r.wait()
            res  = r.get()
            numRows, rownamesl, matrix = res
            #print "got file", filei

            if len(rownamesl) != numRows:
                print "number of rows mismatches"
                sys.exit(1)

            if numrowsG == 0:
                numrowsG = numRows

            if numrowsG != numRows:
                print "number of species not equal:", numrowsG, numRows
                sys.exit(1)

            if len(rownames) == 0:
                rownames = rownamesl

            if len(set(rownames) ^ set(rownamesl)) != 0 :
                print "row names", rownames, "different from", rownamesl, 'differences', set(rownames) ^ set(rownamesl)
                sys.exit(1)

            if filenum == 1:
                print "ALLOCATING MEMORY FOR ROWS"
                for REF in xrange(numrowsG):
                    data[ROWS].append( [] )
                    data[ROWS][REF] = []
                    for FIL in xrange(numfiles):
                        data[ROWS][REF].append([])
                        data[ROWS][REF][FIL] = array.array('d', xrange(numrowsG))
                        #for cn in xrange(numrowsG):
                            #data[ROWS][REF][FIL].append( -1.0 )

                print "ALLOCATING MEMORY FOR COLUMNS"
                for REF in xrange(numrowsG):
                    data[COLS].append( [] )
                    data[COLS][REF] = []
                    for cn in xrange(numrowsG):
                        data[COLS][REF].append( [] )
                        data[COLS][REF][cn] = array.array('d', xrange(numfiles))
                        #for FIL in xrange(numfiles):
                            #data[COLS][REF][cn].append( -1.0 )
                print "ALLOCATING MEMORY FINISHED"

                print "RESUMING MERGING"

            sys.stdout.write('.')
            sys.stdout.flush()
            if filei % 100 == 0:
                sys.stdout.write('\n')
                sys.stdout.flush()


            for REF in xrange(numrowsG):
                rowv = matrix[REF]
                for cn in xrange(numrowsG):
                    val = rowv[cn]
                    data[ COLS ][ REF ][ cn       ][ filei - 1 ] = val
                    data[ ROWS ][ REF ][ filei -1 ][ cn        ] = val

    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating workers"
        pool1.terminate()
        pool1.join()
        sys.exit(1)

    pool1.join()
    pool1.terminate()
    print "FINISHED MERGING FILES"
    print


    print "ROW NAMES"   , numrowsG, rownames
    print "COL NAMES"   , numfiles#, colnamesshs
    print "DATA ::: SPPS  :: COLS: %4d ROWS: %4d" % ( len(data[ROWS][0]), len(data[ROWS][0][0]) )
    print "DATA ::: FILES :: COLS: %4d ROWS: %4d" % ( len(data[COLS][0]), len(data[COLS][0][0]) )
    #print data
    #sys.exit(0)

    db = {
        'rownames': rownames,
        'colnames': colnamesshs,
        'numspps' : numrowsG,
        'numfiles': numfiles,
        'clusters': [None]*numrowsG
    }

    pool2    = Pool(threads, init_worker)
    results2 = []
    for sppi in xrange(numrowsG):
        sppname = rownames[sppi]
        rows    = data[ROWS][ sppi ]
        cols    = data[COLS][ sppi ]

        print "CLUSTERING SPP: %d/%d %s" % ( sppi+1, numrowsG, sppname )
        #res        = calculate_cluster_raw( rows, cols, rowNames=rownames, colNames=colnamesshs )
        opts = {'rowNames':rownames, 'colNames':colnamesshs, 'dotree':dotree, 'dosvg':dosvg, 'dopng':dopng, 'dorows':dorows, 'docols':docols}
        p    = [ sppi, pool2.apply_async(calculate_cluster_raw, ( rows, cols ), opts) ]
        results2.append(p)
        #print res
        #print
        #db['clusters'].append( res )
    pool2.close()


    try:
        for sppi, r in results2:
            r.wait()
            res = r.get()
            print "got spp", sppi,'/',numrowsG
            print "saving res", sppi
            db[ 'clusters' ][ sppi ] = res
            print "res saved", sppi

    except KeyboardInterrupt:
        print "Caught KeyboardInterrupt, terminating workers"
        pool2.terminate()
        pool2.join()
        sys.exit(1)

    pool2.join()
    pool2.terminate()
    print

    print "saving database"
    dumps(outfile, db)
    print "database saved"


def read_file( infile ):
    matrix   = []
    rownames = []

    with open(infile, 'r') as fhd:
        linenum = 0
        numRows = 0

        for line in fhd:
            linenum += 1
            line     = line.strip()

            if len(line) == 0:
                continue
            cols = line.split()
            #print cols

            if len(cols) == 1:
                numRows = int(cols[0])
                continue

            rowname = cols[0]
            cols    = array.array('d', [ float(x) for x in cols[1:] ])

            #print rowname, cols

            rownames.append( rowname )

            matrix.append( cols )

        if linenum != numRows + 1:
            print "wrong number of files"
            sys.exit(1)

    return [ numRows, rownames, matrix ]


def calculate_cluster( rowsO, rowNames=None, colNames=None, dotree=True, dosvg=True, dopng=True, dorows=True, docols=True ):
    #colNames = table['header']['name']
    #rowNames = table['data'  ]['name']
    #rowsO    = table['data'  ]['line']
    rows     = []
    cols     = []

    for r in xrange(len(rowsO)):
        lcols = rowsO[r]
        rows.append([])

        for c in xrange(len(lcols)):
            val        = lcols[c]

            if len(cols) < c+1:
                cols.append([])

            if len(cols[c]) < r+1:
                cols[c].append([])

            cols[c][r] = val[0]
            rows[r].append( val[0] )

    return calculate_cluster_raw( cols, rows, rowNames=rowNames, colNames=colNames, dotree=dotree, dosvg=dosvg, dopng=dopng, dorows=dorows, docols=docols )


def calculate_cluster_raw( cols, rows, rowNames=None, colNames=None, dotree=True, dosvg=True, dopng=True, dorows=True, docols=True ):

    resF = {}
    for method_name, merhod_func in [ ['Chromosome Clustering', cluster_hier] ]:
        resF[ method_name ] = merhod_func( cols, rows, rowNames=rowNames, colNames=colNames, dotree=dotree, dosvg=dosvg, dopng=dopng, dorows=dorows, docols=docols )

    return resF


def cluster_hier(cols, rows, rowNames=None, colNames=None, dotree=True, dosvg=True, dopng=True, dorows=True, docols=True):
    rowsOrder, rowsSvg, rowsNewick, rowsPng = [ None, "", None, None ]
    colsOrder, colsSvg, colsNewick, colsPng = [ None, "", None, None ]

    if dorows:
        print ' clustering rows'
        #print rowNames
        #print rows
        rowsOrder, rowsSvg, rowsNewick, rowsPng = do_cluster( rows, nodeNames=rowNames, dotree=dotree, dosvg=dosvg, dopng=dopng )
        rowsOrder  = list( rowsOrder.tolist() )
        rowsNewick = str(  rowsNewick         )
        rowsSvg    = str(  rowsSvg            )

    if docols:
        print ' clustering cols'
        #print colNames
        #print cols
        colsOrder, colsSvg, colsNewick, colsPng = do_cluster( cols, nodeNames=colNames, dotree=dotree, dosvg=dosvg, dopng=dopng )
        colsOrder  = list( colsOrder.tolist() )
        colsNewick = str(  colsNewick         )
        colsSvg    = str(  colsSvg            )


    print 'finished clustering'
    resD =  {
        'cols': {
            #'colNames'   : colNames,
            #'cols'       : cols.tolist(),
            #'colsDist'   : colsDist.tolist(),
            #'colsDistSqr': colsDistSqr.tolist(),
            #'colsLinkMat': colsLinkMat.tolist(),
            'colsOrder'  : colsOrder,
            #'colsTree'   : colsTree,
            'colsNewick' : colsNewick,
            'colsSvg'    : colsSvg,
            'colsPng'    : colsPng
        },
        'rows': {
            #'rowNames'   : rowNames,
            #'rows'       : rows.tolist(),
            #'rowsDist'   : rowsDist.tolist(),
            #'rowsDistSqr': rowsDistSqr.tolist(),
            #'rowsLinkMat': rowsLinkMat.tolist(),
            'rowsOrder'  : rowsOrder,
            #'rowsTree'   : rowsTree,
            'rowsNewick' : rowsNewick,
            'rowsSvg'    : rowsSvg,
            'rowsPng'    : rowsPng
        }
    }

    return resD


def do_cluster( rows, nodeNames=None, dotree=True, dosvg=True, dopng=True ):
    print "importing numpy"
    import numpy

    print "importing scipy"
    import scipy
    import scipy.cluster.hierarchy as hier
    import scipy.spatial.distance  as dist

    print "converting to array"
    rows = numpy.array(rows)


    print "getting distribution"
    rowsDist          = dist.pdist(       rows        )
    rowsDistSqr       = dist.squareform(  rowsDist    )
    print "calculating linkage"
    rowsLinkMat       = hier.linkage(     rowsDistSqr )
    rowsOrder         = hier.leaves_list( rowsLinkMat )
    rowsSvg           = ""
    rowsNewick        = None
    rowsPng           = None
    if dotree:
        print ' clustering - creating tree'
        rowsTree, rowsSvg = mat2tree( rowsLinkMat, nodeNames=nodeNames, dosvg=dosvg )
        if rowsTree:
            print ' clustering - creating tree - newick'
            rowsNewick = rowsTree.write( format=1 )
        if dopng:
            print ' clustering - creating tree - png'
            rowsPng = newick_to_png.add_seq( rowsNewick, addcaption=False )

    print "returning"
    #print 'rows dist   ', rowsDist
    #print 'rows distsqr', rowsDistSqr
    #print 'rows linkmat', rowsLinkMat
    #print 'rows ord  ', rowsOrder
    #print 'rows tree ', rowsTree
    #print 'rows newi ', rowsNewick
    return ( rowsOrder, rowsSvg, rowsNewick, rowsPng )


def mat2tree(mat, nodeNames=None, dosvg=True):
    #http://stackoverflow.com/questions/9364609/converting-ndarray-generated-by-hcluster-into-a-newick-string-for-use-with-ete2

    import scipy.cluster.hierarchy as hier

    hasTree = False
    try:
        from ete2 import Tree
        import StringIO
        hasTree = True
    except:
        pass


    T         = hier.to_tree( mat )
    root      = Tree()
    root.dist = 0
    root.name = 'root'
    item2node = {T: root}
    to_visit  = [T]

    while to_visit:
        node = to_visit.pop()
        cl_dist = node.dist / 2.0

        for ch_node in [node.left, node.right]:

            if ch_node:
                ch                 = Tree()
                ch.dist            = cl_dist
                ch.name            = str(ch_node.id)

                if nodeNames:
                    if ch_node.id < len(nodeNames):
                        ch.name    = nodeNames[ ch_node.id ]

                item2node[ch_node] = ch
                item2node[node   ].add_child(ch)
                to_visit.append(ch_node)

    svg = ""
    if dosvg:
        fnm = tempfile.mkstemp(suffix=".svg", prefix=os.path.basename(sys.argv[0]) + '_tmp_', text=True, dir=TMP_DIR)[1]
        #output = StringIO.StringIO()
        if os.path.exists( fnm ):
            print fnm
            root.render(fnm)

            with open(fnm, 'r') as fhd:
                svg = fhd.read()
            os.remove(fnm)
        #print svg

    return (root, svg)


if __name__ == '__main__':
    main(sys.argv[1:])
