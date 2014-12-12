//JQUERY EXTENSION
// AUTO COMPLETE COMBOBOX
(function( $ ) {
    $.widget( "custom.combobox", {
        _create: function() {
            this.wrapper = $( "<span>" )
                .addClass( "custom-combobox" )
                .insertAfter( this.element );

            this.element.hide();
            this._createAutocomplete();
            this._createShowAllButton();
        },
    _createAutocomplete: function() {
        var selected = this.element.children( ":selected" ),
            value = selected.val() ? selected.text() : "";
        this.input = $( "<input>" )
            .appendTo( this.wrapper )
            .val( value )
            .addClass( "custom-combobox-input col-lg-3 ui-widget ui-widget-content ui-state-default ui-corner-left" )
            .autocomplete({
                delay: 0,
                minLength: 0,
                source: $.proxy( this, "_source" )
            })
            .attr('title'      , this.element.attr('title'      )) //SAULO. SHOW TOOLTIP
            .attr('placeholder', this.element.attr('placeholder')) //SAULO. SHOW PLACEHOLDER
            .tooltip({
                tooltipClass: "ui-state-highlight"
            });
        this._on( this.input, {
            autocompleteselect: function( event, ui ) {
                ui.item.option.selected = true;
                this._trigger( "select", event, {
                    item: ui.item.option
                });
                //SAULO: ONLY NEEDS TO CHECK FOR THE on select IN THE MAIN SELECT
                this.element.trigger("select");
            },
            autocompletechange: "_removeIfInvalid"
        });
    },
    _createShowAllButton: function() {
        var input = this.input,
        wasOpen = false;
        $( "<a>" )
            .attr( "tabIndex", -1 )
            .attr( "title", "Show All Items" )
            .tooltip()
            .appendTo( this.wrapper )
            .button({
                icons: {
                    primary: "ui-icon-triangle-1-s"
                },
                text: false
            })
            .removeClass( "ui-corner-all" )
            .addClass( "custom-combobox-toggle ui-corner-right" )
            .mousedown(function() {
                wasOpen = input.autocomplete( "widget" ).is( ":visible" );
            })
            .click(function() {
                input.focus();
                // Close if already visible
                if ( wasOpen ) {
                    return;
                }
                // Pass empty string as value to search for, displaying all results
                input.autocomplete( "search", "" );
            });
        },
    _source: function( request, response ) {
        var matcher = new RegExp( $.ui.autocomplete.escapeRegex(request.term), "i" );
        response( this.element.children( "option" ).map(function() {
            var text = $( this ).text();
            if ( this.value && ( !request.term || matcher.test(text) ) ) {
                return {
                    label: text,
                    value: text,
                    option: this
                };
            } else {
                return null;
            }
        }) );
    },
    _removeIfInvalid: function( event, ui ) {
        // Selected an item, nothing to do
        if ( ui.item ) {
            return;
        }
        // Search for a match (case-insensitive)
        var value = this.input.val(),
        valueLowerCase = value.toLowerCase(),
        valid = false;
        this.element.children( "option" ).each(function() {
            if ( $( this ).text().toLowerCase() === valueLowerCase ) {
                this.selected = valid = true;
                return false;
            } else {
                return null;
            }
        });
        // Found a match, nothing to do
        if ( valid ) {
            return;
        }
        // Remove invalid value
        this.input
            .val( "" )
            .attr( "title", value + " didn't match any item" )
            .tooltip( "open" );
        this.element.val( "" );
        this._delay(function() {
            this.input.tooltip( "close" ).attr( "title", "" );
            }, 2500
        );
        this.input.data( "ui-autocomplete" ).term = "";
    },
    _destroy: function() {
        this.wrapper.remove();
        this.element.show();
    }
    });
})( jQuery );
















// GLOBAL VARIABLES
var num_groups   = 30;
var GraphDiv     = "display";
var TreeDiv      = 'wrap';
var db_name      = null;
var H            = Math.round($(window).height() *.99);
var W            = Math.round($(window).width()  *.99);
var maxH         = Math.round(H                  *.95);
var maxW         = Math.round(W                  *.95);



function updateSizes() {
    H            = Math.round($(window).height() *.99);
    W            = Math.round($(window).width()  *.99);
    maxH         = Math.round(H                  *.95);
    maxW         = Math.round(W                  *.95);
}


function showhelp(){
    window.open('/static/help.html', '_blank');
}






var statusKeeper = function(dst, delay) {
    this.dst      = dst;
    this.delay    = delay;
    this.currid   = 0;
};

