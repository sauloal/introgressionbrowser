#!/usr/bin/python
"""
Uses the 
"""
import os, sys
#from pprint import pprint as pp

SEQLEN = 60

def main():
    try:
        outfile = sys.argv[1]
    except:
        print "no output file defined"
        sys.exit(1)

    if os.path.exists(outfile):
        print "output file %s already exists. quitting" % outfile
        sys.exit(1)

    try:
        infiles = sys.argv[2:]
    except:
        print "no input files given to be merged"


    fasta   = False

    for infile in infiles:
        if not os.path.exists(infile):
            print "input file %s does not exists" % infile
            sys.exit(1)

        elif os.path.getsize(infile) == 0:
            print "input file %s is empty" % infile
            sys.exit(1)

        else:
            print infile
            if infile.endswith('.fasta'):
                fasta   = True
                print "FASTA"

            else:
                if fasta:
                    print "mixed?"
                    sys.exit(1)



    with open(outfile, 'w') as ofh:
        inconsistences = []

        if not fasta:
            ofh.write( "CLUSTAL multiple sequence alignment\n" )

            for x in range(len(infiles)):
                inconsistences.append( [] )
        else:
            inconsistences = {}

        filenum = -1



        for infile in infiles:
            print "  parsing file %s" % infile
            filenum += 1

            with open(infile, 'r') as ifh:
                linenum     = 0
                lastseqname = ""

                for line in ifh:
                    linenum += 1
                    line     = line.strip()
                    #print line


                    if linenum == 1:
                        if fasta:
                            if ( line[0] == ">" ):
                                pass
                            else:
                                print "fasta but no >"
                                sys.exit(1)
                        else:
                            if ( line[0] == ">" ):
                                print "not fasta but  >"
                                sys.exit(1)
                            else:
                                pass


                    if fasta:
                        if len(line) == 0:
                            #print "len line",len(line)
                            continue

                        if line[0] == ">":
                            lastseqname                  = line[1:]
                            if lastseqname not in inconsistences:
                                inconsistences[lastseqname]  = []
                            print "    parsing %s" % lastseqname

                        else:
                            inconsistences[lastseqname].append( line )

                    else:
                        if len(line) == 0:
                            ofh.write( line + "\n")
                            continue

                        cols = line.split()
                        if len(cols) != 2:
                            if linenum == 1:
                                continue
                            print "wrong format"
                            print line
                            sys.exit(1)

                        if len(cols[1]) != SEQLEN:
                            inconsistences[filenum].append(cols)

                        else:
                            ofh.write( line + "\n")

        #print inconsistences
        lines = []
        if fasta:
            genLines(ofh, inconsistences)

        else:
            lines = parseinconsistences(inconsistences)
            ofh.writelines(lines)

def genLines(ofh, inconsistences):
    print "exporting fasta"

    for seqname in inconsistences:
        seq = "".join( inconsistences[seqname] )
        print "  sequence %s length %d" % (seqname, len(seq))

        ofh.write( ">%s\n" % seqname )

        for frag in xrange(0, len(seq), SEQLEN):
            ofh.write( seq[frag:frag+60] + "\n" )

        ofh.write("\n")


def parseinconsistences(inconsistences):
    vals   = {}
    keys   = []
    maxlen = 0

    for sppdata in inconsistences:
        for line in sppdata:
            name = line[0]
            seq  = line[1]

            if name is None or len(name) == 0:
                print "wrong name: %s - %s" % (name, seq)
                sys.exit(1)

            if name not in keys:
                keys.append( name )
                vals[name] = ""
                if len(name) > maxlen: maxlen = len(name)
            vals[name] += seq

    namefmt = "%-" + (str(maxlen+2)) + "s"

    res    = []
    seqlen = len(vals[ vals.keys()[0] ])

    for frag in xrange(0, seqlen, SEQLEN):
        print "frag %d" % frag
        for name in keys:
            #print "  name %s" % name
            res.append( namefmt % name + vals[name][frag:frag+60] + "\n")

        res.append("\n\n")

    res.append("\n\n")

    return res

if __name__ == '__main__': main()
