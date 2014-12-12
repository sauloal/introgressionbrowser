#!/usr/bin/python
import os, sys
import cPickle
import argparse
import copy
import glob
import array
import gzip
import zlib
import base64

from subprocess import call

import multiprocessing
from multiprocessing import Pool, Queue

HAS_IMG = True
try:
    import numpy as NP
    from matplotlib import pyplot as PLT
    from matplotlib import cm     as CM

except:
    HAS_IMG = False


# variables
DEBUG    = True
DEBUG    = False



#constants
DB_START          = 0
DB_END            = 1
DB_LEN_OBJ        = 2
DB_LEN_SNP        = 3
DB_NAME           = 4
DB_TREE           = 5
DB_FASTA          = 6
DB_LINE           = 7
NUM_REGISTER_VARS = 8

curr_path         = os.path.abspath(os.curdir)

spps              = {}
wholedata         = {}
db_file           = None



############################################
## WEBSERVER HELPER FUNCTIONS
############################################

if __name__ != '__main__':
    def getRegister( gene, chrom ):
        data      = getData(chrom)
        dataNames = [ x[DB_NAME] for x in data ]

        try:
            geneindex = dataNames.index(gene)
        except:
            print "no such gene:", gene
            return None

        return data[geneindex]


    def getColumn( gene, chrom, db_index):
        register = getRegister(gene, chrom)

        if register is None:
            return None

        try:
            val = register[db_index]

        except:
            print "no data at index:", db_index
            return None

        return val


    def getRegisterDict(gene, chrom):
        register = getRegister(gene, chrom)

        if register is None:
            return register

        res = reg2dict(register)

        return res


    def reg2dict(register):
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


    def getTree( gene, chrom ):
        return getColumn( gene, chrom, DB_TREE )


    def getAlignment( gene, chrom ):
        return getColumn( gene, chrom, DB_FASTA )


    def getMatrix( gene, chrom ):
        matrix = getColumn( gene, chrom, DB_LINE )

        if matrix is None:
            return matrix

        return matrix


    def getStart( gene, chrom ):
        return getColumn( gene, chrom, DB_START )


    def getEnd( gene, chrom ):
        return getColumn( gene, chrom, DB_END )


    def getLenObj( gene, chrom ):
        return getColumn( gene, chrom, DB_LEN_OBJ )


    def getLenSnp( gene, chrom ):
        return getColumn( gene, chrom, DB_LEN_SNP )


    def getGenes( chrom ):
        data       = getData( chrom )
        genesNames = [ x[DB_NAME] for x in data ]
        return genesNames


    def getSpps():
        return spps.keys()


    def getChroms():
        return wholedata.keys()


    def getData( chrom ):
        return wholedata[ chrom ]


    def make_table(db_name, ref, chrom, res, group_every=None, num_classes=None, evenly=False, startPos=None, endPos=None, maxNum=None, page=None):
        excerpt = filter_by(db_name, ref, group_every=group_every, num_classes=num_classes, evenly=evenly, onlyChrom=chrom)
        data    = excerpt[ chrom ]
        return filter_excerpt(data, res, startPos=startPos, endPos=endPos, maxNum=maxNum, page=page)

    def cluster_table( table ):
        return table


    def filter_excerpt(data, res, startPos=None, endPos=None, maxNum=None, page=None):
        res["header"   ] = {}
        res["data_info"] = {}
        res["data"     ] = { 'name': [], 'line': [] }

        #print excerpt[chromosome_name]
        print "making table: from %s to %s" % (str(startPos), str(endPos))

        sppindexinv = getSppIndexInvert( )

        res["header"]["start"      ] = [ x[DB_START  ] for x in data ]

        res["header"]["end"        ] = [ x[DB_END    ] for x in data ]

        res["header"]["num_unities"] = [ x[DB_LEN_OBJ] for x in data ]

        res["header"]["num_snps"   ] = [ x[DB_LEN_SNP] for x in data ]

        res["header"]["name"       ] = [ x[DB_NAME   ] for x in data ]

        minVal =  999999999
        maxVal = -999999999
        for spp in sppindexinv:
            sppindex = spps[ spp ]
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
            res = filterTable(data, res, startPos, endPos, maxNum, sppindexinv, minVal, maxVal, page)

        res['data_info']["length_abs"    ] = res['data_info']["maxPosAbs"] - res['data_info']["minPosAbs"]
        res['data_info']["length"        ] = res['data_info']["maxPos"   ] - res['data_info']["minPos"   ]

        return res


    def filterTable(data, res, startPos, endPos, maxNum, sppindexinv, minVal, maxVal, page):
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




