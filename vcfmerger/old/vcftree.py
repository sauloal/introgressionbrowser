#!/usr/bin/python
"""

"""
import os, sys
import array
#from pprint import pprint as pp
#import io
#import copy
#import tempfile


#import p4
#import dendropy
#import hcluster
#from matplotlib.pyplot    import show
#from hcluster             import pdist, dendrogram
#from hcluster             import linkage, single, complete, average, weighted, centroid, median, ward

from cogent.phylo         import distance, nj, least_squares, maximum_likelihood
from cogent.cluster.UPGMA import upgma
from cogent.draw          import dendrogram
from cogent               import LoadTree
#from cogent.evolve.models import HKY85

def main():
    if len(sys.argv) != 2:
        print "not enought arguments"
        sys.exit(1)

    inputfile = sys.argv[1]
    if not os.path.exists(inputfile):
        print "input file %s does not exists" % inputfile
        sys.exit(1)

    trees = {}
    with open(inputfile, 'r') as fhd:
        name = None
        for line in fhd:
            #print "line", line
            line = line.strip()
            cols = line.split("\t")

            if len(line) > 1 and len(cols) == 1:
                name = cols[0]
                print "name '%s'" % name

                for line in fhd:
                    line = line.rstrip()

                    if len(line) == 0:
                        #print "name '%s' :: empty line" % str(name)
                        name = None
                        break

                    if name is not None and name not in trees:
                        #print "name '%s' :: getting header"       % str(name)
                        #print "name '%s' :: getting header :: %s" % (str(name), line)
                        header      = line
                        headerNames = header.split("\t")

                        if headerNames[0] != "":
                            #print "name '%s' :: getting header :: first not empty :: '%s'" % (str(name), line)
                            name = None
                            continue

                        dimentions  = len(headerNames) - 1
                        trees[name] = {}
                        trees[name]['dimentions'] = dimentions
                        trees[name]['names'     ] = headerNames[1:]
                        trees[name]['matrix'    ] = []
                        #print "name '%s' :: getting header :: dimentions %d" % ( str(name), dimentions )

                    else:
                        if name is not None:
                            colss = line.split("\t")
                            if colss[0] not in trees[name]['names'     ]:
                                print "name '%s' :: getting matrix :: vertical name %s not in names %s" % (str(name), str(name), str(names))
                                sys.exit(1)

                            cols = []
                            for x in colss[1:]:
                                x = float(x)
                                if x == 0: x = 0.00000001
                                cols.append(x)

                            cols = array.array('f', cols )

                            if len(cols) != dimentions:
                                print "name '%s' :: dimentions dont match %d vs %d" % ( str(name), len(cols), dimentions )
                                sys.exit(1)

                            trees[name]['matrix'].append(cols)

    for treename in sorted(trees):
        if (not treename.endswith('_prop')) and (not treename.endswith('_jaccard_')): continue

        print "exporting tree %s" % treename
        treedata   = trees[treename]
        dimentions = treedata['dimentions']
        names      = treedata['names'     ]
        matrix     = treedata['matrix'    ]
        outbase    = "%s.%s" % ( inputfile, treename )

        dissi = {}
        for name1pos in xrange(len(names)):
            name1 = names[name1pos]
            for name2pos in xrange(len(names)):
                if name2pos >= name1pos: continue
                name2       = names[name2pos]
                name        = (name1, name2)
                eman        = (name2, name1)
                val1        = matrix[name1pos][name2pos]
                val2        = matrix[name2pos][name1pos]
                dissi[name] = val1
                dissi[eman] = val2





        mycluster = upgma(dissi).balanced()
        mycluster.writeToFile(outbase + ".upgma", with_distances=True)

        with open(outbase + ".upgma.tree", "w") as upgmat:
            upgmat.write( mycluster.asciiArt() )

        myclusterden     = dendrogram.ContemporaneousDendrogram( mycluster )
        myclusterdendraw = myclusterden.drawToPDF(outbase + '.upgma.tree.pdf', 1024, 2048)

        #d = distance.LoadTree(treestring=mycluster.getNewick(with_distances=True), format='newick')
        #print dissi
        myclusterls    = least_squares.WLS(dissi).evaluateTree(mycluster)
        print "UPGMA Least Square", myclusterls
        #myclusterls    = least_square.evaluateTree(mycluster)
        #print least_square.evaluateTopology( LoadTree(treestring=mycluster.getNewick(with_distances=True), format='newick') )




        mytree = nj.nj(dissi).balanced()
        mytree.writeToFile(outbase + ".nj", with_distances=True )
        #print mytree.getNewick(with_distances=True)
        #print mytree.balanced().getNewick(with_distances=True)

        with open(outbase + ".nj.tree", "w") as njt:
            njt.write( mytree.asciiArt() )

        mytreeden     = dendrogram.ContemporaneousDendrogram( mytree )
        mytreedendraw = mytreeden.drawToPDF(outbase + '.nj.tree.pdf', 1024, 2048)

        mytreels      = least_squares.WLS(dissi).evaluateTree(mytree)
        print "NJ    Least Square", mytreels

        #print njs.description(3)
        #sys.exit(0)

        #ds         = p4.DistanceMatrix()
        #ds.setDim(dimentions)
        #ds.names  = copy.copy( names  )
        #ds.matrix = copy.copy( matrix )
        #
        #tmpf = tempfile.mktemp(prefix='vcftree_', suffix=".nex", dir='/tmp')
        #print tmpf
        #ds.writeNexus(fName=tmpf)
        #ds.writePhylip(fName=tmpf)
        #ds.writeNexus()
        #dataset = dendropy.DataSet.get_from_path(tmpf, 'nexus')


        #tmpf  = io.BytesIO()
        #ds.writeNexusToOpenFile(tmpf, True, False, 6)
        ##ds.writeNexusToOpenFile(flob, writeTaxaBlock, append, digitsAfterDecimal)
        #print tmpf.getvalue()
        #dataset = dendropy.DataSet.get_from_string(tmpf.getvalue(), 'nexus')

        #print dataset.description(3)

        #distance = hcluster.pdist(matrix)
        #linkage  = hcluster.linkage(distance)   #agglomeratively cluster original observations
        #single   = hcluster.single(distance)    #the single/min/nearest algorithm
        #complete = hcluster.complete(distance)  #the complete/max/nearest algorithm
        #average  = hcluster.average(distance)   #the average/UPGMA algorithm
        #weighted = hcluster.weighted(distance)  #the weighted/WPGMA algorithm
        #centroid = hcluster.centroid(distance)  #the centroid/UPGMA algorithm
        #median   = hcluster.median(distance)    #the median/WPGMA algorithm
        #ward     = hcluster.ward(distance)      #the Ward/incremental algorithm

        #print distance
        #print linkage
        #print single
        #print complete
        #print average
        #print weighted
        #print centroid
        #print median
        #print ward
        #print hcluster.dendrogram(linkage)


if __name__ == '__main__': main()
