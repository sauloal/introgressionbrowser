#/usr/bin/python
import os,sys
import re
import string
import argparse

sys.path.insert(0, '.')
import vcffiltergff

m = re.compile( 'ID=(.+?):(.+?);'     )
n = re.compile( 'Parent=(.+?):(.+?);' )

def getParams():
    parser = argparse.ArgumentParser(description='Todo.')
    parser.add_argument('-g', '--gff'                 , dest='gff', default=None, action='store', nargs='?', type=str, help='Gff Coordinate file'  )
    parser.add_argument('-p', '--prot', '--protein'   , dest='pro', default=None, action='store', nargs='?', type=str, help='Fasta protein file'   )
    parser.add_argument('-n', '--nuc' , '--nucleotide', dest='nuc', default=None, action='store', nargs='?', type=str, help='Fasta nucleotide file')

    options = parser.parse_args()

    infile = options.gff
    inprot = options.pro
    innuc  = options.nuc

    checkFile( infile )
    checkFile( inprot )
    checkFile( innuc  )

    return ( infile, inprot, innuc )

def checkFile(filename):
    if not os.path.exists( filename ):
        print "input file %s does not exists" % filename
        sys.exit(1)

    if os.path.getsize( filename ) == 0:
        print "input file %s has size 0" % filename
        sys.exit(1)

def main():
    #SL2.40ch00      ITAG_eugene     exon    16437   17275   .       +       .       ID=exon:Solyc00g005000.2.1.1;Parent=mRNA:Solyc00g005000.2.1;from_BOGAS=1

    infile, inprot, innuc = getParams()

    outfile    = os.path.abspath( infile + '.pmap' )

    print "opening in gff %s" % infile
    gfhd       = open(infile , 'r')

    print "opening in fasta %s" % innuc
    ffhd       = vcffiltergff.fasta( innuc )

    print "opening out %s" % outfile
    ofhd       = open(outfile, 'w')

    print "opening protein %s" % inprot
    prot       = fastaseq( inprot )


    printer    = seqprinter( prot, ffhd, ofhd )

    lastThreeL = []
    lastThreeH = {}

    for line in gfhd:
        line = line.strip()
        if len(line) == 0: continue
        if line[0] == "#": continue
        #print line

        cols = line.split("\t")

        if len(cols) != 9: continue

        chrom =     cols[0]
        start = int(cols[3])
        finis = int(cols[4])
        rev   = False if cols[6] == '+' else True
        info  =     cols[8]


        r     = m.search(info)
        if r is None: continue

        etype = r.group( 1 )
        exon  = r.group( 2 )


        s     = n.search(info)
        if s is None: continue

        gtype = s.group( 1 )
        gene  = s.group( 2 )


        frag  = ffhd.get(chrom, start, finis)
        if rev:
            frag = revcomp( frag )

        #print "\t".join([str(x) for x in [chrom, start, finis, gene, frag, len(frag)]])

        if start >= finis:
            print "start %d >= finish %d" % (start, finis)
            sys.exit(1)

        if  gene not in lastThreeH:
            lastThreeL.append(gene)
            lastThreeH[gene] = [
                chrom,
                gene,
                rev,
                [ [ start, finis ] ],
                [ frag             ]
            ]

        else:
            if rev:
                lastThreeH[gene][ 4 ].insert( 0, frag             )
            else:
                lastThreeH[gene][ 4 ].append(    frag             )

            lastThreeH[gene][ 3 ].append(    [ start, finis ] )


        if len(lastThreeL) > 10:
            for i in range(5):
                first = lastThreeL.pop(0    )
                val   = lastThreeH.pop(first)
                printer.printline( *val )

    for el in lastThreeL:
        val   = lastThreeH.pop(el)
        printer.printline( *val )

    print "DONE"

trdb = string.maketrans('ACGT', 'TGCA')

def revcomp(seq):
    seq = seq[::-1]
    seq = seq.translate(trdb)
    return seq

