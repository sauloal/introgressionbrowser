#!/usr/bin/python
"""
Web server for the Introgression browser.
Reads config.py to setup.
Uses vcf_walk as shared library and either vcf_walk_ram or vcf_walk_sql as database.

NFO FILE:
title=
custom_order=
custom_order=
custom_order=

CUSTOM ORDER FILE:
#ROWNUM=0 (-1 or nothing to ignore)
#COLNUM=1 (-1 or nothing to ignore)
#NAME=
#CHROMOSOME= (__global__ or empty for all chromosomes)
row order\tcol order\n
"""



import os
import sys
import io
import base64
import random
from operator import itemgetter

currpath = os.path.dirname( os.path.abspath( __file__ ) )
print "CURRPATH ", currpath
sys.path.insert(0, currpath )
sys.path.insert(0, os.path.join(currpath, "venv/lib/python2.7/site-packages") )



print "importing hashlib"
import hashlib

print "importing glob"
import glob

print "importing time"
import time

print "importing flask"
from flask       import Flask, request, session, send_file, escape, g, redirect, url_for, abort, render_template, flash, make_response, jsonify, Markup, Response, send_from_directory, Blueprint, json

print "importing jinja2"
from jinja2      import TemplateNotFound

bin_path = os.path.abspath( __file__ )
dir_path = os.path.dirname( bin_path )

#TODO:
#      ADD OPTION FOR MAX_NUMBER_OF_COLUMNS




#VARIABLES
DEBUG                     = True
IDEBUG                    = False
MAX_NUMBER_OF_COLUMNS     = 300
SERVER_PORT               = 10000
SECRET_KEY                = "development key"
SECRET_KEY                = '\xe1:\xbf\xc2\xaa\x0b\x04\xb8\xac\xc1\xff;Z-W\xfcRE\xadY"K\xa1v'
MAX_CONTENT_LENGTH        = 128 * 1024 * 1024
USE_SQL                   = True
INFOLDER                  = None
DATABASEINV               = {}

#import os
#os.urandom(24)
#'\xe1:\xbf\xc2\xaa\x0b\x04\xb8\xac\xc1\xff;Z-W\xfcRE\xadY"K\xa1v'

#import hashlib
#hashlib.sha256("<LOGIN><PASSWORD>").hexdigest()

DATABASES           = []
DATABASES_DB_NAME   = 0
DATABASES_DB_F_NAME = 1
DATABASES_DB_CONF   = 2
DATABASES_MTIME     = 3
DATABASES_INTERFACE = 4

config              = os.path.join( dir_path, 'config.py' )
hasConfig           = False
hasLogin            = False
credentials         = None



if not os.path.exists( config ):
    print "config does not exists"
    sys.exit( 1 )

else:
    hasConfig = True
    execfile(config)



if INFOLDER is None:
    print "no input folder given"
    sys.exit( 1 )



"""
Decides the interface whether RAM or SQL
"""
print "importing vcf_walk"
sys.path.insert( 0, os.path.join( dir_path, 'vcfmerger' ) )

if USE_SQL:
    import vcf_walk_sql as interface
else:
    import vcf_walk_ram as interface



librepaths = [ # pages which can be seen without login
    '/api',
    '/favicon.ico'
]
librepoints = [
    'login',
    'logout',
]

loaded    = False


app                                         = Flask(__name__)
app.config.from_object(__name__)
app.jinja_env.globals['trim_blocks'       ] = True
app.jinja_env.add_extension('jinja2.ext.do')
app.config['MAX_CONTENT_LENGTH']            = MAX_CONTENT_LENGTH
#jsonpickle.set_preferred_backend('simplejson')
#jsonpickle.set_encoder_options('simplejson', ensure_ascii=True, sort_keys=True, indent=1)



#http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask
def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

#    complete_path = os.path.join(root_dir(), "static", "login.html")
#    mimetype      = "text/html"
#    content       = get_file(complete_path)
#    return Response(content, mimetype=mimetype)




@app.before_request
def before_request():
    """
    before each request, add global variables to the global G variable.
    If using WSGI (eg. apache), this won't work
    """
    #print "before request", request.url, request.base_url, request.url_root, request.endpoint
    if hasConfig and credentials and hasLogin:
        #print "before request: has config"
        if 'username' in session:
            #print "before request: has config - has username set"
            print 'Logged in as %s' % (escape(session['username']))

        else:
            is_libre = False
            for librepath in librepaths:
                if request.path.startswith( librepath ):
                    #print "before request: has config - no username set - redirecting to login", url_for('login')
                    print "before request: has config - no username set - libre path: request",request.path, "libre", librepath
                    is_libre = True
                    break
                    #abort(401)


            if not is_libre:
                for librepoint in librepoints:
                    if request.endpoint == librepoint:
                        #print "before request: has config - no username set - redirecting to login", url_for('login')
                        print "before request: has config - no username set - libre endpoint: request",request.endpoint, "libre", librepoint
                        is_libre = True
                        break

                if not is_libre:
                    print "not libre", request.endpoint, request.path, 'redirecting'
                    #for r in dir(request):
                    #    try:
                    #        print "r", r, '=',getattr(request, r)
                    #    except:
                    #        pass
                    return redirect(url_for('login', _external=True))








