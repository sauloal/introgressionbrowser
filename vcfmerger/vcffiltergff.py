#!/usr/bin/env python
"""
Given a VCF file, filters according to parameters
"""

import os, sys
import argparse

#from pprint import pprint as pp
#import copy
#import multiprocessing

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'.')))

import filemanager
import vcfconcat



def main(args):
    parser = argparse.ArgumentParser(description='Filters VCF file according to parameters')
    parser.add_argument('-c', '--chrom', '--chromosome', dest='chromosome', default=None, action='store'     , nargs='?',                       type=str, help='Chromosome to filter [all]')
    parser.add_argument('-g', '--gff'                  , dest='gff'       , default=None, action='store'     , nargs='?',                       type=str, help='Gff Coordinate file')
    parser.add_argument('-I', '--ignore', '--skip'     , dest='ignore'    , default=[]  , action='append'    , nargs='*',                       type=str, help='Chromosomes to skip')
    parser.add_argument('-s', '--start'                , dest='start'     , default=None, action='store'     , nargs='?',                       type=int, help='Chromosome start position to filter [0]')
    parser.add_argument('-e', '--end'                  , dest='end'       , default=None, action='store'     , nargs='?',                       type=int, help='Chromosome end position to filter [-1]')
    parser.add_argument('-k', '--knife'                , dest='knife'     ,               action='store_true',                                            help='Export to separate files')
    parser.add_argument('-n', '--negative'             , dest='negative'  ,               action='store_true',                                            help='Invert gff')
    parser.add_argument('-v', '--verbose'              , dest='verbose'   ,               action='store_true',                                            help='Verbose')
    parser.add_argument('-p', '--prot', '--protein'    , dest='protein'   , default=None, action='store'     ,                                  type=str, help='Input Fasta File to convert to Protein')

    parser.add_argument('-f', '--folder'               , dest='outfolder' , default=None, action='store'     , nargs='?',                       type=str, help='Overrride default output folder name')
    parser.add_argument('-o', '--out', '--output'      , dest='outfile'   , default=None, action='store'     , nargs='?',                       type=str, help='Overrride default output name')

    parser.add_argument('-i', '--input'                , dest='input'     , default=None ,                     nargs='?',                       type=str, help='Input file')
    #parser.add_argument('input'                        ,                    default=None, action='store'     , nargs='?', metavar='input file', type=str, help='Input file')


    options = parser.parse_args(args)

    config = {
        'infile'       : None,
        'outfile'      : None,

        'inchr'        : None,
        'instart'      : None,
        'inend'        : None,

        'protein'      : None,

        'ingff'        : None,
        'ingffreader'  : None,
        'gffnegative'  : False,
        'knife'        : False,
        'ignore'       : [],
    }

    print options

    config['infile'   ] = options.input
    config['outfile'  ] = options.outfile

    if options.input is None:
        print "no input file defined"
        sys.exit(1)

    if not os.path.exists(options.input):
        print "input file %s does not exists" % options.input
        sys.exit(1)


    config['outfolder'] = options.outfolder

    config['inchr'    ] = options.chromosome
    config['instart'  ] = options.start
    config['inend'    ] = options.end

    config['protein'  ] = options.protein

    config['ingff'    ] = options.gff
    config['negative' ] = options.negative
    config['knife'    ] = options.knife

    verbose             = options.verbose



    if not config['outfolder']:
        config['outfolder'] = 'walk_out'

    if config['knife'   ] and config['negative']:
        print "knife and negative can't be used at the same time"
        sys.exit( 1 )

    if config['knife'] and (not config['ingff']):
        print "knife needs gff"
        sys.exit( 1 )

    if config['ingff'] is not None:
        if not os.path.exists(config['ingff']):
            print "input gff %s does not exists" % config['ingff']
            sys.exit(1)
        print "Gff file               : %s" % config['ingff']



    indexFile = config['infile'] + ".idx"

    print "Input File             : %s" % config['infile']
    print "Index File             : %s (exists: %s)" % (indexFile, os.path.exists(indexFile) )

    if not os.path.exists( indexFile ):
        """
        Creates index file for VCF file
        """
        filemanager.makeIndexFile( indexFile, config['infile'] )

    config['idx'] = filemanager.readIndex(indexFile)


    if config['ingff'] is not None:
        """
        Creates a gff reader instance
        """
        config['ingffreader'] = gffReader( config['ingff'] , negative=config['negative'], protein=config['protein'], verbose=verbose)

        print "IDX", config['idx']
        print "GFF", config['ingffreader'].index

        assert set(config['ingffreader'].index.keys()).issubset( set(config['idx'].keys()) ), "VCF chromosomes (%s) are not a subset from GFF (%s)" % (", ".join(config['idx'].keys()), ", ".join(config['ingffreader'].index.keys()) )


    if config['inchr'] is not None:
        """
        If a specific chromosome has been requeste, get file position of the chromosome
        """
        config['insekpos'] = config['idx'][config['inchr']]


    """
    Creates a VCFCONCAT instance
    """
    vcfconcat.readSources(config)


    """
    Read the data and filter
    """
    readData(config, verbose=verbose)


    with open(config['outfolder']+'.ok', 'w') as fhd:
        fhd.write(str(config))


    return config