class fastaseq(object):
    def __init__(self, infile):
        self.infile = infile
        self.db     = {}

        print "opening fasta sequence %s" % infile

        with open(infile, 'r') as fhd:
            lastSeqId = ""
            for line in fhd:
                line = line.strip()
                if len(line) == 0: continue
                if line[0] == ">":
                    space = line.find(" ")
                    if space == -1: space = len(line)
                    seqid   = line[1:space]
                    seqdesc = line[space:]
                    self.db[seqid] = ""

                else:
                    self.db[seqid] += line
            self.db[seqid] += line

        print "acquired %d sequences" % len(self.db)

    def get(self, k, dfl=None):
        return self.db.get(k, dfl)

class seqprinter(object):
    def __init__(self, prot, ffhd, ofhd):
        self.prot = prot
        self.ffhd = ffhd
        self.ofhd = ofhd
        self.createTable()

    def createTable(self):
        #http://www.petercollingridge.co.uk/python-bioinformatics-tools/codon-table
        bases       = ['T', 'C', 'A', 'G']
        codons      = [a+b+c for a in bases for b in bases for c in bases]
        amino_acids = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
        codon_table = dict(zip(codons, amino_acids))
        self.codon_table = codon_table
        self.codon_table['NNN'] = 'X'

    def translate(self, seq):
        peptide = ''

        seq = seq.upper()

        for i in xrange(0, len(seq), 3):
            codon       = seq[i: i+3]
            amino_acid  = self.codon_table.get(codon, '*')

            if codon.find( 'N' ) != -1:
                amino_acid = 'X'

            peptide    += amino_acid

            #if amino_acid == '*':
                #break

        return peptide

    def printline(self, chrom, gene, rev, coords, frags):
        if gene is None: return

        geneseq = "".join(  frags )

        trans   = self.translate( geneseq )
        prot    = self.prot.get( gene, None )

        if prot is None:
            print "no such sequence %s" % gene
            sys.exit(1)


        if trans[-1] == '*' or prot[-1] == '*':
            print "DE-STARING TRANS"
            trans          = trans.rstrip( '*' )
            prot           = prot.rstrip(  '*' )
            print trans[:3],prot[:3]

            if rev:
                print 'r', coords[0]
                coords[ 0][0] += 3
                frags[ -1]     = frags[-1][:-3]
                print 'r', coords[0]
            else:
                print 'f', coords[-1]
                coords[-1][1] -= 3
                frags[  -1]    = frags[-1][:-3]
                print 'f', coords[-1]

            geneseq = "".join(  frags )
            trans   = self.translate( geneseq )

        if len(trans) != len(prot):
            if trans[0] != 'M':
                print "FIXING M", trans[:3], geneseq[:6]
                trans   = trans[1:]
                geneseq = geneseq[ 3: ]
                prot    = prot
                frags[0] = frags[0][3:]

            if len(trans) != len(prot):
                print "FIXING LEN"
                if len(trans) > len(prot):
                    print "FIXING LEN TRANS > PROT"
                    trans      = trans[   :len(prot)   ]
                    geneseq    = geneseq[ :len(prot)*3 ]

                else:
                    print "FIXING LEN PROT > TRANS"
                    for pos in xrange( len(trans) ):
                        t = trans[ pos ]
                        p = prot[  pos ]

                        if t != p:
                            print "t %s p %s" % (t,p)
                            if p == '*':
                                print "PROT: ",p
                                trans   = trans[  :pos  ]
                                prot    = prot[   :pos  ]
                                geneseq = geneseq[:pos*3]
                                print "FIXED %s = %s : %s" % ( t, p, triplet )
                                break

        for fpos in xrange(len(frags[-1]), 3):
            pnuc    = len(geneseq) - len(frags[-1]) + fpos
            pos     = int( pnuc/3 )
            t       = trans[  pos ]
            p       = prot[   pos ]
            triplet = geneseq[pnuc:pnuc+3]

            if triplet.lower() == triplet:
                print "LOWER: t %s p %s" % (t,p)
                trans     = trans[    :pos  ]
                prot      = prot[     :pos  ]
                geneseq   = geneseq[  :pnuc ]
                frags[-1] = frags[-1][:fpos ]
                print "FIXED %s = %s : %s" % ( t, p, triplet )
                break


        geneseqlen = len(geneseq)
        fraglensum = 0

        #for fragpos in xrange(len(frags)):
        #    frag       = frags[ fragpos ]
        #    fraglen    = len( frag )
        #    endpos     = geneseqlen - fraglensum
        #
        #    if endpos > 0 :
        #        if ( fraglensum + fraglen ) > geneseqlen:
        #            print "REFRAG"
        #            frag = frag[:endpos]
        #            coords[fragpos][1] = coords[fragpos][0] + endpos - 1
        #        frags[fragpos]  = frag
        #
        #    else:
        #        frags[fragpos]  = ""
        #        coords[fragpos] = None
        #    fraglensum += fraglen

        for fragpos in range( len(frags)-1, 0, -1 ):
            if len(frags[fragpos]) == 0: frags.pop(  fragpos )
            if coords[fragpos] is None : coords.pop( fragpos )

        if len(frags) != len(coords):
            print "len(frags) [%d] != len(coords) [%d]" % (len(frags) , len(coords))
            sys.exit(1)

        geneseq = "".join(  frags )
        trans   = self.translate( geneseq )
        trans   = trans.rstrip( '*' )


        if len(trans) != len(prot):
            print "translantion does not matches protein"
            print "CHROM %s GENE %s COORDS %s REV %s" % ( chrom, gene, str(coords), str(rev) )
            print "NUC", len(geneseq), len(geneseq)/3, ",".join( frags )
            print "TRA", len(trans  ), trans
            print "PRO", len(prot   ), prot
            self.printAln(geneseq, trans, prot)
            sys.exit(1)

        posessum = 0
        genecoo  = ""
        for poses in coords:
            genecoo  += ',' if genecoo != "" else ""
            genecoo  += "%d..%d" % tuple( poses )
            posessum += poses[1] - poses[0] + 1

        if posessum != len(geneseq):
            print "coordinates do not matches lengths"
            print "CHROM %s GENE %s COORDS %s REV %s" % ( chrom, gene, genecoo, str(rev) )
            print "coordinates sum: %d length: %d" % (posessum, len(geneseq))
            print "NUC", len(geneseq), len(geneseq)/3, ",".join( frags )
            print "TRA", len(trans  ), trans
            print "PRO", len(prot   ), prot
            self.printAln(geneseq, trans, prot)
            sys.exit(1)

        genestr = ",".join( frags )
        geneseq = "".join(  frags )
        genelen = len(geneseq)
        genesta = "." if genelen % 3 == 0 else "!"

        if True:
            fragsback = self.getcoords(coords, chrom, rev)
            geneback  = "".join( fragsback )
            if geneback != geneseq:
                print "geneback != genestr"
                #print geneback
                #print genestr
                for pos in range( len(fragsback) ):
                    frag     = frags[     pos ]
                    fragback = fragsback[ pos ]
                    print coords[pos]
                    print len(frag    ), frag
                    print len(fragback), fragback
                    print
                sys.exit( 1 )

        pdata   = (chrom, gene, genelen, genesta, genecoo, genestr, trans)

        self.ofhd.write( "\t".join( [ str(x) for x in pdata ] ) + "\n" )

    def getcoords(self, coords, chrom, rev):
        #self.ffhd

        frags = []
        for coord in coords:
            start = coord[0]
            end   = coord[1]
            frag  = self.ffhd.get(chrom, start, end)
            if rev:
                frag = revcomp( frag )

            frags.append( frag )

        if rev:
            frags.reverse()
        return frags

    def printAln(self, geneseq, trans, prot):
        for pos in xrange(0, len(trans), 20):
            print geneseq[pos*3: (pos*3)+60]
            print "".join( [x+"  " for x in trans[  pos  :  pos + 20 ] ] )
            print "".join( [x+"  " for x in prot [  pos  :  pos + 20 ] ] )


if __name__ == '__main__': main()