@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Perform login
    """
    #print "login"
    if hasConfig and credentials and hasLogin:
        #print "login: has config"
        if request.method == 'POST':
            #print "login: has config - POST"
            username = request.form.get('username', None)
            password = request.form.get('password', None)
            noonce   = request.form.get('noonce'  , None)
            print "login: has config - POST - username %s password %s noonce %s" % ( username, password, noonce )

            if username is not None and password is not None and noonce is not None:
                if "nonce" in session and noonce == session["nonce"]:
                    print "login: has config - POST - not none. noonce match"
                    if username in credentials:
                        #print "login: has config - POST - not none - user in credentials"
                        #pwd = hashlib.sha256(username+password).hexdigest()
                        pwd = credentials[username]
                        print "pwd %s" % pwd
                        cry = hashlib.sha256(noonce+pwd).hexdigest()
                        print "cry %s password %s" % ( cry,  password )
                        #print "login: has config - POST - not none - user in credentials - username %s password %s hex %s" % ( username, password, pwd )

                        if cry == password:
                            #print "login: has config - POST - not none - user in credentials - right password"
                            session['username'] = username
                            del session['nonce']
                            return redirect(url_for('get_main', _external=True))

                else:
                    print "login: has config - POST - not none. noonce does not match", noonce, session["nonce"] if "nonce" in session else None
                 

    session["nonce"] = hashlib.sha256( str(random.randint(0, sys.maxint)) + str(time.time()) ).hexdigest()
    print "new nonce", session["nonce"]
    return render_template('login.html')
    #return app.send_static_file('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    """
    Perform logout
    """
    print "logoff"

    if hasConfig and credentials and hasLogin and 'username' in session:
        print "logoff from user %s: has config" % str(session['username'])
        session.pop('username', None)

    #return redirect(url_for('get_main'))
    return redirect(url_for('login', _external=True))


@app.route("/username", methods=['GET'])
def get_username():
    return jsonify({'username': session['username']})


@app.route("/", methods=['GET'])
def get_main():
    #return redirect ( url_for('static', filename='index.html' ) )
    return app.send_static_file('index.html')


@app.route("/alive", methods=['GET'])
def get_alive():
    res = jsonify( { 'res': True } )
    res.headers['Access-Control-Allow-Origin'] = '*'

    return res





@app.route("/api", methods=['GET'])
def get_api():
    api = {
        "/api/dbs"                               :  { 'databases': ['str:db_name']      },
        "/api/maxnumcol"                         :  { 'maxnumcol': 'int:num_cols'       },
        "/api/mtime/<db_name>"                   :  { 'mtime'    : 'date:creation_date' },
        "/api/spps/<db_name>"                    :  { 'spps'  : ['str:ref'  ]  },
        "/api/chroms/<db_name>"                  :  { 'chroms': ['str:chrom']  },
        "/api/clusterlist/<db_name>"             :  {
                                                        "str:name_space": [
                                                            "str:cluster_name"
                                                        ]
                                                    },
        "/api/genes/<db_name>/<chrom>"           :  { 'genes' : ['str:gene' ]  },
        "/api/tree/<db_name>/<chrom>/<gene>"     :  { 'chrom' : 'str:chrom', 'gene': 'str:gene', 'tree'     : { "newick": "str[newick]:tree_string", "png": "str[base64]:png_image" } },
        "/api/alignment/<db_name>/<chrom>/<gene>":  { 'chrom' : 'str:chrom', 'gene': 'str:gene', "alignment": { "coords": [ 'int:snp_pos' ], "fasta": { "str:ref": "str:alignment" } } },
        "/api/matrix/<db_name>/<chrom>/<gene>"   :  { 'chrom' : 'str:chrom', 'gene': 'str:gene', 'matrix'   : [ [ 'int:distance' ] ] },
        "/api/report/<db_name>/<chrom>/<gene>"   :  {
                                                        "END"  : 'int:end_pos',
                                                        "FASTA": {
                                                            "coords": [ 'int:pos' ],
                                                            "fasta" : { "int:ref": "str:alignment" }
                                                        },
                                                        "LEN_OBJ": 'int:',
                                                        "LEN_SNP": 'int:num_snps',
                                                        "LINE": [ [ 'float:distance' ] ],
                                                        "NAME" : "str:gene",
                                                        "START": "int:start_pos",
                                                        "TREE" : {
                                                            "newick": "str[newick]:tree_string",
                                                            "png"   : "str[base64]:png_image"
                                                        },
                                                        "chrom"  : "str:chrom",
                                                        "db_name": "str:db_name",
                                                        "gene"   : "str:gene",
                                                        "spps"   :  [ "str:ref" ]
                                                    },
        "/api/cluster/<db_name>/<ref>/<chrom>[?(png|svg)&(rows|columns|lst)]"   :  {
                                                        "str:cluster_name": {
                                                            "cols": {
                                                                "colsNewick": None,
                                                                "colsOrder" : None,
                                                                "colsPng"   : None,
                                                                "colsSvg"   : None
                                                            },
                                                            "rows": {
                                                                "rowsNewick": "null|str[newick]:tree_string",
                                                                "rowsOrder" : [ 'int:row_number' ],
                                                                "rowsPng"   : "null|str[base64]: png_image",
                                                                "rowsSvg"   : "null|str[base64]: svg_image"
                                                            }
                                                        }
                                                    },
        "/api/data/<db_name>/<ref>/<chrom>"      :  {
                                                        "clusters": {
                                                            "str:cluster_name": {
                                                                "cols": {
                                                                    "colsNewick": None,
                                                                    "colsOrder" : None,
                                                                    "colsPng"   : None,
                                                                    "colsSvg"   : None
                                                                },
                                                                "rows": {
                                                                    "rowsNewick": "null|str[newick]:tree_string",
                                                                    "rowsOrder" : [ 'int:row_number' ],
                                                                    "rowsPng"   : "null|str[base64]: png_image",
                                                                    "rowsSvg"   : "null|str[base64]: svg_image"
                                                                }
                                                            }
                                                        },
                                                        "data": {
                                                            "line": [
                                                                [
                                                                    [
                                                                      "float:distance",
                                                                      "int:row_num",
                                                                      "int:col_num"
                                                                    ],
                                                               ]
                                                            ],
                                                            "name": [ "str:ref" ]
                                                        },
                                                        "data_info": {
                                                          "length"        : "int:chromosome_length",
                                                          "length_abs"    : "int:absolute_chromosome_length",
                                                          "maxPos"        : "int:max_pos",
                                                          "maxPosAbs"     : "int:absolute_max_pos",
                                                          "maxVal"        : "float:max_matrix_val",
                                                          "minPos"        : "int:min_pos",
                                                          "minPosAbs"     : "int:absolute_min_pos",
                                                          "minVal"        : "float:min_matrix_val",
                                                          "num_cols"      : "int:num_columns",
                                                          "num_cols_total": "int:total_num_columns",
                                                          "num_rows"      : "int:num_rows"
                                                        },
                                                        "header": {
                                                          "end"        : [ "int:segment_end_pos" ],
                                                          "name"       : [ "str:segment_name" ],
                                                          "num_snps"   : [ "int:num_snps_in_segment" ],
                                                          "num_unities": [ "int:num_entities_in_segment" ],
                                                          "start"      : [ "int:segment_start_pos" ]
                                                        },
                                                        "request": {
                                                          "chrom"   : "str:chomosome",
                                                          "classes" : "null|int:num_classes",
                                                          "endPos"  : "null|int:end_pos",
                                                          "evenly"  : "bool:evenly_split",
                                                          "group"   : "null|int:num_groups",
                                                          "maxNum"  : "null|int:max_num_of_segments",
                                                          "page"    : "null|int:current_page",
                                                          "ref"     : "str:ref",
                                                          "startPos": "null|int:start_pos"
                                                        }
                                                    },
        "/api/help"                              : "str:help_string",
        "/api/example"                           : "str:example_data"
    }

    res = jsonify( { 'api': api } )
    res.headers['Access-Control-Allow-Origin'] = '*'

    return res

@app.route("/api/help", methods=['GET'])
def get_api_help():
    hlp = """\
