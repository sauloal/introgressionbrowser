#!/usr/bin/env python
import os
import sys
import fnmatch

sys.path.insert(0,'.')
sys.path.insert(0,'./aux')

import vcfmerger
import vcfsimplify
import vcffiltergff
import vcfconcat
import vcf_walk_ram
import vcf_walk_sql

import fasta_spacer


def main(args):
    inlist, infasta, size, projname = args

    if os.path.exists(inlist):
        #vcfmerger/vcfmerger.py short.lst
        inlist_merged = vcfmerger.main(inlist)

        if os.path.exists(inlist_merged):
            #vcfmerger/vcfsimplify.py short.lst.vcf.gz
            inlist_merged_simple = vcfsimplify.main([inlist_merged])

            if os.path.exists(inlist_merged_simple):
                #vcfmerger/aux/fasta_spacer.py GENOME.fa 50000
                gff = fasta_spacer.main(infasta, size)

                if os.path.exists(gff):
                    #vcfmerger/vcffiltergff.py -k -f PROJNAME -g GENOME.fa_50000.gff -i short2.lst.vcf.gz.simplified.vcf.gz 2>&1 | tee short2.lst.vcf.gz.simplified.vcf.gz.log
                    outdata   = vcffiltergff.main(['-k', '-f', projname, '-g', gff, '-i', inlist_merged_simple])
                    outfolder = outdata['outfolder']
                    outfile   = outdata['outfile'  ]

                    if os.path.exists(outfolder) and os.path.exists(outfile):
                        #find PROJNAME -name '*.vcf.gz' | xargs -I{} -P50 bash -c 'vcfmerger/vcfconcat.py -f -i {} 2>&1 | tee {}.concat.log'
                        vcf_gzs = []

                        for root, dirnames, filenames in os.walk(outfolder):
                            for filename in fnmatch.filter(filenames, '*.vcf.gz'):
                                vcf_gzs.append(os.path.join(root, filename))

                        for mfile in vcf_gzs:
                            mout = vcfconcat.main(['-f', '-i', mfile])


                        fastas = []

                        for root, dirnames, filenames in os.walk(outfolder):
                            for filename in fnmatch.filter(filenames, '*.vcf.gz'):
                                fastas.append(os.path.join(root, filename))

                        outs = []

                        for fasta in fastas:
                            #find PROJNAME -name '*.fasta' | sort | xargs -I{} -P30 bash -c 'vcfmerger/aux/FastTreeMP -fastest -gamma -nt -bionj -boot 100 -log {}.tree.log -out {}.tree {}'
                            #find PROJNAME -name '*.fasta' | sort | xargs -I{} -P30 bash -c 'vcfmerger/aux/FastTreeMP -nt -makematrix {} > {}.matrix'
                            outs.append([ fasta + '.tree', fasta + '.matrix', fasta + '.tree.log' ])

                        vcf_walk_ram.main(['--pickle',projname])

                        vcf_walk_sql.main([projname])






if __name__ == "__main__":
    main(sys.argv[1:])