def readData(config, verbose=False):
    """
    Reads the data and preforms the filtering
    """

    print "reading data"


    """
    Creates a VCFMERGER instance to read the VCF file
    """
    config['infhd']  = filemanager.openvcffile(config['infile'], 'r')



    if config['outfile'] is None:
        """
        Creates output file filename if not defined
        """
        outfn = config['infile'] + '.filtered'

        if config['inchr'] is not None:
            outfn += ".%s" % config['inchr']

        if config['instart'] is not None:
            outfn += ".%012d" % config['instart']

        if config['inend'] is not None:
            outfn += "-%012d" % config['inend']

        outfn += ".vcf.gz"
        print "saving to %s" % outfn
        config['outfn']  = outfn

    else:
        config['outfn']  = config['outfile']



    """
    Creates a VCFMERGER to save the output
    """
    config['oufhd']  = filemanager.openvcffile(config['outfn'], 'w')
    config['oufhd'].write( config['header'] )

    runName = "all"

    if config['idx'] is not None:
        """
        If no index for input file. creates it
        """

        print "reading data :: has idx"
        if config['inchr'] is not None:
            """
            If a particular chromosome has been selected, go to position in file
            """
            print "reading data :: has idx :: seeking chrom %s" % config['inchr']

            assert config['inchr'] in config['idx'], "requested chromosome %s not in vcf file: %s" % ( config['inchr'], config['idx'].keys() )

            config['infhd'].seek( config['insekpos'] )
            runName = config['inchr']

            print "reading data :: has idx :: seeking chrom %s. DONE" % config['inchr']

            if config['ingff'] is not None:
                """
                If a GFF was given, go to chromosome position
                """
                print "reading data :: has gff :: seeking chrom %s" % config['inchr']
                config['ingffreader'].seek( config['inchr'] )
                print "reading data :: has gff :: seeking chrom %s. DONE" % config['inchr']



    print "reading data :: CHR %s" % config['inchr']

    gffreader  = config['ingffreader']


    inchr      = config['inchr'      ]
    instart    = config['instart'    ]
    inend      = config['inend'      ]

    if config['knife']:
        config['knife_last_register_key'] = None
        config['knife_out_fhd'          ] = None
        config['knife_out_fn'           ] = None


    refs       = []
    lastChro   = None
    lastPos    = -1
    lastPosVal = -1
    finalChro  = False
    numSnps    = {}
    valids     = {}
    validst    = 0

    for line in config['infhd']:
        """
        Reads input file
        """

        line = line.strip()

        if len(line) ==  0 :
            continue

        if line[0]   == '#':
            continue


        cols     = line.split("\t")


        if len(cols) < 10:
            print "NOT 10 COLS\n", line
            sys.exit(1)


        chro =     cols[0]
        posi = int(cols[1])
        #src  =     cols[3]
        #dst  =     cols[4]

        #print cols

        if lastChro != chro:
            print "Chromosome", chro
            assert chro in config['idx'], "chromosome %s not in vcf file: %s" % ( chro, config['idx'].keys() )

            if lastChro is not None:
                if inchr is not None:
                    if inchr != lastChro:
                        print "reading data :: %s :: %s :: skipping exporting" % (runName, lastChro)
                        lastChro = chro
                        continue

                    else:
                        finalChro = True

                if finalChro: break

            lastChro   = chro
            lastPos    = -1
            lastPosVal = -1
            if chro not in numSnps:
                numSnps[chro] = 0


        if chro in config['ignore' ]:
            continue


        if lastPos != posi:
            if numSnps[chro] % 100000 == 0:
                print "reading data :: %s :: %s %12d SNPs" % (runName, chro, numSnps[chro])

            numSnps[chro] += 1

            lastPos = posi


        if ( inchr is not None ):
            """
            If a specific chromosome was requested
            """

            if ( inchr   != chro )                           :
                """
                If current chromosome is not the requested chromosome, skip
                """
                #sys.stdout.write("-")
                continue

            if ( instart is not None ) and ( posi < instart ):
                """
                If a specific start position is requested and the current position is smaller than that, skip
                """
                #sys.stdout.write("<")
                #print "%d<%d" % (posi, instart),
                continue

            if ( inend   is not None ) and ( posi > inend   ):
                """
                If a specific end position is requested and the current position is greater than that, skip
                """
                #sys.stdout.write(">")
                #print "%d>%d" % (posi, instart),
                continue

        if ( gffreader is not None ):
            """
            If a GFF file was given
            """

            posis = '{:,}'.format( posi )

            if  not gffreader.isOk(chro, posi):
                """
                If current position is not present in the GFF, skip
                """
                if verbose:
                    print "N CHROM %s POS %13s :: %s" % ( chro, posis, gffreader.latest() )
                #sys.stdout.write("g")
                continue

            else:
                """
                If current position is present in the GFF, continue
                """
                if verbose:
                    print "Y CHROM %s POS %13s :: %s" % ( chro, posis, gffreader.latest() )
                pass

        #sys.stdout.write(".")
        if lastPosVal != posi:
            """
            If position has changed, add to statistics
            """
            if chro not in valids:
                valids[chro] = 0
            valids[chro] += 1
            validst      += 1

            if valids[chro] % 1000 == 0:
                print "reading data :: %s :: %s %12d SNPs valid %12d SNPs valid in total" % (runName, chro, valids[chro], validst)

            lastPosVal  = posi

        if config['knife']:
            """
            If separated in different files
            """

            #print "getting last register"
            last_register     = gffreader.get_last_register()
            #print last_register
            last_register_key = ( last_register['lastChrom'], last_register['lastStart'], last_register['lastEnd'], last_register['lastName'] )

            if last_register['lastStart'] < 0:
                """
                If first register (no previous), skip
                """
                print "If first register (no previous), skip. continuing"
                continue

            if config['knife_last_register_key'] != last_register_key:
                """
                If new coordinate and not continuation of previous, create file
                """
                #print "old register:",config['knife_last_register_key']
                #print "new register:",last_register_key

                if config['knife_out_fhd'] is not None:
                    """
                    Close previous knifed file
                    """
                    #print "closing register:",config['knife_last_register_key']
                    config['knife_out_fhd'].close()
                    config['knife_out_fhd'] = None

                full_path = os.path.abspath(  config['outfolder']             )
                base_name = os.path.basename( config['outfolder']             )
                base_path = os.path.dirname(  full_path                       )
                out_path  = os.path.join(     base_path, config['outfolder']  )
                out_dir   = os.path.join(     out_path , last_register_key[0] )

                if not os.path.exists( out_path ):
                    os.makedirs( out_path )

                if not os.path.exists( out_dir ):
                    os.makedirs( out_dir )

                out_base      = os.path.join( out_dir, base_name )

                knife_out_fn  = out_base

                knife_out_fn += ".%s"    % last_register_key[0]

                knife_out_fn += ".%012d" % last_register_key[1]

                knife_out_fn += "-%012d" % last_register_key[2]

                knife_out_fn += ".%s"    % last_register_key[3]

                knife_out_fn += ".vcf.gz"

                print " saving to knifed %s" % knife_out_fn
                #sys.exit(1)

                config['knife_last_register_key'] = last_register_key
                config['knife_out_fn']            = knife_out_fn
                config['knife_out_fhd']           = filemanager.openvcffile(knife_out_fn, 'w')

                knife_extra                       = [
                    "##KNIFE-chromosome=%s" %     last_register_key[0] ,
                    "##KNIFE-start=%s"      % str(last_register_key[1]),
                    "##KNIFE-end=%s"        % str(last_register_key[2]),
                    "##KNIFE-gene=%s"       %     last_register_key[3]
                ]

                knife_header = config['header'].split("\n")
                knife_header = knife_header[:-2] + knife_extra + [ knife_header[-2] ]
                config['knife_out_fhd'].write( "\n".join(knife_header) + "\n" )

            #print "printing to register:",last_register_key
            config['knife_out_fhd'].write( line )
            config['knife_out_fhd'].write( "\n" )

        config['oufhd'].write(line)
        config['oufhd'].write("\n")

    if  config['oufhd'] is not None:
        """
        Closes filehandle
        """
        config['oufhd'].close()
        config['oufhd'] = None



    if config['knife']:
        if  config['knife_out_fhd'] is not None:
            """
            Closes knifed filehandle
            """
            config['knife_out_fhd'].close()
            config['knife_out_fhd'] = None


    print "reading data :: %s :: finished." % ( runName )

    """
    Print statistics
    """
    keys = sorted(list(set(valids.keys() + numSnps.keys())))
    for chro in keys:
        vals = 0

        if chro in valids:
            vals = valids[chro]

        tot = 0

        if chro in numSnps:
            tot = numSnps[chro]

        print "  CHROM %s TOTAL %12d VALID %12d" % ( chro, tot, vals )

    return 0


