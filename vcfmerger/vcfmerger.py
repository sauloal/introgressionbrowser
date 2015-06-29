#!/usr/bin/python
"""

"""
import os, sys
import gzip
import datetime
import time
import pprint
import math
import copy
from pprint import pprint as pp

sys.path.insert(0, '.')
from filemanager import getFh,openvcffile,openfile,checkfile,makeIndexFile,readIndex

#try:
#    sys.path.insert(0, 'aux/pypy-2.0/pypy-2.0-beta2/pypy-pypy-4b60269153b5/')
#    from rpython.rlib.jit import JitDriver, purefunction
#except:
#    print "no pypy"


#./vcfmerger.py short.lst
#./vcfsimplify.py short.lst.vcf.gz
#./pypy ./vcffiltergff.py --input=short2.lst.vcf.gz.simplified.vcf.gz -g ITAG2.3_gene_models.gff3.exon.gff3
#./pypy ./vcffiltergff.py --input=short2.lst.vcf.gz.simplified.vcf.gz -g ITAG2.3_gene_models.gff3.exon.gff3 --protein S_lycopersicum_scaffolds.2.40.fa

#./pypy ./vcfconcat.py short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz
#./pypy ./alnmerger.py short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.aln *ch??.aln
#for aln in *.aln; do echo $aln; clustalw -TREE -QUICKTREE -INFILE=$aln &\ ; done


#./pypy ./vcfconcat.py --fasta -i short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz --ignore SL2.40ch00
#rm short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.fa
#./pypy alnmerger.py short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.fa *ch??.fasta
#for fa in *ch??.fasta; do echo $fa;  bash runFastTree.sh $fa; done
#bash runFastTree.sh short2.lst.vcf.gz.simplified.vcf.gz.filtered.vcf.gz.fa

#./FastTreeMP -fastest -gtr -gamma -nt -bionj -boot 100 short2.lst.vcf.gz.simplified.vcf.gz.SL2.40ch04_42945354-42947959.fasta | tee short2.lst.vcf.gz.simplified.vcf.gz.SL2.40ch04_42945354-42947959.fasta.tree
#./FastTreeMP -fastest -gtr -gamma -nt -bionj -boot 100 short2.lst.vcf.gz.simplified.vcf.gz.SL2.40ch04.fasta | tee short2.lst.vcf.gz.simplified.vcf.gz.SL2.40ch04.fasta.tree 2>&1 | tee short2.lst.vcf.gz.simplified.vcf.gz.SL2.40ch04.fasta.tree.log

#./pypy alnmerger.py short2.lst.vcf.gz.simplified.vcf.gz.fasta *ch??.fasta


#./vcfstats.py short2.lst.vcf.gz
#./vcftree.py short2.lst.vcf.gz.report.csv
#sumtrees.py --to-newick --no-meta-comments --no-summary-metadata --output short2.lst.vcf.gz.gt1.vcf.gz.simplified.vcf.gz.report.csv.nj *.nj



#grep -P "\tgene\t" ITAG2.3_gene_models.gff3 > ITAG2.3_gene_models.gff3.gene.gff3
#grep -P "\texon\t" ITAG2.3_gene_models.gff3 > ITAG2.3_gene_models.gff3.exon.gff3

#python
#{'count total': 1307102,
# 'count unique': 1205820,
# 'ela': datetime.timedelta(0, 94, 947935),
# 'ela_str': '0:01:34.947935',
# 'end time': '2013-04-24T18:59:54.507488',
# 'first': 280,
# 'last': 21805703,
# 'snp_per_kb_t': 59.943125887755144,
# 'snp_per_kb_u': 55.29837767670228,
# 'speed_t': 13766.513194836729,
# 'speed_u': 12699.802265315197,
# 'start time': '2013-04-24T18:58:19.559448'}
#PYPY purefunction
#{'count total': 1307102,
# 'count unique': 1205820,
# 'ela': datetime.timedelta(0, 31, 721854),
# 'ela_str': '0:00:31.721854',
# 'end time': '2013-04-24T19:01:22.663991',
# 'first': 280,
# 'last': 21805703,
# 'snp_per_kb_t': 59.943125887755144,
# 'snp_per_kb_u': 55.29837767670228,
# 'speed_t': 41205.09475896333,
# 'speed_u': 38012.28011452294,
# 'start time': '2013-04-24T19:00:50.942005'}
#PYPY vanilla
#{'count total': 1307102,
# 'count unique': 1205820,
# 'ela': datetime.timedelta(0, 32, 109961),
# 'ela_str': '0:00:32.109961',
# 'end time': '2013-04-24T19:03:42.957995',
# 'first': 280,
# 'last': 21805703,
# 'snp_per_kb_t': 59.943125887755144,
# 'snp_per_kb_u': 55.29837767670228,
# 'speed_t': 40707.056604646765,
# 'speed_u': 37552.832904406205,
# 'start time': '2013-04-24T19:03:10.847895'}



