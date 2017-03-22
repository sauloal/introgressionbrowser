#!/usr/bin/env python
#!pypy-1.9/bin/pypy
#import numpypy
import sys, os
import re
import array
import numpy
import time
import multiprocessing
import argparse
from pprint import pprint as pp
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'.')))
from filemanager import getFh,openvcffile,openfile,checkfile,makeIndexFile,readIndex




###fileformat=VCFv4.1
###fileDate=2013-04-06T02:40:34.596157
###source=vcfmerger
###sources=Moneymaker (001);Alisa Craig (002);Gardeners Delight (003);Rutgers (004);Galina (005);Taxi (006);Katinka Cherry (007);John's big orange (008);All Round (011);Sonato (012);Cross Country (013);Lidi (014);Momatero (015);Trote Beere (016);T1039 (017);Dana (018);Large Pink (019);Lycopersicon esculentum 825 (020);Lycopersicon esculentum 828 (021);PI129097 (022);PI272654 (023);Jersey Devil (024);S corneliomulleri lycopersicon so (025);Polish Joe (026);Cal J TM VF (027);The Dutchman (028);Black Cherry (029);Anto (030);Winter Tipe (031);Chag Li Lycopersicon esculentum (032);Belmonte (033);Tiffen Mennonite (034);Wheatley's Frost Resistant (035);PI311117 (036);PI365925 (037);Chih-Mu-Tao-Se (038);LA0113 (039);Lycopersicon esculentum Heinz conver infiniens var pluriloculare (040);PI169588 (041);Lycopersicon hirsutum (042);S pimpinellifolium (043);S pimpinellifolium (044);S pimpinellifolium (045);S pimpinellifolium (046);S pimpinellifolium (047);S pimpinellifolium (049);S chiemliewskii (051);S chiemliewskii (052);S cheesemaniae (053);S cheesemaniae (054);S cheesemaniae (055);S neorickii (056);S neorickii (057);S arcanum (058);S arcanum (059);S peruvianum (060);S huaylasense (062);S huaylasense (063);S chilense (064);S chilense (065);S habrochaites glabratum (066);S habrochaites glabratum (067);S habrochaites glabratum (068);S habrochaites glabratum (069);S habrochaites (070);S habrochaites (071);S habrochaites (072);S pennellii (073);S pennellii (074);Unknown (075);Large Red Cherry (077);Porter (078);Bloodt Butcher (088);Brandywine (089);Dixy Golden Giant (090);Giant Belgium (091);Kwntucy Beefsteak (093);Marmande VFA (094);Thessaloniki (096);Watermelon Beefsteak (097);TR00026 (102);TR00027 (103);S galapagense (104);TR00028_LA1479 (105)
###numsources=84
###INFO=<ID=NV,Number=1,Type=Integer,Description="Number of Unique Variants in Position">
###INFO=<ID=NW,Number=1,Type=Integer,Description="Number of Unique Sub-Variants in Variant">
###INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Species in Position">
###INFO=<ID=NT,Number=1,Type=Integer,Description="Number of Species in Variant">
###INFO=<ID=NU,Number=1,Type=Integer,Description="Number of Species in Sub-Variant">
###FORMAT=<ID=FI,Number=1,Type=String,Description="Source Files">
##CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	FILENAMES
#SL2.40ch00	696	.	G	A	.	PASS	NV=2;NW=2;NS=7;NT=7;NU=6	FI	PI365925 (037),LA0113 (039),S pimpinellifolium (044),S pimpinellifolium (045),S pimpinellifolium (047),S cheesemaniae (054)
#SL2.40ch00	696	.	G	T	.	PASS	NV=2;NW=2;NS=7;NT=7;NU=1	FI	S habrochaites glabratum (066)
#SL2.40ch00	778	.	T	A	.	PASS	NV=2;NW=2;NS=16;NT=16;NU=6	FI	S habrochaites glabratum (066),S habrochaites glabratum (067),S habrochaites glabratum (069),S habrochaites (070),S habrochaites (072),S pennellii (074)
#SL2.40ch00	778	.	T	G	.	PASS	NV=2;NW=2;NS=16;NT=16;NU=10	FI	PI365925 (037),LA0113 (039),S pimpinellifolium (044),S pimpinellifolium (045),S pimpinellifolium (047),S cheesemaniae (053),S cheesemaniae (054),S cheesemaniae (055),S neorickii (056),S galapagense (104)
#SL2.40ch00	1163	.	C	G	.	PASS	NV=2;NW=2;NS=3;NT=3;NU=2	FI	S huaylasense (062),S chilense (064)
#SL2.40ch00	1163	.	C	T	.	PASS	NV=2;NW=2;NS=3;NT=3;NU=1	FI	S habrochaites glabratum (068)
#SL2.40ch00	1704	.	C	A	.	PASS	NV=3;NW=3;NS=5;NT=5;NU=1	FI	S chilense (065)
#SL2.40ch00	1704	.	C	T	.	PASS	NV=3;NW=3;NS=5;NT=5;NU=2	FI	S pimpinellifolium (049),S huaylasense (063)
#SL2.40ch00	1704	.	C	T,A	.	PASS	NV=3;NW=3;NS=5;NT=5;NU=2	FI	S huaylasense (062),Unknown (075)
#SL2.40ch00	1818	.	C	G	.	PASS	NV=3;NW=3;NS=8;NT=8;NU=5	FI	S corneliomulleri lycopersicon so (025),S pimpinellifolium (049),S peruvianum (060),S huaylasense (062),S huaylasense (063)
#SL2.40ch00	1818	.	C	G,A	.	PASS	NV=3;NW=3;NS=8;NT=8;NU=1	FI	S chilense (064)
#SL2.40ch00	1818	.	C	T	.	PASS	NV=3;NW=3;NS=8;NT=8;NU=2	FI	S habrochaites glabratum (067),S habrochaites glabratum (069)

