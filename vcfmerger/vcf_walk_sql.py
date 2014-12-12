#!/usr/bin/python
"""
Library to access the SQLite database
Uses WALK_OUT's WALKER class
"""
import os, sys
import time
import copy
import zlib
import cPickle

from pprint import pprint as pp

print "importing vcf_walk sql"
sys.path.insert(0, '.')
import vcf_walk
from   vcf_walk    import walker
from   vcf_walk    import DEBUG
from   filemanager import *
from   database    import *


#INPROJ=walk_out_10k
#echo '.schema'         | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.schema
#echo '.dump'           | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql
#echo '.dump trees'     | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.trees.sql
#echo '.dump chrom'     | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.chrom.sql
#echo '.dump spps'      | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.spps.sql
#echo '.dump fastas'    | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.fastas.sql
#echo '.dump registers' | sqlite3 $INPROJ.sqlite > $INPROJ.sqlite.sql.registers.sql


#maximum chromosome length. needed for sql field
#chromNameLength = 20
#echo sql commands
echo_sql        = False

#interface.DEBUG = DEBUG
#DEBUG           = True
#DEBUG           = False
loaded          = False







class query_buffer_mamager(object):
    """
    Buffer for queries. stores queryies and their results. Returns NONE if query is new
    """
    def __init__(self, maxSize=500, name=''):
        self.index   = {}
        self.keys    = []
        self.maxSize = maxSize
        self.name    = 'BUFFER'
        if len(name) > 0:
            self.name    += ' ' + name
        print "INITIALIZING %s" % self.name

    def get(self, qry):
        if qry in self.index:
            #print "GETTING FROM %s SUCCEEDED %s" % (self.name, str(qry))
            data = self.index[qry]
            return data

        else:
            #print "GETTING FROM %s FAILED %s" % (self.name, str(qry))
            return None

    def put(self, qry, data):
        #print "ADDING TO %s : %s" % (self.name, str(qry))
        if qry in self.index:
            #print "ADDING TWICE TO THE DATABASE",qry
            pass


        self.index[ qry ] = data
        self.keys.append( qry )
        self.clean()

    def clean(self):
        if len(self.keys) > self.maxSize:
            #print "CLEANING %s" % self.name
            dkeys = self.keys[:int(self.maxSize / 2)] # get first 25 keys
            for qry in dkeys:
                #print " REMOVING",qry
                self.keys.remove(qry)
                self.index.pop(qry)