############################################
## AUXILIARY FUNCTIONS
############################################
def compress(data, compresslevel=9):
    res = zlib.compress(data, level)
    res = base64.b64encode(res).replace("\n", '')
    return res


def decompress(data):
    res = base64.b64decode(data)
    res = zlib.decompress(res)
    return res


def dumps(fn, data, compresslevel=9):
    db_fhd    = gzip.open( fn, 'wb', compresslevel )
    cPickle.dump( data, db_fhd, cPickle.HIGHEST_PROTOCOL )
    db_fhd.close()


def loads(fn):
    print "  loading", fn
    return cPickle.load( gzip.open(fn, 'rb') )


def getDbTime():
    dbMtime         = os.stat(db_file).st_mtime
    dbMtime         = time.ctime(dbMtime)
    return dbMtime


def corr(L1, L2):
    nL1   = 1 / (sum([e1*e1 for e1 in L1]) ** 0.5)
    nL2   = 1 / (sum([e2*e2 for e2 in L2]) ** 0.5)
    corr = sum( [ (e1*nL1)*(e2*nL2) for e1,e2 in zip(L1,L2) ] )

    return corr

############################################
## CORE FUNCTIONS
############################################
def load_data(db_name, print_spps_only=False):
    read_raw      = False
    global db_file

    if db_name.endswith('.sqlite'):
        print "db should not end in .sqlite . you gave me the wront type of file"
        sys.exit(1)

    elif not db_name.endswith('.db'):
        db_file       = db_name + '.db'

    spps_fn       = db_file

    global spps
    global wholedata

    if print_spps_only:
        if os.path.exists( spps_fn ):
            read_raw = False

        else:
            read_raw = True

    else:
        read_raw = True


    if read_raw:
        print "globing",db_name+'_*.db'
        dbfiles = glob.glob(db_name+'_*.db')

        if len(dbfiles) != 0:
            p     = Pool(len(dbfiles))
            procs = []

            for dbfn in sorted(dbfiles):
                dbfnbn     = os.path.basename( dbfn )
                chromosome = dbfnbn.replace('.db', '').replace(db_name+'_', '')

                if os.path.exists( dbfn ) and os.path.isfile( dbfn ) and os.path.getsize( dbfn ) > 0:
                    print "walking chromosome: %s :: db file %s exists. loading" % (chromosome, dbfn)
                    res = [ chromosome, p.apply_async( loads, [dbfn] ) ]
                    procs.append( res )
                    if DEBUG: break

            for res in procs:
                chromosome = res[0]
                proc       = res[1]
                print "  getting sync data from chromosome", chromosome

                proc.wait()
                print "  getting sync data from chromosome %s LOADING" % chromosome
                db = proc.get()
                print "  getting sync data from chromosome %s SAVING"  % chromosome
                wholedata[ chromosome ] = db
                print "  getting sync data from chromosome %s DONE"    % chromosome

            p.close()
            p.join()


        else:
            print dbfiles
            print "walking chromosome: reading matrices"
            for chromosome  in sorted( os.listdir( db_name ) ):
                print "walking chromosome: %s" % chromosome

                chromPath = os.path.join( db_name, chromosome )

                if not os.path.isdir( chromPath ): continue

                db_fn     = db_name + '_' + chromosome + '.db'
                db        = []


                files     = os.listdir( chromPath )
                matrices  = [ x for x in files if x.endswith('.matrix') ]
                bn        = os.path.commonprefix( matrices )

                for matrix_name in sorted( matrices ):
                    print
                    print "walking chromosome: %s :: matrix : %s" % ( chromosome, matrix_name )

                    matrix_path = os.path.join( chromPath, matrix_name )
                    fasta_path  = matrix_path.replace('.matrix', '')
                    tree_path   = fasta_path + '.tree'

                    print "walking chromosome: %s :: matrix : matrix %s" % ( chromosome, matrix_path )
                    print "walking chromosome: %s :: matrix : fasta  %s" % ( chromosome, fasta_path  )
                    print "walking chromosome: %s :: matrix : tree   %s" % ( chromosome, tree_path   )


                    epitope     = matrix_name.replace( bn, '' ).replace( '.fasta.matrix', '' )
                    #print "walking chromosome:", chromosome, 'epitope:',epitope
                    #000027040921-000027045187.Solyc04g026380.2.vcf.gz.SL2.40ch04

                    dash_pos    = epitope.find( '-'                 )
                    dot_pos     = epitope.find( '.'      , dash_pos )
                    vcf_pos     = epitope.find( '.vcf.gz', dot_pos  )
                    start       = epitope[          :dash_pos]
                    end         = epitope[dash_pos+1:dot_pos ]
                    name        = epitope[dot_pos +1:vcf_pos ]

                    len_aln_obj = 0
                    len_aln_snp = 0

                    start       = int( start )
                    end         = int( end   )

                    #print "walking chromosome:", chromosome, 'start  :',start, 'end', end, 'name', name


                    if not os.path.isfile(  matrix_path )     : continue
                    if     os.path.getsize( matrix_path ) == 0: continue

                    if not os.path.isfile(  fasta_path  )     : continue
                    if     os.path.getsize( fasta_path  ) == 0: continue

                    if not os.path.isfile(  tree_path   )     : continue
                    if     os.path.getsize( tree_path   ) == 0: continue

                    print "walking chromosome: %s :: matrix : %s fasta: %s" % ( chromosome, matrix_name, fasta_path )
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
                    print "walking chromosome: %s :: matrix : %s fasta: %s DONE" % ( chromosome, matrix_name, fasta_path )
                    print "walking chromosome: %s :: matrix : %s alignment length: %d" % ( chromosome, matrix_name, len_aln_snp )
                    #for seqName in snpSeq:
                        #snpSeq[seqName] = compress(snpSeq[seqName])

                    print "walking chromosome: %s :: matrix : %s tree: %s" % ( chromosome, matrix_name, tree_path)
                    tree_str = ""
                    with open( tree_path, 'r' ) as fhd:
                        for line in fhd:
                            if len(line) == 0: break
                            line = line.strip()
                            if len(line) == 0: break
                            tree_str += line
                    print "walking chromosome: %s :: matrix : %s tree DONE" % ( chromosome, matrix_name )
                    #tree_str = compress(tree_str)

                    print "walking chromosome: %s :: matrix : %s reading matrix: %s"  % ( chromosome, matrix_name, matrix_path )
                    data = []
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

                            if spp_name not in spps:
                                spps[spp_name] = linecount - 2

                            else:
                                if spps[spp_name] != linecount - 2:
                                    print "wrong order"
                                    sys.exit( 1 )

                            data.append( vals )
                    print "walking chromosome: %s :: matrix : %s reading matrix: %s DONE"  % ( chromosome, matrix_name, matrix_path )


                    register = [None]*NUM_REGISTER_VARS
                    register[DB_START  ] = start
                    register[DB_END    ] = end
                    register[DB_LEN_OBJ] = 1
                    register[DB_LEN_SNP] = len_aln_snp
                    register[DB_NAME   ] = name
                    register[DB_TREE   ] = tree_str
                    register[DB_FASTA  ] = snpSeq
                    register[DB_LINE   ] = data
                    db.append( register )
                    print

                print "walking chromosome: %s :: dumping"  % ( chromosome )
                dumps( db_fn, db )
                if DEBUG: break




    if not os.path.exists( spps_fn ):
        dumps( spps_fn, spps )

    else:
        print "db file %s exists. reading" % spps_fn
        spps = loads(spps_fn)


