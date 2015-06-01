#!/usr/bin/python
import os
import sys
import argparse
import time
import datetime
ts        = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')



#/home/assembly/tomato150/programs/vcfmerger_ui/data/src/ara/indata
#./vcfmerger/gen_makefile.py --input arabidopsis.csv         --infasta TAIR10.fasta                                     --size 50000 --project arabidopsis_50k              --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --excluded-chrom chloroplast --excluded-chrom mitochondria --cluster-no-cols
#make -f makefile_arabidopsis_50k
#
#./vcfmerger/gen_makefile.py --input arabidopsis_xianwen.csv --filter-gff TAIR10.fasta_50000.gff.Chr4.gff.inversion.gff              --project arabidopsis_xianwen_50k      --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --excluded-chrom chloroplast --excluded-chrom mitochondria --cluster-no-cols
#make -f makefile_arabidopsis_xianwen_50k
#
#./vcfmerger/gen_makefile.py --input arabidopsis_xianwen.csv --filter-gff TAIR10.fasta_50000.gff.Chr4.gff.inversion.gff              --project arabidopsis_xianwen_50k_sing --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --excluded-chrom chloroplast --excluded-chrom mitochondria --cluster-no-cols --simplify-include-singleton
#make -f makefile_arabidopsis_xianwen_50k_sing
#
#./vcfmerger/gen_makefile.py --input arabidopsis_xianwen.csv --filter-gff TAIR10.fasta_10000.gff.Chr4.gff.inversion.gff              --project arabidopsis_xianwen_10k      --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --excluded-chrom chloroplast --excluded-chrom mitochondria --cluster-no-cols
#make -f makefile_arabidopsis_xianwen_10k
#
#./vcfmerger/gen_makefile.py --input arabidopsis_xianwen.csv --filter-gff TAIR10.fasta_10000.gff.Chr4.gff.inversion.gff              --project arabidopsis_xianwen_10k_sing --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --excluded-chrom chloroplast --excluded-chrom mitochondria --cluster-no-cols --simplify-include-singleton
#make -f makefile_arabidopsis_xianwen_10k_sing
#
#
#
#/home/assembly/tomato150/programs/vcfmerger_ui/data/src/tom85
#./vcfmerger/gen_makefile.py --input short2.lst --infasta S_lycopersicum_chromosomes.2.40.fa --size 10000               --project tom84_10k               --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --cluster-no-cols
#make -f makefile_tom84_10k
#
#./vcfmerger/gen_makefile.py --input short2.lst --infasta S_lycopersicum_chromosomes.2.40.fa --size 50000               --project tom84_50k               --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --cluster-no-cols
#make -f makefile_tom84_50k
#
#./vcfmerger/gen_makefile.py --input short2.lst --filter-gff ITAG2.3_gene_models.gff3.gene.gff3                         --project tom84_genes             --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --cluster-no-cols
#make -f makefile_tom84_genes
#
#./vcfmerger/gen_makefile.py --input short2.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_10000_introgression.gff --project tom84_10k_introgression --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --cluster-no-cols
#make -f makefile_tom84_10k_introgression
#
#./vcfmerger/gen_makefile.py --input short2.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_50000_introgression.gff --project tom84_50k_introgression --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --cluster-no-cols
#make -f makefile_tom84_50k_introgression
#
#
#
#/home/assembly/tomato150/programs/vcfmerger_ui/data/src/RIL
#./vcfmerger/gen_makefile.py --input RIL.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_50000.gff   --project RIL_50k                        --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --cluster-no-cols
#make -f makefile_RIL_50k
#
#./vcfmerger/gen_makefile.py --input RIL.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_50000.gff   --project RIL_50k_mode_ril               --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --concat-RIL --cluster-no-cols
#make -f makefile_RIL_50k_mode_ril
#
#./vcfmerger/gen_makefile.py --input RIL.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_50000.gff   --project RIL_50k_mode_ril_greedy        --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --concat-RIL --concat-RIL-greedy --cluster-no-cols
#make -f makefile_RIL_50k_mode_ril_greedy
#
#./vcfmerger/gen_makefile.py --input RIL.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_50000.gff   --project RIL_50k_mode_ril_delete        --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --concat-RIL --concat-RIL-delete --cluster-no-cols
#make -f makefile_RIL_50k_mode_ril_delete
#
#./vcfmerger/gen_makefile.py --input RIL.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_50000.gff   --project RIL_50k_mode_ril_delete_greedy --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --concat-RIL --concat-RIL-greedy --concat-RIL-delete --cluster-no-cols
#make -f makefile_RIL_50k_mode_ril_delete_greedy
#
#./vcfmerger/gen_makefile.py --input RIL.lst --filter-gff S_lycopersicum_chromosomes.2.40.fa_10000.gff   --project RIL_10k                        --no-pickle --cluster-no-svg --smart_threads 25 --cluster-threads 5 --cluster-no-cols
#make -f makefile_RIL_10k

SCRIPT_DIR   = 'vcfmerger'
AUX_DIR      = os.path.join(SCRIPT_DIR)


