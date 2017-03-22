#!/usr/bin/env python
import os
import sys
import csv
import datetime
import argparse

from copy        import deepcopy
from filemanager import checkfile, openfile, openvcffile
from csv_renamer import get_translation

"""
EX1=vcfmerger/vcfmerger_multicolumn.py
VCF=1001genomes_snp-short-indel_only_ACGTN.vcf.gz
LST=A_thaliana_master_accession_list_1135_20151008.csv

${EX1} ${VCF}
${EX1} --input ${VCF} --table ${LST} --keys tg_ecotypeid --table-values name,othername,CS_number --chromosome-translation "1:Chr1;2:Chr2;3:Chr3;4:Chr4;5:Chr5" --keep-no-coverage


ln -s 1001genomes_snp-short-indel_only_ACGTN.vcf.gz.vcf.gz arabidopsis.csv.vcf.gz
ln -s 1001genomes_snp-short-indel_only_ACGTN.vcf.gz.vcf.gz arabidopsis.csv.vcf.gz.simplified.vcf.gz
"""


class vcf(object):
    def __init__(self, fhd=None, printEvery=100000):
        self.ctime        = datetime.datetime.now().isoformat()
        self.fhd          = fhd
        self.printEvery   = printEvery
        self.lastChrom    = None
        self.numRegs      = 0
        self.numRegsChrom = 0
        self.stats        = {}
        self.statsC       = {}

    def setFhd(self, fhd):
        self.fhd          = fhd

    def printRegister(self, register):
        self.numRegs      += 1
        self.numRegsChrom += 1
        self.printString( self.parseRegister(register) )

        if register['chrom'] != self.lastChrom:
            self.numRegsChrom -= 1
            if self.lastChrom is not None:
                sys.stdout.write('\nChrom {:14,d} Total {:14,d}\n'.format(self.numRegsChrom, self.numRegs))
                print 'Chromosome Stats:', " ".join([ "{:s}: {:10,d}".format(*i) for i in sorted(self.statsC[self.lastChrom].items()) ])
                print 'Global Stats    :', " ".join([ "{:s}: {:10,d}".format(*i) for i in sorted(self.stats.items())                  ])
                self.fhd.flush()

            sys.stdout.write('\nChromosome {0}\n'.format(register['chrom']))
            sys.stdout.flush()

            self.numRegsChrom = 1
            self.lastChrom    = register['chrom']

        if self.numRegs % (self.printEvery / 100) == 0:
            sys.stdout.write('.')
            if self.numRegs % self.printEvery == 0:
                sys.stdout.write(' Chrom {:14,d} Total {:14,d}\n'.format(self.numRegsChrom, self.numRegs))
            sys.stdout.flush()

    def add_stat(self, chrom, k, v):
        if chrom not in self.statsC:
            self.statsC[chrom] = {}

        self.stats        [k] = self.stats        .get(k, 0) + v
        self.statsC[chrom][k] = self.statsC[chrom].get(k, 0) + v

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
                'UN': stats['gap'     ],
                'HO': stats['homo'    ],
                'HE': stats['het'     ]
            }
        
        
        for k,v in stats.items():
            self.add_stat(register['chrom'], k, v)

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
        self.fhd.flush()








