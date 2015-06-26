#!/usr/bin/python
"""
Accepts a VCF file (designed for a a merged VCF file) and simplify it by merging its lines and excluding complicating SNPs as requested
Requires vcfmerger
"""
import sys, os
import argparse
sys.path.insert(0, '.')
import vcfmerger
#import gzip
#import datetime
#import time
#import pprint
#import copy





def main(args):
    parser  = argparse.ArgumentParser(description='Simplify merged VCF file.')
    parser.add_argument('-i', '--input'            , dest='input'              , default=None,                       help='Input file'                       )
    parser.add_argument('-o', '--output'           , dest='output'             , default=None,                       help='Output file'                      )
    parser.add_argument('-H', '--include-hetero'   , dest='do_hetero_filter'   , default=True, action='store_false', help='Do not simplify heterozygous SNPS')
    parser.add_argument('-I', '--include-indel'    , dest='do_indel_filter'    , default=True, action='store_false', help='Do not simplify indel SNPS'       )
    parser.add_argument('-S', '--include-singleton', dest='do_singleton_filter', default=True, action='store_false', help='Do not simplify single SNPS'      )

    options = parser.parse_args(args)


    #infile  = options.input
    invcf   = options.input #vcfmerger.checkfile(infile)
    if not invcf:
        print "no vcf given"
        sys.exit( 1 )

    if not os.path.exists( invcf ):
        print "vcf does not exists", invcf
        sys.exit( 1 )



    outfile    = invcf + '.simplified'
    dataFilter = vcfmerger.SIMP_SNP
    if options.do_hetero_filter:
        dataFilter += vcfmerger.SIMP_EXCL_HETEROZYGOUS
        outfile    += '.hetero'

    if options.do_indel_filter:
        dataFilter += vcfmerger.SIMP_EXCL_INDEL
        outfile    += '.indel'

    if options.do_singleton_filter:
        dataFilter += vcfmerger.SIMP_EXCL_SINGLETON
        outfile    += '.single'



    if not options.output:
        outfile += '.vcf.gz'
    else:
        outfile = options.output



    if os.path.exists( outfile ):
        print "output file %s exists. quitting like a whimp" % outfile
        sys.exit( 1 )




    #dataFilter = vcfmerger.SIMP_SNP + vcfmerger.SIMP_EXCL_INDEL + vcfmerger.SIMP_EXCL_SINGLETON
    #dataFilter = vcfmerger.SIMP_SNP + vcfmerger.SIMP_EXCL_SINGLETON
        #SIMP_NO_SIMPLIFICATION =    0 # no simplification
        #SIMP_SNP               = 2**1 # simplify SNPs
        #SIMP_EXCL_HETEROZYGOUS = 2**2 # exclude heterozygous
        #SIMP_EXCL_INDEL        = 2**3 # exclude indels
        #SIMP_EXCL_SINGLETON    = 2**4 # exclude singletons
    #parser.add_argument('input'                           ,                          default=None  , action='store'      , nargs=1  , metavar='input file', help='Input file')



    data    = vcfmerger.vcfHeap( simplify=dataFilter )


    print "saving to %s" % outfile


    data.addFile('1', invcf, 'merged')

    with vcfmerger.openvcffile(outfile+'.tmp.vcf.gz', 'w', compresslevel=1) as mfh:
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

    os.rename(outfile+'.tmp.vcf.gz', outfile)
    
    print
    print data.getFilterStats()

    print "Finished"

    return outfile

if __name__ == '__main__':
    main(sys.argv[1:])