curl "http://assembly.ab.wurnet.nl:10000/api
LIST OF API METHODS

curl "http://assembly.ab.wurnet.nl:10000/api/example"
EXAMPLE DATA

curl "http://assembly.ab.wurnet.nl:10000/api/dbs"
{
  "databases": [
    "Arabidopsis 50k",
    "Arabidopsis 10k - Chr 4 - Xianwen",
    "Tomato 84 - 10Kb - Introgression",
    "Tomato 84 - 10Kb",
    "Tomato 60 RIL - 50k - RIL mode - Delete",
    "Arabidopsis 10k - Chr 4 - Xianwen - Single",
    "Tomato 84 - 50Kb",
    "Tomato 60 RIL - 50k",
    "Tomato 84 - Genes",
    "Tomato 60 RIL - 10k",
    "Tomato 60 RIL - 50k - RIL mode - Greedy",
    "Tomato 60 RIL - 50k - RIL mode",
    "Arabidopsis 50k - Chr 4 - Xianwen",
    "Tomato 84 - 50Kb - Introgression",
    "Arabidopsis 50k - Chr 4 - Xianwen - Single"
  ]
}


curl "http://assembly.ab.wurnet.nl:10000/api/spps/Arabidopsis%2050k"
{
  "spps": [
    "11C1",
    "7015",
    "8411",
    "Zupan-1",
    "ref"
  ]
}


curl "http://assembly.ab.wurnet.nl:10000/api/chroms/Arabidopsis%2050k"
{
  "chroms": [
    "Chr1",
    "Chr2",
    "Chr3",
    "Chr4",
    "Chr5"
  ]
}


