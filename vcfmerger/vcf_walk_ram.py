#!/usr/bin/env python
"""
Library to access the RAM database
Uses WALK_OUT's WALKER class
"""
import os
import sys

from subprocess import call


HAS_IMG = True





#constants

curr_path         = os.path.abspath(os.curdir)


print "importing vcf_walk"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'.')))
from vcf_walk import walker
from vcf_walk import DEBUG
import vcf_walk




class manager(walker):
    """
    Manages all queries and buffer.
    Extends the walker class which contains the filtering algorithm
    """
    def __init__( self ):
        walker.__init__(self)

        self.spps              = {}
        self.wholedata         = {}
        self.db_name           = None
        self.db_file           = None
        self.dataNames         = None
        self.dbMtime           = None
        self.spps_fn           = None
        self.sppindexinv       = None


    def _getRegister( self, gene, chrom ):
        """
        Get the full register from a gene. Tree and alignment included
        """
        data      = self.getData(chrom)
        dataNames = [ x[ vcf_walk.DB_NAME ] for x in data ]

        try:
            geneindex = self.dataNames.index(gene)

        except:
            print "no such gene:", gene
            return None

        return data[geneindex]

    def _getColumn( self, gene, chrom, db_index ):
        """
        get a specific column from a specific register
        """
        register = self._getRegister(gene, chrom)

        if register is None:
            return None

        try:
            val = register[db_index]

        except:
            print "no data at index:", db_index
            return None

        return val

    def getTree( self, gene, chrom ):
        """
        Get the phyagenetic tree of a gene
        """
        return self._getColumn( gene, chrom, vcf_walk.DB_TREE )

    def getAlignment( self, gene, chrom ):
        """
        Get the fasta alignment of a gene
        """
        return self._getColumn( gene, chrom, vcf_walk.DB_FASTA )

    def getMatrix( self, gene, chrom ):
        """
        Get the distance matrix of a gene
        """
        matrix = self._getColumn( gene, chrom, vcf_walk.DB_LINE )

        if matrix is None:
            return matrix

        return matrix

    def getRow( self, gene, chrom, sppi ):
        matrix = self.getMatrix( gene, chrom )
        if matrix is None:
            return matrix
        return matrix[ sppi ]

    def getStart( self, gene, chrom ):
        """
        Get the start position of a gene
        """
        return self._getColumn( gene, chrom, vcf_walk.DB_START )

    def getEnd( self, gene, chrom ):
        """
        Get the end position of a gene
        """
        return self._getColumn( gene, chrom, vcf_walk.DB_END )

    def getLenObj( self, gene, chrom ):
        """
        Get number of sub-objects a fragment
        """
        return self._getColumn( gene, chrom, vcf_walk.DB_LEN_OBJ )

    def getLenSnp( self, gene, chrom ):
        """
        Get the number of SNPs in a gene
        """
        return self._getColumn( gene, chrom, vcf_walk.DB_LEN_SNP )

    def getGenes( self, chrom ):
        """
        Get a list of all the genes in a chromosome
        """
        data       = self.getData( chrom )
        genesNames = [ x[ vcf_walk.DB_NAME ] for x in data ]

        return genesNames

    def getSpps(self):
        """
        Get a list of all species
        """
        return self.spps.keys()

    def getChroms(self):
        """
        Get a list of all chromosomes
        """
        return self.wholedata.keys()

    def getData( self, chrom ):
        """
        Get all the data of a chromosome
        """
        return self.wholedata[ chrom ]

    def order_by( self, inspp, outfolder=curr_path, make_csv=True, make_graph=False, make_tree=False, make_tree_x=False, make_tree_y=False, group_every=None, num_classes=None, evenly=False ):
        """
        Order and export data
        """
        db_name_short = os.path.basename(self.db_name).replace('.pickle.gz', '')

        if inspp not in self.spps:
            print "requested species(%s) does not exist" % inspp
            print self.spps
            sys.exit( 1 )


        pos_extra = ""
        spp_extra = ""

        db_fn     = os.path.join( outfolder, db_name_short + '.pickle.gz.' + inspp )

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

        db_fn  += '.pickle.gz'

        excerpt   = {}

        if os.path.exists( db_fn ):
            print "ordering %s :: db file %s exists. reading" % ( inspp, db_fn )
            excerpt = vcf_walk.loads( db_fn )

        else:
            print "ordering %s :: db file %s does not exists. parsing" % ( inspp, db_fn )
            excerpt = self.filter_by(inspp, group_every=None, num_classes=None, evenly=False)

            #leng = max([len(x) for x in spps])
            #fmt  = " %-"+str(leng)+"s: %12d %12d "

            #for chromosome_name in excerpt:
            #    print " ", chromosome_name
            #    for start, end, name, line in excerpt[ chromosome_name ]:
            #        print "    %-12s %12d %12d %s" % ( name, start, end, str(line) )

            print "ordering %s :: ordered :: dumping" % inspp
            vcf_walk.dumps( db_fn, excerpt )
            print "ordering %s :: ordered :: done" % inspp


        sppindex    = self.spps[ inspp ]
        sppindexinv = self.getSppIndexInvert( )


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
                    hlines.append( ",".join([ str(x[vcf_walk.DB_START  ] ) for x in excerpt[chromosome_name] ]) )
                    hlines.append( "\n" )

                    hlines.append( "end,"  )
                    hlines.append( ",".join([ str(x[vcf_walk.DB_END    ] ) for x in excerpt[chromosome_name] ]) )
                    hlines.append( "\n" )

                    hlines.append( "num_unities,"  )
                    hlines.append( ",".join([ str(x[vcf_walk.DB_LEN_OBJ] ) for x in excerpt[chromosome_name] ]) )
                    hlines.append( "\n" )

                    hlines.append( "num_snps,"  )
                    hlines.append( ",".join([ str(x[vcf_walk.DB_LEN_SNP] ) for x in excerpt[chromosome_name] ]) )
                    hlines.append( "\n" )

                dlines.append( "name,"  )
                dlines.append( ",".join([     str(x[vcf_walk.DB_NAME   ] ) for x in excerpt[chromosome_name] ]) )
                dlines.append( "\n" )

                for spp in sppindexinv:
                    sppindex = self.spps[ spp ]
                    data     = []

                    for x in excerpt[chromosome_name]:
                        xline = x[vcf_walk.DB_LINE]
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
                        chromLen       = db[-1][vcf_walk.DB_END] - db[0][vcf_walk.DB_START]

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