class manager(walker):
    """
    Manages all queries and buffer.
    Extends the walker class which contains the filtering algorithm
    """
    def __init__( self ):
        walker.__init__(self)

        self.engine             = None
        self.Session            = None
        self.session            = None

        self.spps               = None
        self.clusters           = None
        self.sppindexinv        = None
        self.numRegsChrom       = None
        self.db_file            = None
        self.clusterList        = None

        self.dbMtime            = None

        self.query_buffer       = query_buffer_mamager(name='query'  )
        self.filter_buffer      = query_buffer_mamager(name='filter' )
        self.get_buffer_genes   = query_buffer_mamager(name='genes'  )
        self.get_buffer_data    = query_buffer_mamager(name='data'   )
        self.get_buffer_tree    = query_buffer_mamager(name='tree'   )
        self.get_buffer_algn    = query_buffer_mamager(name='algn'   )
        self.get_buffer_mtrx    = query_buffer_mamager(name='mtrx'   )
        self.get_buffer_reg     = query_buffer_mamager(name='reg'    )
        self.get_buffer_cluster = query_buffer_mamager(name='clust'  )

        self.load_data_raw      = self.load_data
        self.load_data          = self.load_data_sql


    ##########################
    ############# USING BUFFER
    ##########################
    #interface.getChroms()
    def getChroms( self ):
        """
        Get list of chromosomes
        """
        return self.numRegsChrom.keys()

    #interface.getSpps()
    def getSpps( self ):
        """
        Get list of species
        """
        return copy.deepcopy( self.spps )


    def getClusterList( self ):
        #print 'getClusterList', self.clusterList
        return copy.deepcopy( self.clusterList )


    ##########################
    ############# USING QUERY REPORTING ALL
    ##########################
    #interface.getGenes( chrom )
    def getGenes( self, chrom ):
        """
        Get list of genes for a given chromosome
        """
        data = self.get_buffer_genes.get( chrom )

        if data is None:
            data = self.session.query( register_db.name ).filter( register_db.chrom == chrom ).all()
            self.get_buffer_genes.put( chrom, data )

        return [x[0] for x in data]

    def _get_data( self, chrom ):
        """
        Get all information about a given chromosome
        """
        #sel       = register_db.select( register_db.chrom == chrom).compile()
        #datas     = session.execute( sel.statement, sel.params ).fetchall()

        #datas     = session.query( register_db ).filter( register_db.chrom == chrom ).all()

        registers = self.get_buffer_data.get( chrom )

        if registers is None:
            q          = self.session.query( register_db ).filter( register_db.chrom == chrom )
            #print q
            #print q.statement
            qc = q.statement.compile()
            #print qc
            #print qc.string
            #print qc.params
            #datas      = session.execute(qc.string, qc.params)
            print "QUERYING"
            registers  = [None]*self.numRegsChrom[chrom]
            for data in self.session.execute(qc.string, qc.params):
                #print data
                #datar = data.raw()
                datar = self.registerSelectToRaw( data )
                registers[ datar[0] ] = datar[ 1 ]
            print "DONE"

            self.get_buffer_data.put( chrom, registers )

        return registers



    ##########################
    ############# USING QUERY REPORTING ONE
    ##########################
    #interface.getTree( gene, chrom )
    def getTree( self, gene, chrom ):
        """
        Get the phylogenetic tree from a gene
        """
        print "getting tree for chrom %s gene %s" % ( chrom, gene )
        data = self.get_buffer_tree.get( (chrom, gene) )

        if data is None:
            data = self.session.query( tree_db.tree ).filter( and_(tree_db.chrom == chrom, tree_db.name == gene) ).first()
            if data is not None:
                data = loads_data(data[0])
            self.get_buffer_tree.put( (chrom, gene), data )

        return data

    #interface.getAlignment( gene, chrom )
    def getAlignment( self, gene, chrom ):
        """
        Get the fasta alignement from a gene
        """
        print "getting alignment for chrom %s gene %s" % ( chrom, gene )
        data = self.get_buffer_algn.get( (chrom, gene) )

        if data is None:
            data = self.session.query( fasta_db.fasta ).filter( and_(fasta_db.chrom == chrom, fasta_db.name == gene) ).first()
            if data is not None:
                data = loads_data(data[0])
            self.get_buffer_algn.put( (chrom, gene), data )

        return data

    #interface.getMatrix( gene, chrom )
    def getMatrix( self, gene, chrom ):
        """
        Get the distance matrix from a gene
        """
        print "getting matrix for chrom %s gene %s" % ( chrom, gene )
        data = self.get_buffer_mtrx.get( (chrom, gene) )

        if data is None:
            data = self.session.query( matrix_db.matrix ).filter( and_(matrix_db.chrom == chrom, matrix_db.name == gene) ).all()
            if data is not None:
                res = []
		#print "data", data[0]
                for row in data:
                    #print "row", row
                    rowc = loads_data( row[0] )
                    res.append( rowc )
                data = res
            self.get_buffer_mtrx.put( (chrom, gene), data )

        return data


    def getRow( self, db, chromosome_name, regnum, inspp ):
        """
        Get the distance matrix from a gene
        """
        sppindex    = self.spps[ inspp ]
        sppindexinv = self.getSppIndexInvert( )

        #print "GETTING ROW :: CHROMOSOME:", chromosome_name, 'REG:',regnum, 'INSPP:',inspp,'INSPPINDEX:',sppindex
        #print "getting matrix for chrom %s regnum %d spp %s sppnum %d" % ( chromosome_name, regnum, inspp, sppindex )
        data = self.get_buffer_mtrx.get( (chromosome_name, regnum, inspp) )

        if data is None:
            data = self.session.query( matrix_db.matrix ).filter( and_(matrix_db.chrom == chromosome_name, matrix_db.regnum == regnum, matrix_db.sppi == sppindex) ).order_by( matrix_db.sppi ).all()
            if data is None:
                return None
                #res = []
	    #print "data", data[0][0]
            data = loads_data( data[0][0] )
	    #print "data", data
                #for row in data.all():
                #    print "row", row
                #    rowc = loads_data( row )
                #    res.append( rowc )
                #data = res
            self.get_buffer_mtrx.put( (chromosome_name, regnum, inspp), data )

        return data



    #interface.getRegisterDict( gene, chrom )
    def getRegisterDict( self, gene, chrom ):
        """
        Converts database columns into a dictionary
        """
        res = self.get_buffer_reg.get( (gene, chrom) )

        #print "getRegisterDict BUFFER", res

        if res is None:
            res = self._get_register(gene, chrom)
            if res is not None:
                regpos, register = res
                #print "getRegisterDict RES", res
                #print regpos, register
                res      = self.reg2dict(register)
                #print res
            self.get_buffer_reg.put( (gene, chrom), res )

        return res

    def getCluster(self, chrom, ref):
        """
        Get cluster for chromosome
        """
        print "getting cluster for chrom %s ref %s" % ( chrom, ref )
        data = self.get_buffer_cluster.get( (chrom, ref) )

        if data is None:
            data = self.session.query( cluster_db.cluster ).filter( and_(cluster_db.chrom == chrom, cluster_db.spp == ref) ).first()

            if data is not None:
                data = loads_data( data[0] )
                #print "CLUSTER DATA:", data
                #data = self.session.query( cluster_db ).filter( cluster_db.chrom == chrom ).first()
                #data = data.raw()
            self.get_buffer_cluster.put( (chrom, ref), data )

        return data

    def _get_register( self, gene, chrom ):
        """
        Get the full register from a gene. Tree and alignment included
        """
        data = self.session.query( register_db ).filter( and_(register_db.chrom == chrom, register_db.name == gene) ).first()
        if data is not None:
            #print "_get_register", data
            data = data.raw()
            #print "_get_register", data
            data[ 1 ][ vcf_walk.DB_TREE  ] = self.getTree(      gene, chrom )
            data[ 1 ][ vcf_walk.DB_FASTA ] = self.getAlignment( gene, chrom )
            data[ 1 ][ vcf_walk.DB_LINE  ] = self.getMatrix(    gene, chrom )
        return data

    #interface.make_table(db_name, ref, chrom, res, group_every=group_every, num_classes=num_classes, evenly=evenly, startPos=startPos, endPos=endPos, maxNum=maxNum, page=page)
    def make_table( self, ref, chrom, res, group_every=None, num_classes=None, evenly=False, startPos=None, endPos=None, maxNum=None, page=None ):
        """
        make a full table to a given chromososome.
        Filters using the parent class
        """
        qry = (ref, chrom, group_every, num_classes, evenly)

        resD = self.filter_buffer.get(qry+(startPos, endPos, maxNum, page))

        if resD is None:
            excerptD = self.query_buffer.get( qry )

            if excerptD is None:
                data     = self._get_data(chrom)

                excerpt  = {}

                self.filter_db( ref, chrom, data, excerpt,
                                    group_every=group_every,
                                    num_classes=num_classes,
                                    evenly=evenly
                                   )

                excerptD = excerpt[chrom]

                self.query_buffer.put( qry, excerptD )


            self.filter_excerpt(    excerptD, res,
                                        startPos=startPos,
                                        endPos=endPos,
                                        maxNum=maxNum,
                                        page=page
                                    )



            if 'clusters' not in res:
                res['clusters'] = {}

            cg = self.getCluster( chrom, ref )

            if  cg and 'clusters' in cg:
                res['clusters'] = cg['clusters']

            self.filter_buffer.put(qry+(startPos, endPos, maxNum, page), res)

            #print "MAKE TABLE RES:", res

            resD = res

        #print "MAKE TABLE RES:", resD

        return resD

    def _get_spps_raw( self ):
        """
        Get list of species from database
        """
        sppsL = self.session.query( spp_db ).order_by( 'spp' ).all()
        return self._concatHashs( [x.raw() for x in sppsL] )

    def _get_cluster_list_raw( self ):
        #data = self.session.query( cluster_db ).filter( and_(cluster_db.chrom == chrom, cluster_db.spp == ref) ).first()
        data = self.session.query( cluster_db.chrom, cluster_db.cluster ).first()

        res = {}
        if data is not None:
            chrom, infob = data
            #print "cl", chrom, infoh
            #print "cl", chrom
            if infob is not None:
                #print "cl", chrom, 'not none'
                infoh = loads_data( infob )
                if infoh is not None:
                    #print "cl", chrom, 'not none', 'converted'
                    infod = infoh['clusters']
                    if infod is not None:
                        #print "cl", chrom, 'not none', 'converted', 'has cluster'
                        for cname in infod:
                            #print "cl", chrom, 'not none', 'converted', 'has cluster', 'cname', cname
                            cinfo = infod[ cname ]
                            if 'rows' in cinfo and 'rowsOrder' in  cinfo['rows']:
                                #print "cl", chrom, 'not none', 'converted', 'has cluster', 'cname', cname, 'APPENDING'
                                if '__global__' not in res:
                                    res[ '__global__' ] = []

                                if cname in res[ '__global__' ]:
                                    print "duplicated filter", cname
                                else:
                                    res[ '__global__' ].append( cname )

        return res


    def _get_num_regs_chrom( self ):
        """
        Get list of chromosomes from database
        """
        regsL = self.session.query( chroms_db ).order_by( 'chrom' ).all()
        return self._concatHashs( [x.raw() for x in regsL] )

    def _concatHashs( self, dictLists ):
        """
        Axiliary function to merge dictionaries, concatenating values if necessary
        """
        res = {}
        for dic in dictLists:
            for key in dic:
                if key in res:
                    res[key] += dic[key]
                else:
                    res[key]  = dic[key]
        return res

    def registerSelectToRaw( self, data ):
        """
        Convert the database rows to standard WALKER (parent class) structure
        """
        chrom  = data[ 0 ]
        regnum = data[ 1 ]

        reg    = [None]*vcf_walk.NUM_REGISTER_VARS

        reg[ vcf_walk.DB_START   ] =        data[ 2 ]
        reg[ vcf_walk.DB_END     ] =        data[ 3 ]
        reg[ vcf_walk.DB_LEN_OBJ ] =        data[ 4 ]
        reg[ vcf_walk.DB_LEN_SNP ] =        data[ 5 ]
        reg[ vcf_walk.DB_NAME    ] =        data[ 6 ]
        #reg[ vcf_walk.DB_TREE    ] =        data[ 7 ]
        #reg[ vcf_walk.DB_FASTA   ] = loads( data[ 8 ] )
        #reg[ vcf_walk.DB_LINE    ] = loads_data( data[ 7 ] )

        return (regnum, reg)

    #interface.load_data(db_name)
    def load_data_sql( self, db_name, print_spps_only=False, read_threads=1, dopickle=False, cluster_extension=None, cluster_threads=None, cluster_global=False, cluster_dopng=True, cluster_dosvg=True, cluster_dotree=True, cluster_dorows=True, cluster_docols=True ):
        """
        Initialized the database, linking to SQLite

        Converts the RAM database to SQLite if it does not exists.
        Print it otherwise
        """
        self.db_name = db_name

        """
        Checks for extension
        """
        if  self.db_name.endswith('.sqlite'):
            self.db_name.replace( '.sqlite', '')

        elif self.db_name.endswith('.pickle.gz'):
            print "db should end in .pickle.gz . you gave me the wrong type of file"
            sys.exit(1)


        """
        Connects to SQLite
        """
        self.db_file = db_name + '.sqlite'

        print "INITIALIZING SQLDB", self.db_file,'DO PICKLE',dopickle

        fileExists = os.path.exists(self.db_file)
        db_file    = self.db_file
        db_filef   = self.db_file
        if not fileExists:
            db_file = self.db_file + '.tmp'
            print "SQLDB FILE DOES NOT EXISTS. SAVING TO", db_file

            if os.path.exists(db_file):
                print "SQLDB FILE DOES NOT EXISTS. TMP FILE EXISTS", db_file,"REMOVING"
                os.remove(db_file)

        #engine    = create_engine('sqlite:///:memory:', echo=True)
        self.engine, self.Session, self.session = getsession(db_file, echo=echo_sql)
        #self.engine    = create_engine('sqlite:///'+db_file, echo=echo_sql )
        #self.Session   = sessionmaker(bind=self.engine)
        #self.session   = self.Session()


        if not fileExists:
            """
            If file does not exists, create
            """
            print "CREATING SQL DATABASE FROM SOURCE"

            #if not os.path.exists( self.db_name + '.pickle.gz' ):
            #    """
            #    If RAM database does not exists, exit
            #    """
            #    print "db file %s.db does not exists" % self.db_name
            #    sys.exit( 1 )



            print "READING PICKLE"
            """
            Read pickled database basic information
            """
            print "loading db pickle. do pickle:", dopickle

            self.sppindexinv = None

            hasspps = False
            for chromosome  in sorted( os.listdir( self.db_name ) ):
                chromPath = os.path.join( self.db_name, chromosome )

                if os.path.isfile( chromPath ):
                    continue

                #def load_data(self, db_name, print_spps_only=False, cluster_threads=10, cluster_global=True):
                self.load_data_raw(self.db_name, singlechrom=chromosome, read_threads=read_threads, dopickle=dopickle, cluster_extension=cluster_extension, cluster_threads=cluster_threads, cluster_global=cluster_global, cluster_dopng=cluster_dopng, cluster_dosvg=cluster_dosvg, cluster_dotree=cluster_dotree, cluster_dorows=cluster_dorows, cluster_docols=cluster_docols)
                print "db pickle loaded"

                sppsL           = self.spps
                clustersL       = self.clusters
                wholedataL      = self.wholedata


                if not hasspps:
                    print "READING SPECIES"
                    """
                    Save species to database
                    """
                    hasspps = True
                    self.sppindexinv = [None]*len(sppsL)
                    for spp in sppsL:
                        val   = sppsL[spp]
                        self.sppindexinv[val] = spp
                        dbval = spp_db(spp, val)
                        self.session.add( dbval )

                    print "COMMITING SPECIES"
                    self.session.commit()
                    self.session.flush()

                    #print sppsL
                    #print self.sppindexinv




                print "READING CHROMOSOME DATA"
                """
                Reads chromosome data and save it to database
                """
                print

                print "READING CHROMOSOME DATA", chromosome
                chromData   = wholedataL[chromosome]
                chromLen    = len(chromData)

                dbval       = chroms_db(chromosome, chromLen)
                self.session.add( dbval )

                for regnum in xrange(len(chromData)):
                    reg       = chromData[ regnum ]
                    START     =            reg[ vcf_walk.DB_START   ]
                    END       =            reg[ vcf_walk.DB_END     ]
                    LEN_OBJ   =            reg[ vcf_walk.DB_LEN_OBJ ]
                    LEN_SNP   =            reg[ vcf_walk.DB_LEN_SNP ]
                    NAME      =            reg[ vcf_walk.DB_NAME    ]

                    TREE      = dumps_data(reg[ vcf_walk.DB_TREE    ])
                    FASTA     = dumps_data(reg[ vcf_walk.DB_FASTA   ])
                    LINE      =            reg[ vcf_walk.DB_LINE    ]

                    dbval     = register_db( chromosome, regnum, START, END, LEN_OBJ, LEN_SNP, NAME )#, LINE)#, TREE, FASTA, LINE)
                    treeval   = tree_db(     chromosome, regnum, NAME, TREE  )
                    fastaval  = fasta_db(    chromosome, regnum, NAME, FASTA )

                    for sppi in xrange(len(self.sppindexinv)):
                        line      = LINE[ sppi ]
                        matrixval = matrix_db(   chromosome, regnum, NAME, sppi, dumps_data(line) )
                        self.session.add( matrixval )

                    sys.stdout.write('.')
                    if (regnum+1) % 100 == 0:
                        sys.stdout.write('\n')
                    sys.stdout.flush()

                    """
                    Saves tree and fasta in separated databases
                    """
                    self.session.add( dbval     )
                    self.session.add( treeval   )
                    self.session.add( fastaval  )
                print
                print "COMMITTING CHROMOSOME DATA", chromosome
                self.session.commit()
                self.session.flush()
                del wholedataL[chromosome]






                print "READING CLUSTERS"
                """
                Save clusters to database
                """
                print

                print "READING CLUSTERS", chromosome
                cdata    = clustersL[chromosome]
                clusters = cdata[ 'clusters' ]
                colnames = cdata[ 'colnames' ]
                rownames = cdata[ 'rownames' ]
                numspps  = cdata[ 'numspps'  ]
                numfiles = cdata[ 'numfiles' ]
                #print 'clusters len',len(clusters)

                for refi in xrange(len(clusters)):
                    ref   = self.sppindexinv[refi]
                    #print "READING CLUSTERS %s REFi %4d / %4d REFn %s" % ( chrom, refi, len(clusters), ref)
                    val   = dumps_data(
                        {
                            'colnames': colnames,
                            'rownames': rownames,
                            'numspps' : numspps,
                            'numfiles': numfiles,
                            'clusters': clusters[refi]
                        }
                    )
                    dbval = cluster_db(chromosome, ref, val)
                    self.session.add( dbval )
                    self.session.commit()
                    self.session.flush()
                    sys.stdout.write('.')
                    if (refi+1) % 100 == 0:
                        sys.stdout.write('\n')
                    sys.stdout.flush()

                print
                print "COMMITING CLUSTERS", chromosome
                sys.stdout.flush()
                self.session.flush()
                del clustersL[chromosome]



            self.session.flush()

            print "DONE CREATING SQL DATABASE",db_file,"RENAMING TO",db_filef

            os.rename (db_file, db_filef)

            sys.exit( 0 )

        else:
            """
            Database exists. print it to screen
            """
            """
            Get creation time
            """
            self.getDbTime()

            print "DB %s EXISTS" % db_name
            self.spps          = self._get_spps_raw()
            self.sppindexinv   = [None]*len(self.spps)

            self.clusterList   = self._get_cluster_list_raw()


            for k in self.spps:
                #print " adding",k,"at pos",spps[k],"/",len(spps)
                self.sppindexinv[ self.spps[k] ] = k

            if DEBUG:
                print "SPPS    ", self.spps
                print "SPPS INV", self.sppindexinv



            self.numRegsChrom = self._get_num_regs_chrom()

            if DEBUG:
                print "CHROM", self.numRegsChrom


                for chrom in self.numRegsChrom:
                    genes   = self.getGenes(chrom)
                    data    = self._get_data(chrom)
                    cluster = self.getCluster(chrom, self.spps[0])

                    print "  CHROM:",chrom
                    #print "    ", genes

                    gene = genes[ 0 ]
                    print "    GENE", gene

                    tree = self.getTree( gene, chrom )
                    print "    TREE\n", tree

                    aln  = self.getAlignment( gene, chrom )
                    #print "    ALIGNMENT\n", aln

                    mat  = self.getMatrix( gene, chrom )
                    print "    MATRIX"
                    #pp( mat )

                    dic  = self.getRegisterDict( gene, chrom )
                    print "    REG DICT"
                    #pp( dic )

                    reg  = self._get_register(gene, chrom)
                    print "    REGISTER"
                    #pp( reg )

                    #data = self._get_data(chrom)

                    pp( data )