statusKeeper.prototype.add = function(status, msg) {
    var self     = this;
    self.currid += 1;
    var id       = self.currid;

    $('<p id="lbl_status_'+id+'"><span class="pull-right alert alert-'+status+'">'+msg+'</span></p>')
        .appendTo('#'+self.dst)
        .fadeIn('fast', function() {
            //console.log('statusKeeper present val %o faded in', val);

            setTimeout(function(){
                            //console.log('deleting '+id);
                            $('#'+'lbl_status_'+id).fadeOut('fast').remove();
                        }
                , self.delay);
        });
};

statusKeeper.prototype.clear = function() {
    var self = this;
    $('#'+self.dst).html('');
};




var progressKeeper = function(dst) {
    this.dst     = dst;
    this.create();
};

progressKeeper.prototype.exists = function() {
    if ( $('#'+this.dst).length ) {
        if ( $('#'+this.dst+'_progress').length ) {
            return true;
        }
    }
    return false;
};

progressKeeper.prototype.create = function(val) {
    if ( ! this.exists() ) {
        $('<div>', {'class': 'progress progress-stripped'    , 'id': this.dst+'_progress'    }).appendTo('#'+this.dst);
        this.bar     = $('<div>', {'class': 'progress-bar', 'role': 'progressbar', 'aria-valuenow':0, 'aria-valuemin':0, 'aria-valuemax':100, 'style': 'width:0%;', 'id': this.dst+'_progress_bar'}).appendTo('#'+this.dst+'_progress');
    }
};

progressKeeper.prototype.update = function(val) {
    //console.log('progress update', val);
    var self = this;

    this.create();

    this.show();

    if ( this.exists() ) {
        this.bar.attr('aria-valuenow', val);
        this.bar.attr('style', 'width:'+val+'%;');
    }

    if (val == 100) {
        window.setTimeout(function(){ self.hide(); }, 6000);
    }
};

progressKeeper.prototype.show = function(val) {
    this.create();
    if ( this.exists() ) {
        $('#'+this.dst).show();
    }
};

progressKeeper.prototype.hide = function(val) {
    this.create();
    if ( this.exists ) {
        $('#'+this.dst).hide();
    }
};







//var graphController = function(GraphDiv, TreeDiv, clusterSppChkBox, clusterGenesChkBox ) {
var graphController = function(GraphDiv, TreeDiv) {
    this.GraphDiv            = GraphDiv;

    this.TreeDiv             = TreeDiv;

    //this.clusterSppChkBox    = clusterSppChkBox;

    //this.clusterGenesChkBox  = clusterGenesChkBox;
};


graphController.prototype.clean = function () {
    console.log('cleaning graph memory');
    console.log(this);
    console.log(this.currMatrix);

    if (typeof(this.currMatrix) !== 'undefined') {
        console.log('cleaning graph memory MATRIX');
        this.currMatrix.clean()();
    }

    delete this.spp;
    delete this.chrom;
    delete this.qry;
    delete this.currMatrix;

    this.spp        = null;
    this.chrom      = null;
    this.qry        = null;
    this.currMatrix = null;

    $('#'+this.GraphDiv).html('');

    console.log('memory clean');
};


graphController.prototype.submitDataQuery = function (spp, chrom, qry) {
    var self   = this;

    if (this.spp !== null) {
        this.clean();
    }

    this.spp   = spp;
    this.chrom = chrom;
    this.qry   = qry;


    var href    = '/data/' + db_name + '/' + this.spp + '/' + this.chrom + '?' + $.param(this.qry);
    console.log(this.qry);
    console.log('getting data from url: ' + href);

    $('#'+this.GraphDiv)           .html('');
    //$('#'+this.clusterSppChkBox   ).hide();
    //$('#'+this.$clusterGenesChkBox).hide();

    this.changeStatus('warning','<span class="glyphicon glyphicon-arrow-down">Downloading '+href+'</span>');
    this.progresser(0);

    console.log('getting data');

    (function(hr, fc){
        $.ajax({
            url     : hr,
            success : fc,
            dataType: "text"
        });
    })(href, self.loadData());

    console.log('request sent %o', this.qry);
};


graphController.prototype.getReport = function () {
    var self = this;
    return function (chrom, gene) {
        console.log('requesting report chrom %s gene %s', chrom, gene);
        $.getJSON('/report/'+db_name+'/'+chrom+'/'+gene, self.loadReport());
    };
};


graphController.prototype.getReportGene = function () {
    var self = this;
    return function (gene) {
        var chrom = self.chrom;
        console.log('requesting report gene %s', chrom, gene);
        self.getReport()(chrom, gene);
    };
};