def genR(chromosome_name, spp_name, in_csv, out_img, out_pdf, out_svg, make_tree=False, make_tree_x=False, make_tree_y=False, pos_extra="", spp_extra=""):
    img_height = 2048
    img_dpi    =  500
    pdf_height =   22

    make_tree_str     = 'Rowv=FALSE, Colv=FALSE, '
    if   make_tree:
        make_tree_str = ""
    elif make_tree_x:
        make_tree_str = 'Rowv=FALSE, Colv=TRUE , '
    elif make_tree_y:
        make_tree_str = 'Rowv=TRUE , Colv=FALSE, '

    data = {
        'chromosome_name': chromosome_name,
        'spp_name'       : spp_name,
        'in_csv'         : in_csv,
        'img_height'     : img_height,
        'img_dpi'        : img_dpi,
        'pdf_height'     : pdf_height,
        'out_img'        : out_img,
        'out_pdf'        : out_pdf,
        'out_svg'        : out_svg,
        'num_colors'     : 30,
        'x_name'         : 'Position' + pos_extra,
        'y_name'         : 'Species'  + spp_extra,
        'make_tree'      : make_tree_str
    }


    #install.packages("heatmap.plus")
    #library("heatmap.plus")
    #require("heatmap.plus")


    #source("http://www.bioconductor.org/biocLite.R")
    #biocLite("ALL")

    # IF R > 3.0
    #source("http://www.bioconductor.org/biocLite.R")
    #install.packages("gplots")
    #biocLite("gplots")

    # ELSE
    #wget http://cran.r-project.org/src/contrib/Archive/gplots/gplots_2.11.0.tar.gz
    #wget http://cran.r-project.org/src/contrib/Archive/gtools/gtools_2.7.0.tar.gz
    #wget http://cran.r-project.org/src/contrib/Archive/gdata/gdata_2.12.0.tar.gz
    #wget http://cran.r-project.org/src/contrib/Archive/caTools/caTools_1.13.tar.gz

    #install.packages("gtools_2.7.0.tar.gz", repos=NULL, type="source")
    #install.packages("gdata_2.12.0.tar.gz", repos=NULL, type="source")
    #install.packages("caTools_1.13.tar.gz", repos=NULL, type="source")
    #install.packages("gplots_2.11.0.tar.gz", repos=NULL, type="source")




    #nba <- read.csv("/tmp/heat.csv", sep=",")
    #nba <- read.csv(file="/dev/stdin", sep=",", header=TRUE)
    #nba
    #nba

    #http://www2.warwick.ac.uk/fac/sci/moac/people/students/peter_cock/r/heatmap/
    #nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=cm.colors(256)  , scale="column", margins=c(5,10)) # blue
    #nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10)) # red
    #nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
    #nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
    #nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
    #nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), cexRow=0.5, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
    #nba_heatmap <- heatmap(nba_matrix, Rowv=NA, Colv=NA, col=heat.colors(256), scale="column", margins=c(5,10), cexRow=0.5, cexCol=0.1, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
    #density.info="none",
    #topo.colors(50)  # blue-gree-yellow
    #heat.colors(256) # red yellow
    #cm.colors(256)   # blue


    #require('Cairo')
    #apt-get install libpixman-1-dev libcairo2-dev
    #CairoPNG("%(out_img)s", width=img_width, height=img_height, bg="transparent", units="px", res=img_dpi, type="cairo-png", antialias="none")
    #CairoPDF("%(out_pdf)s", width=pdf_width, height=pdf_height, title=main_name, compress=TRUE)



    #svg("%(out_svg)s", width=pdf_width, height=pdf_height)
    #CairoSVG("%(out_svg)s", width=pdf_width, height=pdf_height)
    #nba_heatmap <- heatmap.2(nba_matrix, col=heat.colors(%(num_colors)d), symkey=FALSE, %(make_tree)strace="none", scale="column", margins=c(5,10), key=TRUE, cexRow=pdf_cex_row, cexCol=pdf_cex_col, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
    #dev.off()

    #library(ggplot2)
    #library(reshape2)
    #library(scales)
    #library(plyr)

    #base_size <- 9

    #nba.m    <- melt(nba)
    #nba.m    <- ddply(nba.m, .(variable), transform, rescale = rescale(value))
    #nba.s    <- ddply(nba.m, .(variable), transform, rescale = scale(  value))


    #(p <- ggplot(nba.s, aes(variable, name)) + geom_tile(aes(fill = rescale), colour="white") + scale_fill_gradient(low = "white", high = "steelblue"))

    #ggsave(file="test.svg", plot=p)


    R = """\
library("ALL")
data("ALL")



library("gplots")

in_csv    <- "%(in_csv)s"
main_name <- "Gene by gene phylogeny\nChromosome: %(chromosome_name)s\nReference Species: %(spp_name)s"
x_name    <- "%(x_name)s"
y_name    <- "%(y_name)s"

img_height  = %(img_height)d
img_width   = img_height * 3
img_dpi     = %(img_dpi)s
img_cex_row = 0.25
img_cex_col = 0.15
pdf_height  = %(pdf_height)d
pdf_width   = pdf_height * 3
pdf_cex_row = 1
pdf_cex_col = .8

nba <- read.csv(file=in_csv, sep=",", header=TRUE)

row.names( nba ) <- nba$name
nba <- nba[,2:length(nba)]

nba_matrix     <- data.matrix( nba )

png("%(out_img)s", width=img_width, height=img_height, bg="transparent", units="px", res=img_dpi, type="cairo-png", antialias="none")
nba_heatmap <- heatmap.2(nba_matrix, col=heat.colors(%(num_colors)d), symkey=FALSE, %(make_tree)strace="none", scale="column", margins=c(5,10), key=TRUE, cexRow=img_cex_row, cexCol=img_cex_col, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
dev.off()

pdf("%(out_pdf)s", width=pdf_width, height=pdf_height, title=main_name, compress=TRUE)
nba_heatmap <- heatmap.2(nba_matrix, col=heat.colors(%(num_colors)d), symkey=FALSE, %(make_tree)strace="none", scale="column", margins=c(5,10), key=TRUE, cexRow=pdf_cex_row, cexCol=pdf_cex_col, main=main_name, xlab=x_name, ylab=y_name) # red + dendrogram
dev.off()
""" % data

    return R


