#!/usr/bin/python
"""
Concatenates all SNPs from a VCF file in either FASTA or aln (clustal) format
"""
import os, sys
import copy
import argparse
import multiprocessing
from pprint      import pprint as pp
from collections import defaultdict, Counter

sys.path.insert(0, '.')
import vcfmerger
import editdist
from treemanager import fixsppname

#GZ=SL2.40ch06g50000_000100001_000150000.vcf.gz.raw.vcf.gz; FA=$GZ.SL2.40ch06.fasta; ../vcfconcat.py -f -RIL -Rg -Rd -i $GZ; ../FastTreeMP -fastest -gamma -nt -bionj -boot 100 -log $FA.log -out $FA.tree $FA; ../FastTreeMP -nt -makematrix $FA > $FA.matrix; ./newick_to_png.py $FA.tree
#FA=SL2.40ch06g50000_000100001_000150000.vcf.gz.SL2.40ch06.fasta; ../FastTreeMP -fastest -gamma -nt -bionj -boot 100 -log $FA.log -out $FA.tree $FA; ../FastTreeMP -nt -makematrix $FA > $FA.matrix; ./newick_to_png.py $FA.tree



def main(args):
    methods = {
        'median' : grouper_median,
        'linkage': grouper_linkage
    }


    dflmethod = methods.keys()[0]


    parser = argparse.ArgumentParser(description='Concatenate SNPs as a single sequence for each species.')
    parser.add_argument('-c', '--chrom', '--chromosome', dest='chromosome' , default=None     , action='store'      , nargs='?',                         type=str  , help='Chromosome to filter [all]')
    parser.add_argument('-I', '--ignore', '--skip'     , dest='ignore'     , default=[]       , action='append'     , nargs='*',                         type=str  , help='Chromosomes to skip')
    parser.add_argument('-s', '--start'                , dest='start'      , default=None     , action='store'      , nargs='?',                         type=int  , help='Chromosome start position to filter [0]')
    parser.add_argument('-e', '--end'                  , dest='end'        , default=None     , action='store'      , nargs='?',                         type=int  , help='Chromosome end position to filter [-1]')
    parser.add_argument('-t', '--threads'              , dest='threads'    , default=0        , action='store'      , nargs='?',                         type=int  , help='Number of threads [num chromosomes]')
    parser.add_argument('-f', '--fasta'                , dest='fasta'      ,                    action='store_true' ,                                                help='Output in fasta format [default: clustal alignment .aln format]')
    parser.add_argument('-r', '--noref'                , dest='noref'      ,                    action='store_false',                                                help='Do not print reference [default: true]')
    parser.add_argument('-R', '--RIL'                  , dest='RIL'        ,                    action='store_true' ,                                                help='RIL mode: false]')
    parser.add_argument('-Rm','--RIL-mads'             , dest='RILmads'    , default=0.25     , action='store'      , nargs='?',                         type=float, help='RIL percentage of Median Absolute Deviation to use (smaller = more restrictive): 0.25]')
    parser.add_argument('-Rs','--RIL-minsim'           , dest='RILminsim'  , default=0.75     , action='store'      , nargs='?',                         type=float, help='RIL percentage of nucleotides identical to reference to classify as reference: 0.75]')
    parser.add_argument('-Rg','--RIL-greedy'           , dest='RILgreedy'  ,                    action='store_true' ,                                                help='RIL greedy convert nucleotides to either the reference sequence or the alternative sequence: false]')
    parser.add_argument('-Rd','--RIL-delete'           , dest='RILdelete'  ,                    action='store_true' ,                                                help='RIL delete invalid sequences: false]')
    parser.add_argument('-M' ,'--RIL-method'           , dest='groupMethod', default=dflmethod, action='store'      , nargs='?', choices=methods.keys(), type=str  , help='Clustering method for RIL selection of good and bad sequences [' + ','.join(methods.keys()) + ']')

    parser.add_argument('-i', '--input'                , dest='input'      , default=None     ,                       nargs='?',                         type=str  , help='Input file')
    #parser.add_argument('input'                        ,                    default=None     , action='store'      , nargs='?', metavar='input file', type=str  , help='Input file')

    options = parser.parse_args(args)

    print options

    indexFile    = None
    parallel     = False

    config = {
        'format'       : 'aln',
        'ignore'       : [],
        'inchr'        : None,
        'inend'        : None,
        'infhd'        : None,
        'infile'       : None,
        'instart'      : None,
        'noref'        : True,
        'ouchr'        : None,
        'oufhd'        : None,
        'RIL'          : False,
        'RILmads'      : 0.25,
        'RILminsim'    : 0.75,
        'RILgreedy'    : False,
        'RILdelete'    : False,
        'sppmaxlength' : None,
        'threads'      : None,
    }




    config['infile'     ] = options.input
    config['ignore'     ] = options.ignore
    config['inchr'      ] = options.chromosome
    config['inend'      ] = options.end
    config['instart'    ] = options.start
    config['noref'      ] = options.noref
    config['threads'    ] = options.threads
    config['RIL'        ] = options.RIL
    config['RILmads'    ] = options.RILmads
    config['RILminsim'  ] = options.RILminsim
    config['RILgreedy'  ] = options.RILgreedy
    config['RILdelete'  ] = options.RILdelete
    config['groupMethod'] = options.groupMethod



    if config['groupMethod'] not in methods:
        print "%s not a valid method" % config['groupMethod']
        sys.exit(1)

    config[ 'grouper' ] = methods[ config['groupMethod'] ]



    if options.input is None:
        print "no input file defined"
        sys.exit(1)

    if not os.path.exists(options.input):
        print "input file %s does not exists" % options.input
        sys.exit(1)


    if options.fasta:
        config['format'  ]   = 'fasta'


    if ( config['instart'] is not None ) and ( config['inend'] is not None ):
        if config['inend'] <= config['instart']:
            print "end position smaller than start position %d < %d" % (config['inend'] < config['instart'])
            sys.exit(1)

    parallel = False
    if ( config['inchr'] is None ) and ( config['instart'] is None ) and ( config['inend'] is None ):
        parallel = True


    indexFile = config['infile'] + ".idx"

    print "Input File             : %s"              % config['infile']
    print "Index File             : %s (exists: %s)" % ( indexFile, os.path.exists(indexFile) )
    print "Print Reference        : %s"              % ( str(options.noref)                   )

    if not os.path.exists( indexFile ):
        vcfmerger.makeIndexFile( indexFile, config['infile'] )

    config['idx'] = vcfmerger.readIndex(indexFile)

    if config['inchr'] is not None:
        if config['inchr'] not in config['idx']:
            print "requested chromosome %s does not exists" % config['inchr']
            sys.exit(1)
        config['insekpos'] = config['idx'][config['inchr']]


    readSources(config)


    if parallel:
        parallelize(config)
    else:
        readData(config)

    return config