FHDOPEN       = 0
FHDJUSTCLOSED = 1
FHDCLOSED     = 2

"""
Constants
"""
SIMP_NO_SIMPLIFICATION =    0 # no simplification
SIMP_SNP               = 2**1 # simplify SNPs
SIMP_EXCL_HETEROZYGOUS = 2**2 # exclude heterozygous
SIMP_EXCL_INDEL        = 2**3 # exclude indels
SIMP_EXCL_SINGLETON    = 2**4 # exclude singletons


def getBits(val):
    """
    Split the bits from the configuration
    """
    #print "getting bits from %3d" % val
    #print "size of value     %3d" % sys.getsizeof(val)
    try:
        sizeofval = sys.getsizeof(val)
    except: # pypy
        sizeofval = 24

    res = []
    for offset in range(sizeofval * 8):
        mask = 1 << offset
        bitv = val & mask

        #print "offset %3d" % offset
        #print "mask   %3d" % mask
        #print "bit    %3d" % bitv
        #print

        if bitv > 0: res.append( True  )
        else       : res.append( False )

    return res



class vcfResult(object):
    """
    Main class controlling the merging and filtering of vcf files
    """
    simplifybits     = None
    simplifySNP      = None
    excludeHET       = None
    excludeINDEL     = None
    excludeSingleton = None
    noncarefiles     = None
    simpliStats      = None
    prints           =    0
    printsReal       =    0
    printsRealLast   =    0
    print_every      = 1000
    linelen          =  100

    def __init__(self, simplify=SIMP_NO_SIMPLIFICATION, noncarefiles=[]):
        self.result       = None
        self.chom         = None
        self.pos          = None
        self.chrCount     = None
        self.posCount     = None
        self.simplify     = simplify


        if vcfResult.simpliStats is None:
            vcfResult.simpliStats = {
                'Heterozygous Dest' : 0,
                'Heterozygous Indel': 0,
                'Homozygous Indel'  : 0,
                'Source Indel'      : 0,
                'Singleton 1'       : 0,
                'Singleton 2'       : 0,
                'Singleton 3'       : 0,
                'Ok'                : 0,
            }


        if vcfResult.simplifybits is None:
            #print "simplifying"
            vcfResult.simplifybits     = getBits(simplify)
            #print "simplifying :: simplify bits  ", self.simplifybits
            vcfResult.simplifySNP      = vcfResult.simplifybits[ int( math.log( SIMP_SNP               , 2 ) ) ] # simplify SNP
            vcfResult.excludHET        = vcfResult.simplifybits[ int( math.log( SIMP_EXCL_HETEROZYGOUS , 2 ) ) ] # exclude heterozygous
            vcfResult.excludeINDEL     = vcfResult.simplifybits[ int( math.log( SIMP_EXCL_INDEL        , 2 ) ) ] # exclude indels (len > 1)
            vcfResult.excludeSingleton = vcfResult.simplifybits[ int( math.log( SIMP_EXCL_SINGLETON    , 2 ) ) ] # exclude single species SNPs
            print "simplifying :: SNP          [%3d, %3d] %s" % ( SIMP_SNP              , math.log(SIMP_SNP               , 2 ), str(vcfResult.simplifySNP     ) )
            print "simplifying :: Heterozygous [%3d, %3d] %s" % ( SIMP_EXCL_HETEROZYGOUS, math.log(SIMP_EXCL_HETEROZYGOUS , 2 ), str(vcfResult.excludHET       ) )
            print "simplifying :: Indel        [%3d, %3d] %s" % ( SIMP_EXCL_INDEL       , math.log(SIMP_EXCL_INDEL        , 2 ), str(vcfResult.excludeINDEL    ) )
            print "simplifying :: Singleton    [%3d, %3d] %s" % ( SIMP_EXCL_SINGLETON   , math.log(SIMP_EXCL_SINGLETON    , 2 ), str(vcfResult.excludeSingleton) )

            print 'Progress Legend:'
            print ' print every       :', vcfResult.print_every
            print ' Heterozygous Dest : h'
            print ' Heterozygous Indel: I'
            print ' Homozygous Indel  : i'
            print ' Source Indel      : s'
            print ' Singleton 1       : 1'
            print ' Singleton 2       : 2'
            print ' Singleton 3       : 3'
            print ' Ok                : .'

            #sys.exit(0)

        #TODO: IMPLEMENT
        if vcfResult.noncarefiles is None:
            vcfResult.noncarefiles = noncarefiles

    def simplifier(self, srcs):
        """
        Reads each register and simplifies it
        """
        #if len(sourc) > 1:
        #todo: if len(src) != len(tgt)
        #{'G': {'A': ['S neorickii (056)']},  'GTAT': {'GTATATACCTATCTTTTCTTTCTAT': ['Moneymaker (001)', 'S cheesemaniae (053)']}}
        #{'G': {'A': ['S neorickii (056)']},  'GTAT': {'GTATATACCTATCTTTTCTTTCTAT': ['Moneymaker (001)', 'S cheesemaniae (053)']}}

        #SL2.40ch00      23317   .       T       TC      .       PASS    NV=3;NW=2;NS=13;NT=10;NU=9      FI      S chilense (064),S chilense (065),S corneliomulleri lycopersicon so (025),S huaylasense (062),S huaylasense (063),S pennellii (073),S peruvianum (060),S pimpinellifolium (049),Unknown (075)
        #SL2.40ch00      23317   .       TAAAAAA TAAAAAAA        .       PASS    NV=3;NW=1;NS=13;NT=3;NU=3       FI      S cheesemaniae (054),S pimpinellifolium (044),S pimpinellifolium (045)


        if len(srcs) == 0: return srcs
        simpl = {}
        for src in srcs:
            dsts = srcs[ src ]
            if src not in simpl: simpl[src] = {}
            simplsrc = simpl[src]

            for dst in dsts:
                files = dsts[ dst ]

                if dst.find(',') != -1:
                    for dstl in dst.split(','):
                        if dstl not in simplsrc: simplsrc[dstl] = []
                        simplsrc[dstl].extend(files)
                else:
                    if dst not in simplsrc: simplsrc[dst] = []
                    simplsrc[dst].extend(files)

        for src in simpl:
            for dst in simpl[src]:
                simpl[src][dst] = sorted(list(set(simpl[src][dst])))

        #print
        #print "SIMPLIFIER :: ORIGINAL   :", pprint.pformat(srcs ).replace("\n", " ")
        #print "SIMPLIFIER :: SIMPLIFIED :", pprint.pformat(simpl).replace("\n", " ")

        return simpl
        #return srcs

    def printprogress(self, msg, key=None, skip=0):
        vcfResult.prints += 1

        if skip != 0:
            if key is None:
                if vcfResult.prints % skip == 0:
                    sys.stderr.write(msg)
                    vcfResult.printsReal += 1

            else:
                if vcfResult.simpliStats[key] % skip == 0:
                    sys.stderr.write(msg)
                    vcfResult.printsReal += 1
        else:
            sys.stderr.write(msg)
            vcfResult.printsReal += 1

        if vcfResult.printsReal % vcfResult.linelen == 0 and vcfResult.printsReal != vcfResult.printsRealLast:
            vcfResult.printsRealLast = vcfResult.printsReal
            sys.stderr.write(' {:14,d}\n'.format( vcfResult.prints ) )

        sys.stderr.flush()

    def __str__(self):
        #SL2.40ch01      2118853 .       T       G       222     .       DP=40;AF1=1;CI95=1,1;DP4=0,0,16,23;MQ=60;FQ=-144        GT:PL:DP:GQ     1/1:255,117,0:39:99

        restr = ""
        if self.result is None:
            print "current result is none"
            return restr


        #print "exporting chr %s pos %d with %d results" % ( self.chr, self.pos, len( self.result ) )
        #outFileHandle << val.chr << "\t" << val.pos;
        #
        #for ( int fileNum = 0; fileNum < numFiles; ++fileNum ) {
        #    //outFileHandle << " cov " << val.result[fileNum].cov << " chr " << val.result[fileNum].chr << " pos " << val.result[fileNum].pos;
        #    outFileHandle << "\t" << val.result[fileNum].cov;
        #    if ( val.result[fileNum].cov > 0 ) {
        #        statistics.add( val.result[fileNum].cov );
        #    }
        #}
        #outFileHandle << "\n";


        srcs   = {}
        rcount = 0
        #print "RESULTS", self.result
        for register in self.result:
            rcount += 1
            if register is None:
                print "register #%d is empty" % register
                sys.exit( 1 )

            #if rcount % 100 == 0:
            #    sys.stderr.write("\n")
            #    sys.stderr.flush()

            chrom    = register['chrom'   ]
            posit    = register['pos'     ]
            sourc    = register['src'     ]
            desti    = register['dst'     ]
            descr    = register['desc'    ]
            state    = register['state'   ]
            filedesc = register['filedesc']

            if chrom != self.chrom:
                print "wrong chromosome %s vs %s" % ( chrom, self.chrom )
                sys.exit( 1 )

            if posit != self.pos:
                print "wrong position %d vs %d" % ( posit , self.pos )
                sys.exit( 1 )


            if ( vcfResult.excludHET    ) and ( desti.find(',') != -1 ):
                vcfResult.simpliStats['Heterozygous Dest'] += 1
                #print "heretozygous: %s" % desti
                self.printprogress('h', key='Heterozygous Dest', skip=vcfResult.print_every)
                #return ""
                continue

            if ( vcfResult.excludeINDEL ):
                if desti.find(',') != -1: # is heterozygous
                    destis = desti.split(',')
                    for alt in destis:
                        if len(alt) > 1:
                            vcfResult.simpliStats['Heterozygous Indel'] += 1
                            #print "has het indel: %s > %s" % ( desti, alt )
                            self.printprogress('I', key='Heterozygous Indel', skip=vcfResult.print_every)
                            #return ""
                            continue

                else: # homozygous
                    if ( len( desti ) > 1 ):
                        vcfResult.simpliStats['Homozygous Indel'] += 1
                        #print "has hom indel: %s" % desti
                        self.printprogress('i', key='Homozygous Indel', skip=vcfResult.print_every)
                        #return ""
                        continue

                if len(sourc) > 1:
                    vcfResult.simpliStats['Source Indel'] += 1
                    # todo: if len(src) != len(tgt)
                    #print "not single nucleotide source: %s" % str(register)
                    self.printprogress('s', key='Source Indel', skip=vcfResult.print_every)
                    #return ""
                    continue



            if sourc not in srcs:
                srcs[ sourc ]          = {}
            dsts = srcs[ sourc ]

            if desti not in dsts:
                dsts[ desti ] = []
            files = dsts[ desti ]

            if vcfResult.simplifySNP:
                files.extend( descr.split(',') )

            else:
                if filedesc in files:
                    print "source already present"
                    sys.exit(1)

                files.append( filedesc )

        if len(srcs) == 0: return ""

        if vcfResult.simplifySNP:
            srcs = self.simplifier(srcs)

        nv    = 0
        ns    = 0



        allspps = []
        for src in srcs:
            for dst in srcs[src]:
                nv += 1
                allspps.extend( srcs[src][dst] )

        ns = len( set(allspps) )

        if (vcfResult.excludeSingleton) and (ns == 1):
            vcfResult.simpliStats['Singleton 1'] += 1
            #print "singleton ns: %s" % str(srcs)
            self.printprogress('1', key='Singleton 1', skip=vcfResult.print_every)
            return ""

        for src in sorted( srcs ):
            dsts = srcs[ src ]
            nt   = 0

            ntspps = []
            for dst in dsts:
                ntspps.extend( dsts[ dst ] )
            nt = len(set(ntspps))

            nw = len(dsts)

            for dst in sorted( dsts ):
                files = dsts[ dst ]
                nu    = len( files )

                if (vcfResult.excludeSingleton) and (nu == 1):
                    vcfResult.simpliStats['Singleton 2'] += 1
                    #print "singleton 1: %s" % str(srcs)
                    self.printprogress('2', key='Singleton 2', skip=vcfResult.print_every)
                    continue

                files_str = ",".join( files )
                info_str  = "NV=%d;NW=%d;NS=%d;NT=%d;NU=%d" % ( nv, nw, ns, nt, nu )

                #                      chr  pos         id   ref  alt  qual filter  info      FORMAT filenames
                restr += "\t".join([ chrom, str(posit), '.', src, dst, '.', 'PASS', info_str, 'FI',  files_str]) + "\n"

        if len(restr) == 0:
            vcfResult.simpliStats['Singleton 3'] += 1
            #print "singleton l: %s" % str(srcs)
            self.printprogress('3', key='Singleton 3', skip=vcfResult.print_every)

        else:
            vcfResult.simpliStats['Ok'] += 1
            self.printprogress('.', key='Ok', skip=vcfResult.print_every)

        return restr