def getSppIndexInvert( ):
    sppindexinv = [None]*len(spps)
    for k in spps:
        #print " adding",k,"at pos",spps[k],"/",len(spps)
        sppindexinv[ spps[k] ] = k
    return sppindexinv


def filter_by(db_name, inspp, group_every=None, num_classes=None, evenly=False, onlyChrom=None):
    print "ordering %s" % inspp

    if len( wholedata ) == 0:
        print "ordering %s :: chromosome database does not exists. reading raw matrices" % ( inspp )
        load_data(db_name, print_spps_only=False)
        print "ordering %s :: chromosome database created" % ( inspp )

    excerpt = filter_data(inspp, group_every=group_every, num_classes=num_classes, evenly=evenly, onlyChrom=onlyChrom)

    return excerpt


def filter_data(inspp, group_every=None, num_classes=None, evenly=False, onlyChrom=None):
    excerpt     = {}

    chromsToFilter = wholedata.keys()
    if onlyChrom is not None:
        if onlyChrom not in wholedata:
            print "ordering %s :: chromosome %s does not exists" % ( inspp, str(onlyChrom) )
            return None
        chromsToFilter = [ onlyChrom ]

    for chromosome_name in sorted(chromsToFilter):
        print "ordering %s :: chromosome %s" % ( inspp, chromosome_name )

        db       = wholedata[ chromosome_name ]
        filter_db(inspp, chromosome_name, db, excerpt, group_every=group_every, num_classes=num_classes, evenly=evenly)

    return excerpt