def getOptionInFile(pars, opts):
    """
    Returns input file from argument
    """
    infile = opts.iinput if opts.input is None else opts.iinput

    if infile is None:
        print "no input file given"
        pars.print_help()
        sys.exit(1)


    if isinstance(infile, list):
        if len(infile) > 1:
            print "more than one file given"
            print infile
            pars.print_help()
            sys.exit(1)

        infile = infile[0]
    else:
        infile = infile

    return infile


def parallelize(config):
    """
    Runs in parallel
    """
    print "parallelizing"
    if config['threads' ] == 0:
        config['threads' ] = len( config['idx'] )

    print "num threads %d" % config['threads' ]
    #config['thread' ] = 1
    #sys.exit(0)

    pool    = multiprocessing.Pool(processes=config['threads' ])
    #pool    = multiprocessing.Pool(processes=1)
    results = []

    for chrom, pos in sorted(config['idx'].items(), key=lambda item: item[1]):
        config['inchr'   ] = chrom
        config['insekpos'] = pos

        if chrom in config['ignore' ]:
            continue

        print "parallelizing :: chrom %s" % chrom
        results.append( [chrom, pool.apply_async( readData, [ copy.copy( config ) ] )] )

    while len(results) > 0:
        for info in results:
            try:
                #print "getting result"
                chrom, res = info
                res.get( 5 )
                results.remove( info )
                print "getting result %s. OK" % chrom

            except multiprocessing.TimeoutError:
                #print "getting result FAILED. waiting"
                pass


def readSources(config):
    """
    Read list of VCF files
    """
    print "reading sources"
    print "opening",
    with vcfmerger.openvcffile(config['infile'], 'r') as infhd:
        print "ok"

        print "reading"

        header    = ""

        sources   = {}
        names     = None
        for line in infhd:
            line = line.strip()
            if len(line) == 0: continue
            if line[0]   == '#':
                header += line + "\n"
                if line.startswith('##sources='):
                    names = line[10:].split(';')
                    for name in names:
                        sources[name] = []
                    #pp(sources)

                elif line.startswith('##numsources='):
                    numsources = int(line[13:])
                    if numsources != len(sources):
                        print "error parsing sources", numsources, len(sources),sources, len(names), names
                        sys.exit(1)
                    else:
                        print "num sources:",numsources

                continue
            break


        sppmaxlength = 0
        for spp in sorted(sources):
            sppname = fixsppname( spp )
            if len(sppname) > sppmaxlength: sppmaxlength = len(sppname)

        sppmaxlength += 2
        sppmaxlength  = "%-"+str(sppmaxlength)+"s"

        config['sppmaxlength'] = sppmaxlength
        config['sources'     ] = sources
        config['names'       ] = names
        config['header'      ] = header