graphController.prototype.loadReport = function () {
    var self = this;

    return function(data) {
        console.log('got report data %o', data);

        updateSizes();

        //TREE DIV
        var $TreeDiv = $('<div>'      , { 'class': 'tree'   , 'id': self.TreeDiv+'_tree'  } ).appendTo('#'+self.TreeDiv);
        //$('#'+TreeDiv).dialog({ autoOpen: false, 'maxWidth': maxW, 'width': maxW, 'maxHeight': maxH, 'height': maxH });


        $TreeDiv.dialog({
            'autoOpen': false,
            'maxWidth': maxW,
            'width': maxW,
            'maxHeight': maxH,
            'height': maxH,
            'close': function() {
                $TreeDiv.dialog("destroy");
                $TreeDiv.remove();
            }
        });


        $TreeDiv.html('');

        $TreeDiv.html('<span class="label label-warning lblstatus" id="lbl_status">Processing</span>');

        console.log('separating data');

        var start   = data['START'  ];
        var end     = data['END'    ];
        var name    = data['NAME'   ];
        var lenObj  = data['LEN_OBJ'];
        var lenSnp  = data['LEN_SNP'];
        var gene    = data['gene'   ];
        var chrom   = data['chrom'  ];

        var spps    = data['spps'   ];
        var matrix  = data['LINE'   ];

        var treeStr = data['TREE'   ];

        var aln     = data['FASTA'  ];


        $('<table>', { 'class': 'table table-stripped table-condensed reportTable', 'id': 'reportTable' }).appendTo($TreeDiv);

        var rtable  = $('#reportTable');

        var pairs = [
                        [ 'Start'      , start   ],
                        [ 'End'        , end     ],
                        [ 'Name'       , name    ],
                        [ '# Objects'  , lenObj  ],
                        [ '# SNPs'     , lenSnp  ],
                        [ 'Object Name', gene    ],
                        [ 'Chromosome' , chrom   ],
                    ];

        var trs     = new Array(pairs.length + 3);

        for ( ppos = 0; ppos < pairs.length; ++ppos ) {
            var pval = pairs[ppos];
            trs[ppos] = $('<tr>', {'class': 'reportLine'})
                            .append( $('<td>', { 'class': 'reportCell reportHeader' }).html( pval[0] ) )
                            .append( $('<td>', { 'class': 'reportCell reportVal'    }).html( pval[1] ) );
        }

        var treeDst   = 'treeDst';
        var matrixDst = 'matrixDst';
        var alnDst    = 'alignmentDst';

        trs[pairs.length + 0] = $('<tr>', {'class': 'reportLine'}).append( $('<td>', { 'class': 'reportCell reportHeader' }).html('Tree'     ) ).append( $('<td>', { 'class': 'reportCell reportVal' }).append( $('<div>', { 'id': treeDst   } ) ) );
        trs[pairs.length + 1] = $('<tr>', {'class': 'reportLine'}).append( $('<td>', { 'class': 'reportCell reportHeader' }).html('Alignment') ).append( $('<td>', { 'class': 'reportCell reportVal' }).append( $('<div>', { 'id': alnDst    } ) ) );
        trs[pairs.length + 2] = $('<tr>', {'class': 'reportLine'}).append( $('<td>', { 'class': 'reportCell reportHeader' }).html('Matrix'   ) ).append( $('<td>', { 'class': 'reportCell reportVal' }).append( $('<div>', { 'id': matrixDst } ) ) );

        rtable.append(trs);

        self.showTree(      { 'chrom': chrom, 'gene': gene, 'tree': treeStr}, treeDst);
        self.showMatrix(    chrom, gene, spps, matrix, matrixDst );
        self.showAlignment( chrom, gene, spps, aln   , alnDst    );

        $('#lbl_status').remove();

        $TreeDiv.dialog('open');
    };
};


graphController.prototype.getTree = function ( request, cname ) {
    var self     = this;

    var evenly   = request[ 'evenly'  ] || null;
    var every    = request[ 'every'   ] || null;
    var nclasses = request[ 'nclasses'] || null;
    var chrom    = request[ 'chrom'   ] || null;


    if ( (!evenly)  && every === null && nclasses === null ) {
        var href = '/tree/'+db_name+'/'+chrom+'/'+cname;
        console.log('getting tree: '+href);
        $.getJSON(href, this.showTreePopUp);

    } else {
        var actstr = ""
        if ( evenly            ) { actstr += ' evenly' };
        if ( every    !== null ) { actstr += ' every ' + every    + ' bp'      };
        if ( nclasses !== null ) { actstr += ' in '    + nclasses + ' classes' };
        alert('I can only show tree without concatenations (evenly, every or classes). Currently you have '+actstr+' active');
    }
};