merger       = os.path.abspath( os.path.join( SCRIPT_DIR, 'vcfmerger.py'    ) )
simplify     = os.path.abspath( os.path.join( SCRIPT_DIR, 'vcfsimplify.py'  ) )
filtergff    = os.path.abspath( os.path.join( SCRIPT_DIR, 'vcffiltergff.py' ) )
concat       = os.path.abspath( os.path.join( SCRIPT_DIR, 'vcfconcat.py'    ) )
walk_ram     = os.path.abspath( os.path.join( SCRIPT_DIR, 'vcf_walk_ram.py' ) )
walk_sql     = os.path.abspath( os.path.join( SCRIPT_DIR, 'vcf_walk_sql.py' ) )
cluster      = os.path.abspath( os.path.join( SCRIPT_DIR, 'cluster.py'      ) )
topng        = os.path.abspath( os.path.join( SCRIPT_DIR, 'newick_to_png.py') )
fasta_spacer = os.path.abspath( os.path.join( SCRIPT_DIR, 'fasta_spacer.py' ) )
tree_maker   = os.path.abspath( os.path.join( SCRIPT_DIR, 'FastTreeMP'      ) )


class makewriter(object):
    def __init__(self, outf='makefile', dry=False):
        self.dry  = dry
        self.outf = outf
        if not self.dry:
            self.fhd = open(outf, 'w')

    def write(self, src, dst, cmd, nick=None):
        if not self.dry:
            self.fhd.write(dst)
            self.fhd.write(': '+src+'\n')
            self.fhd.write("\t"+cmd+'\n\n')

            if nick:
                phony = """\
.PHONY: %s
%s: %s

""" % ( nick, nick, dst )
                self.fhd.write(phony)


        else:
            sys.stdout.write(self.outf + ' :: ' + dst )
            sys.stdout.write(': '+src+'\n')
            sys.stdout.write(self.outf + ' :: ' + "\t"+cmd+'\n\n')

    def raw(self, line):
        if not self.dry:
            self.fhd.write(line)
        else:
            n = '\n%s :: '%self.outf
            sys.stdout.write( n + n.join( line.split('\n') ) + '\n' )

    def close(self):
        if not self.dry:
            self.fhd.close()


def listChromsFasta(infasta):
    chroms = []
    with open(infasta) as fhd:
        for line in fhd:
            if line[0] == '>':
                print line
                chroms.append( line.strip()[1:].split()[0])
    if len(chroms) == 0:
        print "no chroms in fasta"
        sys.exit(1)
    return chroms


def listChromsGff(ingff):
    chroms = []
    with open(ingff) as fhd:
        for line in fhd:
            if line[0] == '#':
                continue
            pos = line.find("\t")
            if pos != -1:
                chrom = line[:pos]
                if chrom not in chroms:
                    print line
                    chroms.append( chrom )

    if len(chroms) == 0:
        print "no chroms in gff"
        sys.exit(1)

    return chroms