def readData(config):
    """
    read data from specific VCF file
    """
    print "reading data"
    config['infhd']  = vcfmerger.openvcffile(config['infile'], 'r')
    config['ouchr']  = None
    config['oufhd']  = None

    runName = "all"

    if config['idx'] is not None:
        print "reading data :: has idx"
        if config['inchr'] is not None:
            print "reading data :: has idx :: seeking chrom %s" % config['inchr']

            config['infhd'].seek( config['insekpos'] )
            runName = config['inchr']

            print "reading data :: has idx :: seeking chrom %s. DONE" % config['inchr']

        else:
            print "reading data :: has idx :: error seeking"
            sys.exit(1)




    print "reading data :: %s" % config['inchr']

    inchr      = config['inchr'      ]
    instart    = config['instart'    ]
    inend      = config['inend'      ]

    config['coords' ] = set()

    refs       = []
    lastChro   = None
    numSnps    = -1
    numSnpsVal = -1
    lastPos    = -1
    lastPosVal = -1
    finalChro  = False
    for line in config['infhd']:
        line = line.strip()
        if len(line) == 0: continue
        if line[0]   == '#':
            continue


        cols     = line.split("\t")


        if len(cols) != 10:
            print line
            sys.exit(1)



        chro =     cols[0]
        posi = int(cols[1])
        src  =     cols[3]
        dst  =     cols[4]
        spps =     cols[9].split(",")



        if lastChro != chro:
            print chro
            if lastChro is not None:
                if inchr is not None:
                    if inchr != lastChro:
                        print "reading data :: %s :: %s :: skipping exporting" % (runName, lastChro)
                        lastChro = chro
                        continue
                    else:
                        finalChro = True

                parse(config, refs, lastChro)
                if finalChro: break

            print "reading data :: %s :: %s :: empting" % (runName, lastChro)
            refs     = []
            lastChro = chro
            lastPos  = -1
            numSnps  = -1

            for spp in config['sources']:
                config['sources'][spp] = []

        if chro in config['ignore' ]:
            continue

        if lastPos != posi:
            if numSnps % 100000 == 0:
                print "reading data :: %s :: %s %12d" % (runName, chro, numSnps)

            numSnps += 1

            lastPos = posi

        if ( inchr is not None ):
            if ( inchr   != chro )                           :
                #sys.stdout.write(".")
                continue
            if ( instart is not None ) and ( posi < instart ):
                #sys.stdout.write("<")
                #print "%d<%d" % (posi, instart),
                continue
            if ( inend   is not None ) and ( posi > inend   ):
                #sys.stdout.write(">")
                #print "%d>%d" % (posi, instart),
                continue


        if lastPosVal != posi:
            if numSnpsVal % 1000 == 0:
                print "reading data :: %s :: %s %12d valid" % (runName, chro, numSnpsVal)

            numSnpsVal += 1

            for spp in config['sources']:
                config['sources'][spp].append(None)

            refs.append(src)
            lastPosVal = posi



        for spp in spps:
            config['sources'][spp][numSnps] = dst
            config['coords' ].add( posi )

        #print '.',


    if ( inchr is None ) or ( inchr == lastChro ):
        parse(config, refs, lastChro)


    if  config['oufhd'] is not None:
        config['oufhd'].write('\n\n')
        config['oufhd'].close()
        config['oufhd'] = None

    print "reading data :: %s :: finished" % runName

    return 0


