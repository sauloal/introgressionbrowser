#!/usr/bin/env python
import os, sys
import datetime

def main(infile, size):
    if not os.path.exists( infile ):
        print "input file", infile, "does not exists"
        sys.exit( 1 )

    if not (infile.endswith( '.fa' ) or infile.endswith( '.fasta' )):
        print "input file", infile, "is not fasta"
        sys.exit( 1 )

    try:
        size = int(size)
    except:
        print "error in size", size
        print "not a number"
        sys.exit( 1 )

    print "reading fasta"
    data    = {}
    dataord = []
    with open(infile, 'r') as fhd:
        lastHeader = ""

        for line in fhd:
            line = line.strip()
            #print line

            if len(line) == 0 : continue

            if line[0] == ">":
                lastHeader = line[1:]

                if " " in lastHeader:
                    lastHeader = lastHeader.split()[0]

                print " ", lastHeader

                if lastHeader in data:
                    print "duplicated chromosome", lastHeader
                    sys.exit( 1 )

                data[lastHeader] = 0
                dataord.append( lastHeader )

                continue

            data[lastHeader] += len(line)
    print "reading fasta DONE"

    print data

    print "generating gff"
    gffout   = gffprinter( infile, os.path.basename( infile ) + '_' + str(size) + '.gff', size )
    printgff = gffout.printgff

    for chromosome in dataord:
        csize = data[chromosome]
        if csize <= size:
            printgff(chromosome, 1, csize, csize)

        else:
            for start in xrange(1, csize, size):
                printgff(chromosome, start, start+size-1, csize)


    gffout.close()
    print "generating gff DONE"

    return gffout.outfile

class gffprinter(object):
    def __init__(self, infile, outfile, spacer_size):
        self.infile      = infile
        self.outfile     = outfile
        self.spacer_size = spacer_size
        self.fhd         = open(outfile, 'w')
        self.init_gff()

##gff-version 3
##feature-ontology http://song.cvs.sourceforge.net/*checkout*/song/ontology/sofa.obo?revision=1.93
##sequence-region SL2.40ch00 1 21805821
#SL2.40ch00      ITAG_eugene     gene    16437   18189   .       +       .       Alias=Solyc00g005000;ID=gene:Solyc00g005000.2;Name=Solyc00g005000.2;from_BOGAS=1;length=1753

    def init_gff(self):
        header = [
            "##gff-version 3\n",
            "##fileDate=%s\n"       % datetime.datetime.now().isoformat(),
            "##source=fasta_spacer\n",
            "##spacer_size=%d\n"    % self.spacer_size,
            "##spacer_source=%s\n"  % self.infile,
        ]
        self.fhd.writelines(header)
        self.chromosomeCount = {}
        self.counter         = 0

    def printgff(self, chromosome, start, end, csize):
        if chromosome in self.chromosomeCount:
            self.chromosomeCount[chromosome] += 1
        else:
            self.chromosomeCount[chromosome]  = 1

        self.counter += 1

        chromosomeCount = self.chromosomeCount[chromosome]
        #startPos        = ((chromosomeCount-1)*self.spacer_size) + 1
        #endPos          =   chromosomeCount   *self.spacer_size
        startPos        = start
        endPos          = end
        alias           = 'Frag_%sg%d_%09d_%09d' % (chromosome, self.spacer_size, startPos, endPos)
        data = {
            'chromosome': chromosome,
            'size'      : self.spacer_size,
            'start'     : start,
            'end'       : end,
            'alias'     : alias,
            'id'        : 'fragment:%s' % alias,
            'name'      : alias,
            'length'    : end-start+1,
            'csize'     : csize,
            'num'       : chromosomeCount,
            'count'     : self.counter
        }
        line = "%(chromosome)s\t.\tfragment_%(size)d\t%(start)d\t%(end)d\t.\t.\t.\tAlias=%(alias)s;ID=%(id)s;Name=%(name)s;length=%(length)d;order=%(num)d;count=%(count)d;csize=%(csize)d\n" % data
        self.fhd.write( line )

    def close(self):
        fhd = getattr(self, 'fhd', None)
        if fhd:
            fhd.close()


if __name__ == '__main__':
    try:
        infile = sys.argv[1]
        size   = sys.argv[2]
    except:
        print "not enough parameters given"
        sys.exit( 1 )

    main(infile, size)