def filter_db(inspp, chromosome_name, db, excerpt, group_every=None, num_classes=None, evenly=False):
    if evenly:
        group_every = None
        num_classes = None

    if group_every is not None:
        num_classes = None


    sppindex    = spps[ inspp ]
    sppindexinv = getSppIndexInvert( )


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
    for register in db:
        #print "ordering %s :: chromosome %s register %d" % ( inspp, chromosome_name, registerNum )
        #print registerNum,

        start       = register[DB_START  ]
        end         = register[DB_END    ]
        len_aln_obj = register[DB_LEN_OBJ]
        len_aln_snp = register[DB_LEN_SNP]
        name        = register[DB_NAME   ]
        #tree        = register[DB_TREE   ]
        #fasta       = register[DB_FASTA  ]
        data        = register[DB_LINE   ]
        line        = []

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

        if group_every is None:
            register_new          = copy.copy( register )
            register_new[DB_LINE] = line

            excerpt[ chromosome_name ].append( register_new )

        else:
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
                register_new[DB_START  ] = lastStart     * group_every
                register_new[DB_END    ] = (lastStart+1) * group_every
                register_new[DB_NAME   ] = str(register_new[DB_START]) + ".." + str(register_new[DB_END  ]) + "(%d;%d)" % (lastLenOBJ, lastLenSNP)
                #register_new[DB_TREE   ] = "\n".join(lastTrees)
                #register_new[DB_FASTA  ] = concatHashs(lastFastas)
                #register_new[DB_NAME  ] = ";".join( lastNames )
                register_new[DB_LEN_OBJ] = lastLenOBJ
                register_new[DB_LEN_SNP] = lastLenSNP
                register_new[DB_LINE   ] = avg_data

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
            register_new[DB_START  ] = lastStart     * group_every
            register_new[DB_END    ] = (lastStart+1) * group_every
            register_new[DB_NAME   ] = str(register_new[DB_START]) + ".." + str(register_new[DB_END  ]) + "(%d;%d)" % (lastLenOBJ, lastLenSNP)
            #register_new[DB_TREE   ] = "\n".join(lastTrees)
            #register_new[DB_FASTA  ] = concatHashs(lastFastas)
            #register_new[DB_NAME  ] = ";".join( lastNames )
            register_new[DB_LEN_OBJ] = lastLenOBJ
            register_new[DB_LEN_SNP] = lastLenSNP
            register_new[DB_LINE   ] = avg_data

            excerpt[ chromosome_name ].append( register_new )

            lastLenOBJ = 0
            lastLenSNP = 0
            lastNames  = [  ]
            #lastTrees  = [  ]
            #lastFastas = [  ]
            lastDatas  = [  ]

    print "ordering %s :: chromosome %s done" % ( inspp, chromosome_name )