def parse(config, refs, chro):
    """
    Export alignment either in FASTA or ALN (clustal)
    """
    print "  exporting: chro %s" % chro

    sources = config['sources']
    names   = config['names'  ]

    for spp in sources:
        #print "  parsing %s :: %s" % (chro, spp)

        poses = sources[spp]

        for pos in xrange(len(poses)):
            nuc = poses[pos]

            if nuc is None:
                nuc = refs[pos]

            poses[pos] = nuc


    sourcesStrs = {}
    for spp in names:
        sourcesStrs[spp] = "".join( sources[spp] )

    refsStrs    = "".join( refs )
    emptyStr    = "N"*len(sourcesStrs[spp])


    if config[ 'RIL' ]:
        print 'RIL'
        refsStrs, sourcesStrs, emptyStr = RIL( config, refsStrs, sourcesStrs, emptyStr )




    if config['format'] == 'aln':
        for frag in xrange(0, len(refs), 60):
            #print frag,

            if config['noref'   ]:
                refsfrag = refsStrs[frag:frag+60]
                printfilealn( config, 'ref'  , refsfrag, chro )

            for spp in sorted( sourcesStrs ):
                poses     = sourcesStrs[spp]
                posesfrag = poses[frag:frag+60]

                sppname   = fixsppname( spp )
                printfilealn( config, sppname, posesfrag, chro )

            config['oufhd'].write('\n\n')

    elif config['format'] == 'fasta':
        for spp in sorted( sourcesStrs ):
            sppname   = fixsppname( spp )
            poses     = sourcesStrs[spp]
            printfilefasta(config, sppname, poses   , chro)

        if config['noref'   ]:
            printfilefasta(config, 'ref'  , refsStrs, chro)



    printfilecoords(config, chro)

    if  config['oufhd'] is not None:
        config['oufhd'].write('\n\n')
        config['oufhd'].close()
        config['oufhd'] = None


def RIL( config, refsStrs, sourcesStrs, emptyStr ):
    high, low, valids, invalids     = config[ 'grouper' ]( config, refsStrs, sourcesStrs, emptyStr )

    #valids, invalids                = filterSimilarity( valids, invalids, config, refsStrs, sourcesStrs, emptyStr )

    refsStrs, sourcesStrs, emptyStr = filter( high, low, valids, invalids, config, refsStrs, sourcesStrs, emptyStr )

    return ( refsStrs, sourcesStrs, emptyStr )


def grouper_median( config, refsStrs, sourcesStrs, emptyStr ):
    distMatrix  = {}

    mindist     = sys.maxint
    maxdist     = 0
    dists       = []

    # CALCULATE PAIRWISE, MIN AND MAX DISTANCES
    sourceskeys = sourcesStrs.keys()
    for spp1 in sourceskeys:
        #print "spp1", spp1p, spp1n
        spp1seq = sourcesStrs[ spp1 ]
        dist    = editdist.distance( refsStrs, spp1seq )

        if dist > 0:
            dists.append( dist )

        distMatrix[ spp1 ] = dist
        if dist < mindist:
            mindist = dist

        if dist > maxdist:
            maxdist = dist

    dists.sort()

    print 'MIN DIST      ', mindist
    print 'MAX DIST      ', maxdist
    print 'DISTS         ', len(dists), " ".join(["%3d" % x for x in dists])

    median        = dists[ int((len(dists) / 2) + 0.5) ]
    vals          = [ x for x in dists if x <= median ]

    print 'MEDIAN        ', median

    delta         = maxdist - median

    print 'DELTA         ', delta

    threshold_low = mindist + delta
    threshold_hig = median  - delta

    print 'THRESHOLD LOW ', threshold_low
    print 'THRESHOLD HIGH', threshold_hig

    good_low      = [ k for k in distMatrix if distMatrix[k] <= threshold_low ]
    good_hig      = [ k for k in distMatrix if distMatrix[k] >= threshold_hig ]
    invalids      = [ k for k in distMatrix if distMatrix[k] > threshold_low and distMatrix[k] < threshold_hig ]
    valids        = good_low + good_hig

    good_low.sort()
    good_hig.sort()
    invalids.sort()
    valids.sort()

    print 'GOOD LOW      ', len(good_low), good_low
    print 'GOOD HIGH     ', len(good_hig), good_hig
    print 'INVALIDS      ', len(invalids), invalids
    print 'VALIDS        ', len(valids  ), valids

    #print 'DISTS         ', len(dists), " ".join(["%3d" % x for x in dists])
    #
    #median_global = dists[ int((len(dists) / 2) + 0.5) ]
    #vals_low      = [ x for x in dists if x <= median_global ]
    #vals_hig      = [ x for x in dists if x >  median_global ]
    #
    #print 'MEDIAN GLOBAL ', median_global
    #print 'VALS LOW      ', len(vals_low), " ".join(["%3d" % x for x in vals_low])
    #print 'VALS HIGH     ', len(vals_hig), " ".join(["%3d" % x for x in vals_hig])
    #
    #median_low    = vals_low[ int((len(vals_low) / 2) + 0.5) ]
    #median_hig    = vals_hig[ int((len(vals_hig) / 2) + 0.5) ]
    #
    #print 'MEDIAN LOW    ', median_low
    #print 'MEDIAN HIGH   ', median_hig
    #
    #delta_low     = median_low - mindist
    #delta_hig     = maxdist    - median_hig
    #
    #print 'DELTA LOW     ', delta_low
    #print 'DELTA HIGH    ', delta_hig
    #
    #threshold_low = median_low + delta_low
    #threshold_hig = median_hig - delta_hig
    #
    #print 'THRESHOLD LOW ', threshold_low
    #print 'THRESHOLD HIGH', threshold_hig
    #
    #good_low      = [ k for k in distMatrix if distMatrix[k] <= median_low ]
    #good_hig      = [ k for k in distMatrix if distMatrix[k] >= median_hig ]
    #bad           = [ k for k in distMatrix if distMatrix[k] > median_low and distMatrix[k] < median_hig ]
    #
    #print 'GOOD LOW      ', len(good_low), good_low
    #print 'GOOD HIGH     ', len(good_hig), good_hig
    #print 'BAD           ', len(bad     ), bad

    return ( good_hig, good_low, valids, invalids )



