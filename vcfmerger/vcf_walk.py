"""
Defined WALK_OUT's WALKER class
Shared functions between RAM and SQL
"""

import os
import sys
import copy
import glob
import time
import argparse
from subprocess import call

import multiprocessing
from multiprocessing import Pool, Queue

## CUSTOM CLUSTER
#ROWNUM=
#COLNUM=
#NAME=
#CHROMOSOME=


DEBUG             = False
DB_START          = 0
DB_END            = 1
DB_LEN_OBJ        = 2
DB_LEN_SNP        = 3
DB_NAME           = 4
DB_TREE           = 5
DB_FASTA          = 6
DB_LINE           = 7
NUM_REGISTER_VARS = 8

sys.path.insert(0, '.')
from filemanager import *
import cluster
import newick_to_png
from treemanager import fixsppname

############################################
## AUXILIARY FUNCTIONS
############################################
def corr(L1, L2):
    """
    Somple correlation
    """
    nL1   = 1 / (sum([e1*e1 for e1 in L1]) ** 0.5)
    nL2   = 1 / (sum([e2*e2 for e2 in L2]) ** 0.5)
    corr = sum( [ (e1*nL1)*(e2*nL2) for e1,e2 in zip(L1,L2) ] )

    return corr



############################################
## WEBSERVER HELPER FUNCTIONS
############################################
class walkermeta(type):
    def __init__(self, *args):
        super(walkermeta, self).__init__(*args)


