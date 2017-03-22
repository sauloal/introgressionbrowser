import glob
import os
import sys
import configurer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath( __file__ )), "vcfmerger"))

import runAnalysis

def get(app, data):
    serial = data["serial"]
    
    res = { "serial": serial, "valid": False }
    
    inFolder = app.config["INFOLDER"]
    
    for projectName in [ os.path.basename(p) for p in glob.glob( os.path.join(inFolder, "*") ) if os.path.isdir( p ) ]:
        print "Project", projectName
        projectFolder = os.path.join(inFolder, projectName)
        
        for analysisName in [ os.path.basename(p) for p in glob.glob( os.path.join(projectFolder, "*") ) if os.path.isdir( p ) ]:
            print " Analysis name", analysisName
            analysisFolder = os.path.join(projectFolder, analysisName)
             
            inConfs = glob.glob( os.path.join(analysisFolder, '*.conf') )
             
            for conf in inConfs:
                print "  Conf", conf
                
                #options = configurer.loadFromJson(options.fromJson, parser, "programs", "gen_makefile")
             
        #     inputFolder = os.path.join(analysisFolder, "input")
        #     
        #     if os.path.exists(inputFolder) and os.path.isdir(inputFolder):
        #         print "  Valid. Has input"
        #         
        #         infiles = []
        #         
        #         vcfs = glob.glob( os.path.join(inputFolder, "*.vcf") ) + glob.glob( os.path.join(inputFolder, "*.vcf.gz") )
        #         
        #         if len( vcfs ) > 0:
        #             for fileName in [ os.path.basename(p) for p in vcfs if (os.path.isfile( p ) or (os.path.islink( p ) and os.path.isfile(os.readlink( p )))) ]:
        #                 print "   Filename", fileName
        #                 infiles.append( fileName )
        #         else:
        #             print "   No file"
        #             
        #         
        #     else:
        #         print "  Invalid. Has No input"
    
    #files =       glob.glob( os.path.join( app.config["INFOLDER"], '*.pickle.gz') )
    #files.extend( glob.glob( os.path.join( app.config["INFOLDER"], '*.sqlite'   ) ) )
    
    
    return res

def run(data):
    serial = data["serial"]
    
    res = { "serial": serial, "valid": False }
    
    return res