def grouper_linkage( config, refsStrs, sourcesStrs, emptyStr ):
    #entropy_cutoff = config[ 'RILentro' ]
    #
    ##print "len names", len(names)
    #model = bioMixture.getModel(3, len(refsStrs))
    ##print model
    #sourcesKeys = sourcesStrs.keys()
    #dataset = [list(sourcesStrs[x]) for x in sourcesKeys ]
    ##print dataset
    #data    = mixture.DataSet()
    #data.fromList( dataset, IDs=sourcesKeys )
    ##print data
    #model.EM(data, 40, entropy_cutoff)
    #c = model.classify( data, labels=sourcesKeys, entropy_cutoff=entropy_cutoff )#, silent=1)
    #print len(c), c
    #clusters = defaultdict( list )
    #for spppos, clusternum in enumerate(c):
    #    clusters[ clusternum ].append( sourcesKeys[ spppos ] )
    #
    #for key in clusters:
    #    spps = clusters[ key ]
    #
    #    dists = []
    #    for x in range(1, len(spps)):
    #        dists.append( editdist.distance( sourcesStrs[ spps[0] ], sourcesStrs[ spps[x] ] ) )
    #    print 'key', key, 'dists', dists


    tolerance   = config[ 'RILmads'   ]

    distMatrix  = {}

    mindist     = sys.maxint
    maxdist     = 0


    # CALCULATE PAIRWISE, MIN AND MAX DISTANCES
    sourceskeys = sourcesStrs.keys()
    for spp1p, spp1n in enumerate( sourceskeys ):
        #print "spp1", spp1p, spp1n

        for spp2n in sourceskeys[spp1p+1:]:
            #print " spp2", sourceskeys.index(spp2n), spp2n

            sppKey = tuple(set(sorted( [ spp1n, spp2n ] )))

            dist = editdist.distance( sourcesStrs[ spp1n ], sourcesStrs[ spp2n ] )

            #print " sppKey", sppKey, 'dist', dist

            distMatrix[ sppKey ] = dist
            if dist < mindist:
                mindist = dist

            if dist > maxdist:
                maxdist = dist


    # CALCULATE DELTA OF DISTANCE FOR SCALE
    deltadist   = (maxdist - mindist) * 1.0
    print 'min', mindist, 'max', maxdist, 'delta', deltadist


    # NORMALIZE THE DATA
    for sppKey in distMatrix:
        #print "norma %-60s %4d" % ( str(sppKey), distMatrix[ sppKey ] ),
        if deltadist == 0:
            distMatrix[ sppKey ] = 1.0

        else:
            distMatrix[ sppKey ] = ( distMatrix[ sppKey ] - mindist ) / deltadist # convert to percentage
        #print "%.4f" % distMatrix[ sppKey ]


    # SEPARATE IN TWO GROUPS: REFERENCE (d<0.5) AND WILD (d>=0.5)
    tolvalsmin = []
    tolvalsmax = []
    for sppKey in distMatrix:
        spp1 = sppKey[ 0 ]
        spp2 = sppKey[ 1 ]
        dist = distMatrix[ sppKey ]

        if dist >= 0.5:
            tolvalsmax.append( dist )

        else:
            tolvalsmin.append( dist )



    tolvalsmin.sort()
    tolvalsmax.sort()


    # CALCULATE MIDPOINTS FOR EACH GROUP TO CALCULATE MEDIAN
    #print 'tol vals', tolvals
    tolvalsminmidpoint = int( (len(tolvalsmin) / 2) + 0.5)
    tolvalsmaxmidpoint = int( (len(tolvalsmax) / 2) + 0.5)
    print 'tol val min midpoint', tolvalsminmidpoint, 'tol val min len', len( tolvalsmin )
    print 'tol val max midpoint', tolvalsmaxmidpoint, 'tol val max len', len( tolvalsmax )


    # CALCULATE MEDIAN FOR EACH GROUP
    tolvalsminmedian   = tolvalsmin[ tolvalsminmidpoint ]
    tolvalsmaxmedian   = tolvalsmax[ tolvalsmaxmidpoint ]
    print "dist min median", tolvalsminmedian
    print "dist max median", tolvalsmaxmedian


    # CALCULATE MAD
    tolvalsminMADs     = [ abs(x - tolvalsminmedian) for x in tolvalsmin ]
    tolvalsmaxMADs     = [ abs(x - tolvalsmaxmedian) for x in tolvalsmax ]
    tolvalsminMADs.sort()
    tolvalsmaxMADs.sort()
    #for y, x in enumerate(tolvalsmin):
    #    print 'min pos %4d val %.5f diff %.5f' % ( y, x, abs(x - tolvalsminmedian) )
    #for y, x in enumerate(tolvalsmax):
    #    print 'max pos %4d val %.5f diff %.5f' % ( y, x, abs(x - tolvalsmaxmedian) )


    #print 'tol mads', tolMADs
    tolvalsminMAD    = tolvalsminMADs[ tolvalsminmidpoint ]
    tolvalsmaxMAD    = tolvalsmaxMADs[ tolvalsmaxmidpoint ]

    print 'MAD min before', tolvalsminMAD
    print 'MAD max before', tolvalsmaxMAD
    print 'tolerance     ', tolerance
    if tolerance > 0:
        tolvalsminMAD    = tolvalsminMAD * tolerance
        tolvalsmaxMAD    = tolvalsmaxMAD * tolerance

        print 'MAD min tolerance', tolvalsminMAD
        print 'MAD max tolerance', tolvalsmaxMAD

    tolvalsmaxMAD = 1 - tolvalsmaxMAD
    print 'MAD min final', tolvalsminMAD
    print 'MAD max final', tolvalsmaxMAD



    # DEFINE WHICH INDIVIDUALS PASS THRESHOLD OF SIMILARITY
    setsSim = defaultdict( set )
    setsDis = defaultdict( set )
    for sppKey in distMatrix:
        spp1 = sppKey[ 0 ]
        spp2 = sppKey[ 1 ]
        dist = distMatrix[ sppKey ]
        #print "%.4f" % distMatrix[ sppKey ],

        if   dist <= tolvalsminMAD:
            setsSim[ spp1 ].add( spp2 )
            setsSim[ spp2 ].add( spp1 )
            #print '+'

        elif dist >= tolvalsmaxMAD:
            setsDis[ spp1 ].add( spp2 )
            setsDis[ spp2 ].add( spp1 )
            #print '-'

        else:
            #print
            pass

    print 'len sim', len(setsSim), 'dis', len(setsDis)
    similar    = set()
    dissimilar = set()


    # GENERATE FINAL LISTS
    # LIST OF SIMILAR TO REFERENCE
    for spp in setsSim:
        sppset = setsSim[ spp ]
        #print "spp SIM %-30s %s" % ( spp, str( sppset ) )
        similar = similar.union( sppset )

    # LIST OF DISSIMILAR TO REFERENCE
    for spp in setsDis:
        sppset = setsDis[ spp ]
        #print "spp DIS %-30s %s" % ( spp, str( sppset ) )
        dissimilar = dissimilar.union( sppset )


    # MERGE SIMILAR AND DISSIMILAR LISTS INTO VALID LIST
    # ADD REMAINING SPECIES INTO INVALID SPECIES
    shared    = dissimilar.intersection( similar    )
    simonly   = similar.difference(      dissimilar )
    disonly   = dissimilar.difference(   similar    )

    valids    = set().union(similar, dissimilar)
    invalids  = set(sourceskeys).difference(valids)

    print "Similar  ", len(sorted(list( similar    ))), sorted(list( similar    ))
    print "Disimilar", len(sorted(list( dissimilar ))), sorted(list( dissimilar ))
    print
    print "Shared   ", len(sorted(list( shared     ))), sorted(list( shared     ))
    print "Sim Only ", len(sorted(list( simonly    ))), sorted(list( simonly    ))
    print "Dis Only ", len(sorted(list( disonly    ))), sorted(list( disonly    ))
    print
    print "Valids   ", len(sorted(list( valids     ))), sorted(list( valids     ))
    print "Invalids ", len(sorted(list( invalids   ))), sorted(list( invalids   ))

    #Similar   31 ['609', '610', '612', '614', '615', '623', '634', '644', '649', '651', '654', '660', '665', '666', '667', '668', '670', '674', '676', '679', '685', '688', '692', '693', '694', '697', '702', '706', '710', 'Slycopersicum MoneyMaker', 'Spimpinellifolium LYC2740']
    #Disimilar 45 ['609', '610', '612', '614', '615', '618', '623', '625', '626', '634', '644', '649', '651', '653', '654', '659', '660', '665', '666', '667', '668', '670', '674', '676', '679', '684', '685', '688', '691', '692', '693', '694', '696', '697', '702', '705', '706', '707', '710', '711', 'Slycopersicum MoneyMaker', 'Spimpinellifolium LA1578', 'Spimpinellifolium LA1584', 'Spimpinellifolium LYC2740', 'Spimpinellifolium LYC2798']
    #
    #Shared    31 ['609', '610', '612', '614', '615', '623', '634', '644', '649', '651', '654', '660', '665', '666', '667', '668', '670', '674', '676', '679', '685', '688', '692', '693', '694', '697', '702', '706', '710', 'Slycopersicum MoneyMaker', 'Spimpinellifolium LYC2740']
    #Sim Only  0 []
    #Dis Only  14 ['618', '625', '626', '653', '659', '684', '691', '696', '705', '707', '711', 'Spimpinellifolium LA1578', 'Spimpinellifolium LA1584', 'Spimpinellifolium LYC2798']
    #
    #Valids    45 ['609', '610', '612', '614', '615', '618', '623', '625', '626', '634', '644', '649', '651', '653', '654', '659', '660', '665', '666', '667', '668', '670', '674', '676', '679', '684', '685', '688', '691', '692', '693', '694', '696', '697', '702', '705', '706', '707', '710', '711', 'Slycopersicum MoneyMaker', 'Spimpinellifolium LA1578', 'Spimpinellifolium LA1584', 'Spimpinellifolium LYC2740', 'Spimpinellifolium LYC2798']
    #Invalids  20 ['601', '603', '608', '611', '619', '622', '624', '630', '631', '639', '643', '646', '648', '656', '658', '669', '675', '678', '682', '701']

    return ( sorted(list(dissimilar)), sorted(list(similar)), sorted(list( valids )), sorted(list( invalids)) )