graphController.prototype.showTreePopUp = function (treeData){
    this.showTree(treeData, this.TreeDiv);
    console.log('opening');

    var $TreeDiv            = $('#'+this.TreeDiv+'_tree');

    $TreeDiv.dialog('open');
};


graphController.prototype.showTree = function (treeData, dst){
    var self    = this;

    console.log('showing tree');

    var chrom   = treeData['chrom'];
    var gene    = treeData['gene' ];
    var treeStr = treeData['tree' ];

    var $dst    = $('#'+dst);

    $dst.html('');

    $('<div>', {'id': 'tree_render'}).appendTo($dst);


    //Smits.PhyloCanvas.Render.Style['text']['font-size'] = 10;
    //Smits.PhyloCanvas.Render.Style['Rectangular']['bufferX'] = 200;
    console.log('creating');
    //console.log(treeStr);
    updateSizes();
    var phylocanvas = new Smits.PhyloCanvas(
        {'newick': treeStr}, // Newick or XML string
        'tree_render',       // div id where to render
        maxH * 1.0,          // height, in pixels
        maxW * 0.7,          // width in pixels
        'rectangular'
        //'circular'
    );
    console.log('created');

    console.log('adding data');
    $('#tree_render').data('phylo', phylocanvas);

    var nfile  = chrom+'_'+gene+'.newick';
    $('<a>', {'ofile': nfile}).data('src', treeStr).data('filetype', "text/plain"  ).text('Download Newick').click(this.downloadData).insertAfter('#tree_render');

    var ofile  = chrom+'_'+gene+'.svg';
    var svgSrc = phylocanvas.getSvgSource();
    $('<a>', {'ofile': ofile}).data('src', svgSrc).data('filetype', "image/svg+xml").text('Download SVG'   ).click(this.downloadData).insertAfter('#tree_render');
};


graphController.prototype.downloadData = function () {
    var ofile     = $(this).data('ofile'   );
    var dataobj   = $(this).data('src'     );
    var datatype  = $(this).data('filetype');

    var blob      = new Blob([dataobj], {type: datatype});
    saveAs(blob, ofile);
};


graphController.prototype.showMatrix = function (    chrom, gene, spps, matrix, matrixDst ) {
    var self = this;
    var $dst = $('#'+matrixDst);
    var $tbl = $('<table>', { 'class': 'matrixTable' }).appendTo($dst);
    //console.log(spps);
    //console.log(matrix);

    $.each( spps, function (k,v) {
        //console.log('matrix k '+k+' v '+v);
        var $tr  = $('<tr>', {'class': 'matrixLine'             }).appendTo($tbl);
        $tr.append($('<td>', {'class': 'matrixCell matrixHeader'}).append(v));

        $.each( matrix[k], function (l,col) {
            if ( l == k ) {
                $td = $('<td>', {'class': 'matrixCell matrixVal matrixDiagonal'}).append(col).appendTo($tr);

            } else if ( l > k ) {
                $td = $('<td>', {'class': 'matrixCell matrixVal matrixParallel'}).append(col).appendTo($tr);

            } else {
                $td = $('<td>', {'class': 'matrixCell matrixVal matrixMain'    }).append(col).appendTo($tr);
            }
            //console.log('aln '+k+' v '+v);
        });
    });

    var nfile  = chrom+'_'+gene+'.matrix';
    $('<a>', {'ofile': nfile}).data('src', matrix).data('filetype', "text/plain").text('Download Matrix').click(self.downloadData).insertAfter($dst);
};


graphController.prototype.showAlignment = function ( chrom, gene, spps, aln, alnDst ) {
    var self = this;
    var $dst = $('#'+alnDst);
    var $tbl = $('<table>', { 'class': 'alignmentTable'}).appendTo($dst);

    $.each( spps, function (k,v) {
        var seq  = aln[v];
        //console.log('aln    k '+k+' v '+v+' seq '+seq);
        var $tr  =  $('<tr>', { 'class': 'alignmentCell alignmentLine'         })
            .append($('<td>', { 'class': 'alignmentCell alignmentHead'         }).append(v  ))
            .append($('<td>', { 'class': 'monospace alignmentCell alignmentVal'}).append(seq))
            .appendTo($tbl);
        //console.log('aln '+k+' v '+v);
    });

    $('.alignmentVal').each(function(){
        var message = $(this).html();
        var chars   = new Array( message.length );
        for (var i  = 0; i < message.length; i++) {
            var mchar = message[i];
            chars[i] = "<div class='dnaNuc dna"+mchar+"'>" + mchar + "</span>";
        }
        $(this).html(chars);
    });


    var nfile  = chrom+'_'+gene+'.fasta';
    $('<a>', {'ofile': nfile}).data('src', aln).data('filetype', "text/plain").text('Download Alignment').click(self.downloadData).insertAfter($dst);
};