class gffReader(object):
    """
    Indexes, reads and checks whether a position is present in the GFF file
    """
    def __init__(self, gffFile, negative=False, protein=None, verbose=False):
        self.infile  = gffFile
        self.fhd     = None
        self.verbose = verbose

        gffFileIdx = gffFile + ".idx"
        if not os.path.exists(gffFileIdx):
            filemanager.makeIndexFile(gffFileIdx, gffFile)

        self.index      = filemanager.readIndex(gffFileIdx)
        self.lastChrom  = None
        self.lastName   = "-"
        self.lastStart  = None
        self.lastEnd    = None

        self.prevChrom  = None
        self.prevStart  = -1
        self.prevEnd    = -1
        self.prevName   = "-"

        self.firstStart = None
        self.linenum    = 0
        self.EOF        = False
        self.negative   = negative

        self.protein    = protein
        self.proteinFhd = None
        self.lastData   = None
        self.protout    = self.infile + '.prot.gff3'
        self.protoutfhd = None
        self.protLastEx = None

        if protein is not None:
            if not os.path.exists( protein ):
                print "input dna fasta file to be converted to protein %s does not exists" % protein
                sys.exit(1)

            print "Protein fasta          : %s" % protein
            self.proteinFhd = fasta( protein )
            self.proteinFhd.open()

    def has(self, chrom):
        """
        Check if chromosome is present in GFF file
        """
        return chrom in self.index

    def seek(self, chrom):
        """
        Go to start position of chromosome in the file
        """
        print "seek %s" % chrom,
        if self.fhd is None:
            self.open()

        if self.has(chrom):
            print "pos %12s before %12s" % ('{:,}'.format( self.index[ chrom ] ), '{:,}'.format( self.fhd.tell() ) ),
            self.fhd.seek( self.index[ chrom ] )
            print "after %12s" % ( '{:,}'.format( self.fhd.tell() ) )
            self.readRegister()
            self.firstStart = self.lastStart

        else:
            print "chrom %s not in gff" % chrom
            sys.exit(1)

    def open(self):
        """
        Open GFF file
        """
        self.fhd    = filemanager.openfile(self.infile, 'r')

    def readRegister(self):
        """
        Reads next register
        """
        self.prevName  = self.lastName
        self.prevStart = self.lastStart
        self.prevEnd   = self.lastEnd
        prevChrom      = self.lastChrom

        self.lastChrom = None
        self.lastName  = "-"
        self.lastStart = None
        self.lastEnd   = None

        if self.fhd is None:
            self.open()

        res = []
        while (len(res) == 0):
            line = self.fhd.readline()

            if len(line) == 0: #EOF
                self.EOF = True
                self.fhd.close()
                break

            line = line.strip()
            self.linenum += 1

            if len(line) == 0:
                continue

            if line[0] == "#":
                continue

            res = line.split("\t")

            if len(res) != 9: #gff3
                print "invalid gff line (l %d / b %d): %s" % ( self.linenum, self.fhd.tell(), line)
                sys.exit(1)
                res = []
                continue

        if len(res) == 0:
            return None

        self.lastChrom =     res[0]
        self.lastStart = int(res[3])
        self.lastEnd   = int(res[4])
        self.lastName  =     res[8]

        if 'Name=' in self.lastName:
            #Alias=Solyc00g005880;ID=gene:Solyc00g005880.1;Name=Solyc00g005880.1;from_BOGAS=1;length=1150
            pos_start = self.lastName.find('Name=')
            pos_end   = self.lastName.find(';', pos_start)
            #print "  start",pos_start,'end',pos_end
            self.lastName = self.lastName[ pos_start + 5: pos_end ]

        if prevChrom != self.lastChrom:
            self.prevStart  = -1
            self.prevEnd    = -1
            self.firstStart = self.lastStart
            self.prevChrom  = prevChrom

        return True

    def latest(self):
        """
        Returns latest read register
        """
        last_reg   = self.get_last_register()
        lastChrom  = last_reg[ 'lastChrom'  ]
        firstStart = last_reg[ 'firstStart' ]
        prevStart  = last_reg[ 'prevStart'  ]
        prevEnd    = last_reg[ 'prevEnd'    ]
        prevName   = last_reg[ 'prevName'   ]
        lastStart  = last_reg[ 'lastStart'  ]
        lastEnd    = last_reg[ 'lastEnd'    ]
        lastName   = last_reg[ 'lastName'   ]

        firstStart = '{:,}'.format( firstStart )
        prevStart  = '{:,}'.format( prevStart  )
        prevEnd    = '{:,}'.format( prevEnd    )
        lastStart  = '{:,}'.format( lastStart  )
        lastEnd    = '{:,}'.format( lastEnd    )

        #return "%s :: first start %12d previous start %12d last start %12d last end %12d" % (lastChrom, firstStart, prevStart, lastStart, lastEnd)
        #return "%s :: first start %12d\n\tprevious start %12d previous end %12d previous name %s\n\tlast start     %12d last end     %12d last name     %s" % (lastChrom, firstStart, prevStart, prevEnd, prevName, lastStart, lastEnd, lastName)
        return "%s :: first start %13s\n\tprevious start %13s previous end %13s previous name %s\n\tlast start     %13s last end     %13s last name     %s" % (lastChrom, firstStart, prevStart, prevEnd, prevName, lastStart, lastEnd, lastName)

    def printHere(self, text):
        """
        Prints text. debugging purpose
        """
        if self.verbose:
            print text

    def genReturn(self, resp):
        """
        Converts response, negating if requested. Also, converts to protein in requested
        """
        if self.negative:
            resp = not resp

        if resp:
            if self.protein is not None:
                cdata = ( self.lastChrom, self.lastStart, self.lastEnd )
                if cdata != self.lastData:
                    self.lastData = cdata
                    seq = self.proteinFhd.get( self.lastChrom, self.lastStart, self.lastEnd )

                    if self.protoutfhd is None:
                        self.protoutfhd = open(self.protout, 'w')

                    self.protoutfhd.write( "%s\t%d\t%d\t%s\n" % (self.lastChrom, self.lastStart, self.lastEnd, seq) )

        return resp

    def get_last_register( self ):
        """
        Get latest register
        """

        last_reg = {
            'lastChrom'  : self.lastChrom  if self.lastChrom  else "None",
            'firstStart' : self.firstStart if self.firstStart else -1,
            'prevStart'  : self.prevStart  if self.prevStart  else -1,
            'prevEnd'    : self.prevEnd    if self.prevEnd    else -1,
            'prevName'   : self.prevName   if self.prevName   else "-",
            'lastStart'  : self.lastStart  if self.lastStart  else -1,
            'lastEnd'    : self.lastEnd    if self.lastEnd    else -1,
            'lastName'   : self.lastName   if self.lastName   else "-",
        }

        return last_reg

    def isOk(self, chro, posi):
        """
        Returns whether a coordinate is valid or not
        """
        text = "%s POSITION    %13s :: %s" % (chro, '{:,}'.format( posi ), self.latest())

        if chro not in self.index:
            self.printHere( text + " gff01" )
            return False

        if self.EOF:
            self.printHere( text + " gff02" )
            return self.genReturn(False)

        if ( self.lastChrom is None ) or ( self.lastChrom != chro ):
            if ( self.prevChrom is not None ) and ( self.prevChrom == chro ):
                self.printHere( text + " gff03" )
                return False

            text += " gff04 (%s) %s to %s - " % (self.prevChrom, self.lastChrom, chro)
            text += self.latest() + " - "
            self.seek(chro)
            text += self.latest()


        if ( self.lastStart is None ) or ( self.lastEnd is None ):
            text += " gff05"
            self.readRegister()

        if self.EOF:
            self.printHere( text + " gff06" )
            return self.genReturn(False)

        if self.lastChrom != chro:
            self.printHere( text + " gff07" )
            return self.genReturn(False)

        if ( posi < self.firstStart ):
            self.printHere( text + " gff08" )
            return self.genReturn(False)

        if ( self.prevStart != -1 ) and ( posi > self.prevEnd ) and ( posi < self.lastStart ):
            self.printHere( text + "\ngff09 prevstart %s prevend %s posi %s laststart %s lastend %s\n" % ( '{:,}'.format( self.prevStart ), '{:,}'.format( self.prevEnd ), '{:,}'.format( posi ), '{:,}'.format( self.lastStart ), '{:,}'.format( self.lastEnd ) ) )
            return self.genReturn(False)

        if ( posi > self.firstStart ) and ( posi < self.lastStart ):
            """ if already ahead of the position. should only happen if reading out of order"""
            text += " gff10 seek prevstart %s prevend %s posi %s laststart %s lastend %s" % ( '{:,}'.format( self.prevStart ), '{:,}'.format( self.prevEnd ), '{:,}'.format( posi ), '{:,}'.format( self.lastStart ), '{:,}'.format( self.lastEnd ) )
            self.seek(chro)

        if ( posi >= self.lastStart ) and ( posi <= self.lastEnd ):
            self.printHere( text + "\ngff11: %d <= %d <= %d\n" % (self.lastStart, posi, self.lastEnd ) )
            return self.genReturn(True)


        if (( self.lastChrom == chro ) and ( self.lastEnd < posi )):
            text += "\ngff12 b seek prevstart %s prevend %s posi %s laststart %s lastend %s\n" % ( '{:,}'.format( self.prevStart ), '{:,}'.format( self.prevEnd ), '{:,}'.format( posi ), '{:,}'.format( self.lastStart ), '{:,}'.format( self.lastEnd ) )

            while (( self.lastChrom == chro ) and ( self.lastEnd < posi )):
                #text += " gff12"
                self.readRegister()
                #text += "gff12 d seek prevstart %s prevend %s posi %s laststart %s lastend %s\n" % ( '{:,}'.format( self.prevStart ), '{:,}'.format( self.prevEnd ), '{:,}'.format( posi ), '{:,}'.format( self.lastStart ), '{:,}'.format( self.lastEnd ) )

                if self.EOF:
                    self.printHere( text + " gff13" )
                    return self.genReturn(False)

            text += "gff12 a seek prevstart %s prevend %s posi %s laststart %s lastend %s\n\n" % ( '{:,}'.format( self.prevStart ), '{:,}'.format( self.prevEnd ), '{:,}'.format( posi ), '{:,}'.format( self.lastStart ), '{:,}'.format( self.lastEnd ) )


        if self.EOF:
            self.printHere( text + " gff14" )
            return self.genReturn(False)

        if self.lastChrom != chro:
            self.printHere( text + " gff15" )
            return self.genReturn(False)

        if ( posi >= self.lastStart ) and ( posi <= self.lastEnd ):
            self.printHere( text + " gff16" )
            return self.genReturn(True)

        self.printHere( text + " gff17 " + self.latest() )

        return self.genReturn(False)