def filterSimilarity( high, low, valids, invalids, config, refsStrs, sourcesStrs, emptyStr ):
    minsim      = config[ 'RILminsim' ]

    # CALCULATE PERCENTAGE OF SIMILARITY TO REFERENCE
    refsims = {}

    for spp in valids:
        sppseq = sourcesStrs[ spp ]
        refsim = 0

        for nucPos, nucSeq in enumerate( sppseq ):
            refSeq = refsStrs[ nucPos ]

            if refSeq == nucSeq:
                refsim += 1

        refsims[ spp ] = ( float( refsim ) / float( len( sppseq ) ) )


    #print 'REF', refsStrs
    #print 'ALT', altsStrs


    # REPLACE SEQUENCES WITH EITHER REFERENCE OR ALTERNATIVE
    modsCount = defaultdict( int )
    for spp in sourcesStrs:
        if spp in refsims:
            if refsims[ spp ] > minsim:
                modsCount[ 'REF' ] += 1

            else:
                modsCount[ 'ALT' ] += 1
                invalids[ spp ] = valids[ spp ]
                del valids[ spp ]


    #for sppPos, sppNucs in enumerate( nucs ):
        #print sppNucs, list(sppNucs), dict(sppNucs), sppNucs.values()

    for key in modsCount:
        print "count", key, modsCount[ key ]
    print "count NNN", len( invalids )

    return ( valids, invalids, config, refsStrs, sourcesStrs, emptyStr )