def main(args):
    parser = argparse.ArgumentParser(description='Create makefile to convert files.')
    parser.add_argument( '-i'  , '--input', '--inlist'                     , dest='inlist'                      , default=None      , nargs='?',                       type=str  , help='input tab separated file')
    parser.add_argument( '-f'  , '--fasta', '--infasta'                    , dest='infasta'                     , default=None      , nargs='?',                       type=str  , help='input reference fasta. requires split size')
    parser.add_argument( '-s'  , '--size' ,                                  dest='size'                        , default=0         , nargs='?',                       type=int  , help='split size')
    parser.add_argument( '-p'  , '--proj' , '--project'                    , dest='project'                     , default=None      , nargs='?',                       type=str  , help='project name')
    parser.add_argument( '-o'  , '--out'  , '--outfile'                    , dest='outfile'                     , default='makefile', nargs='?',                       type=str  , help='output name [default: makefile]')
    parser.add_argument( '-ec' , '--excluded-chrom'                        , dest='excluded_chroms'             , default=[]        ,            action='append'     , type=str  , help='Do not use the following chromosomes' )
    parser.add_argument( '-ic' , '--included-chrom'                        , dest='included_chroms'             , default=[]        ,            action='append'     , type=str  , help='Use EXCLUSIVELY these chromosomes' )
    #parser.add_argument( '-g' , '--gff'  , '--ingff'                      , dest='ingff'                       , default=None      , nargs='?',                       type=str  , help='input gff file')

    parser.add_argument( '-n'  , '--dry'  , '--dry-run'                    , dest='dry'                         , default=False     ,            action='store_true' ,             help='dry-run')
    parser.add_argument( '-m'  , '--merge', '--cluster_merge'              , dest='merge'                       , default=False     ,            action='store_true' ,             help='do merged clustering (resource intensive) [default: no]')
    parser.add_argument( '-np' , '--no-pickle',                              dest='dopickle'                    , default=True      ,            action='store_false',             help='do not generate pickle database [default: no]')

    parser.add_argument( '-t'  , '--sub_threads'                           , dest='sub_threads'                 , default=5         , nargs='?',                       type=int  , help='threads of submake to tree building [default: 5]')
    parser.add_argument( '-St' , '--smart_threads'                         , dest='smart_threads'               , default=None      , nargs='?',                       type=int  , help='threads of submake to tree building [default: 5]')

    parser.add_argument( '-SH' , '--simplify-include-hetero'               , dest='simplify_do_hetero_filter'   , default=True      ,            action='store_false',             help='Do not simplify heterozygous SNPS')
    parser.add_argument( '-SI' , '--simplify-include-indel'                , dest='simplify_do_indel_filter'    , default=True      ,            action='store_false',             help='Do not simplify indel SNPS')
    parser.add_argument( '-SS' , '--simplify-include-singleton'            , dest='simplify_do_singleton_filter', default=True      ,            action='store_false',             help='Do not simplify single SNPS')
    parser.add_argument( '-So' , '--simplify-output'                       , dest='simplify_output'             , default=None      , nargs='?',                       type=str  , help='Simplify output file')

    parser.add_argument( '-Coc', '--concat-chrom',  '--concat-chromosome'  , dest='concat_chromosome'           , default=None      , nargs='?', action='store'      , type=str  , help='Concat - Chromosome to filter [all]')
    parser.add_argument( '-CoI', '--concat-ignore', '--concat-skip'        , dest='concat_ignore'               , default=[]        , nargs='*', action='append'     , type=str  , help='Concat - Chromosomes to skip')
    parser.add_argument( '-Cos', '--concat-start'                          , dest='concat_start'                , default=None      , nargs='?', action='store'      , type=int  , help='Concat - Chromosome start position to filter [0]')
    parser.add_argument( '-Coe', '--concat-end'                            , dest='concat_end'                  , default=None      , nargs='?', action='store'      , type=int  , help='Concat - Chromosome end position to filter [-1]')
    parser.add_argument( '-Cot', '--concat-threads'                        , dest='concat_threads'              , default=None      , nargs='?', action='store'      , type=int  , help='Concat - Number of threads [num chromosomes]')
    parser.add_argument( '-Cor', '--concat-noref'                          , dest='concat_noref'                ,                                action='store_false',             help='Concat - Do not print reference [default: true]')
    parser.add_argument( '-CoR', '--concat-RIL'                            , dest='concat_RIL'                  ,                                action='store_true' ,             help='Concat - RIL mode: false]')
    parser.add_argument( '-CoRm','--concat-RIL-mads'                       , dest='concat_RILmads'              , default=None      , nargs='?', action='store'      , type=float, help='Concat - RIL percentage of Median Absolute Deviation to use (smaller = more restrictive): 0.25]')
    parser.add_argument( '-CoRs','--concat-RIL-minsim'                     , dest='concat_RILminsim'            , default=None      , nargs='?', action='store'      , type=float, help='Concat - RIL percentage of nucleotides identical to reference to classify as reference: 0.75]')
    parser.add_argument( '-CoRg','--concat-RIL-greedy'                     , dest='concat_RILgreedy'            ,                                action='store_true' ,             help='Concat - RIL greedy convert nucleotides to either the reference sequence or the alternative sequence: false]')
    parser.add_argument( '-CoRd','--concat-RIL-delete'                     , dest='concat_RILdelete'            ,                                action='store_true' ,             help='Concat - RIL delete invalid sequences: false]')

    parser.add_argument( '-Ftt', '--fasttree_threads'                      , dest='fasttree_threads'            , default=1         , nargs='?',                       type=int  , help='FastTree - number of threads for fasttree')
    parser.add_argument( '-Ftb', '--fasttree_bootstrap'                    , dest='fasttree_bootstrap'          , default=100       , nargs='?',                       type=int  , help='FastTree - fasttree bootstrap')

    parser.add_argument( '-Cle', '--cluster-ext', '--cluster-extension'    , dest='cluster_extension'           , default=None      , nargs='?',                       type=str  , help='Cluster - [optional] extension to search. [default: .matrix]')
    parser.add_argument( '-Clt', '--cluster-threads'                       , dest='cluster_threads'             , default=1         , nargs='?',                       type=int  , help='Cluster - threads for clustering [default: 5]')
    parser.add_argument( '-Clp', '--cluster-no-png'                        , dest='cluster_dopng'               ,                                action='store_false',             help='Cluster - do not export cluster png')
    parser.add_argument( '-Cls', '--cluster-no-svg'                        , dest='cluster_dosvg'               ,                                action='store_false',             help='Cluster - do not export cluster svg')
    parser.add_argument( '-Cln', '--cluster-no-tree'                       , dest='cluster_dotree'              ,                                action='store_false',             help='Cluster - do not export cluster tree. precludes no png and no svg')
    parser.add_argument( '-Clr', '--cluster-no-rows'                       , dest='cluster_dorows'              ,                                action='store_false',             help='Cluster - no rows clustering')
    parser.add_argument( '-Clc', '--cluster-no-cols'                       , dest='cluster_docols'              ,                                action='store_false',             help='Cluster - no column clustering')

    parser.add_argument( '-Fic', '--filter-chrom'   , '--filter-chromosome', dest='filter_chromosome'           , default=None      , nargs='?', action='store'      , type=str  , help='Filter - Chromosome to filter [all]')
    parser.add_argument( '-Fig', '--filter-gff'     ,                        dest='filter_gff'                  , default=None      , nargs='?', action='store'      , type=str  , help='Filter - Gff Coordinate file')
    parser.add_argument( '-FiI', '--filter-ignore'  , '--filter-skip'      , dest='filter_ignore'               , default=[]        , nargs='*', action='append'     , type=str  , help='Filter - Chromosomes to skip')
    parser.add_argument( '-Fis', '--filter-start'   ,                        dest='filter_start'                , default=None      , nargs='?', action='store'      , type=int  , help='Filter - Chromosome start position to filter [0]')
    parser.add_argument( '-Fie', '--filter-end'     ,                        dest='filter_end'                  , default=None      , nargs='?', action='store'      , type=int  , help='Filter - Chromosome end position to filter [-1]')
    parser.add_argument( '-Fik', '--filter-knife'   ,                        dest='filter_knife'                ,                                action='store_true' ,             help='Filter - Export to separate files')
    parser.add_argument( '-Fin', '--filter-negative',                        dest='filter_negative'             ,                                action='store_true' ,             help='Filter - Invert gff')
    parser.add_argument( '-Fiv', '--filter-verbose' ,                        dest='filter_verbose'              ,                                action='store_true' ,             help='Filter - Verbose')
    parser.add_argument( '-Fip', '--filter-prot'    , '--filter-protein'   , dest='filter_protein'              , default=None      ,            action='store'      , type=str  , help='Filter - Input Fasta File to convert to Protein')

    parser.add_argument( '-Dbt', '--db-threads'     ,                        dest='db_read_threads'             , default=1         ,                                  type=int  , help='Db - Number of threads to read raw files'                    )

    options                      = parser.parse_args(args)

    inlist                       = options.inlist
    infasta                      = options.infasta
    #ingff                        = options.ingff
    size                         = options.size
    projname                     = options.project
    outfile                      = options.outfile
    sub_threads                  = options.sub_threads
    smart_threads                = options.smart_threads
    fasttree_threads             = options.fasttree_threads
    fasttree_bootstrap           = options.fasttree_bootstrap
    dry                          = options.dry
    merge                        = options.merge
    dopickle                     = options.dopickle
    excluded_chroms              = options.excluded_chroms
    included_chroms              = options.included_chroms

    simplify_do_hetero_filter    = options.simplify_do_hetero_filter
    simplify_do_indel_filter     = options.simplify_do_indel_filter
    simplify_do_singleton_filter = options.simplify_do_singleton_filter
    simplify_output              = options.simplify_output

    #filter_chromosome            = options.filter_chromosome
    filter_gff                   = options.filter_gff
    #filter_ignore                = options.filter_ignore
    filter_start                 = options.filter_start
    filter_end                   = options.filter_end
    #filter_knife                 = options.filter_knife
    filter_negative              = options.filter_negative
    filter_verbose               = options.filter_verbose
    filter_protein               = options.filter_protein

    concat_chromosome            = options.concat_chromosome
    concat_ignore                = options.concat_ignore
    concat_start                 = options.concat_start
    concat_end                   = options.concat_end
    concat_threads               = options.concat_threads
    concat_noref                 = options.concat_noref
    concat_RIL                   = options.concat_RIL
    concat_RILmads               = options.concat_RILmads
    concat_RILminsim             = options.concat_RILminsim
    concat_RILgreedy             = options.concat_RILgreedy
    concat_RILdelete             = options.concat_RILdelete

    cluster_extension            = options.cluster_extension
    cluster_threads              = options.cluster_threads
    cluster_dopng                = options.cluster_dopng
    cluster_dosvg                = options.cluster_dosvg
    cluster_dotree               = options.cluster_dotree
    cluster_dorows               = options.cluster_dorows
    cluster_docols               = options.cluster_docols

    db_read_threads              = options.db_read_threads

    print options

    chroms = None

    if inlist is None:
        print "no input list given"
        sys.exit(1)

    if not os.path.exists(inlist):
        print 'input list %s does not exists' % inlist
        sys.exit(1)

    if infasta and filter_gff:
        print "either fasta or gff expected. not both"
        sys.exit(1)

    if not ( infasta or filter_gff ):
        print "either fasta or gff required"
        sys.exit(1)


    if infasta:
        if not size:
            print "if fasta is define, size has to be defined also"
            sys.exit(1)
        if not os.path.exists(infasta):
            print "infasta %s does not exists" % infasta
            sys.exit(1)
        filter_gff = "%s_%s.gff" % (infasta, size)

        chroms = listChromsFasta(infasta)

    elif filter_gff:
        if not os.path.exists(filter_gff):
            print "input gff %s does not exists" % filter_gff
            sys.exit(1)
        chroms = listChromsGff(filter_gff)


    if len(included_chroms) > 0:
        chroms = list(set(chroms) & set(included_chroms))
        chroms.sort()

    if len(excluded_chroms) > 0:
        chroms = list(set(chroms) - set(excluded_chroms))
        chroms.sort()


    print "CHROMS", chroms







    outmake = outfile + '_' + projname

    writer  = makewriter( outf=outmake, dry=dry )


    writer.raw( "#TIME: " + timestamp        + "\n"   )
    writer.raw( "#CMD : " + " ".join( args ) + "\n"   )
    writer.raw( "#PWD : " + os.getcwd()      + "\n\n" )
    writer.write( projname+".sqlite", 'all', '' )



    #vcfmerger/vcfmerger.py short.lst
    inlist_merged = inlist + '.vcf.gz'
    merge_cmd     = "%s %s" % (merger, inlist)
    writer.write(inlist, inlist_merged, merge_cmd, nick='merged')



    #vcfmerger/vcfsimplify.py short.lst.vcf.gz
    simplify_cmd         = "%s --input %s" % (simplify, inlist_merged)

    inlist_merged_simple = inlist_merged + '.simplified'

    if not simplify_do_hetero_filter:
        simplify_cmd += " --include-hetero"
        inlist_merged_simple  += '.hetero'

    if not simplify_do_indel_filter:
        simplify_cmd += " --include-indel"
        inlist_merged_simple  += '.indel'

    if not simplify_do_singleton_filter:
        simplify_cmd += " --include-singleton"
        inlist_merged_simple  += '.single'

    if not simplify_output:
        inlist_merged_simple += '.vcf.gz'
    else:
        inlist_merged_simple = simplify_output

    simplify_cmd += " --output " + inlist_merged_simple

    writer.write( inlist_merged, inlist_merged_simple, simplify_cmd, nick='simple')






    if infasta:
        #vcfmerger/fasta_spacer.py GENOME.fa 50000
        gff_cmd = "%s %s %s"  % (fasta_spacer, infasta, size)
        writer.write( infasta, filter_gff, gff_cmd, nick='gff' )





    #vcfmerger/vcffiltergff.py -k -f PROJNAME -g GENOME.fa_50000.gff -i short2.lst.vcf.gz.simplified.vcf.gz 2>&1 | tee short2.lst.vcf.gz.simplified.vcf.gz.log
    filter_opts = ""
    #if  filter_chromosome:
    #    filter_opts += ' --chromosome ' + filter_chromosome #'' store str
    if  filter_gff:
        filter_opts += ' --gff ' + filter_gff #        ''        store str
    if len(excluded_chroms) > 0:
        for ichrom in excluded_chroms:
            filter_opts += ' --ignore ' + ichrom
    #if len(filter_ignore) > 0:
    #    for ichrom in filter_ignore:
    #        filter_opts += ' --ignore ' + ichrom
    if  filter_start:
        filter_opts += ' --start %d' % filter_start      #''      store int
    if  filter_end:
        filter_opts += ' --end %d'   % filter_end        #''        store int
    #if  filter_knife:
    #    filter_opts += ' --knife'      #''      true
    if  filter_negative:
        filter_opts += ' --negative'   #''   true
    if  filter_verbose:
        filter_opts += ' --verbose'    #''    true
    if  filter_protein:
        filter_opts += ' --protein %s' % filter_protein    #''    action str

    filter_cmd = "%s --knife --folder %s --gff %s --input %s %s 2>&1 | tee %s.log" % ( filtergff, projname, filter_gff, inlist_merged_simple, filter_opts, inlist_merged_simple )
    filter_ok  = projname+'.ok'
    filter_gff = inlist_merged_simple + ' ' + filter_gff
    writer.write(filter_gff , filter_ok, filter_cmd, nick='filter' )







    conv_ok  = projname+".conv.ok"
    if smart_threads:
        fasttree_threads_2 = int( smart_threads / fasttree_threads )
        cluster_threads_2  = int( smart_threads / cluster_threads  )
        if db_read_threads == 1:
            db_read_threads = smart_threads


        if fasttree_threads != 1:
            conv_cmd = "cd %s && $(MAKE) -j %d fasta" % (projname, smart_threads)
            writer.write( filter_ok, conv_ok + '_fasta', conv_cmd, nick='sub_fasta' )

            conv_cmd = "cd %s && $(MAKE) -j %d tree matrix" % (projname, fasttree_threads_2)
            writer.write( conv_ok + '_fasta', conv_ok + '_fasttree', conv_cmd, nick='sub_tree' )

            conv_cmd = "cd %s && $(MAKE) -j %d rawfiles" % (projname, smart_threads)
            writer.write( conv_ok + '_fasttree', conv_ok + '_raw', conv_cmd, nick='sub_raw' )
        else:
            conv_cmd = "cd %s && $(MAKE) -j %d rawfiles" % (projname, smart_threads)
            writer.write( filter_ok, conv_ok + '_raw', conv_cmd, nick='sub_raw' )


        if merge:
            conv_cmd = "cd %s && $(MAKE) -j %d subpickles" % (projname, cluster_threads_2)
            writer.write( conv_ok + '_raw', conv_ok + '_pickle', conv_cmd, nick='sub_pic' )

            conv_cmd = "cd %s && $(MAKE) -j %d ok" % (projname, smart_threads)
            writer.write( conv_ok + '_pickle', conv_ok, conv_cmd, nick='sub' )
        else:
            conv_cmd = "cd %s && $(MAKE) -j %d ok" % (projname, cluster_threads_2)
            writer.write( conv_ok + '_raw', conv_ok, conv_cmd, nick='sub' )

    else:
        conv_cmd = "cd %s && $(MAKE) -j %d" % (projname, sub_threads)
        writer.write( filter_ok, conv_ok, conv_cmd, nick='sub' )






    walk_db = '.'
    if dopickle:
        #vcf_walk_ram.py --pickle PROJNAME
        walk_cmd_opts = ""
        if cluster_threads:
            walk_cmd_opts += ' --cluster-threads %d' % cluster_threads
        if cluster_extension:
            walk_cmd_opts += ' --cluster-extension ' + cluster_extension
        if merge:
            walk_cmd_opts += ' --cluster-global'
        if not cluster_dopng:
            walk_cmd_opts += ' --cluster-no-png'
        if not cluster_dosvg:
            walk_cmd_opts += ' --cluster-no-svg'
        if not cluster_dotree:
            walk_cmd_opts += ' --cluster-no-tree'
        if not cluster_dorows:
            walk_cmd_opts += ' --cluster-no-rows'
        if not cluster_docols:
            walk_cmd_opts += ' --cluster-no-cols'

        walk_cmd = "%s --pickle %s --database %s" % (walk_ram, walk_cmd_opts, projname)

        walk_db  = projname+".pickle.gz"
        writer.write( conv_ok, walk_db, walk_cmd, nick='db' )








    #vcf_walk_sql.py PROJNAME
    walk_cmd_opts = ""
    walk_db_sql   = projname+".sqlite"
    if cluster_threads:
        walk_cmd_opts += ' --cluster-threads %d' % cluster_threads
    if cluster_extension:
        walk_cmd_opts += ' --cluster-extension ' + cluster_extension
    if merge:
        walk_cmd_opts += ' --cluster-global'
    if not cluster_dopng:
        walk_cmd_opts += ' --cluster-no-png'
    if not cluster_dosvg:
        walk_cmd_opts += ' --cluster-no-svg'
    if not cluster_dotree:
        walk_cmd_opts += ' --cluster-no-tree'
    if not cluster_dorows:
        walk_cmd_opts += ' --cluster-no-rows'
    if not cluster_docols:
        walk_cmd_opts += ' --cluster-no-cols'
    if db_read_threads != 1:
        walk_cmd_opts += ' --threads %d' % db_read_threads

    walk_cmd    = "%s %s --database %s" % (walk_sql, walk_cmd_opts, projname)

    if dopickle:
        walk_cmd    += ' --pickle'
        writer.write( walk_db, walk_db_sql, walk_cmd, nick='sql' )
    else:
        writer.write( conv_ok, walk_db_sql, walk_cmd, nick='sql' )










    cleaners = """\

.PHONY: cleansql
cleansql:
\trm %(sql)s

.PHONY: cleandb
cleandb: cleansql
\trm %(db)s
\trm %(projname)s_*.pickle.gz




.PHONY: cleansub
cleansub: cleandb
\tcd %(projname)s && $(MAKE) clean

.PHONY: cleansubok
cleansubok: cleandb
\tcd %(projname)s && $(MAKE) cleanok

.PHONY: cleansubsubpickles
cleansubsubpickles: cleandb
\tcd %(projname)s && $(MAKE) cleansubpickles

.PHONY: cleansubpickles
cleansubpickles: cleandb
\tcd %(projname)s && $(MAKE) cleanpickles

.PHONY: cleansubrawfiles
cleansubrawfiles: cleandb
\tcd %(projname)s && $(MAKE) cleanrawfiles

.PHONY: cleansubimgs
cleansubimgs: cleandb
\tcd %(projname)s && $(MAKE) cleanimgs

.PHONY: cleansubtrees
cleansubtrees: cleandb
\tcd %(projname)s && $(MAKE) cleantrees

.PHONY: cleansubmatrices
cleansubmatrices: cleandb
\tcd %(projname)s && $(MAKE) cleanmatrices

.PHONY: cleansubfastas
cleansubfastas: cleandb
\tcd %(projname)s && $(MAKE) cleanfastas



.PHONY: cleanfilter
cleanfilter: cleandb
\tcd %(projname)s && $(MAKE) cleangzs
\trm %(subok)s

.PHONY: cleansimple
cleansimple: cleanfilter
\trm %(simple)s

.PHONY: cleanmerged
cleanmerged: cleansimple
\trm %(merged)s

.PHONY: clean
clean: cleanmerged



.PHONY: subfasta
subfasta: filter
\tcd %(projname)s && $(MAKE) fasta

.PHONY: subpng
subpng: filter
\tcd %(projname)s && $(MAKE) png

.PHONY: subtree
subtree: filter
\tcd %(projname)s && $(MAKE) tree

.PHONY: submatrix
submatrix: filter
\tcd %(projname)s && $(MAKE) matrix

.PHONY: subrawfiles
subrawfiles: filter
\tcd %(projname)s && $(MAKE) rawfiles


.PHONY: subpickles
subpickles: filter
\tcd %(projname)s && $(MAKE) pickles

.PHONY: subgpickle
subgpickle: filter
\tcd %(projname)s && $(MAKE) gpickle

.PHONY: subsubpickles
subsubpickles: filter
\tcd %(projname)s && $(MAKE) subpickles

.PHONY: subok
subok: filter
\tcd %(projname)s && $(MAKE) ok




.PHONY: list
list:
\t@echo clean
\t@echo cleanmerged
\t@echo cleansimple
\t@echo cleanfilter
\t@echo cleansubfastas
\t@echo cleansubmatrices
\t@echo cleansubtrees
\t@echo cleansubimgs
\t@echo cleansubrawfiles
\t@echo cleansubpickles
\t@echo cleansub
\t@echo cleandb
\t@echo cleansql
\t@echo
\t@echo merged
\t@echo simple
\t@echo gff
\t@echo filter
\t@echo sub
\t@echo subfasta
\t@echo subpng
\t@echo subtree
\t@echo submatrix
\t@echo subrawfiles
\t@echo subpickles
\t@echo subgpickle
\t@echo subsubpickles
\t@echo subok
\t@echo db
\t@echo sql
\t@echo all
\t@echo
#\tcd %(projname)s && $(MAKE) list

""" % {
        'projname': projname,
        'merged'  : inlist_merged,
        'simple'  : inlist_merged_simple,
        'subok'   : conv_ok,
        'db'      : walk_db,
        'sql'     : walk_db_sql
    }

    writer.raw( cleaners )

    writer.close()










    if not os.path.exists(projname):
        os.mkdir(projname)

    writer2 = makewriter( outf=os.path.join(projname, outfile), dry=dry )


    subpickles = " ".join( [chrom + '.pickle.gz' for chrom in chroms] )
    gpickle    = """\

.PHONY: subpickles
subpickles: %(subpickles)s

""" % {
        "subpickles": subpickles
    }





    clusteropts  = ""
    if cluster_threads:
        clusteropts += ' --threads %d'         % cluster_threads

    if cluster_extension:
        clusteropts += ' --cluster-extension ' + cluster_extension

    if not cluster_dopng:
        clusteropts += ' --nopng'

    if not cluster_dosvg:
        clusteropts += ' --nosvg'

    if not cluster_dotree:
        clusteropts += ' --notree'

    if not cluster_dorows:
        clusteropts += ' --norows'

    if not cluster_docols:
        clusteropts += ' --nocols'

    if merge:
        gpickle += """\

.PHONY: pickles
pickles: subpickles gpickle

.PHONY: gpickle
gpickle: %(gpickle)s

%(gpickle)s: $(OUTMATRIX) $(OUTTREE)
\t%(cluster)s -o %(gpickle)s.tmp -d . %(clusteropts)s
\tmv %(gpickle)s.tmp %(gpickle)s


.PHONY: cleanpickleg
cleanpickleg: cleanok
\trm %(gpickle)s


.PHONY: cleanpickles
cleanpickles: cleanpickleg cleansubpickles cleanok

""" % {
            'gpickle'    : os.path.abspath( os.path.join(projname, projname)+".pickle.gz" ),
            'cluster'    : cluster,
            'clusteropts': clusteropts
       }


    else:
        gpickle += """\

.PHONY: pickles
pickles: subpickles

.PHONY: cleanpickles
cleanpickles: cleansubpickles cleanok

"""











    picklesClean = """\n\n\n\
.PHONY: cleansubpickles
cleansubpickles: cleanok"""

    for chrom in chroms:
        dirFix   = chrom.replace('.', '_').replace(' ', '_').replace('-', '_')
        gpickle += """

INGZS_%(dirFix)s=$(sort $(wildcard     %(dir)s/*.vcf.gz))
OUTTREE_%(dirFix)s=$(patsubst   %%.vcf.gz, %%.vcf.gz.fasta.tree    , $(INGZS_%(dirFix)s))
OUTPNG_%(dirFix)s=$(patsubst    %%.vcf.gz, %%.vcf.gz.fasta.tree.png, $(INGZS_%(dirFix)s))
OUTMATRIX_%(dirFix)s=$(patsubst %%.vcf.gz, %%.vcf.gz.fasta.matrix  , $(INGZS_%(dirFix)s))

%(pickle)s: $(OUTMATRIX_%(dirFix)s) $(OUTTREE_%(dirFix)s) $(OUTPNG_%(dirFix)s)
\t%(cluster)s --output %(pickle)s.tmp --indir %(dir)s %(clusteropts)s
\tmv %(pickle)s.tmp %(pickle)s

.PHONY: cleanpickle_%(dirFix)s
cleanpickle_%(dirFix)s: cleanok
\trm %(pickle)s

""" % {
            'pickle'     : chrom + '.pickle.gz',
            'dir'        : chrom,
            'dirFix'     : dirFix,
            'cluster'    : cluster,
            'threads'    : cluster_threads,
            'clusteropts': clusteropts
        }
        picklesClean += " cleanpickle_%s" % dirFix

    gpickle += picklesClean + "\n\n\n\n"






    concat_opts = ""
    if concat_chromosome:
        concat_opts     += " --chromosome " + concat_chromosome

    if len( concat_ignore ):
        for i in concat_ignore:
            concat_opts += " --skip    %s" % i

    if concat_start:
        concat_opts     += " --start   %d" % concat_start

    if concat_end:
        concat_opts     += " --end     %d" % concat_end

    if concat_threads:
        concat_opts     += " --threads %d" % concat_threads

    if not concat_noref:
        concat_opts     += " --noref"

    if concat_RIL:
        concat_opts     += " --RIL"

    if concat_RILmads:
        concat_opts     += " --RIL-mads"

    if concat_RILminsim:
        concat_opts     += " --RIL-minsim"

    if concat_RILgreedy:
        concat_opts     += " --RIL-greedy"

    if concat_RILdelete:
        concat_opts     += " --RIL-delete"



    header = """\
INGZS=$(sort $(wildcard     */*.vcf.gz))
OUTFASTA=$(patsubst  %%.vcf.gz, %%.vcf.gz.fasta         , $(INGZS))
OUTTREE=$(patsubst   %%.vcf.gz, %%.vcf.gz.fasta.tree    , $(INGZS))
OUTPNG=$(patsubst    %%.vcf.gz, %%.vcf.gz.fasta.tree.png, $(INGZS))
OUTMATRIX=$(patsubst %%.vcf.gz, %%.vcf.gz.fasta.matrix  , $(INGZS))

all: ok

.PHONY: ok
ok: %(okf)s

%(okf)s: fasta tree png matrix pickles
\ttouch %(okf)s

%(gpickle)s

.PHONY: rawfiles
rawfiles: matrix png

.PHONY: matrix
matrix: $(OUTMATRIX)

%%.vcf.gz.fasta.matrix: %%.vcf.gz.fasta
\texport OMP_NUM_THREADS=%(fasttree_threads)d && %(tree)s -nt -makematrix $^ > $@.tmp
\tmv $@.tmp $@

.PHONY: tree
tree: $(OUTTREE)

%%.vcf.gz.fasta.tree: %%.vcf.gz.fasta
\texport OMP_NUM_THREADS=%(fasttree_threads)d && %(matrix)s -fastest -gamma -nt -bionj -boot %(fasttree_bootstrap)d -log $@.log -out $@.tmp $^
\tmv $@.tmp $@

.PHONY: png
png: $(OUTPNG)

%%.vcf.gz.fasta.tree.png: %%.vcf.gz.fasta.tree
\t%(topng)s $^

.PHONY: fasta
fasta: $(OUTFASTA)

%%.vcf.gz.fasta: %%.vcf.gz
\t%(concat)s %(concat_opts)s --fasta -i $^
\tif [ -f "$@" ]; then rm $@; fi
\tln `readlink -f $^.*.fasta` $@








.PHONY: clean
clean: cleanok

.PHONY: cleanok
cleanok:
\trm %(okf)s

.PHONY: cleanrawfiles
cleanrawfiles: cleanimgs cleanmatrices

.PHONY: cleanimgs
cleanimgs: cleanpickles
\trm $(OUTPNG)

.PHONY: cleantrees
cleantrees: cleanimgs
\trm $(OUTTREE)

.PHONY: cleanmatrices
cleanmatrices:
\trm $(OUTMATRIX)

.PHONY: cleanfastas
cleanfastas: cleanmatrices cleantrees
\trm $(OUTFASTA)

.PHONY: cleangzs
cleangzs: cleanfastas
\trm $(INGZS)

.PHONY: list
list:
\t@echo cleangzs
\t@echo cleanfastas
\t@echo cleanmatrices
\t@echo cleantrees
\t@echo cleanimgs
\t@echo cleanrawfiles
\t@echo cleanok
\t@echo cleanpickles
\t@echo cleansubpickles
\t@echo fasta
\t@echo png
\t@echo tree
\t@echo matrix
\t@echo outfiles
\t@echo pickles
\t@echo gpickle
\t@echo subpickles
\t@echo ok
\t@echo all
\t@echo

""" % {
            'okf'               : os.path.abspath( projname+".conv.ok" ),
            'gpickle'           : gpickle,
            'tree'              : tree_maker,
            'matrix'            : tree_maker,
            'concat'            : concat,
            'concat_opts'       : concat_opts,
            'fasttree_threads'  : fasttree_threads,
            'fasttree_bootstrap': fasttree_bootstrap,
            'cluster'           : cluster,
            'threads'           : cluster_threads,
            'topng'             : topng
       }
    writer2.raw( header )
    writer2.close()

    print "SAVED TO",outmake




if __name__ == "__main__":
    main(sys.argv[1:])