class walker(object):
    """
    Super class with shared functions
    """
    #__metaclass__     = walkermeta

    def __init__(self):
        self.spps              = {}
        self.wholedata         = {}
        self.clusters          = {}
        self.db_name           = None
        self.db_file           = None
        self.dataNames         = None
        self.dbMtime           = None
        self.spps_fn           = None
        self.sppindexinv       = None

    def getOpts( self, args ):
        parser = argparse.ArgumentParser(description='Generates a gene by gene tree.')

        parser.add_argument( '-g' , '--graph'           ,                        dest='graph'             ,                                action='store_true' ,                                   help='Export graphics'                         )
        parser.add_argument( '-tx', '--treex'           ,                        dest='treex'             ,                                action='store_true' ,                                   help='Make graph with clustering tree for x (position) (changes position order)')
        parser.add_argument( '-ty', '--treey'           ,                        dest='treey'             ,                                action='store_true' ,                                   help='Make graph with clustering tree for y (species ) (changes species  order)')
        parser.add_argument( '-tr', '--tree'            ,                        dest='tree'              ,                                action='store_true' ,                                   help='Make graph with clustering tree for x and y      (changes species and position orders)')
        parser.add_argument( '-n' , '--no-csv'          ,                        dest='csv'               ,                                action='store_false',                                   help='DO NOT export CSV'                       )

        parser.add_argument( '-t' , '--threads'         ,                        dest='read_threads'      , default=1   ,                                        metavar='Threads'     , type=int, help='Number of threads'                       )

        parser.add_argument( '-s' , '--spp'             , '--species'          , dest='species'           , default=[]  ,                  action='append'     ,                         type=str, help='Export only the following species [all]' )
        parser.add_argument( '-o' , '--outfolder'       ,                        dest='outfolder'         , default=None,                                        metavar='out folder'  , type=str, help='Output Folder [Default: .]'              )

        parser.add_argument( '-c' , '--cluster'         ,                        dest='cluster'           , default=None,                                        metavar='Cluster N bp', type=int, help='Cluster every N bp [default: per gene]'  )
        parser.add_argument( '-C' , '--classes'         ,                        dest='classes'           , default=None,                                        metavar='cluster N cl', type=int, help='Cluster in N classes [default: per gene]')
        parser.add_argument( '-e' , '--evenly'          ,                        dest='evenly'            ,                                action='store_true' ,                                   help='Cluster the features at evenly spaced intervals[default: per gene]')

        parser.add_argument( '-D' , '--DEBUG'           ,                        dest='DEBUG'             ,                                action='store_true' ,                                   help='DEBUG MODE'                              )
        parser.add_argument( '-l' , '--list'            ,                        dest='lst'               ,                                action='store_true' ,                                   help='List available species and quits'        )
        parser.add_argument( '-p' , '--pickle'          ,                        dest='pickle'            ,                                action='store_true' ,                                   help='Pickle only'                             )
        parser.add_argument( '-np', '--no-pickle'       ,                        dest='dopickle'          ,                                action='store_false',                                   help='No picke'                                )
        parser.add_argument( '-d' , '--db'              , '--database'         , dest='db'                , default=None, nargs='?',                             metavar='input db'    , type=str, help='Input db'                                )
        parser.add_argument( '-u' , '--custom'          , '--custom-order'     , dest='custom_order'      , default=[]  , nargs='*',       action='append'     ,                                   help='File(s) containing custom sort order'    )

        parser.add_argument( '-Cle', '--cluster-ext'    , '--cluster-extension', dest='cluster_extension' , default=None, nargs='?',                                                     type=str, help='[optional] extension to search. [default: .matrix]')
        parser.add_argument( '-Clg', '--cluster-global' ,                        dest='cluster_global'    ,                                action='store_true' ,                                   help='perform global clustering'                      )
        parser.add_argument( '-Clt', '--cluster-threads',                        dest='cluster_threads'   , default=None,                                                                type=int, help='number of threads for clustering [default: 5]'  )
        parser.add_argument( '-Clp', '--cluster-no-png' ,                        dest='cluster_dopng'     ,                                action='store_false',                                   help='do not export cluster png')
        parser.add_argument( '-Cls', '--cluster-no-svg' ,                        dest='cluster_dosvg'     ,                                action='store_false',                                   help='do not export cluster svg')
        parser.add_argument( '-Cln', '--cluster-no-tree',                        dest='cluster_dotree'    ,                                action='store_false',                                   help='do not export cluster tree. precludes no png and no svg')
        parser.add_argument( '-Clr', '--cluster-no-rows',                        dest='cluster_dorows'    ,                                action='store_false',                                   help='Cluster - no rows clustering')
        parser.add_argument( '-Clc', '--cluster-no-cols',                        dest='cluster_docols'    ,                                action='store_false',                                   help='Cluster - no column clustering')

        options = parser.parse_args(args)

        return ( parser, options )


        #parser = argparse.ArgumentParser(description='Generates a gene by gene tree.')
        #
        #parser.add_argument( '-d'  , '--db'             , '--database'         , dest='db'               , default=None, nargs='?',                       type=str, help='Input db'                                               )
        #parser.add_argument( '-p'  , '--pickle'                                , dest='pickle'           ,                          action='store_true' ,           help='Save intermediate pickle'                               )
        #parser.add_argument( '-l'  , '--list'                                  , dest='lst'              ,                          action='store_true' ,           help='List available species and quits'                       )
        #parser.add_argument( '-t'  , '--threads'        ,                        dest='read_threads'     , default=1   ,                                  type=int, help='Number of threads to read raw files'                    )
        #
        #parser.add_argument( '-Cle', '--cluster-ext'    , '--cluster-extension', dest='cluster_extension', default=None, nargs='?',                       type=str, help='[optional] extension to search. [default: .matrix]')
        #parser.add_argument( '-Clg', '--cluster-global'                        , dest='cluster_global'   ,                          action='store_true' ,           help='perform global clustering'                              )
        #parser.add_argument( '-Clt', '--cluster-threads'                       , dest='cluster_threads'  , default=5   ,                                  type=int, help='number of threads for clustering [default: 5]'          )
        #parser.add_argument( '-Clp', '--cluster-no-png'                        , dest='cluster_dopng'    ,                          action='store_false',           help='do not export cluster png'                              )
        #parser.add_argument( '-Cls', '--cluster-no-svg'                        , dest='cluster_dosvg'    ,                          action='store_false',           help='do not export cluster svg'                              )
        #parser.add_argument( '-Cln', '--cluster-no-tree'                       , dest='cluster_dotree'   ,                          action='store_false',           help='do not export cluster tree. precludes no png and no svg')
        #parser.add_argument( '-Clr', '--cluster-no-rows',                        dest='cluster_dorows'    ,                                action='store_false',                                   help='Cluster - no rows clustering')
        #parser.add_argument( '-Clc', '--cluster-no-cols',                        dest='cluster_docols'    ,                                action='store_false',                                   help='Cluster - no column clustering')
        #
        #options = parser.parse_args(args)
        #
        #print options


    def getSppIndexInvert( self ):
        """
        Creates inverted index for species list
        """
        if self.sppindexinv is None:
            self.sppindexinv = [None]*len( self.spps )

            for k in self.spps:
                #print " adding",k,"at pos",spps[k],"/",len(spps)
                self.sppindexinv[ self.spps[k] ] = k

        return self.sppindexinv

    def get_spps(self):
        """
        Return list of species
        """
        return self.spps

    def filter_by(self, inspp, group_every=None, num_classes=None, evenly=False, onlyChrom=None):
        """
        Filter data. returns final excerpt
        """
        print "ordering %s" % inspp

        if len( self.wholedata ) == 0:
            print "ordering %s :: chromosome database does not exists. reading raw matrices" % ( inspp )
            self.load_data(self.db_name, print_spps_only=False)
            print "ordering %s :: chromosome database created" % ( inspp )

        excerpt = self.filter_data(inspp, group_every=group_every, num_classes=num_classes, evenly=evenly, onlyChrom=onlyChrom)

        return excerpt

    def filter_data(self, inspp, group_every=None, num_classes=None, evenly=False, onlyChrom=None):
        """
        Filter data algorithm. choose chromosome and get database
        """
        excerpt     = {}

        chromsToFilter = self.wholedata.keys()
        if onlyChrom is not None:
            if onlyChrom not in self.wholedata:
                print "ordering %s :: chromosome %s does not exists" % ( inspp, str(onlyChrom) )
                return None
            chromsToFilter = [ onlyChrom ]

        for chromosome_name in sorted(chromsToFilter):
            print "ordering %s :: chromosome %s" % ( inspp, chromosome_name )

            db       = self.wholedata[ chromosome_name ]
            self.filter_db(inspp, chromosome_name, db, excerpt, group_every=group_every, num_classes=num_classes, evenly=evenly)

        return excerpt

    def getRow( self, db, chromosome_name, regnum, inspp ):
        """
        Reads a whole individual's line by mirroring the diagonal
        """
        #line        = self.get_row( db, chromosome_name, regnum, inspp )
        data = db[ regnum ][ DB_LINE ]

        sppindex    = self.spps[ inspp ]
        sppindexinv = self.getSppIndexInvert( )
        line        = []

        print "GETTING ROW RAM"
        for y in range(len(data)):
            #print " getting %s (%d) vs %s (%d)" % ( inspp, sppindex, sppindexinv[y], y )
            yy = y
            xx = sppindex

            if y > sppindex:
                #print "  inverting"
                yy = sppindex
                xx = y

            val = data[xx][yy]
            #print "  %02dx%02d = val: %f" % ( xx, yy, val )
            line.append( val )

        return line



    def filter_db(self, inspp, chromosome_name, db, excerpt, group_every=None, num_classes=None, evenly=False):
        """
        Filter each database. Actual clustering algorithm
        """
        if evenly:
            group_every = None
            num_classes = None

        if group_every is not None:
            num_classes = None


        dbLen       = len(db)
        chromLen    = db[-1][DB_END] - db[0][DB_START]
        excerpt[ chromosome_name ] = []


        if evenly:
            num_classes = dbLen
            print "ordering %s :: chromosome %s :: grouping evenly in %d classes (%d bp, %d registers)" % ( inspp, chromosome_name, num_classes, chromLen, dbLen )


        if num_classes is not None:
            if num_classes <= len(db):
                ge          = int(chromLen / num_classes)
                group_every = ge
                print "ordering %s :: chromosome %s :: grouping in %d classes (%d bp, %d registers) every %d bp" % ( inspp, chromosome_name, num_classes, chromLen, dbLen, ge )
                #if group_every is None:
                    #group_every = ge
                #else:
                    #group_every = group_every if ge > group_every else ge

        #if evenly:
        #    pos_extra = " - evenly distributed %dbp with %d datapoints in %dbp groups of %dbp" % (chromLen, dbLen, num_classes, group_every)

        lastStart   = 0
        lastEnd     = 0
        lastLenSNP  = 0
        lastLenOBJ  = 0
        registerNum = 0
        lenline     = 0
        lastNames   = []
        #lastTrees   = []
        lastFastas  = []
        lastDatas   = []

        print "ordering %s :: chromosome %s register" % ( inspp, chromosome_name),
        for regnum in xrange(len(db)):
            register = db[regnum]
            #print "ordering %s :: chromosome %s register %d" % ( inspp, chromosome_name, registerNum )
            #print registerNum,

            start       = register[ DB_START   ]
            end         = register[ DB_END     ]
            len_aln_obj = register[ DB_LEN_OBJ ]
            len_aln_snp = register[ DB_LEN_SNP ]
            name        = register[ DB_NAME    ]
            #tree        = register[ DB_TREE    ]
            #fasta       = register[ DB_FASTA   ]
            data        = register[ DB_LINE    ]
            line        = self.getRow( db, chromosome_name, regnum, inspp )


            if group_every is None:
                """
                If no grouping, just add
                """
                register_new            = copy.copy( register )
                register_new[ DB_LINE ] = line

                excerpt[ chromosome_name ].append( register_new )

            else:
                """
                If grouping, group first, save groups
                """
                #print "grouping every", group_every
                start_new = int(start / group_every)
                end_new   = int(end   / group_every)
                #name_new  = str(lastStart * group_every) + '_' + str(lastEnd * group_every)
                #print "start", start, start_new, lastStart, "end",end, end_new, lastEnd

                lastDatasLen = len(lastDatas)
                lenline      = len(line     )
                if (start_new != lastStart) and (lastDatasLen > 0):
                    avg_data = [None]*lenline

                    for linePos in range(lenline):
                        colvals = []
                        for dataPos in range(lastDatasLen):
                            colvals.append( lastDatas[ dataPos ][ linePos ] )

                        sumcolvals = sum(colvals)
                        lencolvals = len(colvals)
                        colvalsst  = colvals[0]
                        colvalsavg = sumcolvals/float(lencolvals)
                        avg_data[ linePos ] = colvalsavg if lencolvals > 1 else colvalsst

                    register_new             = copy.copy( register )
                    register_new[ DB_START   ] = lastStart     * group_every
                    register_new[ DB_END     ] = (lastStart+1) * group_every
                    register_new[ DB_NAME    ] = str(register_new[ DB_START ]) + ".." + str(register_new[ DB_END  ]) + "(%d;%d)" % (lastLenOBJ, lastLenSNP)
                    #register_new[ DB_TREE    ] = "\n".join(lastTrees)
                    #register_new[ DB_FASTA   ] = concatHashs(lastFastas)
                    #register_new[ DB_NAME   ] = ";".join( lastNames )
                    register_new[ DB_LEN_OBJ ] = lastLenOBJ
                    register_new[ DB_LEN_SNP ] = lastLenSNP
                    register_new[ DB_LINE    ] = avg_data

                    excerpt[ chromosome_name ].append( register_new )

                    lastLenOBJ = 0
                    lastLenSNP = 0
                    lastNames  = [  ]
                    #lastTrees  = [  ]
                    #lastFastas = [  ]
                    lastDatas  = [  ]

                lastStart    = start_new
                lastEnd      = end_new
                lastLenOBJ  += len_aln_obj
                lastLenSNP  += len_aln_snp
                lastNames.append( name )
                #lastFastas.append( fasta )
                lastDatas.append( line )

            registerNum += 1



        if group_every is not None:
            """
            Add remaining register
            """
            lastDatasLen = len(lastDatas)
            if (start_new != lastStart) and (lastDatasLen > 0):
                avg_data = [None]*lenline

                for linePos in range(lenline):
                    colvals = []
                    for dataPos in range(lastDatasLen):
                        colvals.append( lastDatas[ dataPos ][ linePos ] )

                    sumcolvals = sum(colvals)
                    lencolvals = len(colvals)
                    colvalsst  = colvals[0]
                    colvalsavg = sumcolvals/float(lencolvals)
                    avg_data[ linePos ] = colvalsavg if lencolvals > 1 else colvalsst

                register_new             = copy.copy( register )
                register_new[ DB_START   ] = lastStart     * group_every
                register_new[ DB_END     ] = (lastStart+1) * group_every
                register_new[ DB_NAME    ] = str(register_new[DB_START]) + ".." + str(register_new[DB_END  ]) + "(%d;%d)" % (lastLenOBJ, lastLenSNP)
                #register_new[ DB_TREE    ] = "\n".join(lastTrees)
                #register_new[ DB_FASTA   ] = concatHashs(lastFastas)
                #register_new[ DB_NAME    ] = ";".join( lastNames )
                register_new[ DB_LEN_OBJ ] = lastLenOBJ
                register_new[ DB_LEN_SNP ] = lastLenSNP
                register_new[ DB_LINE    ] = avg_data

                excerpt[ chromosome_name ].append( register_new )

                lastLenOBJ = 0
                lastLenSNP = 0
                lastNames  = [  ]
                #lastTrees  = [  ]
                #lastFastas = [  ]
                lastDatas  = [  ]

        print "ordering %s :: chromosome %s done" % ( inspp, chromosome_name )

    def make_table(self, ref, chrom, res, group_every=None, num_classes=None, evenly=False, startPos=None, endPos=None, maxNum=None, page=None):
        """
        Get table from database, giltering
        """
        excerpt = self.filter_by(ref, group_every=group_every, num_classes=num_classes, evenly=evenly, onlyChrom=chrom)


        if 'clusters' not in res:
            res['clusters'] = {}

        cg = self.getCluster( chrom, ref )

        if  cg and 'clusters' in cg:
            res['clusters'] = cg['clusters']


        data    = excerpt[ chrom ]

        return self.filter_excerpt(data, res, startPos=startPos, endPos=endPos, maxNum=maxNum, page=page)

    def filter_excerpt( self, data, res, startPos=None, endPos=None, maxNum=None, page=None ):
        """
        create summarized register for chromosome
        """
        res["header"   ] = {}
        res["data_info"] = {}
        res["data"     ] = { 'name': [], 'line': [] }

        #print excerpt[chromosome_name]
        print "making table: from %s to %s" % ( str(startPos), str(endPos) )

        sppindexinv = self.getSppIndexInvert( )

        res["header"]["start"      ] = [ x[DB_START  ] for x in data ]

        res["header"]["end"        ] = [ x[DB_END    ] for x in data ]

        res["header"]["num_unities"] = [ x[DB_LEN_OBJ] for x in data ]

        res["header"]["num_snps"   ] = [ x[DB_LEN_SNP] for x in data ]

        res["header"]["name"       ] = [ x[DB_NAME   ] for x in data ]

        minVal =  999999999
        maxVal = -999999999
        for spp in sppindexinv:
            sppindex = self.spps[ spp ]

            res['data']['name'].append( spp )
            res['data']['line'].append( []  )

            regcount = 0
            for register in data:
                val = register[DB_LINE][sppindex]

                if val > maxVal: maxVal = val
                if val < minVal: minVal = val

                #res["data"][-1]['line'].append( val ) # table
                res['data']['line'][-1].append( [val, sppindex, regcount] ) # d3 svg
                regcount += 1

        numColsTotal = len(res["header"]["name"       ])

        res['data_info']["minPosAbs"     ] = min(res["header"]["start"      ])
        res['data_info']["maxPosAbs"     ] = max(res["header"]["end"        ])
        res['data_info']["num_cols"      ] = len(data       )
        res['data_info']["num_rows"      ] = len(sppindexinv)
        res['data_info']["num_cols_total"] = numColsTotal

        res['data_info']["minPos"        ] = res['data_info']["minPosAbs"     ]
        res['data_info']["maxPos"        ] = res['data_info']["maxPosAbs"     ]

        res['data_info']["minVal"        ] = minVal
        res['data_info']["maxVal"        ] = maxVal




        if  ( startPos is not None) or \
            ( endPos   is not None) or \
            ((maxNum   is not None) and (res['data_info']["num_cols" ] > maxNum)):
            res = self.filterTable(data, res, startPos, endPos, maxNum, sppindexinv, minVal, maxVal, page)

        res['data_info']["length_abs"    ] = res['data_info']["maxPosAbs"] - res['data_info']["minPosAbs"]
        res['data_info']["length"        ] = res['data_info']["maxPos"   ] - res['data_info']["minPos"   ]

        return res

    def filterTable(self, data, res, startPos, endPos, maxNum, sppindexinv, minVal, maxVal, page):
        """
        Clip register
        """
        posStart     =  0
        posEnd       = -1
        print "filtering: shortening table: BEGIN          : start pos %s (index %s) end pos %s (index %s) max num %s (%d) page %s" % ( str(startPos), str(posStart), str(endPos), str(posEnd), str(maxNum), res['data_info']["num_cols"], str(page) )


        if startPos is not None:
            starts = res["header"]["start"      ]
            for pos in range(len(starts)):
                val = starts[pos]
                if val >= startPos:
                    posStart = pos - 1
                    if posStart < 1:
                        posStart = 0
                    break


        if endPos is not None:
            ends = res["header"]["end"      ]
            for pos in range(len(ends)):
                val = ends[pos]
                if val >= endPos:
                    posEnd = pos
                    break


        print "filtering: shortening table: AFTER BEGIN END: start pos %s (index %s) end pos %s (index %s) max num %s (%d) page %s" % ( str(startPos), str(posStart), str(endPos), str(posEnd), str(maxNum), res['data_info']["num_cols"], str(page) )


        if maxNum is not None:
            posLength = posEnd - posStart + 1
            if posEnd == -1:
                posLength = res['data_info']["num_cols" ] - posStart

            posEndEff = posStart + posLength - 1

            print "filtering: shortening table: MAXNUM         : pos start %d pos end %d pos length %d pos end eff %d" % (posStart, posEnd, posLength, posEndEff)

            if posLength > maxNum:
                pagenum = 0
                if page is not None:
                    pagenum = page

                print "filtering: shortening table: MAXNUM         : number of registers (%d) bigger than max number %d page %d" % ( posLength, maxNum, pagenum )

                pstr = None
                pend = None

                if pagenum >= 0:
                    print "filtering: shortening table: MAXNUM         : pagenum >= 0"
                    pstr = posStart  + (maxNum *   pagenum       )
                    pend = posStart  + (maxNum *  (pagenum+1)    )
                    print "filtering: shortening table: MAXNUM         : pos start new %d pos end new %d" % ( pstr, pend )

                else:
                    print "filtering: shortening table: MAXNUM         : pagenum < 0"
                    pstr = posEndEff -  maxNum
                    pend = posEndEff
                    print "filtering: shortening table: MAXNUM         : pos start new %d pos end new %d" % ( pstr, pend )

                if pend < posStart : pend = posStart  + maxNum
                if pend > posEndEff: pend = posEndEff
                if pstr > posEndEff: pstr = posEndEff - maxNum
                if pstr < posStart : pstr = posStart
                if pend < posStart : pend = posStart  + maxNum

                print "filtering: shortening table: MAXNUM         : number of registers (%d) bigger than max number %d page %d :: pos start %d>%d pos end %d[%d]>%d FINAL" % ( posLength, maxNum, pagenum, posStart, pstr, posEnd, posEndEff, pend )

                posStart = pstr
                posEnd   = pend

                startPos = res["header"]["start"    ][posStart]
                endPos   = res["header"]["end"      ][posEnd  ]
            else:
                print "filtering: shortening table: MAXNUM         : pos length %d <= maxnum %d" % ( posLength, maxNum )


        print "filtering: shortening table: AFTER MAXNUM   : start pos %s (index %s) end pos %s (index %s) max num %s (%d) page %s" % ( str(startPos), str(posStart), str(endPos), str(posEnd), str(maxNum), res['data_info']["num_cols"], str(page) )


        res["header"]["start"      ] = res["header"]["start"      ][posStart: posEnd]
        res["header"]["end"        ] = res["header"]["end"        ][posStart: posEnd]
        res["header"]["num_unities"] = res["header"]["num_unities"][posStart: posEnd]
        res["header"]["num_snps"   ] = res["header"]["num_snps"   ][posStart: posEnd]
        res["header"]["name"       ] = res["header"]["name"       ][posStart: posEnd]
        #res['data'  ]['line'       ] = res['data'  ]['line'       ][posStart: posEnd]

        for reglinepos in range(len(res['data'  ]['line'       ])):

            res['data'  ]['line'       ][reglinepos] = res['data'  ]['line'       ][reglinepos][posStart:posEnd]
            regline = res['data'  ]['line'       ][reglinepos]

            #print "regline",regline
            for register in regline:
                #print "  register",register
                register[2] = register[2] - posStart

        minVal   =  999999999
        maxVal   = -999999999
        for regline in res['data'  ]['line'       ]:
            for register in regline:
                val       = register[0]
                if val > maxVal: maxVal = val
                if val < minVal: minVal = val

        res['data_info']["num_cols"] = posEnd - posStart + 1

        res['data_info']["minPos"  ] = min(res["header"]["start"      ])
        res['data_info']["maxPos"  ] = max(res["header"]["end"        ])

        res['data_info']["minVal"  ] = minVal
        res['data_info']["maxVal"  ] = maxVal

        return res

    def getRegisterDict( self, gene, chrom ):
        """
        Convert from array to dictionary
        """
        register = self.getRegister(gene, chrom)

        if register is None:
            return register

        res = self.reg2dict(register)

        return res

    def reg2dict( self, register ):
        """
        Convert from array to dictionary
        """
        res = {
            'START'   : register[ DB_START   ],
            'END'     : register[ DB_END     ],
            'LEN_OBJ' : register[ DB_LEN_OBJ ],
            'LEN_SNP' : register[ DB_LEN_SNP ],
            'NAME'    : register[ DB_NAME    ],
            'TREE'    : register[ DB_TREE    ],
            'FASTA'   : register[ DB_FASTA   ],
            'LINE'    : register[ DB_LINE    ]
        }

        return res

    def load_data(self, db_name, singlechrom=None, read_threads=1, print_spps_only=False, dopickle=True, cluster_extension=None, cluster_threads=None, cluster_global=False, cluster_dopng=True, cluster_dosvg=True, cluster_dotree=True, cluster_dorows=True, cluster_docols=True):
        """
        Load data from disk
        """
        read_raw         = False

        self.db_name     = db_name
        self.sppindexinv = []


        if self.db_name.endswith('.sqlite'):
            print "db should not end in .sqlite . you gave me the wront type of file"
            sys.exit(1)

        elif not self.db_name.endswith('.pickle.gz'):
            """
            Pickle file. load
            """
            print "has .pickle.gz . loading"
            self.db_file       = self.db_name + '.pickle.gz'

        self.spps_fn       = self.db_file
        self.cluster_fn    = self.spps_fn + '.cluster.pickle.gz'



        if print_spps_only:
            if os.path.exists( self.spps_fn ):
                """
                If database exists read it
                """
                print "database exists. loading"
                read_raw = False

            else:
                """
                If database does not exists. create if from raw data
                """
                print "database does not exists. reading raw"
                read_raw = True

        else:
            """
            If database does not exists. create if from raw data
            """
            print "printing species names only. reading raw"
            read_raw = True





        if read_raw:
            """
            Reading all data
            """
            print "globing",self.db_name+'_*.pickle.gz'
            self.dbfiles = glob.glob(self.db_name+'_*.pickle.gz')
            self.dbfiles.sort()

            if len(self.dbfiles) != 0:
                """
                Database files already exists. reading all
                """
                print "found %d databases" % len(self.dbfiles), self.dbfiles


                for dbfn in sorted(self.dbfiles):
                    dbfnbn     = os.path.basename( dbfn )
                    chromosome = dbfnbn.replace('.pickle.gz', '').replace(db_name+'_', '')
                    if os.path.exists( dbfn ) and os.path.isfile( dbfn ) and os.path.getsize( dbfn ) > 0:
                        print "walking chromosome: %s :: db file %s exists. loading" % (chromosome, dbfn)
                    else:
                        print "walking chromosome: %s :: db file %s DOES NOT EXISTS. ERROR" % (chromosome, dbfn)
                        sys.exit(1)

                    if singlechrom is not None:
                        if chromosome == singlechrom:
                            self.wholedata[ chromosome ] = loads( dbfn )
                        else:
                            pass
                    else:
                        self.wholedata[ chromosome ] = loads( dbfn )


                #p     = Pool(len(self.dbfiles))
                ##p     = Pool(1)
                #procs = []
                #
                #for dbfn in sorted(self.dbfiles):
                #    """
                #    Loads all databases in parallel
                #    """
                #    dbfnbn     = os.path.basename( dbfn )
                #    chromosome = dbfnbn.replace('.pickle.gz', '').replace(db_name+'_', '')
                #
                #    if os.path.exists( dbfn ) and os.path.isfile( dbfn ) and os.path.getsize( dbfn ) > 0:
                #        print "walking chromosome: %s :: db file %s exists. loading" % (chromosome, dbfn)
                #        res = [ chromosome, p.apply_async( loads, [dbfn] ) ]
                #        procs.append( res )
                #        if DEBUG: break
                #
                #
                #for res in procs:
                #    chromosome = res[0]
                #    proc       = res[1]
                #    print "  getting sync data from chromosome", chromosome
                #
                #    proc.wait()
                #    print "  getting sync data from chromosome %s LOADING" % chromosome
                #    db = proc.get()
                #    print "  getting sync data from chromosome %s SAVING"  % chromosome
                #    self.wholedata[ chromosome ] = db
                #    print "  getting sync data from chromosome %s DONE"    % chromosome
                #
                #p.close()
                #p.join()

                #clusterfile = self.db_name + '.pickle.gz.cluster.pickle.gz'
                #print "LOADING CLUSTER DB"
                #if not os.path.exists( clusterfile ):
                #    print "CLUSTER DB %s DOES NOT EXISTS" % clusterfile
                #    sys.exit(1)
                #
                #self.clusters = loads( clusterfile )
                #print "CLUSTER DB %s READ" % clusterfile

            else:
                """
                No database files. creating from raw files (fasta,matrix and newick) into database
                """
                print "found %d databases. reading matrices" % len(self.dbfiles)


                print self.dbfiles

                clusterParams = []
                #cluster_threads=5, cluster_global=False, cluster_dopng=True, cluster_dosvg=True, cluster_dotree=True
                if not cluster_dopng:
                    clusterParams.append( '--nopng' )
                if not cluster_dosvg:
                    clusterParams.append( '--nosvg' )
                if not cluster_dotree:
                    clusterParams.append( '--notree' )
                if not cluster_dorows:
                    clusterParams.append( '--norows' )
                if not cluster_docols:
                    clusterParams.append( '--nocols' )
                if cluster_extension:
                    clusterParams.extend( ['--extension', cluster_extension] )
                if cluster_threads:
                    clusterParams.extend( ['--threads'  , str(cluster_threads)] )

                self.clusters  = {}
                self.wholedata = {}

                print "walking chromosome: reading matrices", 'do pickle', dopickle
                for chromosome  in sorted( os.listdir( self.db_name ) ):
                    chromPath = os.path.join( self.db_name, chromosome )

                    if os.path.isfile( chromPath ):
                        continue

                    if singlechrom is not None:
                        if chromosome != singlechrom:
                            continue
                    else:
                        pass

                    print "walking chromosome: %s" % chromosome

                    if not os.path.isdir( chromPath ):
                        continue


                    files     = os.listdir( chromPath )
                    matrices  = sorted( [ x for x in files if x.endswith('.matrix') ] )
                    bn        = os.path.commonprefix( files )

                    print "BN", bn
                    for bnp in xrange(1, len(bn)):
                        sub = bn[bnp * -1:]
                        print "BNP ",bnp,'SUB',sub
                        try:
                            bni = int( sub )
                        except:
                            print "BNP ",bnp,'SUB',sub,'FAILED'
                            if bnp > 1 and '.' in sub:
                                bn = bn[:(bnp-1) * -1]
                                print "BNP ",bnp,'SUB',sub,'FAILED','TRIMMING', bn
                            break
                    #sys.exit(0)

                    db_fn = self.db_name + '_' + chromosome + '.pickle.gz'
                    db    = [None]*len(matrices)

                    if len( matrices ) == 1:
                        print "only one file. skipping chromosome"
                        continue


                    if read_threads == 1:
                        for matrix_pos in xrange(len( matrices )):
                            matrix_name = matrices[ matrix_pos ]
                            sppindexinv, register = process_matrix( chromosome, bn, chromPath, matrix_name )
                            db[ matrix_pos ] = register
                            if self.sppindexinv is None or len(self.sppindexinv) == 0:
                                self.sppindexinv = sppindexinv
                            else:
                                if len(self.sppindexinv) != len(sppindexinv):
                                    print "wrong umber of species"
                                    sys.exit(1)

                                for s in xrange(len(self.sppindexinv)):
                                    if self.sppindexinv[s] != sppindexinv[s]:
                                        print "species order error: position %d was %s now is %s" % (s, self.sppindexinv[s], sppindexinv[s])
                                        sys.exit(1)

                    else:
                        mpool  = Pool(processes=read_threads)
                        mprocs = []
                        for matrix_pos in xrange(len( matrices )):
                            matrix_name = matrices[ matrix_pos ]
                            mproc       = mpool.apply_async(process_matrix, ( chromosome, bn, chromPath, matrix_name ))
                            mprocs.append( [ matrix_pos, matrix_name, mproc ] )
                        mpool.close()
                        print len(mprocs)
                        #sys.exit(1)

                        while len(mprocs) > 0:
                            mprocf  = []

                            for procnum in xrange(len(mprocs)):
                                matrix_pos, matrix_name, mproc = mprocs[procnum]

                                if mproc.ready():
                                    if not mproc.successful():
                                        mpool.terminate()
                                        print "one or more threads failed"
                                        mproc.get()
                                        sys.exit(1)

                                    print "successful procnum %d matrixpos %d matrixname %s left %d" % (procnum, matrix_pos, matrix_name, len(mprocs))
                                    sppindexinv, register = mproc.get()

                                    if self.sppindexinv is None or len(self.sppindexinv) == 0:
                                        self.sppindexinv = sppindexinv
                                    else:
                                        if len(self.sppindexinv) != len(sppindexinv):
                                            print "wrong umber of species"
                                            sys.exit(1)

                                        for s in xrange(len(self.sppindexinv)):
                                            if self.sppindexinv[s] != sppindexinv[s]:
                                                print "species order error: position %d was %s now is %s" % (s, self.sppindexinv[s], sppindexinv[s])
                                                sys.exit(1)

                                    db[ matrix_pos ] = register
                                    mprocf.append( procnum )

                            for procpos in xrange(len(mprocf)):
                                procnum = mprocf.pop()
                                print "deleting procnum %d" % procnum
                                mprocs.pop( procnum )

                        mpool.join()
                        mpool.terminate()

                    print "walking chromosome: %s :: dumping"  % ( chromosome )
                    if dopickle:
                        dumps( db_fn, db )

                    self.wholedata[ chromosome ] = db

                    if DEBUG:
                        break






                    cluster_name = chromPath + '.pickle.gz'
                    print "walking chromosome: %s :: cluster : %s" % (chromosome, cluster_name)
                    if os.path.exists(cluster_name):
                        print "walking chromosome: %s :: cluster : %s . LOADING"  % (chromosome, cluster_name)
                        self.clusters[ chromosome ] = loads(cluster_name)
                        print "walking chromosome: %s :: cluster : %s . LOADED"   % (chromosome , cluster_name)

                    else:
                        #, cluster_dopng=cluster_dopng, cluster_dosvg=cluster_dosvg, cluster_dotree=cluster_dotree
                        #parser.add_argument('-o' , '--out'   , '--output'   , dest='output'   , default=None     , nargs='?', type=str,  help='output file')
                        #parser.add_argument('-d' , '--dir'   , '--indir'    , dest='indir'    , default=None     , nargs='?', type=str,  help='input dir. alternative to giving file names')
                        #parser.add_argument('-t' , '--thr'   , '--threads'  , dest='threads'  , default=2        , nargs='?', type=int,  help='[optional] number of threads. [default: 5]')
                        #parser.add_argument('-e' , '--ext'   , '--extension', dest='extension', default='.matrix', nargs='?', type=str,  help='[optional] extension to search. [default: .matrix]')
                        #parser.add_argument('-p' , '--nopng' ,                dest='dopng'                       , action='store_false', help='do not export png')
                        #parser.add_argument('-s' , '--nosvg' ,                dest='dosvg'                       , action='store_false', help='do not export svg')
                        #parser.add_argument('-n' , '--notree',                dest='dotree'                      , action='store_false', help='do not export tree. precludes no png and no svg')
                        print "walking chromosome: %s :: cluster : %s . CREATING" % (chromosome, cluster_name)

                        cparams = [ '--output', cluster_name, '--indir', chromPath ]
                        cparams.extend( clusterParams )

                        print "walking chromosome: %s :: cluster : %s . CREATING : PARAMS %s" % (chromosome, cluster_name, str(cparams))
 
                        cluster.main(   cparams       )

                        print "walking chromosome: %s :: cluster : %s . CREATED"  % (chromosome, cluster_name)
                        print "walking chromosome: %s :: cluster : %s . LOADING"  % (chromosome, cluster_name)
                        self.clusters[ chromosome ] = loads( cluster_name )
                        print "walking chromosome: %s :: cluster : %s . LOADED"   % (chromosome, cluster_name)


                if cluster_global:
                    chromPath    = os.path.join( self.db_name, self.db_name )
                    cluster_name = chromPath + '.pickle.gz'
                    print "walking chromosome: %s :: cluster : %s" % ('__global__', cluster_name)
                    if os.path.exists(cluster_name):
                        print "walking chromosome: %s :: cluster : %s . LOADING"  % ('__global__', cluster_name)
                        self.clusters[ '__global__' ] = loads( cluster_name )
                        print "walking chromosome: %s :: cluster : %s . LOADED"   % ('__global__', cluster_name)

                    else:
                        print "walking chromosome: %s :: cluster : %s . CREATING" % ('__global__', cluster_name)

                        cparams = [ '--output', cluster_name, '--indir', self.db_name ]
                        cparams.extend( clusterParams )

                        print "walking chromosome: %s :: cluster : %s . CREATING : PARAMS %s" % ('__global__', cluster_name, str(cparams))

                        cluster.main( cparams )

                        print "walking chromosome: %s :: cluster : %s . CREATED"  % ('__global__', cluster_name)
                        print "walking chromosome: %s :: cluster : %s . LOADING"  % ('__global__', cluster_name)
                        self.clusters[ '__global__' ] = loads(cluster_name)
                        print "walking chromosome: %s :: cluster : %s . LOADED"   % ('__global__', cluster_name)



            self.spps = {}

            if len( self.spps ) == 0:
                print 'index inv', self.sppindexinv
                print 'index    ', self.spps
                for i, k in enumerate( self.sppindexinv ):
                    print " adding",k,"at pos",i+1,"/",len(self.sppindexinv), k
                    self.spps[ k ] = i


        if not os.path.exists( self.spps_fn ):
            """
            Create index database
            """
            if dopickle:
                print "saving spp db", self.spps_fn
                dumps( self.spps_fn, self.spps )
                print "saved spp db", self.spps_fn

        else:
            print "db file SPP %s exists. reading" % self.spps_fn
            self.spps = loads(self.spps_fn)



        if not os.path.exists( self.cluster_fn ):
            """
            Create cluster database
            """
            if dopickle:
                print "saving cluster db", self.cluster_fn
                dumps( self.cluster_fn, self.clusters )
                print "saved cluster db", self.cluster_fn

        else:
            print "db file CLUSTER %s exists. reading" % self.cluster_fn
            self.clusters = loads(self.cluster_fn)


        print "finished reading raw db"

    def read_custom_orders(self, custom_orders_files, spps):
        custom_orders = {}

        if not hasattr(self, 'clusters') or self.clusters is None:
            self.clusters = {}

        print "CLUSTERS", self.clusters

        if len( custom_orders_files ) > 0:
            for fn in custom_orders_files:
                print "READING CUSTOM ORDER", fn
                try:
                    co_chrom, co_name, co_data = self.read_custom_order( fn, spps )
                except:
                    continue

                if co_chrom is None:
                    continue

                if co_chrom not in custom_orders:
                    custom_orders[ co_chrom ] = {}
                custom_orders[ co_chrom ][ co_name ] = co_data

            if len(custom_orders) > 0:
                for co_chrom in custom_orders:
                    if co_chrom not in self.clusters:
                        if co_chrom != '__global__':
                            print "custom order chromosome", co_chrom, "does not exists"
                            sys.exit( 1 )
                        else:
                            self.clusters['__global__'] = {}

                    co_names = custom_orders[ co_chrom ]
                    for co_name in co_names:
                        if co_name in self.clusters[ co_chrom ]:
                            print "invalid custom order name", co_name, ". name already used"
                            sys.exit(1)
                        print "adding cluster %s to chrom %s" % ( co_name, co_chrom )
                        self.clusters[ co_chrom ][ co_name ] = co_names[ co_name ]

    def read_custom_order(self, fn, spps):
        co_chrom      = '__global__'
        co_name       = os.path.basename( fn )
        rows          = []
        cols          = []
        numrows       = 0
        numcols       = 0
        numlines      = 0
        numlinestotal = 0

        if not os.path.exists( fn ):
            print "input custom order file %s does not exists" % fn
            raise Exception('fileMissing', fn)
            #sys.exit(1)

        if not os.path.isfile( fn ):
            print "input custom order file %s is not a file" % fn
            raise Exception('fileFolder', fn)
            #sys.exit(1)

        #print spps

        quited = False

        rowo = []
        #colo = []
        with open( fn, 'r' ) as fhd:
            rownum = -1
            colnum = -1
            for line in fhd:
                line = line.strip()
                numlinestotal += 1

                if len( line ) == 0:
                    continue

                #print line
                if line[0] == '#':
                    if   line.startswith('#ROWNUM='):
                        try:
                            rownum   = int(line[ 8:]) - 1
                            print "custom order file %s rownum %d" % ( fn, rownum )
                        except:
                            print "custom order file %s line %d has invalid row number: %s" % ( fn, numlinestotal, line)
                            sys.exit(1)

                    #elif line.startswith('#COLNUM='):
                    #    try:
                    #        colnum   = int(line[ 9:])
                    #        print "custom order file %s colnum %d" % ( fn, colnum )
                    #    except:
                    #        print "custom order file %s line %d has invalid col number: %s" % ( fn, numlinestotal, line)
                    #        sys.exit(1)

                    elif line.startswith('#NAME='):
                        co_name  =     line[ 6:]
                        print "custom order file %s name %s" % ( fn, co_name )

                    elif line.startswith('#CHROMOSOME='):
                        co_chrom =     line[12:]
                        print "custom order file %s chrom %s" % ( fn, co_chrom )

                    elif line.startswith('#QUIT'):
                        quited = True
                        break

                    continue

                if rownum < 0 and colnum < 0:
                    print "no row number and no col number defined in custom order file", fn
                    sys.exit(1)

                numlines  += 1

                cols       = line.split("\t")

                if rownum >= 0:
                    if rownum + 1 > len(cols):
                        print "custom order file %s defined row order as column %d while there are only %d columns in the file" % ( fn, rownum, len(cols) )
                        sys.exit(1)

                    spp_name    = fixsppname( cols[rownum] )

                    if len(spp_name) > 0:
                        numrows   += 1

                        if spp_name in rowo:
                            print "row %d present twice in custom order file %s line %d" % ( spp_name, fn, numlinestotal )
                            sys.exit(1)

                        if spp_name not in spps:
                            print "custom order file %s line %d has spp %s which does not exists" % ( fn, numlinestotal, spp_name )
                            print spps
                            sys.exit(1)

                        rows.append( spps[ spp_name ] )

                #if colnum >= 0:
                #    if colnum + 1 > len(cols):
                #        print "custom order file %s defined col order as column %d while there are only %d columns in the file" % ( fn, colnum, len(cols) )
                #        sys.exit(1)
                #
                #    col_order     = cols[colnum]
                #
                #    if len(col_order) > 0:
                #        numcols    += 1
                #
                #        if col_order in colo:
                #            print "col order %d present twice in custom order file %s line %d" % ( col_order, fn, numlinestotal )
                #            sys.exit(1)
                #
                #        cols.append( col_order )

        #if len( cols ) == 0 and len( rows ) == 0:
        if len( rows ) == 0:
            print "custom order file %s has no order" % ( fn )
            if quited:
                return ( None, None, None )
            else:
                sys.exit(1)

        if len( spps ) != len( rows ):
            print "custom order file %s has wrong number of species %d != %d" % ( fn, len( spps ), len( rows ))
            sys.exit(1)

        co_data = {
            'cols': {
                'colsOrder'  : None,
                'colsNewick' : None,
                'colsSvg'    : '',
                'colsPng'    : None
            },
            'rows': {
                'rowsOrder'  : rows,
                'rowsNewick' : None,
                'rowsSvg'    : '',
                'rowsPng'    : None
            }
        }

        return ( co_chrom, co_name, co_data )


    def getCluster(self, chrom, ref):
        """
        Get cluster for chromosome
        """
        print "getting matrix for chrom %s ref %s" % ( chrom, ref )

        cdata    = self.clusters[chrom]
        data     = {}
        refi     = self.spps[ref]
        for k in cdata:
            if k == 'clusters':
                data[ k ] = cdata[ k ][ refi ]
            else:
                data[ k ] = cdata[ k ]

        return data


    def getClusterList( self ):
        res = {}
        for chrom in self.clusters:
            res[ chrom ] = []
            for cname in self.clusters[chrom]:
                res[ chrom ].append( cname )
        #print 'getClusterList', self.clusters, res
        return copy.copy( res )


    def getClusterNames( self ):
        return copy.copy( self.clusters )

    def getClusterType(self, chrom, ref, ctype):
        data = self.getCluster( chrom, ref )

        data['clusters'] = data['clusters'][ctype]

        return copy.copy( data )


    ############################################
    ## PHONY
    ############################################
    def getRegister(self, gene, chrom):
        """
        Should be implemented by the superseeding class
        """
        pass


    ############################################
    ## AUXILIARY FUNCTIONS
    ############################################
    def getDbTime(self):
        """
        Ger database creation date
        """
        if self.dbMtime is None:
            print "getting creation time:",self.db_file
            dbMtime         = os.stat( self.db_file ).st_mtime
            dbMtime         = time.ctime( dbMtime )
            self.dbMtime    = dbMtime

        return self.dbMtime


    def concatHashs(self, dictLists):
        """
        Concatenate dictionaries
        """
        res = {}
        for dic in dictLists:
            for key in dic:
                if key in res:
                    res[key] += dic[key]
                else:
                    res[key]  = dic[key]
        return res