def filter( high, low, valids, invalids, config, refsStrs, sourcesStrs, emptyStr ):
    greedy      = config[ 'RILgreedy' ]

    # IF IN GREEDY MODE, FIX NUCLEOTIDES FROM VALIDs
    if greedy:
        # COUNT NUCLEOTIDES IN EACH POSITION
        nucs = []
        for spp in sourcesStrs:
            sppseq = sourcesStrs[ spp ]
            for nucPos, nuc in enumerate( sppseq ):
                if len( nucs ) <= nucPos:
                    nucs.append( Counter() )
                nucs[ nucPos ].update( [ nuc ] )

        # GENERATE ALTERNATIVE STRING
        altsStrs  = ""
        refsStrsN = ""
        emptyStr  = ""
        for nucPos, nucRef in enumerate( refsStrs ):
            nucData = list( nucs[ nucPos ] )

            if len( nucData ) != 2:
                print "BAD BAD BAD SEQUENCE. MORE THAN TWO VARIANTES TO THE SAME POSITION", nucData
                altsStrs  += '-'
                refsStrsN += '-'
                emptyStr  += '-'

            else:
                #print 'pos %3d data %-10s ref %s' % ( nucPos, str(nucData), nucRef ),
                nucData.remove( nucRef )
                nucAlt     = nucData[0]
                #print 'alt', nucAlt
                altsStrs  += nucAlt
                refsStrsN += nucRef
                emptyStr  += 'N'

        refsStrs = refsStrsN




        for spp in sourcesStrs:
            if spp in low:
                sourcesStrs[ spp ]  = refsStrs
            #print " fixing spp %-30s to REF" % ( spp )
            #print " fixing spp %-30s to ALT" % ( spp )
            #sourcesStrs[ spp ]  = refsStrs
            #sourcesStrs[ spp ]  = altsStrs
            elif spp in high:
                sourcesStrs[ spp ]  = altsStrs



        if config['RILdelete']:
            for spp in sourcesStrs.keys():
                #sppseq = sourcesStrs[spp]
                #= "".join( sources[spp] )
                if spp in invalids:
                    #print "spp", spp, 'is invalid. converting to NNN'
                    del sourcesStrs[spp]





    # CONVERT UNCLUSTERED SEQUENCES TO N
    for spp in sourcesStrs:
        #sppseq = sourcesStrs[spp]
        #= "".join( sources[spp] )
        if spp in invalids:
            #print "spp", spp, 'is invalid. converting to NNN'
            sourcesStrs[spp] = emptyStr



    return refsStrs, sourcesStrs, emptyStr