def main(args):

    man                = manager()

    parser, options    = man.getOpts( args )

    print options

    db_name            = options.db
    dopickle           = options.pickle
    print_spps_only    = options.lst
    read_threads       = options.read_threads

    cluster_extension  = options.cluster_extension
    cluster_global     = options.cluster_global
    cluster_threads    = options.cluster_threads
    cluster_dopng      = options.cluster_dopng
    cluster_dosvg      = options.cluster_dosvg
    cluster_dotree     = options.cluster_dotree
    cluster_dorows     = options.cluster_dorows
    cluster_docols     = options.cluster_docols

    if db_name is None:
        print "no database selected"
        print parser.print_help()
        sys.exit(1)

    if db_name is not None:
        db_name = db_name.strip("/")

    man.load_data(
                    db_name,
                    print_spps_only   = print_spps_only,
                    dopickle          = dopickle,
                    read_threads      = read_threads,
                    cluster_extension = cluster_extension,
                    cluster_threads   = cluster_threads,
                    cluster_global    = cluster_global,
                    cluster_dopng     = cluster_dopng,
                    cluster_dosvg     = cluster_dosvg,
                    cluster_dotree    = cluster_dotree,
                    cluster_dorows    = cluster_dorows,
                    cluster_docols    = cluster_docols
                )


if __name__ == '__main__':
    args = sys.argv[1:]

    main(args)
