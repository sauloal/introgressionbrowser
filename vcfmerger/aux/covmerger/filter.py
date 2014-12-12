#!/usr/bin/python
import sys, os
import gzip
import argparse
import datetime

#./filter.py <out.mcov.gz> <input list> [<min coverage>]

SOURCE_SPP = "heinz2.40"




FORBID     = 0
REQUIR     = 1
IGNORE     = 2


class gff(object):
    def __init__(self, fn, desc=None, slack=1, minSize=1):
        self.fn        = fn
        self.slack     = slack
        self.minSize   = minSize

        self.fh        = openFile(fn, 'w')
        self.lastChrom = ""
        self.startPos  = 0
        self.finalPos  = 0

        self.indiCount = 0
        self.indiChrCo = {}
        self.featCount = 0
        self.featChrCo = {}


        self.fh.write("##gff-version 3\n")
        if desc is not None:
            self.fh.write(desc)

        self.fh.write("#seqId\tsource\ttype\tstart\tend\tscore\tstrand\tphase\tattributes\n")

    def write(self, chrom, pos):
        #sys.stdout.write('w')

        self.indiCount += 1
        if chrom not in self.indiChrCo:
            self.indiChrCo[chrom]  = 0

        self.indiChrCo[chrom] += 1

        if chrom == self.lastChrom:
            #sys.stdout.write('-s')
            if pos <= self.finalPos + self.slack:
                #sys.stdout.write('w-s-l pos %d finalPos %d slack %d' % (pos, self.finalPos, self.slack))
                self.finalPos = pos

            else:
                #sys.stdout.write('w-s-w pos %d finalPos %d slack %d\n' % (pos, self.finalPos, self.slack))
                self.writeData()
                self.startPos = pos
                self.finalPos = pos

        else:
            #sys.stdout.write('w-n pos %d finalPos %d slack %d\n' % (pos, self.finalPos, self.slack))
            self.lastChrom = chrom
            self.startPos  = pos
            self.finalPos  = pos

    def writeData(self):
        #sys.stdout.write('W')

        if ( self.finalPos - self.startPos + 1 ) >= self.minSize:
            self.featCount += 1

            if self.lastChrom not in self.featChrCo:
                self.featChrCo[self.lastChrom]  = 0

            self.featChrCo[self.lastChrom] += 1

            dsc  = "ID=%d;chr_id=%d;count=%d;chr_count=%d;NAME=%s" % (self.featCount, self.featChrCo[self.lastChrom], self.indiCount, self.indiChrCo[self.lastChrom], self.lastChrom + "_" + str(self.featChrCo[self.lastChrom]))
            #TODO: ADD STATISTICS
            #       seqId source type start end score strand phase attributes
            data = "%s\t%s\tgap\t%d\t%d\t.\t+\t.\t%s\n" % (self.lastChrom, SOURCE_SPP, self.startPos, self.finalPos, dsc)
            self.fh.write(data)

    def close(self):
        self.writeData()
        self.fh.close()


