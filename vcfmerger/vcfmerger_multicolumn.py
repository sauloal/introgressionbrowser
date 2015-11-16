#!/usr/bin/python
import os
import sys
import csv
import datetime

from filemanager import checkfile, openfile, openvcffile
from csv_renamer import get_translation

"""
EX1=vcfmerger/vcfmerger_multicolumn.py
VCF=1001genomes_snp-short-indel_only_ACGTN.vcf.gz
LST=A_thaliana_master_accession_list_1135_20151008.csv

${EX1} ${VCF}
${EX1} ${VCF} ${LST} tg_ecotypeid name,othername,CS_number
"""


class vcf(object):
    def __init__(self, fhd=None, printEvery=100000):
        self.ctime        = datetime.datetime.now().isoformat()
        self.fhd          = fhd
        self.printEvery   = printEvery
        self.lastChrom    = None
        self.numRegs      = 0
        self.numRegsChrom = 0

    def setFhd(self, fhd):
        self.fhd          = fhd

    def printRegister(self, register):
        self.numRegs      += 1
        self.numRegsChrom += 1
        self.printString( self.parseRegister(register) )

        if register['chrom'] != self.lastChrom:
            self.numRegsChrom -= 1
            if self.lastChrom is not None:
                sys.stdout.write(' Chrom {:14,d} Total {:14,d}\n'.format(self.numRegsChrom, self.numRegs))

            sys.stdout.write('\nChromosome {0}\n'.format(register['chrom']))
            sys.stdout.flush()

            self.numRegsChrom = 1
            self.lastChrom    = register['chrom']

        if self.numRegs % (self.printEvery / 100) == 0:
            sys.stdout.write('.')
            if self.numRegs % self.printEvery == 0:
                sys.stdout.write(' Chrom {:14,d} Total {:14,d}\n'.format(self.numRegsChrom, self.numRegs))
            sys.stdout.flush()

    def parseRegister(self, register):
        #print register

        stats = register['stats']

        #"UP=%{UP}d;PH=%{PH}d;UN=%{UN}d;NT=%{NT}d;HO=%{HO}d;HE=%{HE}d;NS=%{NS}d"
        ks = {
                'NV': 1,
                'NW': 1,
                'NS': 1,
                'NT': stats['ref'     ],
                'NU': len(register['desc' ].split('|')),
                'UP': stats['unphased'],
                'PH': stats['phased'  ],
                'UN': stats['uncalled'],
                'HO': stats['homo'    ],
                'HE': stats['het'     ]
            }
        info_str  = ";".join( [ "%s=%d" % ( x, ks[x] ) for x in sorted(ks) ] )

        restr = "\t".join([ register['chrom'], str(register['pos'  ]), '.', register['src'  ], register['dst'  ], '.', 'PASS', info_str, 'FI',  register['desc' ]])

        return restr

    def printString(self, text):
        if self.fhd is not None:
            #print text
            self.fhd.write(text + '\n')

    def printVcfHeader(self, fileDesc):
        fileDesc     = fileDesc
        numFiles     = len(fileDesc)

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
##INFO=<ID=UP,Number=1,Type=Integer,Description=\"Number of UnPhased calls\">
##INFO=<ID=PH,Number=1,Type=Integer,Description=\"Number of Phased calls\">
##INFO=<ID=UN,Number=1,Type=Integer,Description=\"Number of Uncalled spps\">
##INFO=<ID=HO,Number=1,Type=Integer,Description=\"Number of Homozygous calls\">
##INFO=<ID=HE,Number=1,Type=Integer,Description=\"Number of Heterozygous calls\">
##FORMAT=<ID=FI,Number=1,Type=String,Description=\"Source Files\">
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tFILENAMES""" % (self.ctime, "|".join( fileDesc ), numFiles )

        self.printString(header)








def main():
    try:
        invcf  = sys.argv[1]
        checkfile(invcf)
        print "input vcf:              %s" % invcf

    except:
        print "%s <invcf>" % sys.argv[0]
        print "EG.: %s 1001genomes_snp-short-indel_only_ACGTN.vcf.gz" % sys.argv[0]
        sys.exit(1)


    outFile    = invcf + '.vcf.gz'
    outFileTmp = invcf + '.tmp.vcf.gz'


    if os.path.exists( outFile ):
        print "Out File (%s) EXISTS. quitting" % outFile
        sys.exit(1)


    print "Out File:               %s" % outFile


    try:
        intbl  = sys.argv[2]
        tbl_k  = sys.argv[3]
        checkfile(intbl)

    except:
        intbl  = None
        tbl_k  = None



    try:
        tbl_vs = sys.argv[4].split(',')

    except:
        tbl_vs = None



    data, atad = ( None, None )
    if intbl:
        data, atad = get_translation(intbl, tbl_k, tbl_vs)
        print 'DATA', data
        print 'ATAD', atad



    vcf_holder = vcf()
    names      = None
    with openfile(invcf, 'r') as fhdi:
        with openvcffile(outFileTmp, 'w', compresslevel=1) as fhdv:
            vcf_holder.setFhd(fhdv)
            for line in fhdi:
                line = line.strip()

                if len(line) == 0:
                    continue

                if line.startswith("#"): # header
                    print "HEADER", line

                    if line.startswith("##"): # definition lines
                        print "HEADER :: DEF", line

                    else: # column description
                        print "HEADER :: COL", line

                        cols     = line.split("\t")
                        num_cols = len(cols)
                        shared   = cols[:9 ] #CHROM    POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT
                        names    = cols[ 9:]

                        print "HEADER :: COL :: SHARED", shared
                        #print "HEADER :: COL :: NAMES" , names

                        with open(invcf + '.list.csv', 'wb') as fhdl:
                            writer = csv.writer(fhdl, delimiter='\t', quotechar='"')
                            for ln, name in enumerate(names):
                                cols = ["1", "%s|%d" % (invcf, ln+1), name]

                                if data is not None:
                                    assert name in data, "name %s not in db" % name

                                    #print "converting %s to %s" % (name, data[name])
                                    cols[2]   = data[name]
                                    names[ln] = data[name]

                                #print "COLS", cols
                                writer.writerow(cols)

                        print "HEADER :: COL :: NAMES" , names

                        vcf_holder.printVcfHeader(names)

                else:
                    cols     = line.split("\t")

                    assert len( cols ) > 9

                    info      = cols[8]
                    assert ':'  in info
                    assert 'GT' in info

                    #print "has desc"
                    infoC  = info.split(':')
                    assert len(infoC) > 1
                    #print "  info" , info
                    #print "  infoC", infoC

                    gtpos = info.index('GT')
                    #print "  GT pos", gtpos

                    register = {
                        'chrom':     cols[0] ,
                        'pos'  : int(cols[1]),
                        'src'  :     cols[3] ,
                        'dst'  :     cols[4] ,
                        'desc' :         []  ,
                        'stats':         {
                            'unphased' : 0,
                            'phased'   : 0,
                            'uncalled' : 0,
                            'ref'      : 0,
                            'homo'     : 0,
                            'het'      : 0
                        }
                    }
                    descs             =     cols[9:]

                    for colNum, desc in enumerate(cols[9:]):
                        assert ':'  in desc

                        descC = desc.split(":")
                        assert len(descC) > 1
                        #print "  desc" , desc
                        #print "  descC", descC

                        assert len(infoC) == len(descC)
                        #print "   len infoC == len descC", infoC, descC

                        gtDesc   = descC[gtpos]
                        gt0, gt1 = (None, None)

                        if   '/' in gtDesc:
                            gt0, gt1 = gtDesc.split('/')
                            register['stats']['unphased'] += 1

                        elif '|' in gtDesc:
                            gt0, gt1 = gtDesc.split('|')
                            register['stats']['phased'  ] += 1

                        else:
                            assert False, 'unknown info fomat: %s (%s, %s)' % (gtDesc, info, desc)



                        if gt0 == '.' or gt1 == '.':                      # skip no coverage
                            #sys.stdout.write('.')
                            register['stats']['uncalled'] += 1

                        else:
                            if len(set([gt0, gt1])) == 1:
                                #sys.stdout.write('ho')
                                register['stats']['homo'] += 1
                                if (gt0 == '0'): # homozygous identical to reference
                                    register['stats']['ref'] += 1
                                    #sys.stdout.write('0')

                            else:
                                #sys.stdout.write('he')
                                register['stats']['het'] += 1

                            if gt0 == '0' or gt1 == '0': # if heretozygous and has reference, make it explicit
                                #sys.stdout.write('H')
                                alts = sorted(list(set(register['src'  ].split(",") + register['dst'  ].split(","))))
                                alts = [ a for a in alts if a != '.' ]
                                register['dst'  ] = ",".join(alts)
                                #print "   added  src to dst", self.register['dst'  ]

                            register['desc' ].append( names[colNum] )

                    if len(register['desc' ]) > 0:
                        #print '+\n'
                        register['desc' ] = '|'.join(register['desc' ])
                        vcf_holder.printRegister(register)

                    else:
                        #print '-'
                        pass

            fhdv.flush()

        os.rename(outFileTmp, outFile)

if __name__ == '__main__':
    main()