graphController.prototype.loadData = function () {
    var self = this;

    return function(data) {
        console.log('got data');
        console.log('parsing');

        var dataP = JSON.parse(data);

        console.log('parsed');

        console.log('separating data %o', dataP);


        self.changeStatus('info','<span class="glyphicon glyphicon-cog">Processing</span>');
        self.progresser( 25);


        var request        = dataP['request'  ];
        var header         = dataP['header'   ];
        var data_line      = dataP['data'     ];
        var data_info      = dataP['data_info'];

        var resStr   =  'Start: '          + data_info.minPos         +
                        ' bp (min '        + data_info.minPosAbs      +
                        ' bp) End: '       + data_info.maxPos         +
                        ' bp (max '        + data_info.maxPosAbs      +
                        ' bp) min value: ' + data_info.minVal         +
                        ' max value: '     + data_info.mazVal         +
                        ' species: '       + data_info.num_rows       +
                        ' unities: '       + data_info.num_cols       +
                        ' (out of '        + data_info.num_cols_total +
                        ')';

        self.changeStatus('info', '<span class="glyphicon glyphicon-pushpin">Result: '+resStr+'</span>');
        self.progresser( 27);

        var qryStr   = '';

        if (   request.evenly            ) { qryStr += ' evenly;'                                };
        if (   request.every    !== null ) { qryStr += ' every ' + request.every   + ' bp;'      };
        if (   request.classes  !== null ) { qryStr += ' in '    + request.classes + ' classes;' };

        self.changeStatus('info', '<span class="glyphicon glyphicon-pushpin">Query: '+qryStr+'</span>');
        self.progresser( 29);

        var cfg = {
            'header': {
                line_starts    : header[    'start'          ],
                line_ends      : header[    'end'            ],
                line_unities   : header[    'num_unities'    ],
                line_snps      : header[    'num_snps'       ],
                line_names     : header[    'name'           ],
            },
            'data':{
                ddata          : data_line[ 'line'           ],
                dnames         : data_line[ 'name'           ],
            },
            'info': {
                dminPos        : data_info[ 'minPos'         ],
                dmaxPos        : data_info[ 'maxPos'         ],
                dminPosAbs     : data_info[ 'minPosAbs'      ],
                dmaxPosAbs     : data_info[ 'maxPosAbs'      ],
                dmin           : data_info[ 'minVal'         ],
                dmax           : data_info[ 'maxVal'         ],
                num_rows       : data_info[ 'num_rows'       ],
                num_cols       : data_info[ 'num_cols'       ],
                num_cols_total : data_info[ 'num_cols_total' ],
                qryStr         : qryStr,
                resStr         : resStr
            },
            'request': {
                evenly         : request[   'evenly'         ],
                group          : request[   'group'          ],
                classes        : request[   'classes'        ],
                chrom          : request[   'chrom'          ],
                ref            : request[   'ref'            ],
                maxNum         : request[   'maxNum'         ],
                page           : request[   'page'           ],
            }
        };

        //cfg.info.maxNumDefault = $('#maxNumber').data('maxNumberDefault');

        console.log('request     %o', request      );
        console.log('header      %o', header       );
        console.log('data nfo    %o', data_info    );
        console.log('data line   %o', data_line    );


        console.log('adding structures');


        self.currMatrix = (function(GD, cf, cs, pr, rg) {
            var cm = new plotSVG(   GD, cf);

            cm.changeStatus = cs;
            cm.progresser   = pr;
            cm.onClick      = rg;

            cm.init();
            //currMatrix = new Worker('custom_svg.js');
            //new plotSVG(   GraphDiv, cfg );
            //currMatrix.postMessage({'data': {'propertyName': 'start', 'GraphDiv':GraphDiv, 'cfg':cfg}});
            return cm;
        })(self.GraphDiv, cfg, self.changeStatus, self.progresser, self.getReportGene());



        console.log('geting clustering');
        var href2   = '/cluster/' + db_name + '/' + self.spp + '/' + self.chrom + '?' + $.param(self.qry);
        (function(hr, fc){
            $.getJSON(hr, fc);
        }(href2, self.loadCluster()));

        console.log('cleaning memory');
        data         = null;
        dataP        = null;
/*        request      = null;
        cfg          = null;
        header       = null;
        data_line    = null;
        data_info    = null*/;
        console.log('finished');

        //http://www.designchemical.com/blog/index.php/jquery/jquery-tutorial-create-a-flexible-data-heat-map/

        //var data  = data_line['line'];
        //var cline = [];
        //for ( var r=0; r<data.length; r++ ){
        //    var cols = data[r];
        //    var line = [];
        //    for (var c=0; c<cols.length; c++) {
        //        var v = cols[c][0];
        //        line.push(v);
        //    }
        //    cline.push(line);
        //}
        //var root = figue.agglomerate(data_line['name'], cline, figue.EUCLIDIAN_DISTANCE,figue.AVERAGE_LINKAGE);
        ////console.log(data_line['name']);
        //////console.log(cline);
        //console.log(root);
        //console.log(root.toString());
    };
};