def openFile( filename, mode ):
    if filename.endswith( 'gz' ):
        return gzip.open( filename, mode + 'b')
    else:
        return open(filename, mode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('incov' ,                        type=str, help='input coverage file'                )
    parser.add_argument('inlist',                        type=str, help='input tab-delimited files list file')

    parser.add_argument('-c', '--mincov' , default=1   , type=int, help='minimum coverage to consider'       )
    parser.add_argument('-s', '--minsize', default=1   , type=int, help='minimum gap size to report'         )
    parser.add_argument('-l', '--slack'  , default=1   , type=int, help='slack between gaps to merge them'   )
    parser.add_argument('-o', '--outfile', default=None, type=str, help='output name'   )

    args    = parser.parse_args()

    setup   = []
    files   = []
    descr   = []

    print args


    if not os.path.exists( args.inlist ):
        print "input list file %s does not exists" % args.inlist
        sys.exit(1)

    if not os.path.exists( args.incov  ):
        print "input coverage file %s does not exists" % args.incov
        sys.exit(1)

    outfile = args.outfile

    if outfile is None:
        outfile = args.inlist + ".filtered"

    if os.path.exists( outfile + '.gff3.gz' ):
        print "output file %s already exists." % outfile + '.gff3.gz'
        sys.exit( 1 )

    if os.path.exists( outfile + '.cov.gz' ):
        print "output file %s already exists." % outfile + '.cov.gz'
        sys.exit( 1 )

    fileNum = 0

    with openFile(args.inlist, 'r') as inlistfh:
        for line in inlistfh:
            fileNum += 1
            data     = line.strip().split("\t")

            setupnum = int( data[0] )

            filename = "#" + str( fileNum )
            descript = "#" + str( fileNum )
            if len (data) > 1:
                filename = data[1]

                if len(data) > 2:
                    descript = data[2]

            files.append( filename )
            descr.append( descript )

            if   setupnum ==  0: setup.append( IGNORE )
            elif setupnum ==  1: setup.append( REQUIR )
            elif setupnum == -1: setup.append( FORBID )
            else:
                print line
                print "wrong formating. can be 0, 1 -1"
                sys.exit(1)

    desc = ""

    desc += "##Config:\n"
    for par in sorted(vars(args)):
        print par, args.__dict__[ par ]
        desc += "#%s:\t%s\n" % (par, str(args.__dict__[ par ]))

    desc += "#Creation time:\t" + str(datetime.datetime.now()) + "\n"

    for pairs in [(REQUIR, "Required"), (IGNORE, "Ignored"), (FORBID, "Forbidden")]:
        print pairs[1], ":"
        desc += "#" + pairs[1] + ":\n"

        for xpos in range( len( files ) ):
            if setup[ xpos ] == pairs[ 0 ]:
                print    "\t%s" % files[ xpos ],
                desc += "#\t%s" % files[ xpos ]
                if len(descr) > 0:
                    print   "\t%s" % descr[ xpos ],
                    desc += "\t%s" % descr[ xpos ]
                print
                desc += "\n"




    #outgff = gff( inlist + '.filtered.gff3', desc, slack=5, minSize=50)
    outgff = gff( outfile + '.gff3.gz', desc, slack=args.slack, minSize=args.minsize)

    lastChrom  = None
    lastPos    = None

    simplified = False
    posPos     = 1
    dataPos    = 2

    with openFile(outfile + '.cov.gz', 'w') as outlist:
        with openFile(args.incov, 'r') as incovfh:
            mincov     = args.mincov
            linecount  = 0
            validcount = 0

            for line in incovfh:
                #print line
                linecount  += 1
                ldata       = line.strip().split("\t")


                if len(ldata) == 1:
                    posPos      = 0
                    dataPos     = 1
                    simplified  = True

                    currChrom   =      ldata[0]
                    print "S curr chrom", currChrom

                    if currChrom != lastChrom:
                        lastChrom = currChrom
                        print "\n", lastChrom,

                    continue

                else:
                    if not simplified:
                        currChrom   =      ldata[0]

                        if currChrom != lastChrom:
                            lastChrom = currChrom
                            print "curr chrom", currChrom
                            print "\n", lastChrom,


                currPos     = int( ldata[posPos] )

                if currPos != 0:
                    if currPos %  10000 == 0:
                        print "%10d " % currPos,

                    if currPos % 100000 == 0:
                        print "\n",lastChrom,


                data = [ int( x ) for x in ldata[dataPos:] ]
                res  = True

                for xpos in xrange( len(data) ):
                    #print " xpos", xpos,
                    linedata = data[ xpos ]

                    sre      = setup[ xpos ]
                    #print " setup", sre, "val", linedata,

                    if   sre == IGNORE: # if ignore
                        pass

                    elif sre == REQUIR and ( linedata < mincov ): # if required and value too low, error, skip
                        #print " ",files[ xpos ],"setup", sre, "val", linedata,"required and value too low (< ",args.mincov,"). skipping"
                        res = False
                        break

                    elif sre == FORBID and ( linedata >= mincov ): # if forbidden and value is ok, error, skip
                        #print " ",files[ xpos ],"setup", sre, "val", linedata," forbidden and value is ok (>= ",args.mincov,"). skipping"
                        res = False
                        break

                if res:
                    validcount += 1
                    #sys.stdout.write( "+"  )
                    outlist.write(    line               )
                    outgff.write(     lastChrom, currPos )

                else:
                    #sys.stdout.write("-")
                    pass


    outgff.close()

    print
    print "total lines:", linecount
    print "valid lines:", validcount

if __name__ == '__main__':
    main()