############################################
## CORE FUNCTIONS
############################################


def genR(chromosome_name, spp_name, in_csv, out_img, out_pdf, out_svg, make_tree=False, make_tree_x=False, make_tree_y=False, pos_extra="", spp_extra=""):
    """
    Creates R script to generate static PNG/PDF output
    """
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




def main(args):
    """
    Command line interface
    """

    man = manager()

    parser, options = man.getOpts( args )

    print options

    global DEBUG
    DEBUG = DEBUG or options.DEBUG

    make_graph         = options.graph
    make_tree          = options.tree
    make_tree_x        = options.treex
    make_tree_y        = options.treey
    make_csv           = options.csv
    read_threads       = options.read_threads

    req_spps           = options.species
    outfolder          = options.outfolder

    cluster            = options.cluster
    classes            = options.classes
    evenly             = options.evenly

    print_spps_only    = options.lst
    pickle_only        = options.pickle
    dopickle           = options.dopickle
    db_name            = options.db

    cluster_extension  = options.cluster_extension
    cluster_global     = options.cluster_global
    cluster_threads    = options.cluster_threads
    cluster_dopng      = options.cluster_dopng
    cluster_dosvg      = options.cluster_dosvg
    cluster_dotree     = options.cluster_dotree
    cluster_dorows     = options.cluster_dorows
    cluster_docols     = options.cluster_docols

    print_all          = False

    if db_name is None:
        print "no input db given"
        print parser.print_help()
        sys.exit( 1 )

    if db_name is not None:
        db_name = db_name.strip("/")

        #if outfolder is None:
        #    db_name_short = os.path.basename( db_name ).replace('.pickle.gz', '')
        #    outfolder     = os.path.join( curr_path, db_name_short)
        #
        #    if len(req_spps) == 0:
        #        outfolder += '_all'
        #    else:
        #        outfolder += '_' + '_'.join(req_spps)
        #
        #    if evenly:
        #        outfolder += '_evenly'
        #    elif classes is not None:
        #        outfolder += '_classes_' + str(classes)
        #    elif cluster is not None:
        #        outfolder += '_cluster_' + str(cluster)
        #
        #    if make_tree:
        #        outfolder += '_tree'
        #    if make_tree_x:
        #        outfolder += '_treex'
        #    if make_tree_y:
        #        outfolder += '_treey'
        #
        #    outfolder.rstrip('_')

    #print "options", options

    print "DB NAME                           :", db_name
    print "SPECIES                           :", req_spps
    #print "OUTPUT FOLDER                     :", outfolder
    print "PRINT SPECIES NAMES AND QUIT      :", print_spps_only
    print "PICKLE ONLY                       :", pickle_only
    print "DO PICKLE                         :", dopickle

    print "CLUSTER AT EVENLY SPACED INTERVALS:", evenly
    print "CLUSTER IN n CLASSES              :", classes
    print "CLUSTER EVERY n BP                :", cluster

    print "PRINT ALL SPECIES                 :", print_all
    print "MAKE CSV                          :", make_csv
    print "MAKE GRAPHICS                     :", make_graph
    print "              W/ TREE             :", make_tree
    print "              W/ TREE X           :", make_tree_x
    print "              W/ TREE Y           :", make_tree_y

    print "CLUSTER THREADS                   :", cluster_threads
    print "CLUSTER EXTENSION                 :", cluster_extension
    print "CLUSTER GLOBAL                    :", cluster_global
    print "CLUSTER DO PNG                    :", cluster_dopng
    print "CLUSTER DO SVG                    :", cluster_dosvg
    print "CLUSTER DO TREE                   :", cluster_dotree
    print "CLUSTER DO ROWS                   :", cluster_dorows
    print "CLUSTER DO COLS                   :", cluster_docols

    print "HAS_IMG                           :", HAS_IMG



    if (not os.path.exists( db_name )) and (not os.path.exists( db_name + '.pickle.gz' )):
        print "input file %s[.pickle.gz] does not exists" % db_name
        print parser.print_help()
        sys.exit( 1 )

    if len( req_spps ) == 0:
        print_all = True

    if make_graph and ( not HAS_IMG ):
        print "NO SCIPY OR MATPLOT INSTALLED. NO IMAGE"
        make_graph = False

    if (pickle_only and ( not dopickle )):
        print "pickle only and no picke are incompatible"
        sys.exit(1)

    #if not os.path.exists( outfolder ):
    #    os.makedirs( outfolder )





    print "loading database"

    man.load_data(
                    db_name,
                    print_spps_only   = False,
                    read_threads      = read_threads,
                    dopickle          = dopickle,
                    cluster_extension = cluster_extension,
                    cluster_threads   = cluster_threads,
                    cluster_global    = cluster_global,
                    cluster_dopng     = cluster_dopng,
                    cluster_dosvg     = cluster_dosvg,
                    cluster_dotree    = cluster_dotree,
                    cluster_dorows    = cluster_dorows,
                    cluster_docols    = cluster_docols
                )

    print "data loaded"

    if pickle_only:
        print "pickling"
        print "finished pickling"
        sys.exit( 0 )


    spps = man.getSpps()

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
        man.order_by(   spp,
                        outfolder=outfolder,
                        make_csv=make_csv,
                        make_graph=make_graph,
                        make_tree=make_tree,
                        make_tree_x=make_tree_x,
                        make_tree_y=make_tree_y,
                        group_every=cluster,
                        num_classes=classes,
                        evenly=evenly
                    )
        print "parsing spp:", spp, 'done'



if __name__ == '__main__':
    main(sys.argv[1:])