class vcfRegister(dict):
    """
    Class containg all information of a given position
    """
    def __init__(self, *args, **kwargs):
        #if 'defaultres' in kwargs:
        #    self.defaultres = kwargs['defaultres']
        #else:
        #    self.defaultres = None

        super(vcfRegister, self).__init__(*args, **kwargs)
        self.__dict__ = self

    #def __getattr__(self, attr):
    #    if attr in self:
    #        return self[attr]
    #    else:
    #        return self.defaultres
    #
    #__setattr__ = dict.__setitem__

    def __repr__(self):
        res = "CHROM %s POS %s SRC %s DST %s DESC '%s' STATE %s FILENAME '%s' FILEDESC '%s' FILECARE %s" % (
                self['chrom'   ],
            str(self['pos'     ]),
                self['src'     ],
                self['dst'     ],
                self['desc'    ],
            str(self['state'   ]),
                self['filename'],
                self['filedesc'],
            str(self['filecare'])
        )
        return res



class vcfFile(object):
    """
    Reads a VCF file and keeps the positions until NEXT is called.
    Used to facilitate the parallel reading of VCF files where all files have to be in the same coordinate.
    """
    def __init__(self, infile, filedesc, filecare):
        self.infile   = infile
        self.filedesc = filedesc
        self.filecare = filecare

        infile = checkfile(infile)
        fhd    = openvcffile(infile, 'r')

        #print "  opening %s" % infile
        self.names    = []
        self.infhd    = fhd
        self.state    = FHDOPEN
        self.currLine = ""
        self.register = vcfRegister()
        self.register['filename'] = infile
        self.register['filedesc'] = filedesc
        self.register['filecare'] = filecare

    def next(self):
        """
        Requests the next line in the VCF file as a register
        """
        if self.state == FHDOPEN:
            currLine = ""
            while currLine is not None and len(currLine) == 0:
                currLine = self.infhd.readline()
                if len( currLine ) == 0 or currLine[-1] != "\n": # EOF
                    currLine = None
                    self.state = FHDJUSTCLOSED
                    return
                elif len(currLine) == 1: # EMPTY LINE
                    self.next()
                    return
                else: #normal line
                    pass

            #0               1       2       3       4       5       6       7                                                       8               9
            #SL2.40ch01      2118853 .       T       G       222     .       DP=40;AF1=1;CI95=1,1;DP4=0,0,16,23;MQ=60;FQ=-144        GT:PL:DP:GQ     1/1:255,117,0:39:99
            currLine = currLine.strip()
            cols     = currLine.split("\t")

            if len(cols) == 0:
                self.next()
                return

            elif currLine[0] == "#":
                if currLine.startswith('##sources='):
                    self.names = currLine[10:].split(';')
                    pp(self.names)

                elif currLine.startswith('##numsources='):
                    numsources = int(currLine[13:])
                    if numsources != len(self.names):
                        print "error parsing sources"
                        print "num sources", numsources,"!=",len(self.names),sorted(self.names)
                        sys.exit(1)
                    else:
                        print "num sources:",numsources

                self.next()
                return

            try:
                self.register['chrom'] =     cols[0]
                self.register['pos'  ] = int(cols[1])
                self.register['src'  ] =     cols[3]
                self.register['dst'  ] =     cols[4]

                if len( cols ) > 9:
                    self.register['desc' ] =     cols[9]

                    try:
                        #print "has desc"
                        info  = cols[8].split(':')

                    except:
                        info  = []

                    #print " info", info
                    if len(info) > 1:
                        try:
                            gtpos = info.index('GT')

                        except:
                            gtpos = None

                        if gtpos is not None:
                            #print "  GT pos", gtpos
                            desc  = self.register['desc' ].split(":")
                            #print "  desc", desc
                            if len(info) == len(desc):
                                #print "   len info == len desc", info, desc
                                gtinfo = desc[gtpos]
                                #print "   gtinfo", gtinfo
                                #print "    gt1", gtinfo[ 0]
                                #print "    gt2", gtinfo[-1]
                                if any([gt == '0' for gt in (gtinfo[ 0], gtinfo[-1])]):
                                    #print "has desc"
                                    #print " info", info
                                    #print "  GT pos", gtpos
                                    #print "  desc", desc
                                    #print "   len info == len desc", info, desc
                                    #print "   gtinfo", gtinfo
                                    #print "    gt1", gtinfo[ 0]
                                    #print "    gt2", gtinfo[-1]
                                    #print "   adding src to dst", self.register['src'  ], self.register['dst'  ]

                                    self.register['dst'  ] = ",".join(sorted(list(set([self.register['src'  ]] + self.register['dst'  ].split(",")))))
                                    #print "   added  src to dst", self.register['dst'  ]

                else:
                    self.register['desc' ] = ""

                self.register['state'] = self.state

            except (RuntimeError, TypeError, NameError):
                print RuntimeError, TypeError, NameError
                print "error getting colums", cols, currLine, "\n"
                #self.next()
                #return
                sys.exit(1)
        else:
            self.register['chrom'] = None
            self.register['pos'  ] = None
            self.register['src'  ] = None
            self.register['dst'  ] = None
            self.register['desc' ] = None

    def close( self ):
        """
        Close filehandle
        """
        self.state = FHDCLOSED
        self.infhd.close()

    def currRegister(self):
        """
        Get current register
        """
        if self.state == FHDOPEN:
            return self.register
        else:
            return None

    def getstate(self):
        """
        Get file state
        """
        return self.state