def order_by( db_name, inspp, outfolder=curr_path, make_csv=True, make_graph=False, make_tree=False, make_tree_x=False, make_tree_y=False, group_every=None, num_classes=None, evenly=False ):
    db_name_short = os.path.basename(db_name).replace('.db', '')

    if inspp not in spps:
        print "requested species(%s) does not exist" % inspp
        print spps
        sys.exit( 1 )


    pos_extra = ""
    spp_extra = ""

    db_fn     = os.path.join( outfolder, db_name_short + '.db.' + inspp )

    if   group_every is not None:
        db_fn     += ".every_"   + str(group_every)
        pos_extra += " - every %dbp" % group_every

    elif num_classes is not None:
        db_fn     += ".classes_" + str(num_classes)
        pos_extra += " - in %d groups" % num_classes

    elif evenly:
        db_fn     += ".evenly"

    if make_tree:
        db_fn     += ".tree"
        spp_extra += " with clustering"
        pos_extra += " with clustering"

    elif make_tree_x:
        db_fn     += ".treex"
        pos_extra += " with clustering"

    elif make_tree_y:
        db_fn     += ".treey"
        spp_extra += " with clustering"

    db_fn  += '.db'

    excerpt   = {}

    if os.path.exists( db_fn ):
        print "ordering %s :: db file %s exists. reading" % ( inspp, db_fn )
        excerpt = loads( db_fn )

    else:
        print "ordering %s :: db file %s does not exists. parsing" % ( inspp, db_fn )
        excerpt = filter_by(db_name, inspp, group_every=None, num_classes=None, evenly=False)

        #leng = max([len(x) for x in spps])
        #fmt  = " %-"+str(leng)+"s: %12d %12d "

        #for chromosome_name in excerpt:
        #    print " ", chromosome_name
        #    for start, end, name, line in excerpt[ chromosome_name ]:
        #        print "    %-12s %12d %12d %s" % ( name, start, end, str(line) )

        print "ordering %s :: ordered :: dumping" % inspp
        dumps( db_fn, excerpt )
        print "ordering %s :: ordered :: done" % inspp


    sppindex    = spps[ inspp ]
    sppindexinv = getSppIndexInvert( )


    if make_csv or make_graph:
        print "ordering %s :: exporting" % inspp

        fhdcsv = None
        if make_csv:
            fhdcsv = open(db_fn + '.csv', 'w')

        for chromosome_name in sorted(excerpt):
            hlines = []
            dlines = []
            #print excerpt[chromosome_name]

            if make_csv:
                hlines.append( chromosome_name + "\n" )
                hlines.append( "start,"  )
                hlines.append( ",".join([ str(x[DB_START  ] ) for x in excerpt[chromosome_name] ]) )
                hlines.append( "\n" )

                hlines.append( "end,"  )
                hlines.append( ",".join([ str(x[DB_END    ] ) for x in excerpt[chromosome_name] ]) )
                hlines.append( "\n" )

                hlines.append( "num_unities,"  )
                hlines.append( ",".join([ str(x[DB_LEN_OBJ] ) for x in excerpt[chromosome_name] ]) )
                hlines.append( "\n" )

                hlines.append( "num_snps,"  )
                hlines.append( ",".join([ str(x[DB_LEN_SNP] ) for x in excerpt[chromosome_name] ]) )
                hlines.append( "\n" )

            dlines.append( "name,"  )
            dlines.append( ",".join([     str(x[DB_NAME   ] ) for x in excerpt[chromosome_name] ]) )
            dlines.append( "\n" )

            for spp in sppindexinv:
                sppindex = spps[ spp ]
                data     = []

                for x in excerpt[chromosome_name]:
                    xline = x[DB_LINE]
                    val   = xline[sppindex]
                    data.append( str(val) )

                dlines.append( spp + ","  )
                dlines.append( ",".join( data ) )
                dlines.append( "\n" )


            if make_csv:
                print "ordering %s :: exporting :: exporting chromosome %s to csv" % (inspp, chromosome_name)

                fhdcsv.writelines( hlines      )
                fhdcsv.writelines( dlines      )
                fhdcsv.write(      "\n\n=\n\n" )


            if make_graph:
                print "ordering %s :: exporting :: exporting chromosome %s to image" % (inspp, chromosome_name)
                #Rscript heat.R < /tmp/heat.csv

                pos_extra_str = pos_extra
                if evenly:
                    db             = excerpt[ chromosome_name ]
                    dbLen          = len(db)
                    chromLen       = db[-1][DB_END] - db[0][DB_START]

                    num_classes    = dbLen

                    group_every    = int(chromLen / num_classes)

                    pos_extra_str += " - evenly distributed %dbp in %d groups of %dbp" % (chromLen, dbLen, group_every)


                fn_R   = db_fn + '.csv.%s.R'        % chromosome_name
                fn_R_o = db_fn + '.csv.%s.R.stdout' % chromosome_name
                fn_R_e = db_fn + '.csv.%s.R.stderr' % chromosome_name
                fn_Png = db_fn + '.csv.%s.png'      % chromosome_name
                fn_Pdf = db_fn + '.csv.%s.pdf'      % chromosome_name
                fn_Svg = db_fn + '.csv.%s.svg'      % chromosome_name
                fn_csv = db_fn + '.csv.%s.csv'      % chromosome_name

                R = genR(chromosome_name, inspp, fn_csv, fn_Png, fn_Pdf, fn_Svg, make_tree=make_tree, make_tree_x=make_tree_x, make_tree_y=make_tree_y, pos_extra=pos_extra_str, spp_extra=spp_extra)

                with open( fn_csv, 'w' ) as fhdcsvr:
                    fhdcsvr.writelines( dlines )

                with open( fn_R, 'w' ) as fhd:
                    fhd.write( R )

                print "ordering %s :: exporting :: exporting chromosome %s to image :: running R script: %s" % (inspp, chromosome_name, fn_R)
                #print R

                call(["Rscript", fn_R], stdout=open(fn_R_o, 'wb'), stderr=open(fn_R_e, 'wb'))

                #to_img( db_name, spps, dlines, inspp )

                print "ordering %s :: exporting :: exported  chromosome %s to image" % (inspp, chromosome_name)
                print
        print "ordering %s :: exporting :: done" % inspp