graphController.prototype.loadCluster  = function () {
    var self = this;

    return function(data) {
        console.log('got cluster');

        if (! self.currMatrix) { return; };

        console.log('got cluster. appending');

        //$('#'+self.clusterSppChkBox  ).show();
        //$('#'+self.clusterGenesChkBox).show();

        console.log('got cluster %o', data);
        self.changeStatus('info', '<span class="glyphicon glyphicon-ok">Got clustering</span>');
        self.progresser(98);

        (function(data) {
            self.currMatrix.appendClustering(data);
        })(data);

        self.changeStatus('success', '<span class="glyphicon glyphicon-ok">Finished</span>');

        self.progresser(100);
    };
};


graphController.prototype.mapColor     = function ( color       ) { if (! this.currMatrix) { console.log('no matrix'); return; }; this.currMatrix.mapColor(     color ); };
graphController.prototype.showHeader   = function ( val         ) { if (! this.currMatrix) { console.log('no matrix'); return; }; this.currMatrix.showHeader(   val   ); };
graphController.prototype.showSpecies  = function ( val         ) { if (! this.currMatrix) { console.log('no matrix'); return; }; this.currMatrix.showSpecies(  val   ); };
graphController.prototype.clusterSpp   = function ( val         ) { if (! this.currMatrix) { console.log('no matrix'); return; }; this.currMatrix.clusterSpp(   val   ); };
graphController.prototype.clusterGenes = function ( val         ) { if (! this.currMatrix) { console.log('no matrix'); return; }; this.currMatrix.clusterGenes( val   ); };
graphController.prototype.changeStatus = function ( status, msg ) { console.log(status); console.log(msg); };
graphController.prototype.progresser   = function ( val         ) { console.log(val   );                   };




var control      = {};