def process_matrix( chromosome, bn, chromPath, matrix_name ):
    sys.stdout.write( "\n" )
    sys.stdout.write( "walking chromosome: %s :: matrix : %s bn: %s\n" % ( chromosome, matrix_name, bn ) )

    matrix_path = os.path.join( chromPath, matrix_name )
    tree_path   = matrix_path.replace('.matrix', '.tree')
    fasta_path  = matrix_path.replace('.matrix', '')
    coord_path  = matrix_path.replace('.fasta.matrix', '.' + chromosome + '.fasta.coords')

    sys.stdout.write( "walking chromosome: %s :: matrix : matrix %s\n" % ( chromosome, matrix_path ) )
    sys.stdout.write( "walking chromosome: %s :: matrix : fasta  %s\n" % ( chromosome, fasta_path  ) )
    sys.stdout.write( "walking chromosome: %s :: matrix : coord  %s\n" % ( chromosome, coord_path  ) )
    sys.stdout.write( "walking chromosome: %s :: matrix : tree   %s\n" % ( chromosome, tree_path   ) )


    epitope     = matrix_name.replace( bn, '' ).replace( '.fasta.matrix', '' )
    #print "walking chromosome:", chromosome, 'epitope:',epitope
    #000027040921-000027045187.Solyc04g026380.2.vcf.gz.SL2.40ch04
    #
    #000039950001-000040000000.Frag_SL2.40ch06g50000_039950001_040000000.vcf.gz.fasta.matrix

    dash_pos    = epitope.find( '-'                 )
    dot_pos     = epitope.find( '.'      , dash_pos )
    vcf_pos     = epitope.find( '.vcf.gz', dot_pos  )
    start       = epitope[          :dash_pos]
    end         = epitope[dash_pos+1:dot_pos ]
    name        = epitope[dot_pos +1:vcf_pos ]
    print "star %s end %s name %s" % ( start, end, name )

    len_aln_obj = 0
    len_aln_snp = 0

    try:
        start       = int( start )
        end         = int( end   )
    except:
        print "error parsing file name", matrix_name, "chromosome", chromosome, "epitope", epitope, "dash pos", dash_pos, "dop pos", dot_pos, "vcf pos", vcf_pos, "start", start, "end", end, "name", name
        sys.exit( 1 )

    #print "walking chromosome:", chromosome, 'start  :',start, 'end', end, 'name', name


    if not os.path.isfile(  matrix_path )     :
        print "MATRIX DOES NOT EXISTS", matrix_path
        sys.exit(1)
        return None
    if     os.path.getsize( matrix_path ) == 0:
        print "MATRIX HAS SIZE ZERO", matrix_path
        sys.exit(1)
        return None


    if not os.path.isfile(  fasta_path  )     :
        print "FASTA DOES NOT EXISTS", fasta_path
        sys.exit(1)
        return None
    if     os.path.getsize( fasta_path  ) == 0:
        print "FASTA HAS SIZE ZERO", fasta_path
        sys.exit(1)
        return None


    if not os.path.isfile(  coord_path  )     :
        print "COORD DOES NOT EXISTS", coord_path
        sys.exit(1)
        return None
    if     os.path.getsize( coord_path  ) == 0:
        print "COORD HAS SIZE ZERO", coord_path
        sys.exit(1)
        return None


    if not os.path.isfile(  tree_path   )     :
        sys.exit(1)
        print "TREE DOES NOT EXISTS", tree_path
        return None
    if     os.path.getsize( tree_path   ) == 0:
        print "TREE HAS SIZE ZERO", tree_path
        sys.exit(1)
        return None



    sys.stdout.write( "walking chromosome: %s :: matrix : %s fasta: %s\n" % ( chromosome, matrix_name, fasta_path ) )
    snpSeq      = {}
    lastSnpName = None
    with open( fasta_path, 'r' ) as fhd:
        for line in fhd:
            if len(line) == 0: continue
            line = line.strip()
            if len(line) == 0: continue
            if line[0]   == ">":
                if lastSnpName is not None:
                    len_aln_snp = len(snpSeq[lastSnpName])

                lastSnpName = line[1:]
                snpSeq[lastSnpName] = ""
                continue
            snpSeq[lastSnpName] += line

    sys.stdout.write( "walking chromosome: %s :: matrix : %s fasta: %s DONE\n"       % ( chromosome, matrix_name, fasta_path  ) )
    sys.stdout.write( "walking chromosome: %s :: matrix : %s alignment length: %d\n" % ( chromosome, matrix_name, len_aln_snp ) )
    #for seqName in snpSeq:
        #snpSeq[seqName] = compress(snpSeq[seqName])




    sys.stdout.write( "walking chromosome: %s :: matrix : %s coord: %s\n" % ( chromosome, matrix_name, coord_path) )
    coords = None
    with open( coord_path, 'r' ) as fhd:
        lines = fhd.read().split("\n")
        coordsNum = int(lines[0])
        coords    = [ int(x) for x in lines[1].split('|') ]

        if coordsNum != len(coords):
            print "length of coords %s differs from number of coords %d" % (coordsNum, len(coords))
            sys.exit(1)


    if len_aln_snp != len(coords):
        print "length of SNP %s differs from number of coords %d" % (len_aln_snp, len(coords))
        sys.exit(1)




    sys.stdout.write( "walking chromosome: %s :: matrix : %s tree: %s\n" % ( chromosome, matrix_name, tree_path) )
    tree_str = ""
    with open( tree_path, 'r' ) as fhd:
        for line in fhd:
            if len(line) == 0: break
            line = line.strip()
            if len(line) == 0: break
            tree_str += line



    tree_path_img = tree_path + '.png'
    sys.stdout.write( "walking chromosome: %s :: matrix : %s tree image: %s\n" % ( chromosome, matrix_name, tree_path_img ) )
    tree_img      = None
    if os.path.exists(tree_path_img):
        sys.stdout.write( "walking chromosome: %s :: matrix : %s tree image: %s - EXISTS - Reading\n" % ( chromosome, matrix_name, tree_path_img ) )
        with open(tree_path_img, 'rb') as fho:
            tree_img = fho.read()
    else:
        sys.stdout.write( "walking chromosome: %s :: matrix : %s tree image: %s - DOS NOT EXISTS - Creating\n" % ( chromosome, matrix_name, tree_path_img ) )
        tree_img = newick_to_png.add_seq(tree_str)
        with open(tree_path_img, 'wb') as fho:
            fho.write( tree_img )
        sys.stdout.write( "walking chromosome: %s :: matrix : %s tree image: %s - DOS NOT EXISTS - Creating DONE\n" % ( chromosome, matrix_name, tree_path_img ) )




    sys.stdout.write( "walking chromosome: %s :: matrix : %s tree DONE\n" % ( chromosome, matrix_name ) )
    #tree_str = compress(tree_str)



    sys.stdout.write( "walking chromosome: %s :: matrix : %s reading matrix: %s\n"  % ( chromosome, matrix_name, matrix_path ) )
    data        = []
    sppindexinv = []
    with open( matrix_path, 'r') as fhd:
        linecount = 0
        numspps   = -1

        for line in fhd:
            linecount += 1

            if linecount == 1:
                numspps = int(line.strip())
                continue

            cols     = line.strip().split()

            spp_name = cols[0]

            vals     = [ float(x) for x in cols[1:] ]

            if spp_name not in sppindexinv:
                sppindexinv.append( spp_name )

            #if spp_name not in self.spps:
            #    self.spps[spp_name] = linecount - 2
            #
            #else:
            #    if self.spps[spp_name] != linecount - 2:
            #        print "wrong order"
            #        sys.exit( 1 )

            while len( data ) < len( sppindexinv ):
                data.append( None )

            data[ sppindexinv.index( spp_name ) ] = vals
            #data[ self.sppindexinv.index( spp_name ) ] = vals[:self.sppindexinv.index( spp_name )]

    sys.stdout.write( "walking chromosome: %s :: matrix : %s reading matrix: %s DONE\n"  % ( chromosome, matrix_name, matrix_path ) )
    sys.stdout.write( "\n" )
    sys.stdout.flush()

    register = [None]*NUM_REGISTER_VARS
    register[ DB_START   ] = start
    register[ DB_END     ] = end
    register[ DB_LEN_OBJ ] = 1
    register[ DB_LEN_SNP ] = len_aln_snp
    register[ DB_NAME    ] = name
    register[ DB_TREE    ] = { 'newick': tree_str, 'png'   : tree_img  }
    register[ DB_FASTA   ] = { 'fasta' : snpSeq  , 'coords': coords    }
    register[ DB_LINE    ] = data

    return (sppindexinv, register)