def main(args):
    parser  = argparse.ArgumentParser(description='Simplify merged VCF file.')
    parser.add_argument('-i', '--input'                 , dest='input'            , required=True,                                    nargs='?', type=str, help='Input file'                                                 )
    parser.add_argument('-o', '--output'                , dest='output'           ,                default=None,                      nargs='?', type=str, help='Output file'                                                 )
    parser.add_argument('-t', '--table'                 , dest='table'            ,                default=None,                      nargs='?', type=str, help='Input table'                                                )
    parser.add_argument('-k', '--keys'                  , dest='keys'             ,                default=None,                      nargs='?', type=str, help='Input keys'                                                 )
    parser.add_argument('-v', '--table-values'          , dest='table_vs'         ,                default=None,                      nargs='?', type=str, help='Input table values'                                         )
    parser.add_argument('-c', '--chromosome-translation', dest='translation'      ,                default=None,                      nargs='?', type=str, help='Translation table to chromosome names [e.g.: 1:Chr1;2:Chr2' )
    parser.add_argument('-s', '--samples'               , dest='samples'          ,                default=None,                      nargs='?', type=str, help='Samples (Columns) to keep [e.g.: Spp1;Spp3;Spp5' )
    parser.add_argument('-n', '--keep-no-coverage'      , dest='keep_no_coverage' ,                              action='store_true',                      help='Keep rows containing no coverage'                           )
    parser.add_argument('-e', '--keep-heterozygous'     , dest='keep_heterozygous',                              action='store_true',                      help='Keep rows hoterozygosity'                           )

    options = parser.parse_args(args)

    print "Options", options

    invcf   = options.input
    
    try:
        checkfile(invcf)
        print "input vcf:              %s" % invcf

    except:
        parser.print_usage()
        #print "%s --input <invcf>" % sys.argv[0]
        print "EG.: %s --input 1001genomes_snp-short-indel_only_ACGTN.vcf.gz" % sys.argv[0]
        sys.exit(1)


    outbn = invcf
    if options.output is not None:
        outbn = options.output

    outbn      += (".nc" if options.keep_no_coverage else "") + (".het" if options.keep_heterozygous else "")
    listFile    = outbn + '.list.csv'
    vcfFile     = outbn + '.list.csv.vcf.gz'
    outFile     = outbn + '.list.csv.vcf.gz.simplified.vcf.gz'
    outFileTmp  = outbn + '.list.csv.vcf.gz.simplified.tmp.vcf.gz'

    if os.path.exists( outFile ):
        print "Out File (%s) EXISTS. quitting" % outFile
        sys.exit(1)


    print "Out File:               %s" % outFile


    try:
        intbl  = options.table
        checkfile(intbl)
        print "Input Table: %s" % intbl

    except:
        intbl  = None


    tbl_k  = None
    if options.keys is not None:
        tbl_k  = options.keys
        print "Input Table keys: %s" % tbl_k


    tbl_vs = None
    if options.table_vs is not None:
        tbl_vs = options.table_vs.split(',')
        print "Table values: %s" % options.table_vs


    data, atad = ( None, None )
    if intbl:
        data, atad = get_translation(intbl, tbl_k, tbl_vs)
        print 'DATA', data
        print 'ATAD', atad


    translation = {}
    if options.translation is not None:
        for pair in options.translation.split(';'):
            src, dst = pair.split(':')
            assert src not in translation
            translation[ src ] = dst

        print "Translation", translation
    else:
        translation = None


    columns = None
    if options.samples is not None:
        columns = options.samples.split(';')
        assert len(columns) > 0, "No Columns %s" % str(columns)


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

                        if columns is not None:
                            cdiff = list( set(columns) - set(names) )
                            assert len( cdiff ) == 0, "Unknown column name: %s" % ( str(cdiff) )

                        with open(listFile, 'wb') as fhdl:
                            writer = csv.writer(fhdl, delimiter='\t', quotechar='"')
                            for ln, name in enumerate(names):
                                if columns is not None:
                                    if name not in columns:
                                        continue

                                cols = ["1", "%s|%d" % (invcf, ln+1), name]

                                if data is not None:
                                    assert name in data, "name %s not in db %s" % (name, str(data))

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
                    #assert ':'  in info, line
                    if ':' not in info:
                        continue
                    assert 'GT' in info, line

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
                        'desc' :         {}  ,
                        'stats':         {
                            'unphased' : 0,
                            'phased'   : 0,
                            'gap'      : 0,
                            'ref'      : 0,
                            'homo'     : 0,
                            'het'      : 0,
                            'x_mnp_ref': 0,
                            'x_mnp_alt': 0,
                            'x_gap'    : 0,
                            'x_het'    : 0
                        }
                    }



                    if len(cols[3]) > 1:
                        print "MNP ref", cols[3]
                        vcf_holder.add_stat(cols[0], 'x_mnp_ref', 1)
                        continue

                    if any([len(x) != 1 for x in cols[4].split(',')]):
                        print "MNP alt", cols[4]
                        vcf_holder.add_stat(cols[0], 'x_mnp_alt', 1)
                        continue

                    #descs             =     cols[9:]
                    has_gap           = False
                    is_het            = False

                    for colNum, desc in enumerate(cols[9:]):
                        colname = names[colNum]

                        if columns is not None:
                            if colname not in columns:
                                continue

                        if (desc == './.') or (desc == '.'):
                            if not options.keep_no_coverage:
                                vcf_holder.add_stat(cols[0], 'x_gap', 1)
                                has_gap = True
                                break

                            else:
                                register['stats']['gap'] += 1
                                continue

                        assert ':'  in desc, desc + " " + str(cols[9:])

                        descC = desc.split(":")
                        assert len(descC) > 1
                        #print "  desc" , desc
                        #print "  descC", descC

                        #assert len(infoC) == len(descC), str(infoC) + " " + str(descC) + " " + str(cols[9:])
                        if len(infoC) != len(descC):
                            if not options.keep_no_coverage:
                                vcf_holder.add_stat(cols[0], 'x_gap', 1)
                                has_gap = True
                                break

                            else:
                                register['stats']['gap'] += 1
                                continue

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
                            if not options.keep_no_coverage:
                                register['stats']['uncalled'] += 1
                                has_gap = True
                                break
                            else:
                                vcf_holder.add_stat(cols[0], 'x_gap', 1)
                                continue

                        else:
                            if len(set([gt0, gt1])) == 1:
                                #sys.stdout.write('o')
                                register['stats']['homo'] += 1
                                
                                if (gt0 == '0'): # homozygous identical to reference
                                    register['stats']['ref'] += 1
                                    continue
                                    #register['desc' ].append( names[colNum] )

                            else:
                                #sys.stdout.write('e')
                                if not options.keep_heterozygous:
                                    vcf_holder.add_stat(cols[0], 'x_het', 1)
                                    is_het = True
                                    break
                                else:
                                    register['stats']['het'] += 1
                                    continue
                            
                            dstC = register['dst'].split(',')
                            nuc0 = register['src'] if gt0 == '0' else dstC[ int(gt0) - 1 ]
                            nuc1 = register['src'] if gt1 == '0' else dstC[ int(gt1) - 1 ]
                            nucK = (nuc0, nuc1)
                            
                            if nucK not in register['desc' ]:
                                register['desc' ][nucK] = []
                                
                            register['desc' ][nucK].append( names[colNum] )

                            #if gt0 == '0' or gt1 == '0': # if heretozygous and has reference, make it explicit
                            #    #sys.stdout.write('H')
                            #    alts = sorted(list(set(register['src'  ].split(",") + register['dst'  ].split(","))))
                            #    alts = [ a for a in alts if a != '.' ]
                            #    register['dst'  ] = ",".join(alts)
                            #    #print "   added  src to dst", self.register['dst'  ]

                            
                            #register['desc' ].append( names[colNum] )

                    #sys.stdout.flush()
                    
                    if has_gap:
                        continue

                    if is_het:
                        continue
                    
                    if len(register['desc' ]) > 0:
                        #print '+\n'
                        
                        if translation:
                            register['chrom'] = translation.get(register['chrom'], register['chrom'])
                        
                        descs = deepcopy(register['desc' ])
                        for desc in descs:
                            register['desc' ] = '|'.join(descs[desc])

                            if len(set(desc)) == 1:
                                desc = desc[0]

                            register['dst'  ] = ','.join(sorted(list(set(desc))))
                            vcf_holder.printRegister(register)

                    else:
                        #print '-'
                        pass

            fhdv.flush()

        print "\nGLOBAL STATS"
        print 'Global Stats    :', " ".join([ "{:s}: {:10,d}".format(*i) for i in sorted(vcf_holder.stats.items())                   ])

        os.rename(outFileTmp, outFile)

    os.utime(listFile, None)        

    if not os.path.exists(vcfFile):
        print "symlinking {} to {}".format(os.path.basename(invcf), vcfFile)
        os.symlink(os.path.basename(invcf), vcfFile)

    os.utime(vcfFile , None)

    os.utime(outFile , None)        

if __name__ == '__main__':
    main(sys.argv[1:])