class infostats(object):
    PRINTEVERY = 2500000

    def __init__(self, outfile, titles, allowed_dup_keys=['NU'], add_only_significant=True, debug=False, significancy_filter=[]):
        self.outfile              = outfile
        self.titles               = titles
        self.allowed_dup_keys     = allowed_dup_keys
        self.add_only_significant = add_only_significant
        self.significancy_filter  = significancy_filter
        self.debug                = debug
        self.pairs                = {}
        self.spps                 = {}
        self.allchro              = {}
        self.data                 = {}
        self.cons                 = {}
        self.lastPos              = -1
        self.lastPrint            = -1

    def add(self, chro, posi, infoDic, spps):
        if self.add_only_significant:
            for key, meth, val in self.significancy_filter:
                if meth == 'gt':
                    if infoDic[key] <= val:
                        return

        if chro not in self.data:
            print "parsing chromosome %s" % chro
            self.lastPrint  = -1
            self.lastPos    = -1
            self.data[chro] = {}

            for key in infoDic:
                if key in self.titles:
                    key = self.titles[key]['Description']

                self.data[chro][key] = {}

            self.stats     = self.data[chro]



        if chro not in self.allchro: self.allchro[chro] = 0
        self.allchro[chro] += 1

        #print "SPPS", spps,"LEN",len(spps)
        for spp1pos in xrange(len(spps)):
            #print "SPPS", spps,"LEN",len(spps),"",spp1pos

            spp1 = spps[spp1pos]
            if spp1 not in self.spps:
                self.spps[spp1]  = {}
            if chro not in self.spps[spp1]:
                self.spps[spp1][chro]  = 1
            else:
                self.spps[spp1][chro] += 1

            for spp2pos in xrange(spp1pos, len(spps)):
                spp2 = spps[spp2pos]
                if spp1 == spp2                 : continue
                #print "SPPS", spps,"LEN",len(spps),"",spp1pos,"vs",spp2pos
                pair = tuple(sorted([spp1, spp2]))
                if pair  not in self.pairs      : self.pairs[pair]       = {}
                if chro  not in self.pairs[pair]: self.pairs[pair][chro] = 0
                self.pairs[pair][chro] += 1

                #if spp2 not in self.spps:
                #    self.spps[spp2]  = {}
                #
                #if chro not in self.spps[spp2]:
                #    self.spps[spp2][chro]  = 1
                #
                #else:
                #    self.spps[spp2][chro] += 1


        posi_div = int(posi / self.PRINTEVERY)
        if posi_div != self.lastPrint:
            self.lastPrint = posi_div
            print "  %s %12d" % (chro, posi)

        if posi != self.lastPos:
            self.lastPos = posi

            for key,val in infoDic.items():
                if key in self.titles:
                    key = self.titles[key]['Description']

                statskey = self.stats[key]
                if val not in statskey: statskey[val] = 0
                statskey[val] += 1
        else:
            for key in allowed_dup_keys:
                val      = infoDic[key]
                if key in self.titles:
                    key = self.titles[key]['Description']
                statskey = self.stats[key]
                if val not in statskey: statskey[val] = 0
                statskey[val] += 1

    def consolidate(self):
        print "consolidating"
        self.cons      = {}

        for chro in self.data:
            keys = self.data[chro]
            for key in keys:
                vals = keys[key]

                if key not in self.cons: self.cons[key] = {}
                conskey = self.cons[key]

                for val in vals:
                    if val not in conskey: conskey[val] = 0
                    conskey[val] += vals[val]

        print "consolidate"

    def pp(self):
        pp( self.data )

    def export(self):
        print "exporting"

        #pp(self.pairs)
        #pp(self.spps)

        with open(self.outfile, 'w') as fhd:
            sppsKeys = sorted(self.spps)
            lines    = { '_sum_': [], '_std_dev_': [], '_std_dev_perc_': [], '_avg_': [], '_jaccard_': [] }

            for chro in self.allchro:
                lines[chro          ] = []
                lines[chro + '_prop'] = []

            for spp1pos in (xrange(len(sppsKeys))):
                spp1      = sppsKeys[spp1pos]
                spp1Total = sum( [ self.spps[spp1][chro] for chro in self.spps[spp1] ] )

                lines['_sum_'         ].append(spp1)
                lines['_std_dev_'     ].append(spp1)
                lines['_std_dev_perc_'].append(spp1)
                lines['_avg_'         ].append(spp1)
                lines['_jaccard_'     ].append(spp1)
                for chro in self.allchro:
                    lines[chro          ].append(spp1)
                    lines[chro + '_prop'].append(spp1)

                for spp2pos in (xrange(len(sppsKeys))):
                    spp2      = sppsKeys[spp2pos]
                    spp2Total = sum( [ self.spps[spp2][chro] for chro in self.spps[spp2] ] )

                    name      = tuple(sorted([spp1, spp2]))

                    if name in self.pairs:
                        sharedGlobal      = [self.pairs[name][chro] for chro in self.pairs[name]]
                        sharedGlobalSum   = sum( sharedGlobal )
                        sharedGlobalAvg   = numpy.mean( sharedGlobal )
                        sharedGlobalDev   = numpy.std(  sharedGlobal )
                        sharedGlobalDevP  = sharedGlobalDev / sharedGlobalAvg * 100.0

                        sharedGlobalJacIndex = float( spp1Total + spp2Total - sharedGlobalSum )
                        sharedGlobalJac      = ((float(sharedGlobalSum) / sharedGlobalJacIndex) ** 2.0) ** 0.5

                        lines['_sum_'         ].append( "\t%d"   % sharedGlobalSum  )
                        lines['_std_dev_'     ].append( "\t%.6f" % sharedGlobalDev  )
                        lines['_std_dev_perc_'].append( "\t%.6f" % sharedGlobalDevP )
                        lines['_avg_'         ].append( "\t%.6f" % sharedGlobalAvg  )
                        lines['_jaccard_'     ].append( "\t%.6f" % sharedGlobalJac  )

                        for chro in self.allchro:
                            if chro in self.pairs[name]:
                                sharedChro         = self.pairs[name][chro]
                                sharedChroJacIndex = self.spps[spp1][chro] + self.spps[spp2][chro] - sharedChro
                                sharedChroJac      = (((float(sharedChro) / float(sharedChroJacIndex)) ** 2.0) ** 0.5)
                                lines[chro          ].append("\t%d"   % sharedChro   )
                                lines[chro + '_prop'].append("\t%.6f" % sharedChroJac)
                            else:
                                lines[chro          ].append("\t%d"   % 0  )
                                lines[chro + '_prop'].append("\t%.6f" % 0.0)

                    else:
                        lines['_sum_'         ].append( "\t%d"   % 0   )
                        lines['_std_dev_'     ].append( "\t%.6f" % 0.0 )
                        lines['_std_dev_perc_'].append( "\t%.6f" % 0.0 )
                        lines['_avg_'         ].append( "\t%.6f" % 0.0 )
                        lines['_jaccard_'     ].append( "\t%.6f" % 0.0 )
                        for chro in self.allchro:
                            lines[chro          ].append("\t%d"   % 0  )
                            lines[chro + '_prop'].append("\t%.6f" % 0.0)

                for chro in lines:
                    lines[chro].append("\n")

            for src in sorted(lines):
                llines    = [ src + "\n\t" ]
                llines.append("\t".join(sppsKeys) + "\n")
                llines.extend( lines[src] )
                llines.append("\n\n\n")
                fhd.writelines(llines)





            for key in sorted( [ self.titles[name]['Description'] for name in self.titles ] ):
                lines = []

                lines.append( key + "\n" )
                lines.append( "val\t" )
                lines.append( "\t".join(sorted( self.data )) + "\tsum\tmean\tmedian\tstd_dev\tstd_dev_perc\n" )
                keyvals = [ ]

                for chro in self.data:
                    for val in self.data[chro][key]:
                        keyvals.append( val )

                keyvals = list(set(sorted( keyvals )))
                weights = []
                sppvals = {}

                for val in xrange(min(keyvals), max(keyvals)):
                    weights.append( val )
                    lines.append( "%d" % val )

                    vals = array.array('L')
                    for chro in sorted( self.data ):
                        res = 0

                        if val in self.data[chro][key]:
                            res = self.data[chro][key][val]
                        vals.append( res )
                        if chro not in sppvals: sppvals[chro] = []
                        sppvals[chro].append( res )

                        lines.append( "\t%d" % res )
                        sSum, sMean, sMedian, sStd = (sum(vals), numpy.mean(vals), numpy.median(vals), numpy.std(vals))
                        sStdPerc = 0
                        if sMean > 0:
                            sStdPerc = (sStd/sMean*100.0)

                    lines.append( "\t%d\t%.6f\t%.6f\t%.6f\t%.6f\n" % ( sSum, sMean, sMedian, sStd, sStdPerc) )

                lines.append( "sum" )
                for chro in sppvals:
                    lines.append( "\t%d" % sum( sppvals[chro] ) )
                lines.append( "\n" )

                lines.append( "weightened_average" )
                for chro in sppvals:
                    sAve = numpy.average( sppvals[chro], weights=weights )
                    lines.append( "\t%.6f" % sAve )
                lines.append( "\n" )

                lines.append( "mean" )
                for chro in sppvals:
                    sMean = numpy.mean( sppvals[chro] )
                    lines.append( "\t%.6f" % sMean )
                lines.append( "\n" )

                lines.append( "median" )
                for chro in sppvals:
                    sMedian = numpy.median( sppvals[chro] )
                    lines.append( "\t%.6f" % sMedian )
                lines.append( "\n" )

                lines.append( "std_dev" )
                for chro in sppvals:
                    sStdDev = numpy.std( sppvals[chro] )
                    lines.append( "\t%.6f" % sStdDev )
                lines.append( "\n" )

                lines.append( "std_dev_perc" )
                for chro in sppvals:
                    sStdDev     = numpy.std( sppvals[chro] )
                    sStdDevPerc = sStdDev / sum( sppvals[chro] ) * 100
                    lines.append( "\t%.6f" % sStdDevPerc )
                lines.append( "\n" )

                # TODO: ADD STATS PER CHROMOSOME
                lines.append( "\n\n" )
                fhd.writelines( lines )


            #for key in sorted( [ self.titles[name]['Description'] for name in self.titles ] ):
            #    lines = []
            #
            #    lines.append( key + "\n"     )
            #    lines.append( "val\tcount\n" )
            #
            #    for val in xrange(min(self.cons[key]), max(self.cons[key])):
            #        lines.append( str(val) )
            #        res = 0
            #
            #        if val in self.cons[key]:
            #            res = self.cons[key][val]
            #        lines.append( "\t%d\n" % res )
            #
            #    lines.append( "\n" )
            #    fhd.writelines( lines )

        print "exported"

    def __add__(self, other):
        #print "adding"
        #self.pairs[name1][chro]   += 1
        #self.spps[spp1]        = 1
        #self.allchro[chro]       += 1
        #self.data[chro][key][val] = 0
        for spp in other.pairs:
            if spp  not in self.pairs     : self.pairs[spp]       = {}
            for chro in other.pairs[spp]:
                if chro not in self.pairs[spp]: self.pairs[spp][chro] = 0
                self.pairs[spp][chro] += other.pairs[spp][chro]

        for spp in other.spps:
            if spp not in self.spps: self.spps[spp] = {}
            for chro in other.spps[spp]:
                if chro not in self.spps[spp]: self.spps[spp][chro] = 0
                self.spps[spp][chro] += other.spps[spp][chro]

        for chro in other.allchro:
            if chro not in self.allchro: self.allchro[chro] = 0
            self.allchro[chro] += other.allchro[chro]

        for chro in other.data:
            if chro not in self.data           : self.data[chro]           = {}

            for key in other.data[chro]:
                if key  not in self.data[chro]     : self.data[chro][key]      = {}

                for val in other.data[chro][key]:
                    if val  not in self.data[chro][key]: self.data[chro][key][val] = 0
                    self.data[chro][key][val] += other.data[chro][key][val]

        return self

    def __iadd__(self, other):
        #print "iadd"
        return self.__add__(other)

    def __radd__(self, other):
        print "radd"
        return self.__add__(other)