$(document).ready(function(){
    //FUNCTIONS

    var progresser   = new progressKeeper('progress_row');

    var statuser     = new statusKeeper('status_row', 4500);
    var changeStatus = statuser.add;


    $(document).on('keyup',      'input.numbersOnly'      , function(){
        this.value = this.value.replace(/[^0-9]/g,'');
    });

    //$('#sel_gene').combobox();

    return;
    graphController.prototype.changeStatus = function(a,b) { statuser.add(a,b);   };
    graphController.prototype.progresser   = function(v  ) { progresser.update(v) };

    //FORMATING DIVS
    $('<div>'       , { 'class': 'row col-lg-12'           , 'id': 'main_row'     } ).appendTo('#wrap'       );

    $('<div>'       , { 'class': 'row col-lg-12'           , 'id': 'main_col'     } ).appendTo('#main_row'   );

    $('<div>'       , { 'class': 'row col-lg-12'           , 'id': 'head_row_1'   } ).appendTo('#main_col'   );
    $('<div>'       , { 'class': 'row col-lg-12'           , 'id': 'head_row_2'   } ).appendTo('#main_col'   );

    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_1_1' } ).appendTo('#head_row_1' );
    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_2_1' } ).appendTo('#head_row_2' );

    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_1_2' } ).appendTo('#head_row_1' );
    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_2_2' } ).appendTo('#head_row_2' );

    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_1_3' } ).appendTo('#head_row_1' );
    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_2_3' } ).appendTo('#head_row_2' );

    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_1_4' } ).appendTo('#head_row_1' );
    $('<div>'       , { 'class': 'row col-lg-3'            , 'id': 'head_row_2_4' } ).appendTo('#head_row_2' );

    $('<div>'       , { 'class': 'row col-lg-12 progress-g', 'id': 'progress_row' } ).appendTo('#main_row'   );
    $('<div>'       , { 'class': 'row col-lg-12'           , 'id': 'graph_col'    } ).appendTo('#main_row'   );




    //DYNAMIC SELECTS
    $('<select>'    , { 'class': 'sel col-lg-3 form-control input-sm'            , 'id': 'sel_spp'      } )
    .attr('title', 'Species for reference')
    .appendTo('#head_row_1_1');

    $('<select>'    , { 'class': 'sel col-lg-3 form-control input-sm'            , 'id': 'sel_chr'      } )
    .attr('title', 'Chromosome'           )
    .appendTo('#head_row_1_2');

    $('<select>'    , { 'class': 'sel col-lg-3 form-control input-sm'            , 'id': 'sel_gene', 'disabled': true} )
    .attr('title'      , 'Select a Individual Gene to Visualize' )
    .attr('placeholder', 'Select a Individual Gene'              )
    .appendTo('#head_row_1_3');




    //SELECT CLUSTERING
    var clusterSel   = $('<select>'     , { 'class': 'sel input-sm form-control col-lg-3'                   , 'id': 'sel_cluster', 'tgt' : 'clusterVal',                                                'title': 'Clustering by N base pairs, N groups or evenly distributed' }).appendTo('#head_row_2_1');
    var clusterInput = $('<input>'      , { 'class': 'inp input-sm form-control col-lg-3 numbersOnly number', 'id': 'clusterVal' , 'type': 'text', 'placeholder': 'clustering value', 'disabled': true, 'title': 'Clustering Value'}).appendTo('#head_row_2_2');
    var opts         =  [
                            ['- Group by -'      , 'none'   ],
                            ['Group by N bp'     , 'group'  ],
                            ['Group by N classes', 'classes'],
                            ['Group evenly'      , 'evenly' ]
                        ];
    for (var oindex  = 0; oindex < opts.length; ++oindex) {
        var optName  = opts[oindex][0];
        var optVal   = opts[oindex][1];
        var divBtnLi = $('<option>', { 'class': 'clusteropt', 'value': optVal })
                        .text(optName)
                        .appendTo(clusterSel);
    }



    //BUTTON
    $('<input>'    , { 'class': 'btn btn-primary btn-block ', 'id': 'btn_send', 'type': 'button' } ).val('Send').appendTo('#head_row_2_3');
    $('#btn_send'       ).attr('title', 'Send Query');


    $('<i>'        , { 'class': 'glyphicon glyphicon-question-sign' , 'title': 'Help'                }).click(showhelp).appendTo( '#head_row_2_4' );

    $('<span>'     , { 'class': ''                                  , 'id': 'status_row'             }).appendTo( '#head_row_3_4' );


    //RESPONSE DIV
    $('<div>'      , { 'class': 'display', 'id': GraphDiv } ).appendTo('#graph_col');





    //GLOBAL SELECTORS
    $(document).on('change',     '#sel_chr'          , function(){
        var sel = $(this).val();

        console.log('selected chromosome '+sel);

        $.getJSON('/genes/'+db_name+'/'+sel, function(data) {
            var selg = $('#sel_gene')
                .attr('disabled', true)
                .data('chrom'   , sel )
                .html('')
                .combobox();

            //selg.append($('<option>').attr('value', "").text("Select one..."));

            $.each(data['genes'], function() {
                selg.append($('<option>').attr('value', this).text(this));
            });

            $(selg).attr('disabled', false);
        });
    });


    $(document).on('select',     '#sel_gene'         , function(){
        var gene  = $(this).val();
        var chrom = $(this).data('chrom');

        console.log('selected gene '+gene+' for chrom '+chrom);

        if (!control.graphControl) {
            (
                //function(div1,div2,div3,div4,sp,ch,qr) {
                function(div1,div2,sp,ch,qr) {
                    delete control.graphControl;
                    //control.graphControl = new graphController(div1,div2,div3,div4);
                    control.graphControl = new graphController(div1,div2);

                    //control.graphControl.submitDataQuery(sp,ch,qr);
                }
            //)(GraphDiv,TreeDiv,'lab_clusterspp','lab_clustergenes',spp, chrom, qry);
            )(GraphDiv,TreeDiv,null, chrom, null);
        }

        (function(ch,ge){
            control.graphControl.getReport()(ch,ge);
        })(chrom, gene);
    });


    $(document).on('change',     '#sel_cluster'      , function(){
        var opt = $(this).val();
        var tgt = $(this).attr('tgt'  );

        console.log('selected option '+opt+' target '+tgt);

        if ((opt == 'evenly') || (opt == 'none')){
            $('#'+tgt).attr('disabled', true);
        }else{
            $('#'+tgt).attr('disabled', false);
        }
    });






    $(document).on('click',      'input#btn_send', function(){
        var spp          = $('#sel_spp'    ).val();
        var chrom        = $('#sel_chr'    ).val();
        var clusterType  = $('#sel_cluster').val();
        var clusterVal   = $('#clusterVal' ).val();

        $('#'+GraphDiv).html('');

        statuser.clear();

        var qry          = { 'page': 0 };

        if ($('#maxNumber'  ).length) {
            var maxnumVal    = $('#maxNumber'  ).val();
            var maxnumValDfl = $('#maxNumber'  ).data('maxNumberDefault');
            if ( maxnumVal != maxnumValDfl ) {
                qry['maxNum'] = maxnumVal;
            } else {
                qry['maxNum'] = maxnumValDfl;
            }
        } else {
            qry['maxNum'] = null;
        }

        if ( clusterType != 'none'   )
        {
            qry[clusterType] = clusterVal;
        };

        console.log(qry);




        (
            //function(div1,div2,div3,div4,sp,ch,qr) {
            function(div1,div2,sp,ch,qr) {
                delete control.graphControl;
                //control.graphControl = new graphController(div1,div2,div3,div4);
                control.graphControl = new graphController(div1,div2);

                //$('#clean').click(
                //    function() {
                //        (
                //            function () {
                //                if (control.graphControl) {
                //                    control.graphControl.clean();
                //                    $('#clean').unbind('click');
                //                };
                //            }
                //        )();
                //    }
                //);

                control.graphControl.submitDataQuery(sp,ch,qr);
            }
        //)(GraphDiv,TreeDiv,'lab_clusterspp','lab_clustergenes',spp, chrom, qry);
        )(GraphDiv,TreeDiv,spp, chrom, qry);
    });



    $.getJSON('/dbs'  , function(data) {
        var sel = $('#database');
        sel.html('');

        var dbSel = $('<select>', { 'class': 'sel', 'id': 'sel_database', 'tgt' : 'clusterVal', 'title': 'Choose database' }).appendTo( sel );
        dbSel.append($('<option>').data('value', null).text('-select one database-'));

        console.log(data);

        $.each(data['databases'], function() {
            dbSel.append($('<option>').data('value', this).text(this));
        });
    });



    $(document).on('change',     '#sel_database'      , function(){
        var opt = $(this).val();
        var tgt = $(this).attr('tgt'  );

        console.log('selected option '+opt+' target '+tgt);

        db_name = opt;

        if ( db_name == '-select one database-') {
            db_name = null;
        }

        if (db_name) {
            clearSelectors();
            updateSelectors();
        } else {
            clearSelectors();
        }
    });

    function clearSelectors() {
        $('#sel_spp').html('');
        $('#sel_chr').html('');
        $('#dbmtime').html('');
    }

    function updateSelectors() {
        if ( typeof(db_name) != null ) {
            //LOADING DATA
            $.getJSON('/spps/'+db_name  , function(data) {
                var sel = $('#sel_spp');
                $.each(data['spps'], function() {
                    sel.append($('<option>').data('value', this).text(this));
                });
            });


            $.getJSON('/chroms/'+db_name, function(data) {
                var sel = $('#sel_chr');
                $.each(data['chroms'], function() {
                    sel.append($('<option>').data('value', this).text(this));
                });
                $(sel).trigger('change');
            });


            $.getJSON('/mtime/'+db_name, function(data) {
                console.log('mtime '+data)
                $('#dbmtime').html(data['mtime']);
            });
        }
    }


    $.getJSON('/username', function(data) {
        console.log('username '+data)
        $('#username').html(data['username']);
    });


    $.getJSON('/maxnumcol', function(data){
        var val = data['maxnumcol'];
        $('#maxNumber').val( val ).data('maxNumberDefault', val);
    });

    //setTimeout( function() { statuser.add('info', 'Welcome');                      },  3000);
    //setTimeout( function() { statuser.add('info', 'Please select reference');      },  6000);
    //setTimeout( function() { statuser.add('info', 'Please select chromosome');     },  9000);
    //setTimeout( function() { statuser.add('info', 'Please select grouping (opt)'); }, 12000);
    //setTimeout( function() { statuser.add('info', 'And click send');               }, 15000);
    //
    //setTimeout( function() { progresser.update( 25); },  3000);
    //setTimeout( function() { progresser.update( 50); },  6000);
    //setTimeout( function() { progresser.update( 75); },  9000);
    //setTimeout( function() { progresser.update(100); }, 12000);

    //$('#lab_clusterspp'  ).hide();
    //$('#lab_clustergenes').hide();
});