curl "http://assembly.ab.wurnet.nl:10000/api/data/Arabidopsis%2050k/ref/Chr5"
FULL DATA
"""

    resp = Response(
        response=hlp,
        status=200,
        mimetype='text/html'
    )
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/api/example", methods=['GET'])
def get_api_example():
    dbs         = json.loads( get_dbs().data )
    db_name     = dbs['databases'][0]
    maxnumcol   = json.loads( get_max_num_col().data )
    mtime       = json.loads( get_mtime(db_name).data )
    spps        = json.loads( get_spps(db_name).data )
    chroms      = json.loads( get_chroms(db_name).data )
    chrom       = chroms["chroms"][0]
    clusterlist = json.loads( get_cluster_list(db_name).data )
    genes       = json.loads( get_genes(db_name, chrom).data )
    gene        = genes["genes"][0]
    tree        = json.loads( get_tree(db_name, chrom, gene).data )
    alignment   = json.loads( get_aln(db_name, chrom, gene).data )
    matrix      = json.loads( get_matrix(db_name, chrom, gene).data )
    report      = json.loads( get_report(db_name, chrom, gene).data )
    ref         = spps["spps"][0]
    cluster     = json.loads( get_cluster(db_name, ref, chrom).data )
    data        = json.loads( get_data(db_name, ref, chrom).data )

    api = {
        "/api/dbs"                               : dbs,
        "/api/maxnumcol"                         : maxnumcol,
        "/api/mtime/<db_name>"                   : mtime,
        "/api/spps/<db_name>"                    : spps,
        "/api/chroms/<db_name>"                  : chroms,
        "/api/clusterlist/<db_name>"             : clusterlist,
        "/api/genes/<db_name>/<chrom>"           : genes,
        "/api/tree/<db_name>/<chrom>/<gene>"     : tree,
        "/api/alignment/<db_name>/<chrom>/<gene>": alignment,
        "/api/matrix/<db_name>/<chrom>/<gene>"   : matrix,
        "/api/report/<db_name>/<chrom>/<gene>"   : report,
        "/api/cluster/<db_name>/<chrom>/<gene>"  : cluster,
        "/api/data/<db_name>/<chrom>/<gene>"     : data
    }

    #print "DBS", dbs, dir(dbs)
    #for r in dir(dbs):
    #    try:
    #        print " R", r, " = ", getattr(dbs, r)
    #    except:
    #        pass


    res = jsonify( { 'api': api } )
    res.headers['Access-Control-Allow-Origin'] = '*'

    return res


@app.route("/api/spps/<db_name>", methods=['GET'])
def get_spps(db_name):
    """
    Get list of species available to the database
    """
    man  = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    spps = get_spps_raw( man )

    if spps is None:
        print "no species information"
        abort(404)

    if len(spps) == 0:
        print "no species"
        abort(404)

    return jsonify({'spps' : spps})


@app.route("/api/chroms/<db_name>", methods=['GET'])
def get_chroms(db_name):
    """
    Get list of chromosomes available to the database
    """
    man    = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    chroms = get_chroms_raw( man )

    if chroms is None:
        print "no chromosome information"
        abort(404)

    if len(chroms) == 0:
        print "no chromosomes"
        abort(404)

    return jsonify({'chroms': chroms})


@app.route("/api/genes/<db_name>/<chrom>", methods=['GET'])
def get_genes(db_name, chrom):
    """
    Get list of genes available for database/chromosome combination
    """
    man = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    genes = get_genes_raw(man, chrom)

    if genes is None:
        print "no genes information"
        abort(404)

    if len(genes) == 0:
        print "no genes"
        abort(404)

    return jsonify({'genes': genes})


@app.route("/api/tree/<db_name>/<chrom>/<gene>", methods=['GET'])
def get_tree(db_name, chrom, gene):
    """
    Get phylogenetic tree from gene
    """
    man = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    if chrom not in man.getChroms():
        abort( 404 )

    genes = get_genes_raw(man, chrom)

    if genes is None:
        abort(404)

    if gene  not in genes:
        abort(404)

    tree = get_tree_raw(man, chrom, gene)

    if tree is None:
        abort(404)

    try:
        tree['png'] = base64.standard_b64encode( tree['png'] )
    except:
        print "error getting tree png"
        abort(404)

    return jsonify( {'chrom': chrom, 'gene': gene, 'tree': tree } )


@app.route("/api/alignment/<db_name>/<chrom>/<gene>", methods=['GET'])
def get_aln(db_name, chrom, gene):
    """
    Get fasta alignment from gene
    """
    man = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    if chrom not in man.getChroms():
        abort(404)

    genes = get_genes_raw(man, chrom)

    if genes is None:
        print "genes is none"
        abort(404)

    if len(genes) == 0:
        print "no genes"
        abort(404)

    if gene  not in genes:
        print "gene not in genes"
        abort(404)

    aln   = get_aln_raw(man, chrom, gene)

    return jsonify( {'chrom': chrom, 'gene': gene, 'alignment': aln } )


@app.route("/api/matrix/<db_name>/<chrom>/<gene>", methods=['GET'])
def get_matrix(db_name, chrom, gene):
    """
    Ger distance matrix from gene
    """
    man = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    if chrom not in man.getChroms():
        print "chrom",chrom,"not in chroms"
        abort(404)

    genes = get_genes_raw(man, chrom)

    if genes is None:
        print "genes is none"
        abort(404)

    if gene  not in genes:
        print "gene",gene,"not in genes"
        abort(404)

    matrix = get_matrix_raw(man, chrom, gene)

    if matrix is None:
        print "no matrix"
        abort(404)

    return jsonify( {'chrom': chrom, 'gene': gene, 'matrix': matrix } )


@app.route("/api/report/<db_name>/<chrom>/<gene>", methods=['GET'])
def get_report(db_name, chrom, gene):
    """
    Get full report for gene
    """
    man = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    if chrom not in man.getChroms():
        print "chromosome",chrom,"not in chroms"
        abort(404)

    genes  = get_genes_raw(man, chrom)

    if genes is None:
        print "no genes"
        abort(404)

    if gene  not in genes:
        print "gene",gene,"not in genes"
        abort(404)

    #print "getting report", db_name, chrom, gene
    res    = get_report_raw(db_name, man, chrom, gene)
    #print "got report", res
    if res is None:
        print "no report"
        abort(404)

    return jsonify( res )


@app.route("/api/clusterlist/<db_name>", methods=['GET'])
def get_cluster_list(db_name):
    man = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    clusterlist = get_cluster_list_raw(man)
    appendClusterList( man, clusterlist )

    return jsonify(clusterlist)


@app.route("/api/cluster/<db_name>/<ref>/<chrom>", methods=['GET'])
def get_cluster(db_name, ref, chrom):
    """
    Get clustering information
    """
    man = getManager(db_name)

    if man is None:
        print "no such manager"
        abort(404)

    cluster = get_cluster_raw(man, ref, chrom)
    #print cluster
    #if cluster is None:
    #    clusters = get_clusters_raw(man)
    #    if clusters is not None:
    #        if chrom in clusters:
    #            cluster = clusters[ chrom ]

    if cluster is None:
        print "no cluster information"
        abort(404)

    if len(cluster) is None:
        print "no clusters"
        abort(404)

    png  = 'png'  in request.args
    svg  = 'svg'  in request.args
    rows = 'rows' in request.args
    cols = 'cols' in request.args
    lst  = 'lst'  in request.args

    if png or svg:
        print 'png or svg'
        data = cluster['clusters']
        #print 'png or svg', data
        if data is None:
            print "no data"
            abort(404)

        fmt   = 'svg'
        cna   = 'Svg'
        mtype = 'image/svg+xml'
        if png:
            fmt   = 'png'
            cna   = 'Png'
            mtype = 'image/png'

        print 'png or svg: fmt:',fmt,"cna",cna,"mtype",mtype
        rc    = None
        fname = None
        if rows:
            rc = 'rows'
            fname = db_name+'_'+ref+'_'+chrom+'_'+rc+'.'+fmt

        elif cols:
            rc = 'cols'
            fname = db_name+'_'+ref+'_'+chrom+'_'+rc+'.'+fmt

        print 'png or svg: fmt:',fmt,"cna",cna,"mtype",mtype,"rc",rc,"fname",fname


        if rc is not None:
            print "png or svg: rc",rc
            cna   = rc + cna

            if rc not in data:
                print rc,"not in data"
                abort(404)

            if cna not in data[rc]:
                print cna,"not in data",rc
                abort(404)

            rdata = data[rc][cna]
            if rdata is None:
                print "no such data"
                abort(404)

            return send_file(io.BytesIO( rdata ), mimetype=mtype, as_attachment=False, attachment_filename=fname)

        else:
            print 'png or svg: PNG ALL'
            res = {}

            for rc in ['rows', 'cols']:
                if rc not in data:
                    print rc,"not in data"
                    abort(404)
                rcName = rc + cna
                print 'png or svg:', rc, rcName

                if rcName not in data[ rc ]:
                    print "no rcname", rcName
                    abort(404)

                rdata = data[ rc ][ rcName ]
                if rdata is None:
                    print "no such data"
                    abort(404)

                res[rc] = base64.standard_b64encode( rdata )

            return jsonify(res)
    elif lst:
	data = cluster['clusters']
	filterClusters(data, "DEL")
	return jsonify(data)


    else:
        data = cluster['clusters']
        filterClusters(data, "B64")
        return jsonify(data)


@app.route("/api/data/<db_name>/<ref>/<chrom>", methods=['GET'])
def get_data(db_name, ref, chrom):
    man  = getManager( db_name )

    if man is None:
        print "no such manager"
        abort(404)

    data = check_get_data(man, ref, chrom, request)

    if data is None:
        print "no data"
        abort(404)

    (ref, chrom, startPos, endPos, group_every, num_classes, evenly, maxNum, page) = data

    table = get_data_raw(man, ref, chrom, startPos, endPos, group_every, num_classes, evenly, maxNum=maxNum, page=page)

    if table is None:
        print "no table"
        abort(404)

    print "sending table"

    return jsonify(table)


@app.route("/api/mtime/<db_name>", methods=['GET'])
def get_mtime(db_name):
    if db_name not in DATABASEINV:
        abort(404)

    return jsonify( { 'mtime': DATABASES[ DATABASEINV[db_name] ][ DATABASES_MTIME ] } )


@app.route("/api/maxnumcol", methods=['GET'])
def get_max_num_col():
    return jsonify({'maxnumcol': MAX_NUMBER_OF_COLUMNS})


@app.route("/api/dbs", methods=['GET'])
def get_dbs():
    return jsonify( { 'databases': DATABASEINV.keys() } )











def get_spps_raw( man ):
    """
    Retrieve list of species from interface
    """
    sppsinv = man.getSppIndexInvert()

    return sppsinv


def get_chroms_raw( man ):
    """
    Retrieve list of chromosomes from interface
    """
    return sorted( man.getChroms() )


def get_genes_raw(man, chrom):
    """
    Retrieve list of genes from interface
    """
    genes = man.getGenes( chrom )

    return genes


def get_tree_raw(man, chrom, gene):
    """
    Retriece phylogenetic tree from interface
    """
    tree  = man.getTree( gene, chrom )
    return tree


def get_aln_raw(man, chrom, gene):
    """
    Retrieve fasta alignment for gene from interface
    """
    aln   = man.getAlignment( gene, chrom )

    return aln


def get_matrix_raw(man, chrom, gene):
    """
    Retrieve distance matrix for gene from interface
    """
    matrix = man.getMatrix( gene, chrom )

    return matrix


def get_report_raw(db_name, man, chrom, gene):
    """
    Retrieve all information for gene from interface
    """
    dic            = man.getRegisterDict( gene, chrom )
    #print "got report dic", dic

    dic['db_name'] = db_name
    dic['chrom'  ] = chrom
    dic['gene'   ] = gene

    try:
        dic['spps'   ] = get_spps_raw( man )
    except:
        print "no spps"
        abort(404)

    try:
        dic['TREE'   ]['png'] = base64.standard_b64encode( dic['TREE'   ]['png'] )
    except:
        print "error converting tree png"
        abort(404)

    #register[ DB_TREE    ] = { 'newick': tree_str, 'png'   : tree_img  }
    #register[ DB_FASTA   ] = { 'fasta' : snpSeq  , 'coords': coords    }
    #print "DICT",dic
    return dic


def get_cluster_raw(man, ref, chrom):
    res = man.getCluster(chrom       , ref)
    return res


def get_cluster_list_raw(man):
    res = man.getClusterList()
    #print "get_cluster_list_raw", res
    return res


def appendClusters( man, clusters, chrom ):
    gcluster = get_clusters_raw(  man )
    #print 'CLUSTERS', clusters
    #print 'GCLUSTER', gcluster
    if gcluster is not None:
        if chrom in gcluster:
            lcluster = gcluster[ chrom ]
            #print "lcluster chrom %s " % chrom, lcluster
            for lcl in lcluster:
                clusters[ lcl ] = lcluster[ lcl ]

        if '__global__' in gcluster:
            lcluster = gcluster[ '__global__' ]
            #print "lcluster '__global__'", lcluster
            for lcl in lcluster:
                clusters[ lcl ] = lcluster[ lcl ]

    #print "RES CLUSTER", clusters


def appendClusterList( man, clusterlist ):
    gcluster = get_clusters_raw(  man )
    #print 'CLUSTERLIST', clusterlist
    #print 'GCLUSTER   ', gcluster
    if gcluster is not None:
        for chrom in gcluster:
            #print 'GCLUSTER    chrom', chrom
            if chrom not in clusterlist:
                clusterlist[chrom] = {}
            lcluster = gcluster[ chrom ]
            #print "lcluster chrom %s " % chrom, lcluster
            for lcl in lcluster:
                #print "lcluster chrom %s " % chrom, lcluster
                #print 'GCLUSTER    chrom %s lcluster %s' % ( chrom, lcl )
                clusterlist[ chrom ].append( lcl )

    #print "RES CLUSTER LIST:", clusterlist


def get_clusters_raw(  man ):
    res = man.getClusterNames()
    #print 'get_clusters_raw', res
    return res


def check_get_data(man, ref, chrom, request):
    if ref not in man.getSpps():
        print "no such species %s" % ref
        abort(404)

    if chrom not in man.getChroms():
        print "no such chrom %s" % chrom
        abort(404)

    startPos    = request.args.get('startPos', None )
    endPos      = request.args.get('endPos'  , None )
    group_every = request.args.get('group'   , None )
    num_classes = request.args.get('classes' , None )
    evenly      = request.args.get('evenly'  , None )
    maxNum      = request.args.get('maxNum'  , None )
    page        = request.args.get('page'    , None )

    print request.args

    try:
        if startPos    is not None:
            startPos    = int(startPos   )

    except:
        print "no such start pos %s" % startPos
        abort(404)

    try:
        if endPos      is not None:
            endPos      = int(endPos     )

    except:
        print "no such end pos %s" % endPos
        abort(404)

    try:
        if group_every == '':
            group_every = None

        if group_every is not None:
            group_every = int(group_every)
    except:
        print "no such group %s" % group_every
        abort(404)

    try:
        if num_classes == '':
            num_classes = None

        if num_classes is not None:
            num_classes = int(num_classes)
    except:
        print "no such classes %s" % num_classes
        abort(404)

    if evenly is None:
        print 'evenly is None', evenly
        evenly = False

    elif evenly == '':
        print 'evenly is empty', evenly
        evenly = False

    elif evenly == 'false':
        print 'evenly is "false"', evenly
        evenly = False

    elif not evenly:
        print 'evenly is false', evenly
        evenly = False

    else:
        print 'evenly true', evenly
        evenly = True



    try:
        if maxNum == '':
            print 'maxnum not empty', maxNum
            maxNum = None

        elif maxNum is not None:
            maxNum = int(maxNum)

    except:
        print "no such max num %s" % maxNum
        abort(404)



    try:
        if page is not None:
            page = int(page)
    except:
        print "no such page %s" % page
        abort(404)



    #print request.args
    print "every",group_every,'classes',num_classes,'evenly',evenly,'startPos',startPos,'endPos',endPos,'max num',maxNum,'page',page

    return (ref, chrom, startPos, endPos, group_every, num_classes, evenly, maxNum, page)


def get_data_raw(man, ref, chrom, startPos, endPos, group_every, num_classes, evenly, maxNum=None, page=None):
    res =   {
                'request' : {
                    'ref'     : ref,
                    'chrom'   : chrom,
                    'startPos': startPos,
                    'endPos'  : endPos,
                    'group'   : group_every,
                    'classes' : num_classes,
                    'evenly'  : evenly,
                    'maxNum'  : maxNum,
                    'page'    : page
                }
        }

    #if maxNum is None:
        #maxNum = MAX_NUMBER_OF_COLUMNS

    table   = man.make_table(ref, chrom, res, group_every=group_every, num_classes=num_classes, evenly=evenly, startPos=startPos, endPos=endPos, maxNum=maxNum, page=page)

    if table is None:
        print "table is none"
        return table
    print "got table"

    #DELETING IMAGES
    if 'clusters' in table:
        clusters = table['clusters']
        #print "CLUSTERS", clusters
        filterClusters(clusters, "DEL")
        appendClusters( man, clusters, chrom )

    print "RETURNING TABLE"
    #print "TABLE", table

    return table


def filterClusters(data, method):
    #print "cls", data.keys()

    for cls in data:
        #print "cls", cls, "rcS", data[cls].keys()

        for rc in data[cls]:
            #print "cls", cls, "rc", rc, data[cls][rc].keys()

            for rct in ['Png', 'Svg']:
                rctName = rc+rct
                #print "cls", cls, "rc", rc, 'rct', rct, 'rctName', rctName

                if rctName not in data[cls][rc]:
                    print "no rctname in table", cls, rc, rctName
                    continue

                #print "cls", cls, "rc", rc, 'rct', rct, 'rctName', rctName, 'method', method

                if method == "DEL":
                    del data[cls][rc][rctName]
                elif method == "B64":
                    val = data[cls][rc][rctName]
                    if val is not None:
                        data[cls][rc][rctName] = base64.standard_b64encode( val )
                    else:
                        data[cls][rc][rctName] = None

                #print "rc", rc, 'rct', rct, 'rctName', rctName, method, 'FINISHED'

        #for rc in ['rows', 'cols']:
        #    if rc not in data[cls]:
        #        print "no rc",rc,"in table",cls
        #        continue
        #    print "cls", cls,"rc",rc
        #
        #    for rct in ['Png', 'Svg']:
        #        rctName = rc+rct
        #        print "cls", cls,"rc",rc,'rct',rct,'rctName',rctName
        #
        #        if rctName not in data[cls][rc]:
        #            print "no rctname in table",cls,rc
        #            continue
        #
        #        print "cls", cls,"rc",rc,'rct',rct,'rctName',rctName,method
        #
        #        if method == "DEL":
        #            del data[cls][rc][rctName]
        #        elif method == "B64":
        #            data[cls][rc][rctName] = base64.standard_b64encode( data[cls][rc][rctName] )
        #
        #        print "cls", cls,"rc",rc,'rct',rct,'rctName',rctName,method,'FINISHED'


def getManager(db_name):
    if db_name not in DATABASEINV:
        print "db",db_name,"does not exists"
        abort(404)

    return DATABASES[ DATABASEINV[db_name] ][ DATABASES_INTERFACE ]


def init_db():
    """
    Load global/shared database
    """
    global DATABASES


    if len(DATABASES) == 0:
        """
        If no database defined in config.py. quit
        """
        print 'no databases given. please edit config.py'
        sys.exit(1)

    else:
        with app.app_context():
            global loaded
            global DATABASEINV

            print "loading db"
            #g.loaded        = False
            interface.DEBUG = IDEBUG

            DATABASEINV = {}

            #TODO: LOAD ON DEMAND INSTEAD OF HAVING ALL OF THEN AT THE SAME TIME
            for dbp in range(len(DATABASES)):
                """
                Loads each database, get creation date and initialize interface
                """
                db      = DATABASES[dbp]
                dbname  = db[ DATABASES_DB_NAME   ]
                dbfname = db[ DATABASES_DB_F_NAME ]
                dbconf  = db[ DATABASES_DB_CONF   ]

                DATABASEINV[ dbname ] = dbp

                man      = interface.manager()
                man.load_data( dbfname )

                if 'custom_order' in dbconf:
                    custom_orders = dbconf['custom_order']
                    spps = man.getSpps()
                    man.read_custom_orders(custom_orders, spps)

                dbMtime = man.getDbTime()

                db.append( dbMtime )
                db.append( man     )

                #g.loaded        = True
                print DATABASEINV
                print "db loaded"



def load_database():
    global DATABASES
    print "GLOBING", INFOLDER
    files =       glob.glob( os.path.join( INFOLDER, '*.pickle.gz') )
    files.extend( glob.glob( os.path.join( INFOLDER, '*.sqlite'   ) ) )
    #print "GLOBBED", files
    files.sort()

    for db_name in files:
        db_nfo       = db_name + ".nfo"
        db_name_base = db_name

        if  db_name.endswith( '.sqlite' ):
            db_name_base = db_name[:-7]

        elif db_name.endswith( '.pickle.gz' ):
            db_name_base = db_name[:-10]

        db_title     = db_name_base
        db_conf      = {}

        if os.path.exists( db_nfo ):
            db_title, db_conf = read_nfo( db_title, db_nfo, path=INFOLDER )

            if len( db_title ) == 0:
                print "db %s has no title. using file name", db_name
                db_title = db_name_base
        else:
            #print "database %s has no nfo file (%s), skipping" % (db_name, db_nfo)
            print "database %s has no nfo file (%s), using filename" % (db_name, db_nfo)

        DATABASES.append( [db_title, db_name_base, db_conf] )
        print "appending database %s (base %s) with description '%s'" % (db_name, db_name_base, db_title)

    DATABASES.sort(key=itemgetter(0))

    print DATABASES



def read_nfo( db_title, db_nfo, path='.' ):
    print "reading nfo %s title %s" % ( db_nfo, db_title )
    title = db_title
    conf  = {}
    with open( db_nfo, 'r' ) as fhd:
        for line in fhd:
            line = line.strip()
            if len( line ) == 0:
                continue
            if line[0] == "#":
                continue
            elif line.startswith( 'title=' ):
                title = line[6:]
                if len(title) == 0:
                    title = db_title
            elif line.startswith( 'custom_order=' ):
                co_file = line[13:]
                if 'custom_order' not in conf:
                    conf[ 'custom_order' ] = []

                if co_file[0] != '/':
                    co_file = os.path.abspath( os.path.join( path, co_file ) )
                conf[ 'custom_order' ].append( co_file )

    print "read nfo %s title %s res" % ( db_nfo, db_title ), conf

    return ( title, conf )


load_database()
#app.debug = True #DEBUG
app.debug = False #DEBUG
app.debug = DEBUG
app.before_first_request(init_db)


def main():
    app.run(port=SERVER_PORT, host='0.0.0.0')



if __name__ == '__main__':
    main()

else:
    application = app




#    init_classes()
#
#def init_classes():
#    """
#    reads the data from the disk, parses and loads it to global variables.
#    has to be changed if using WSGI servers aroung it (eg. apache) once global variables
#    are not shared.
#    """

    #global data
    #
    #if data is None:
    #    with app.app_context():
    #        print "initializing db"
    #
    #        #data = status.DataManager( db_path=dbPath, ext=pycklerext )
    #
    #        print "db loaded"
    #
    #else:
    #    with app.app_context():
    #        print "updating db"
    #        data.loadlast()
    #        print "db updated"
    #pass
#
#@app.route("/stats", methods=['GET'])
#def get_stats():
#    resp = Response(
#        response=res,
#        status=200,
#        mimetype='text/html'
#    )
#
#@app.route("/raw", methods=['GET'])
#def get_raw():
#    resp = Response(
#        response=jsonpickle.encode( data.get_dict() ),
#        status=200,
#        mimetype='application/json'
#    )
#    return resp

# ===== API TO GETTERS =====
#@app.route("/get/<module>", methods=['GET'])
#def get_module(module):
#    if module in g.modules:
#        return g.modules[ module ]( data, request )
#    else:
#        return abort( 404 )
#def get_mem_all( data, request ):
#    return jsonify( mem_data )