infoRE     = re.compile("INFO=<ID=(\w+?),Number=(\d+),Type=(\w+?),Description=\"(.+)\">")
def getTitle(infile):
    ##INFO=<ID=NV,Number=1,Type=Integer,Description="Number of Unique Variants in Position">
    #self.titles

    ifh = getFh(infile)

    titles = {}

    for line in ifh:
        if line[0] == "#":
            infores    = infoRE.search(line)

            if infores is not None:
                infoMa = infores.group(0)
                infoId = infores.group(1)
                infoNu = infores.group(2)
                infoTy = infores.group(3)
                infoDe = infores.group(4)

                titles[infoId] = {
                    'Number'     : infoNu,
                    'Type'       : infoTy,
                    'Description': infoDe
                }
        else:
            break

    return titles


def readParsel(reportName, idx, infile, chrom):
    ifh    = getFh(infile)

    titles = getTitle(infile)

    pos = idx[chrom]
    ifh.seek( pos )
    print "reading chrom %s pos %d (%d)" % ( chrom, pos, ifh.tell() )

    nfostats   = infostats(reportName, titles)

    for line in ifh:
        if line[0] == "#":
            continue

        line    = line.strip()
        cols    = line.split("\t")
        if len(cols) < 10: continue
        chro    = cols[0]

        if chro != chrom:
            print "finished reading chrom %s in chrom %s pos %d curr pos %d" % (chrom, chro, pos, ifh.tell())
            break

        posi    = int(cols[1])
        info    = cols[7]
        spps    = cols[9].split('|')
        infoDic = {}

        for cel in info.split(";"):
            name, val = cel.split("=")
            infoDic[name] = int(val)

        nfostats.add(chro, posi, infoDic, spps)

    ifh.close()

    return nfostats


