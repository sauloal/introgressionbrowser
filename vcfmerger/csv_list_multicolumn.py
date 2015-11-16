#!/usr/bin/python

import os
import sys
import csv
import re
import unicodedata
from unidecode import unidecode

from filemanager import checkfile, openfile

"""
EX1=vcfmerger/csv_list_multicolumn.py
EX2=vcfmerger/csv_renamer.py
VCF=1001genomes_snp-short-indel_only_ACGTN.vcf.gz
LST=A_thaliana_master_accession_list_1135_20151008.csv

${EX1} ${VCF}
${EX2} ${VCF}.list.csv ${LST} tg_ecotypeid name,othername,CS_number
"""

def main():
    try:
        invcf  = sys.argv[1]

    except:
        print "<invcf>"
        print "EG.: csv_list_multicolumn.py.py 1001genomes_snp-short-indel_only_ACGTN.vcf.gz"
        sys.exit(1)

    print "input vcf              %s" % invcf

    checkfile(invcf)

    names = None
    with openfile(invcf, 'r') as fhdi:
        with open(invcf + '.list.csv', 'wb') as fhdo:
            writer = csv.writer(fhdo, delimiter='\t', quotechar='"')
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
                        shared   = cols[:9] #CHROM    POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT
                        names    = cols[9:]

                        print "HEADER :: COL :: SHARED", shared
                        print "HEADER :: COL :: NAMES" , names

                        for ln, name in enumerate(names):
                            cols = ["1", "%s|%d" % (invcf, ln+1), name]

                            writer.writerow(cols)

                        break

if __name__ == '__main__':
    main()
