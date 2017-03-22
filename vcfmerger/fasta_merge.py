#!/usr/bin/env python

import sys
import os
from collections import OrderedDict

def main():
    outfile = sys.argv[1]
    if os.path.exists(outfile):
        print "output file %s exists. quitting" % outfile
        sys.exit(1)

    else:
        print "output file %s" % outfile


    infiles = sys.argv[2:]


    for infile in infiles:
        if not os.path.exists(infile):
            print "input file %s does not exists" % infile
            sys.exit(1)


    data = OrderedDict()
    for infile in infiles:
        print "reading %s" % infile
        with open(infile, 'r') as fhd:
            for line in fhd:
                line = line.strip()
                if len(line) == 0:
                    continue
                if line[0] == ">":
                    name = line
                    print "reading %s seq %s" % (infile, name),
                    if name not in data:
                        data[name] = ""
                        print " *"
                    else:
                        print
                else:
                    data[name] += line

    with open(outfile, 'w') as fhd:
        for name in data:
            line = data[name]
            print "saving %s (%d)" % (name, len(line))
            fhd.write(name + "\n")
            for seq in split_by_n(line, 80):
                fhd.write(seq + "\n")

def split_by_n( seq, n ):
    """
    A generator to divide a sequence into chunks of n units.
    http://stackoverflow.com/questions/9475241/split-python-string-every-nth-character
    """
    while seq:
        yield seq[:n]
        seq = seq[n:]


if __name__ == '__main__':
    main()