def getOptionInFile(options, parser):
    infile = options.input
    if infile is None:
        infile = options.iinput
        if infile is None:
            print "no input file given"
            parser.print_help()
            sys.exit(1)

    if isinstance(infile, list):
        if len(infile) > 1:
            print "more than one file given"
            print infile
            parser.print_help()
            sys.exit(1)

        infile = infile[0]

    return infile



def main(args):
    parser = argparse.ArgumentParser(description='Merge VCF files.')
    parser.add_argument('-k', '--allowed-duplicated-keys' , dest='allowed_dup_keys', default=['NU'], action='store'      , nargs='+', metavar='key'       ,           help='Which info keys should be counted despite being duplicated at a given position [NU]')
    parser.add_argument('-a', '--add-all'                 , dest='add_all'         , default=False , action='store_false',                                            help='Add all instead of filtering (>1)')
    parser.add_argument('-d', '--debug'                   , dest='debug'           , default=False , action='store_true' ,                                            help='Run only first three chromosomes')
    parser.add_argument('-t', '--threads'                 , dest='threads'         , default=0     , action='store'      , nargs=1                        , type=int, help='Number of threads (default: number of chromosomes)')

    parser.add_argument('-i', '--input'                   , dest='iinput'          , default=None                        ,                                            help='Input file')
    parser.add_argument('input'                           ,                          default=None  , action='store'      , nargs='?', metavar='input file',           help='Input file')

    options = parser.parse_args(args)


    allowed_dup_keys     =     options.allowed_dup_keys
    add_only_significant = not options.add_all
    debug                =     options.debug
    threads              =     options.threads
    #debug                = True

    #TODO: ACCEPT ARGUMENT
    significancy_filter  =  [
                                #['NV', 'gt', 1],
                                #['NW', 'gt', 1],
                                ['NS', 'gt', 1],
                                #['NT', 'gt', 1]
                                ['NU', 'gt', 1]
                            ]

    print args

    infile    = getOptionInFile(options, parser)
    print "infile", infile
    infile    = checkfile(infile)
    indexFile = infile + ".idx"

    print "Allowed Duplicated Keys: %s" % str(allowed_dup_keys    )
    print "Add Only Significant   : %s" % str(add_only_significant)
    print "Debug                  : %s" % str(debug               )
    print "Input File             : %s" % infile
    print "Index File             : %s (exists: %s)" % (indexFile, os.path.exists(indexFile) )

    if not os.path.exists( indexFile ):
        makeIndexFile( indexFile, infile )

    idx        = readIndex(indexFile)

    reportName = infile + '.report.csv'

    titles     = getTitle(infile)

    nfostats   = infostats(reportName, titles)

    global threads
    if threads == 0:
        threads = len(idx)

    pool    = multiprocessing.Pool(processes=threads)
    #pool    = multiprocessing.Pool(processes=1)
    results = []

    for chrom, pos in sorted(idx.items(), key=lambda item: item[1]):
        if len(results) > 3 and debug:
            print "debug. breaking"
            break
        results.append( pool.apply_async( readParsel, [reportName, idx, infile, chrom], {allowed_dup_keys:allowed_dup_keys, add_only_significant:add_only_significant, debug:debug, significancy_filter:significancy_filter} ) )

    while len(results) > 0:
        for res in results:
            try:
                #print "getting result"
                nfostats += res.get( 5 )
                results.remove( res )
                print "getting result OK"

            except multiprocessing.TimeoutError:
                #print "getting result FAILED. waiting"
                pass

    nfostats.export()


if __name__ == '__main__':
    main(sys.argv[1:])
