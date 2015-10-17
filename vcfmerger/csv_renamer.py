#!/usr/bin/python

import os
import sys
import csv
import re
import unicodedata
from unidecode import unidecode

def main():
    try:
        inlst  = sys.argv[1]
        intbl  = sys.argv[2]
        tbl_k  = sys.argv[3]
        tbl_vs = sys.argv[4].split(',')

    except:
        print "<inlist> <in table> <column key name> <column val names>"
        sys.exit(1)

    print "input list             %s" % inlst
    print "input table            %s" % intbl
    print "table column key name  %s" % tbl_k
    print "table column val names %s" % tbl_vs

    data      = {}
    atad      = {}
    col_names = None
    tbl_k_id  = None
    tbl_v_ids = None
    with open(intbl, 'rb') as fhd:
        reader = csv.reader(fhd, delimiter=',', quotechar='"')
        for ln, cols in enumerate(reader):
            #print "ln", ln, "cols", cols

            if len(cols) == 0:
                continue

            if ln == 0: #header
                print cols
                assert tbl_k in cols, "key   %s not in header %s" % (tbl_k, ", ".join(cols))
                tbl_k_id  = cols.index(tbl_k)

                tbl_v_ids = []
                for tbl_v in tbl_vs:
                    assert tbl_v in cols, "value %s not in header %s" % (tbl_v, ", ".join(cols))
                    tbl_v_ids.append( cols.index(tbl_v) )

            else:
                k  =   cols[tbl_k_id]

                vs = []
                for tbl_v_id in tbl_v_ids:
                    try:
                        c = cols[tbl_v_id]
                        if c not in vs:
                            for s in vs:
                                if s in c:
                                    c = c.replace(s, '')
                                if c in s:
                                    c = c.replace(c, '')
                            vs.append( c )

                    except:
                        print "id", tbl_v_id, "cols", ", ".join(cols), "len", len(cols)
                        sys.exit(1)

                #k  =   unidecode(k)#unicodedata.normalize('NFKD', unidecode(k)).encode('ascii','ignore')
                #vs = [ unidecode(v) for v in vs ]

                v  = "_".join(vs)
                k  = sanitize(k, ' -.,:()=#&;')
                v  = sanitize(v, ' -.,:()=#&;')

                assert k not in data, "key %s found more than once" % ( k )
                assert v not in atad, "val %s found more than once" % ( v )

                data[k] = v
                atad[v] = k

    print "data"
    for k,v in data.iteritems():
        print " %-7s %s" % (k, v)

    with open(inlst, 'rb') as fhdi:
        reader = csv.reader(fhdi, delimiter='\t', quotechar='"')
        with open(inlst + '.renamed.csv', 'wb') as fhdo:
            writer = csv.writer(fhdo, delimiter='\t', quotechar='"')
            for ln, cols in enumerate(reader):
                if len(cols) == 0:
                    continue

                if cols[0][0] == "#":
                    continue

                assert len(cols) == 3, "wrong number of columns: %d %d %s" % (len(cols), ln, str(cols))

                name = cols[2]

                assert name in data, "name %s not in db" % name

                cols[2] = data[name]

                writer.writerow(cols)


def sanitize(s, k, v="_"):
    for r in k:
        s = s.replace(r, v)

    s  = re.sub(v+'+', v, s)
    s  = s.strip(v)
    s  = s.decode('utf8').encode('ascii', 'xmlcharrefreplace')

    return s

if __name__ == '__main__':
    main()