class vcfHeap(object):
    """
    Maintain the latest line in all VCF files at the same time
    """

    def __init__(self, simplify=SIMP_NO_SIMPLIFICATION):
        self.fileNames    = [] #vecString   fileNames;
        self.filehandle   = [] #vecIfstream filehandle;
        self.fileStates   = [] #vecBool     fileStates;
        self.filePos      = {} #map<   string, int          > filePos;
        self.numOpenFiles = 0 #int         numOpenFiles;

        self.lastPos      = 0  #int            lastPos;
        self.lastChr      = "" #string         lastChr;
        self.heapHead     = [] #vecCovRegister heapHead;
        self.ctime        = datetime.datetime.now().isoformat()
        self.stats        = {}
        self.stats        = {
            'chroms'    : {},
            'start time': self.ctime
        }
        self.simplify     = simplify
        self.noncarefiles = []
        self.currResult   = vcfResult( simplify=self.simplify, noncarefiles=self.noncarefiles )
        self.currResult   = None
        print self.ctime

    def addFile( self, filecare, fileName, filedesc ):
        """
        Adds file to be taken track of
        """
        print "adding file to heap"
        filecare = filecare == '1'
        self.filePos[ (fileName, filedesc, filecare) ] = len( self.fileNames )

        if not filecare:
            self.noncarefiles.append(filedesc)

        self.fileNames.append( (fileName, filedesc, filecare) )

        print "creating vcf handler"
        self.filehandle.append( vcfFile( fileName, filedesc, filecare) );
        print "created vcf handler"
        self.fileStates.append( True );
        self.numOpenFiles += 1

        print "getting first register"
        firstRegister = self.getRegister( self.filePos[ ( fileName, filedesc, filecare ) ] );
        print "got first register"

        self.heapHead.append( firstRegister );
        print "added to heap"

    def getFileNames(self):
        """
        Lists all files
        """
        return [ x[0] for x in self.fileNames ]

    def getFileDesc(self):
        """
        Returns list of file descriptions (pretty name)
        """
        if self.simplify:
            return self.filehandle[0].names
        else:
            return [ x[1] for x in self.fileNames ]

    def getCurrChr(self):
        """
        Returns current chromosome
        """
        return self.lastChr

    def getCurrpos(self):
        """
        Returns current position
        """
        return self.lastPos

    def getNumFiles(self):
        """
        Returns number of files
        """
        if self.simplify:
            return len( self.filehandle[0].names )
        else:
            return len( self.fileNames )

    def getNumOpenFiles(self):
        """
        Returns number of files still open
        """
        if self.simplify:
            return len( self.filehandle[0].names )
        else:
            return self.numOpenFiles

    def isempty( self ):
        """
        Returns if there's still open files
        """
        #print "is empty? %d\n" % self.numOpenFiles
        return self.numOpenFiles == 0

    def getRegister( self, fileNum ):
        """
        Gets the current register of a file
        """
        infilehandle = self.filehandle[ fileNum ]
        infilehandle.next()
        currRegister = infilehandle.currRegister()

        if currRegister is None:
            infilehandle.close()
            self.fileStates[ fileNum ] = False
            self.numOpenFiles -= 1
            return None

        return currRegister;

    def getFilterStats(self):
        """
        Gets the number of simplifications performed in the VCF files
        """
        return pprint.pformat(vcfResult.simpliStats)

    def next( self ):
        """
        Gets the next position shared by all files
        """
        self.currResult = vcfResult( )
        response        = []

        chromCount = 0
        posCount   = 0

        has_more_chr = True
        if self.lastChr == "":
            poses = [ heap.chrom for heap in self.heapHead if (heap is not None) and (heap.state == FHDOPEN) ]
            if len(poses) > 0:
                self.lastChr = sorted( poses )[0]

                self.stats['chroms'][ self.lastChr ] = {
                    'start time'  : datetime.datetime.now().isoformat(),
                    'count unique': 1,
                    'count total' : 0
                }
                print "   STARTING CHROMOSOME %s" % self.lastChr
            else:
                has_more_chr = False
                return None
        else:
            self.stats['chroms'][ self.lastChr ][ 'count unique' ] += 1

        poses = []
        if has_more_chr:
            poses = [ heap.pos for heap in self.heapHead if ((heap is not None) and (heap.chrom == self.lastChr ) and ( heap.state == FHDOPEN )) ]

        if (len( poses ) > 0):
            lastChromData = self.stats['chroms'][ self.lastChr ]
            self.lastPos  = min( poses )

            for fileNum in xrange( len( self.fileNames ) ):
                #print "filenum %d last chr %s lasPos %d len %d" % ( fileNum, self.lastChr, self.lastPos, len( self.fileNames ) )

                if self.fileStates[ fileNum ]: # if file not closed
                    #print " file open"
                    heapdata = self.heapHead[ fileNum ]

                    if heapdata.state == FHDOPEN: # is valid
                        #print "  heap open"

                        if heapdata.chrom == self.lastChr: # if chrom is correct
                            #print "    heap head chr ok %s" % self.lastChr
                            chromCount += 1 # chrom still exists

                            while heapdata.pos == self.lastPos: # if pos is correct
                                #print "    heap head pos ok %d" % self.lastPos
                                #print "!"*200
                                lastChromData[ 'count total' ] += 1

                                posCount += 1
                                #print heapdata
                                response.append( copy.copy( heapdata ) ) # add to response

                                self.heapHead[ fileNum ] = self.getRegister( fileNum ) # add to response
                                heapdata = self.heapHead[ fileNum ]
                                if heapdata is None              : break
                                if heapdata.state != FHDOPEN     : break
                                if heapdata.chrom != self.lastChr: break
                            #print "    heap head pos NOT ok %d" % self.heapHead[ fileNum ].pos
                        else:
                            #print "    heap head chr NOT ok %s" % self.heapHead[ fileNum ].chr
                            pass
                    else:
                        #print "    file is closed"
                        pass
                else:
                    #print "    state is closes"
                    pass

            #print "    end for loop"

            if 'first' not in lastChromData:
                lastChromData[ 'first' ] = self.lastPos
                lastChromData[ 'ela'   ] = datetime.datetime.now()

        else: # no more positions to current chromosome
            #print "    len poses == 0"
            chromData = self.stats['chroms'][ self.lastChr ]
            chromData[ 'last'         ] = self.lastPos
            chromData[ 'end time'     ] = datetime.datetime.now().isoformat()
            chromData[ 'ela'          ] = datetime.datetime.now() - chromData[ 'ela' ]
            chromData[ 'ela_str'      ] = str( chromData[ 'ela' ] )
            chromData[ 'snp_per_kb_t' ] = ( chromData[ 'count total'  ] * 1.0 ) / self.lastPos * 1000.0
            chromData[ 'snp_per_kb_u' ] = ( chromData[ 'count unique' ] * 1.0 ) / self.lastPos * 1000.0
            chromData[ 'speed_t'      ] = ( chromData[ 'count total'  ] * 1.0 ) / chromData[ 'ela' ].total_seconds()
            chromData[ 'speed_u'      ] = ( chromData[ 'count unique' ] * 1.0 ) / chromData[ 'ela' ].total_seconds()
            pprint.pprint( chromData )

            self.lastPos = 0
            self.lastChr = ""
            #sys.exit(0)
            print "empty. nexting"
            return self.next()

        self.currResult.result   = response
        self.currResult.chrom    = self.lastChr
        self.currResult.pos      = self.lastPos
        self.currResult.chrCount = chromCount
        self.currResult.posCount = posCount

        self.lastPos += 1

        return self.currResult

    def getVcfHeader(self):
        """
        Returns a VCF header
        """

        header = """\
##fileformat=VCFv4.1
##fileDate=%s
##source=vcfmerger
##sources=%s
##numsources=%d
##INFO=<ID=NV,Number=1,Type=Integer,Description=\"Number of Unique SNPs Variants in Position\">
##INFO=<ID=NW,Number=1,Type=Integer,Description=\"Number of Unique Source Nucleotides\">
##INFO=<ID=NS,Number=1,Type=Integer,Description=\"Number of Species in Position\">
##INFO=<ID=NT,Number=1,Type=Integer,Description=\"Number of Species Having Source Nucleotide\">
##INFO=<ID=NU,Number=1,Type=Integer,Description=\"Number of Species Having Source and Target Nucleotides\">
##FORMAT=<ID=FI,Number=1,Type=String,Description=\"Source Files\">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tFILENAMES
""" % (self.ctime, ";".join( self.getFileDesc() ), self.getNumFiles() )
        return header



