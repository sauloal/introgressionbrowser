#!/usr/bin/env python

import sys
import os
import argparse

from   ete2 import Tree
try:
    print "importing image"
    import Image
    import ImageFont
    import ImageDraw
    import ImageMath
except ImportError:
    print "importing image from pil"
    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw
    from PIL import ImageMath

import math
import tempfile

#ls trees/*.tree | xargs -I{} -P 20 bash -c 'echo {};  ./newick_to_png.py --input {} --inlist pimp_problems.lst; ./newick_to_png.py {} cherry.lst;'


print_ascii        = False
transparent_color  = (255, 255, 255)
transparent_thresh = 5
frame_prop         = 0.05

TMP_DIR            = '/var/run/shm'

#http://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent
def distance2(a, b):
    return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2])

def makeColorTransparent(image, color, thresh2=0):
    image = image.convert("RGBA")
    red, green, blue, alpha = image.split()
    image.putalpha(ImageMath.eval("""convert(((((t - d(c, (r, g, b))) >> 31) + 1) ^ 1) * a, 'L')""",
        t=thresh2, d=distance2, c=color, r=red, g=green, b=blue, a=alpha))
    return image

def main():
    parser = argparse.ArgumentParser(description='Convert Newick file to PNG.')
    parser.add_argument('--infile'       , dest='infile'       , default=None     , action='store'      , nargs='?', required=True,          type=str  , help='Input Newick file'          )
    parser.add_argument('--inlist'       , dest='inlist'       , default=None     , action='store'      , nargs='?',                         type=str  , help='Input rename list'          )
    parser.add_argument('--caption'      , dest='caption'      , default=None     , action='store'      , nargs='?',                         type=str  , help='Image caption'              )
    parser.add_argument('--prefix'       , dest='prefix'       , default=None     , action='store'      , nargs='?',                         type=str  , help='File prefix'                )
    parser.add_argument('--output'       , dest='output'       , default=None     , action='store'      , nargs='?',                         type=str  , help='Output name'                )
    parser.add_argument('--extension'    , dest='extension'    , default="png"    , action='store'      , nargs='?',                         type=str  , help='Image extension'            )

    parser.add_argument('--dpi'          , dest='dpi'          , default=1200     , action='store'      , nargs='?',                         type=int  , help='Image DPI'                  )
    parser.add_argument('--fontsize'     , dest='fontsize'     , default=14       , action='store'      , nargs='?',                         type=int  , help='Font size'                  )

    parser.add_argument('--no_ladderize' , dest='ladderize'    ,                    action='store_false',                                                help="Don't ladderize image"      )
    parser.add_argument('--no_addcaption', dest='addcaption'   ,                    action='store_false',                                                help='Do not add caption to image')
    parser.add_argument('--show_distance', dest='show_distance',                    action='store_true' ,                                                help='Plot with distance')

    options = parser.parse_args()

    print options

    if options.infile is None:
        print "No input file given"
        parser.print_help()
        sys.exit(1)

    run(options.infile, 
	inlist        = options.inlist       ,
	capt          = options.caption      ,
	ofp           = options.prefix       ,
	output        = options.output       ,
	ladderize     = options.ladderize    ,
	addcaption    = options.addcaption   ,
	extension     = options.extension    ,
	dpi           = options.dpi          ,
    show_distance = options.show_distance,
	fontsize      = options.fontsize)


def run(infile, inlist=None, capt=None, ofp=None, output=None, ladderize=True, addcaption=True, extension="png", dpi=1200, fontsize=14, show_distance=False):
    add_file(infile, inlist=inlist, capt=capt, ofp=ofp, output=output, ladderize=ladderize, addcaption=addcaption, extension=extension, dpi=dpi, fontsize=fontsize, show_distance=show_distance)


def add_file(infile, inlist=None, capt=None, ofp=None, output=None, ladderize=True, addcaption=True, extension="png", dpi=1200, fontsize=14, show_distance=False):
    if not os.path.exists( infile ):
        print "input file %s does not exists" % infile
        sys.exit( 1 )

    print "reading input file %s" % infile

    caption = infile
    caption = caption.replace("/", "_")

    if capt:
        caption = capt


    outfile = infile + "." + extension
    if ofp:
        outfile = ofp + "." + extension

    if show_distance:
        tree = Tree(infile, format=0)
    else:
        #tree = Tree(infile, format=2)
        #tree = Tree(infile, format=5)
        tree = Tree(infile, format=9)

    #tree = Tree(open(infile, 'r').read())

    #root = tree.get_tree_root()

    #print tree.children
    #print tree.get_children()
    #print root.get_children()

    if inlist is not None:
        prune(inlist, tree, ladderize=ladderize)

        caption = infile  + "_" + inlist
        if capt:
            caption = capt + "_" + inlist
            caption = caption.replace("/", "_")

        outfile = infile + "_" + inlist + "." + extension

        if ofp:
            outfile = ofp + "_" + inlist + "." + extension

    elif ladderize:
        tree.ladderize()


    if output:
        outfile = output


    makeimage(infile, outfile, caption, tree, addcaption=addcaption, dpi=dpi, fontsize=fontsize)

    return outfile