def printfilename(config, chro, coords=False):
    inchr   = config['inchr'  ]
    instart = config['instart']
    inend   = config['inend'  ]

    posstr = ''

    if (instart is not None) or (inend is not None):
        if (instart is not None) and (inend is not None):
            posstr = '_%06d-%06d' % (instart, inend)

        elif (instart is not None):
            posstr = '_%06d-end' % (instart)

        elif (inend is not None):
            posstr = '_000000-%06d' % (inend)

    ext = '.aln'

    if config['format'] == 'fasta':
        ext = '.fasta'

    if coords:
        ext += '.coords'

    outfile = config['infile'] + '.' + chro + posstr + ext

    return outfile


def printfileopen(config, spp, chro, header=None):
    """
    Save to file
    """
    if config['ouchr'] != chro:
        print "    printing aln chromosome '%s'" % chro
        if config['oufhd'] is not None:
            config['oufhd'].write('\n\n')
            config['oufhd'].close()
            config['oufhd'] = None
        config['ouchr'] = chro

    outfile = printfilename(config, chro)

    if config['oufhd'] is None:
        print "      opening %s" % outfile
        config['oufhd']   = open(outfile, 'w')

        if header is not None:
            config['oufhd'].write(header)


def printfilealn(config, spp, line, chro):
    """
    Print alignment header
    """
    printfileopen(config, spp, chro, header='CLUSTAL multiple sequence alignment\n\n\n')

    config['oufhd'].write(config['sppmaxlength'] % spp)
    config['oufhd'].write(line)
    config['oufhd'].write("\n")


def printfilefasta(config, spp, line, chro):
    """
    Print fasta header
    """
    printfileopen(config, spp, chro)

    config['oufhd'].write('>' + spp + "\n")
    for frag in xrange(0, len(line), 60):
        config['oufhd'].write(line[frag:frag+60])
        config['oufhd'].write("\n")
    config['oufhd'].write("\n")


def printfilecoords(config, chro):
    outfile = printfilename(config, chro, coords=True)
    print "exporting coords to %s" % outfile

    coords  = config['coords' ]

    with open(outfile, 'w') as fhd:
        fhd.write( str( len( coords ) ) )
        fhd.write( "\n" )
        fhd.write( ",".join( [ str(x) for x in sorted(coords) ] ) )







if __name__ == '__main__':
    main(sys.argv[1:])