def main(incsv):
    data       = vcfHeap()
    outfile    = incsv + '.vcf.gz'

    if not os.path.exists( incsv ):
        print "input file does not exists. quitting like a whimp"
        sys.exit( 1 )
    print "reading %s" % incsv


    if os.path.exists( outfile ):
        print "output file %s exists. quitting like a whimp" % outfile
        sys.exit( 1 )
    print "saving to %s" % outfile

    cfh = openfile(incsv, 'r')
    for line in cfh:
        if line[0] == "#": continue
        line = line.strip()
        cols = line.split('\t')

        try:
            if not os.path.exists( cols[1] ):
                print "vcf file %s does not exists" % cols[ 1 ]
                sys.exit( 1 )
            else:
                print "vcf file %s does exists" % cols[ 1 ]

        except:
            print line
            print cols
            print "error parsing"
            sys.exit(1)

        print cols, cols[:3]
        data.addFile(*cols[:3])





    mfh = openvcffile(outfile + '.tmp.vcf.gz', 'w', compresslevel=1)

    mfh.write( data.getVcfHeader() )

    lines = []
    while not data.isempty():
        val = data.next()
        if val is not None: # if not empty
            lines.append( str( val ) )
            if len( lines ) == 50000:
                mfh.write( "".join( lines ) )
                lines = []

        else:
            print "val is empty"
            break

    mfh.write( "".join( lines ) )
    lines = []

    mfh.close()

    os.rename(outfile + '.tmp.vcf.gz', outfile)

    print "Finished"

    return outfile

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "wrong number of arguments. %s <input list>" % sys.argv[0]
        sys.exit(1)

    incsv      = sys.argv[ 1 ]

    main(incsv)