class fasta(object):
    """
    Fasta reader class
    """
    def __init__(self, infile):
        self.infile = infile
        self.idx     = infile + '.idx'
        self.fhd     = None # filehandle
        self.index   = None
        self.chrom   = None
        self.seq     = None

    def seek(self, pos):
        """
        Seeks a a specific postion in the file in bytes
        """
        if self.fhd is None:
            self.open()
        print "seeking pos %d" % pos
        self.fhd.seek( pos )

    def open(self):
        """
        Open file
        """
        print "opening fasta %s" % self.infile

        self.getIndex()

        if self.fhd is None:
            self.fhd = open(self.infile, 'r')

        print "opening fasta %s FINISHED" % self.infile

    def doIndex(self):
        """
        Index fasta file
        """
        print "indexing fasta %s to %s" % ( self.infile, self.idx )
        index   = []

        with open(self.infile, 'r') as fhd:
            chroPos = 1
            for line in iter(fhd.readline, ''):
                if len( line ) == 0: break
                line            = line.strip()

                if line[0] == ">":
                    index.append( [
                            line[1:],                   # 0 chrom name
                            fhd.tell() - len(line) - 1, # 1 start position
                            chroPos,                    # 2 chromosome number
                            0,                          # 3 chrom size
                            0                           # 4 len line
                        ]
                    )
                    chroPos += 1
                    #print index[-1]

                elif len( line ) > 1:
                    lenLine         = len(line)
                    index[ -1 ][3] += lenLine
                    if lenLine > index[ -1 ][4]: index[ -1 ][4] = lenLine

        with open( self.idx, 'w') as fhd:
            for vals in index:
                print vals
                fhd.write( "\t".join( [str(x) for x in vals] ) + "\n" )

        print "indexing fasta %s to %s FINISHED" % ( self.infile, self.idx )

    def getIndex(self):
        """
        Returns fasta file index with sequence names byte positin in file
        """
        if not os.path.exists( self.idx ):
            self.doIndex()

        if self.index is None:
            self.index = {}

            with open(self.idx, 'r') as fhd:
                for line in fhd:
                    cols = line.strip().split("\t")

                    self.index[ cols[0] ] = {
                        'pos': int( cols[1] ),
                        'num': int( cols[2] ),
                        'len': int( cols[3] ),
                        'lin': int( cols[4] )
                    }

                    print cols

    def getChro(self, chro):
        """
        Returns whole sequence
        """
        if self.index is None:
            self.open()

        if chro not in self.index:
            print "requesting inexistent chromosome %s" % chro
            print self.index
            sys.exit(1)

        if chro == self.chrom:
            return self.seq

        else:
            self.chrom = chro
            startPos   = self.index[chro][ 'pos' ]
            startNum   = self.index[chro][ 'num' ]
            chromLen   = self.index[chro][ 'len' ]
            lineLen    = self.index[chro][ 'lin' ]

            endPos     = startPos + chromLen + int( chromLen / lineLen )

            self.seek( startPos )
            seq     = []
            lastPos = self.fhd.tell()

            linenum = 0
            for line in iter(self.fhd.readline, ''):
                linenum += 1
                if linenum == 1:
                    if len(line) == 0:
                        print "error loading file. len 0"
                        sys.exit(1)

                    line = line.strip()

                    if line[0] != ">":
                        print "not a fasta or index is wrong"
                        sys.exit( 1 )
                    else:
                        print line
                        continue

                #if ( endPos > -1 ) and ( lastPos >= endPos ):
                #    print line
                #    line = line.strip()
                #    seq.append( line )
                #
                #    print "b1 %d >= %d" % ( lastPos, endPos )
                #    break

                if len(line) == 0:
                    print "b2 EOF"
                    break

                if line[0] == ">":
                    print "b3 NSEQ"
                    break

                line = line.strip()

                if len(line) == 0:
                    print "b4 EMP"
                    break

                lastPos = self.fhd.tell()
                seq.append( line )

            self.seq = "".join( seq )

            if chromLen != len(self.seq):
                print "error acquiring chromosome %s. got len %d instead of %d" % ( chro, chromLen, len(self.seq) )
                print self.seq[: 100]
                print self.seq[-100:]
                sys.exit(1)

            return self.seq

    def getStart(self, chro, start):
        """
        Get sequence starting from start position
        """
        self.getChro(chro)
        chromLen = self.getChromSize(chro)
        if start > chromLen:
            print "start %s bigger than chromosome size %d (%s)" % (start, chromLen, chro)
            sys.exit(1)

        return self.seq[start+1:]

    def get(self, chro, start, end):
        """
        Get a sequence fragment
        """
        self.getChro(chro)
        chromLen = self.getChromSize(chro)

        if start > chromLen:
            print "start %s bigger than chromosome size %d (%s)" % (start, chromLen, chro)
            sys.exit(1)

        if end   > chromLen:
            print "end   %s bigger than chromosome size %d (%s)" % (end  , chromLen, chro)
            sys.exit(1)

        return self.seq[start-1:end]

    def getChroms(self):
        """
        Get list of sequences
        """
        return self.index.keys()

    def getChromSize(self, chro):
        """
        Get chromosome size
        """
        return self.index[chro]['len']

if __name__ == '__main__':
    main(sys.argv[1:])
