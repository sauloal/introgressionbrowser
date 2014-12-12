#!/usr/bin/python

import os
import sys
import glob

def getCommonSuffix( names ):
    minsize  = sys.maxint
    currsize = 0

    for name in names:
        nsize = len(name)
        if nsize < minsize:
            minsize = nsize

    currsize = minsize - 1
    print "minsize", minsize
    name1   = names[0]

    while currsize >= 0:
        sublen  = len(name1) - currsize - 1
        sub     = name1[sublen:]
        #print " currsize", currsize, "sub", sub
        present = True

        for name in names:
            #print "  name", name, "sub", sub
            if not name.endswith( sub ):
                present = False
                break

        if present:
            print "PRESENT"
            break

        else:
            #print "not present"
            currsize -= 1

    if currsize > 0:
        sublen  = len(name1) - currsize - 1
        sub     = name1[sublen:]
        return sub

    else:
        return ""


def main(outfile, infolder, spps):
    if os.path.exists( outfile ):
        print "output file exists"
        sys.exit( 1 )


    if ( not os.path.exists( infolder ) )  or ( not os.path.isdir( infolder ) ):
        print "output file exists or not folder"
        sys.exit( 1 )



    infiles  = glob.glob(os.path.join(infolder, '*.matrix'))
    infiles.sort()

    cp = os.path.commonprefix( infiles )
    cs = getCommonSuffix(      infiles )

    print "infolder" , infolder
    print "spps"     , ", ".join(spps)
    #print "infiles"  , ", ".join(infiles)
    print "num files", len(infiles)

    data      = [ None ]*len(infiles)
    colnames  = []
    filecount = -1

    for filename in infiles:
        print filename

        filecount += 1

        with open( filename, 'r' ) as fhd:
            linecount = -1

            for line in fhd:
                line = line.strip()

                cols = line.split( " " )

                if linecount == -1:
                    linecount += 1
                    #print "first line", line
                    line = line.strip()
                    numcols = int(line)
                    print "numcols",numcols

                    data[ filecount ] = [None]*numcols
                    filedata          = data[ filecount ]
                    for r in xrange(numcols):
                        filedata[ r ] = [None]*numcols

                        for c in xrange(numcols):
                            filedata[ r ][ c ] = -1
                    continue


                filedata = data[ filecount ]
                #print linecount, line
                linedata = filedata[ linecount ]
                rowname  = cols[0 ]
                rowvals  = [ float(x) for x in cols[1:] ]

                #print rowname, rowvals

                if rowname not in colnames:
                    colnames.append( rowname )

                else:
                    if colnames[ linecount ] != rowname:
                        print "inconsistency in row names", linecount, colnames[ linecount -1 ], rowname
                        sys.exit( 1 )



                if colnames[ linecount ] != rowname:
                    print "wrong row name", linecount, colnames[ linecount ], rowname
                    print colnames
                    sys.exit( 1 )


                for colpos in xrange(len(rowvals)):
                    colval = rowvals[  colpos ]
                    val    = linedata[ colpos ]

                    if val != -1:
                        if colval != val:
                            print "inconsistent values", linecount, colpos, filecount, val, colval

                    else:
                        linedata[ colpos ] = colval

                linecount += 1

    if len ( spps ) == 0:
        spps = colnames

    print colnames
    print [ x for x in colnames if x in spps]
    #print data

    with open( outfile, 'w' ) as fhd:
        for filepos in xrange(len(infiles)):
            filename = infiles[ filepos ]
            dn       = filename.replace( cp, "" ).replace( cs, "" )

            header = [[],[],[]]
            if filepos == 0:
                header[0].append("\t")
                header[1].append("\t")
                header[2].append("\t")

            cols = []

            for rowpos in xrange(len(colnames)):
                if colnames[ rowpos ] in spps:

                    for colpos in xrange(len(colnames)):
                        if colnames[ colpos ] in spps:

                            if rowpos < colpos:
                                if filepos == 0:
                                    header[0].append( "\t" + colnames[ rowpos ] + "+" + colnames[ colpos ] )
                                    header[1].append( "\t" + colnames[ rowpos ] )
                                    header[2].append( "\t" + colnames[ colpos ] )
                                cols.append( data[ filepos ][ rowpos ][ colpos ] )

            if filepos == 0:
                header[0].append("\n")
                header[1].append("\n")
                header[2].append("\n")
                fhd.write("".join(header[0]))
                fhd.write("".join(header[1]))
                fhd.write("".join(header[2]))

            fhd.write( infiles[filepos] + "\t" + dn + "\t" + "\t".join( [ str(x) for x in cols ] ) + "\n" )


if __name__ == '__main__':
    try:
        outfile = sys.argv[1 ]
    except:
        print "no output file given"
        sys.exit( 1 )

    try:
        infolder = sys.argv[2 ]
    except:
        print "no input folder given"
        sys.exit( 1 )

    spps = []
    try:
        spps     = sys.argv[3:]

    except:
        print "no spps given"
        #sys.exit( 1 )

    main(outfile, infolder, spps)