def concatHashs(dictLists):
    res = {}
    for dic in dictLists:
        for key in dic:
            if key in res:
                res[key] += dic[key]
            else:
                res[key]  = dic[key]
    return res


def main():
    parser = argparse.ArgumentParser(description='Generates a gene by gene tree.')

    parser.add_argument( '-g' , '--graph'    ,               dest='graph'    ,               action='store_true' ,                                              help='Export graphics'                         )
    parser.add_argument( '-tx', '--treex'    ,               dest='treex'    ,               action='store_true' ,                                              help='Make graph with clustering tree for x (position) (changes position order)')
    parser.add_argument( '-ty', '--treey'    ,               dest='treey'    ,               action='store_true' ,                                              help='Make graph with clustering tree for y (species ) (changes species  order)')
    parser.add_argument( '-t' , '--tree'     ,               dest='tree'     ,               action='store_true' ,                                              help='Make graph with clustering tree for x and y      (changes species and position orders)')
    parser.add_argument( '-n' , '--no-csv'   ,               dest='csv'      ,               action='store_false',                                              help='DO NOT export CSV'                       )

    parser.add_argument( '-s' , '--spp'      , '--species' , dest='species'  , default=[]  , action='append'     ,                                    type=str, help='Export only the following species [all]' )
    parser.add_argument( '-o' , '--outfolder',               dest='outfolder', default=None,                                  metavar='out folder'  , type=str, help='Output Folder [Default: .]'              )

    parser.add_argument( '-c' , '--cluster'  ,               dest='cluster'  , default=None,                                  metavar='Cluster N bp', type=int, help='Cluster every N bp [default: per gene]'  )
    parser.add_argument( '-C' , '--classes'  ,               dest='classes'  , default=None,                                  metavar='cluster N cl', type=int, help='Cluster in N classes [default: per gene]'  )
    parser.add_argument( '-e' , '--evenly'   ,               dest='evenly'   ,               action='store_true' ,                                              help='Cluster the features at evenly spaced intervals[default: per gene]')

    parser.add_argument( '-D' , '--DEBUG'    ,               dest='DEBUG'    ,               action='store_true' ,                                              help='DEBUG MODE'                              )
    parser.add_argument( '-l' , '--list'     ,               dest='lst'      ,               action='store_true' ,                                              help='List available species and quits'        )
    parser.add_argument( '-p' , '--pickle'   ,               dest='pickle'   ,               action='store_true' ,                                              help='Pickle only'                             )
    parser.add_argument( '-d' , '--db'       , '--database', dest='ddb'      , default=None,                                  metavar='input db'    , type=str, help='Input db'                                )
    parser.add_argument( 'db' ,                                                default=None, action='store'      , nargs='?', metavar='input db'    , type=str, help='Input db'                                )

    options = parser.parse_args()

    global DEBUG
    DEBUG = DEBUG or options.DEBUG

    make_graph      = options.graph
    make_tree       = options.tree
    make_tree_x     = options.treex
    make_tree_y     = options.treey
    make_csv        = options.csv

    req_spps        = options.species
    outfolder       = options.outfolder

    cluster         = options.cluster
    classes         = options.classes
    evenly          = options.evenly

    print_spps_only = options.lst
    pickle_only     = options.pickle
    db_name         = options.db if options.db is not None else options.ddb
    print_all       = False

    if db_name is not None:
        db_name = db_name.strip("/")

        if outfolder is None:
            db_name_short = os.path.basename( db_name ).replace('.db', '')
            outfolder     = os.path.join( curr_path, db_name_short)

            if len(req_spps) == 0:
                outfolder += '_all'
            else:
                outfolder += '_' + '_'.join(req_spps)

            if evenly:
                outfolder += '_evenly'
            elif classes is not None:
                outfolder += '_classes_' + str(classes)
            elif cluster is not None:
                outfolder += '_cluster_' + str(cluster)

            if make_tree:
                outfolder += '_tree'
            if make_tree_x:
                outfolder += '_treex'
            if make_tree_y:
                outfolder += '_treey'

            outfolder.rstrip('_')

    #print "options", options

    print "DB NAME                           :", db_name
    print "SPECIES                           :", req_spps
    print "OUTPUT FOLDER                     :", outfolder
    print "PRINT SPECIES NAMES AND QUIT      :", print_spps_only

    print "CLUSTER AT EVENLY SPACED INTERVALS:", evenly
    print "CLUSTER IN n CLASSES              :", classes
    print "CLUSTER EVERY n BP                :", cluster

    print "PRINT ALL SPECIES                 :", print_all
    print "MAKE CSV                          :", make_csv
    print "MAKE GRAPHICS                     :", make_graph
    print "              W/ TREE             :", make_tree
    print "              W/ TREE X           :", make_tree_x
    print "              W/ TREE Y           :", make_tree_y

    print "HAS_IMG                           :", HAS_IMG

    if db_name is None:
        print "no input db given"
        print parser.print_help()
        sys.exit( 1 )


    if (not os.path.exists( db_name )) and (not os.path.exists( db_name + '.db' )):
        print "input file %s[.db] does not exists" % db_name
        print parser.print_help()
        sys.exit( 1 )

    if len( req_spps ) == 0:
        print_all = True

    if make_graph and ( not HAS_IMG ):
        print "NO SCIPY OR MATPLOT INSTALLED. NO IMAGE"
        make_graph = False

    if not os.path.exists( outfolder ):
        os.makedirs( outfolder )



    if pickle_only:
        load_data(db_name, print_spps_only=False)
        print "data loaded"
        print "finished pickling"
        sys.exit( 0 )

    else:
        load_data(db_name, print_spps_only=True)
        print "data loaded"



    if print_spps_only:
        leng = max([len(x) for x in spps])
        fmt  = " %-"+str(leng)+"s: %d"

        for sppname in spps:
            print fmt % ( sppname, spps[sppname] )

        print "finished printing species"
        sys.exit( 0 )






    if print_all:
        req_spps = sorted( spps.keys() )



    if len( req_spps ) == 0:
        print "no species to process. can't do anything"
        sys.exit( 1 )



    for spp in req_spps:
        if spp not in spps:
            print "required specie %s does not exists" % spp
            print spps
            sys.exit( 1 )



    for spp in req_spps:
        print "parsing spp:", spp
        order_by( db_name, spp, outfolder=outfolder, make_csv=make_csv, make_graph=make_graph, make_tree=make_tree, make_tree_x=make_tree_x, make_tree_y=make_tree_y, group_every=cluster, num_classes=classes, evenly=evenly )
        print "parsing spp:", spp, 'done'




if __name__ == '__main__': main()