def add_seq(inseq, inlist=None, capt=None, ladderize=True, addcaption=False, extension="png", dpi=1200, fontsize=14):
    fnm = tempfile.mkstemp(suffix=".tree", prefix=os.path.basename(sys.argv[0]) + '_tmp_', text=True, dir=TMP_DIR)[1]

    print "saving tree", fnm
    with open(fnm, 'w') as fhi:
        fhi.write(inseq)

    ofn  = add_file(fnm, inlist=inlist, capt=capt, ladderize=ladderize, addcaption=addcaption, extension=extension, dpi=dpi, fontsize=fontsize)

    data = None

    print "opening png", ofn

    if os.path.exists( ofn ):
        with open(ofn, 'rb') as fho:
            data = fho.read()
        os.remove(ofn)

    else:
        print "tree image %s does not exists" % ofn

    os.remove(fnm)

    return data


def prune(inlist, tree, ladderize=True):
    print "pruning", inlist

    reqlist = []

    with open( inlist, 'r' ) as fhd:
        for line in fhd:
            line  = line.strip()

            if len( line ) == 0:
                continue

            if line[0] == "#":
                continue

            print "excluding %s" % line

            reqlist.append( line )

    print reqlist
    
    tree.prune( reqlist, preserve_branch_length=True )
    
    if ladderize:
        tree.ladderize()

    return tree


def makeimage(infile, outfile, caption, tree, addcaption=True, dpi=1200, fontsize=14):
    if os.path.exists( outfile ):
        os.remove( outfile )

    #print tree.get_midpoint_outgroup()
    #print tree.get_sisters()
    #print tree.get_tree_root()
    #root = tree.get_tree_root()
    #tree.delete( root )
    #print "root", root
    #root.unroot()

    if print_ascii:
        print "redering tree", infile, "to", outfile,'in ASCII'
        print tree.get_ascii()
        print tree.write()

    print "redering tree", infile, "to", outfile
    tree.render( outfile, dpi=dpi )

    if not os.path.exists( outfile ):
        print "redering tree", infile, "to", outfile, 'FAILED'
        return None

    orig             = Image.open( outfile )
    orig             = makeColorTransparent(orig, transparent_color, thresh2=transparent_thresh);
    (orig_w, orig_h) = orig.size
    orig_dpi         = orig.info["dpi"]


    print "ORIG width",orig_w,"height",orig_h,"dpi",orig_dpi

    charsperline    = int( math.floor( orig_w/math.ceil(fontsize/1.6) ) )

    textlines       = []
    if addcaption:
        print "charsperline", charsperline
        print "caption",caption

        for pos in xrange(0, len(caption), charsperline):
            #print "pos",pos,"end", pos+charsperline, caption[pos: pos+charsperline]
            textlines.append( caption[pos: pos+charsperline] )

    numlines        = len(textlines)
    print "numlines", numlines
    htext           = (fontsize*numlines)
    himgtext        = orig_h + htext

    frame_w         = int( orig_w * frame_prop )
    orig_w_frame    =      orig_w + ( 2 * frame_w )
    out             = Image.new( 'RGBA', (orig_w_frame, himgtext), (255,255,255) )
    out.info["dpi"] = (dpi, dpi)

    maski           = Image.new('L', (orig_w_frame, himgtext), color=255)
    mask            = ImageDraw.Draw( maski )
    mask.rectangle((0, 0, orig_w_frame, himgtext), fill=0)
    out.putalpha( maski )
    out.paste( orig, ( frame_w, 0 ) )


    if addcaption:
        fontname = 'Consolas.ttf'
        if os.path.exists( fontname ):
            zoomout = 20
            font    = ImageFont.truetype(fontname, fontsize*zoomout)
            texti   = Image.new("RGBA", (orig_w*zoomout, htext*zoomout))
            text    = ImageDraw.Draw( texti )
            for linepos in xrange( len(textlines) ):
                hline = linepos * fontsize
                line  = textlines[linepos]
                text.text( (fontsize*zoomout, hline*zoomout), line, (0,0,0), font=font)
            texti   = texti.resize((orig_w,htext), Image.ANTIALIAS)
            out.paste( texti, ( frame_w, orig_h ) )


    (out_w, out_h)  = out.size
    out_dpi         = out.info["dpi"]
    print "OUT width", out_w, "height", out_h, "dpi", out_dpi

    out.save( outfile, optimize=True, dpi=(dpi,dpi) )

    print "saved to %s" % outfile

    return


if __name__ == '__main__':
    main()
