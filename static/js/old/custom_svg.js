//height of each row in the heatmap
//var h = 5;
//width of each column in the heatmap
//var w = 5;
//var currMatrix = null;
//onmessage = function (event) {
//    var data = event.data.data;
//    var name = data.propertyName;
//
//    console.log('ON MESSAGE');
//    console.log(event);
//    console.log(name);
//    console.log(data);
//    console.log(data.GraphDiv);
//    console.log(data.cfg);
//
//    if ( name == 'start') {
//        currMatrix = plotSVG(event.data.GraphDiv, event.data.cfg);
//    }
//    if (currMatrix) {
//        if ( name == 'mapColor') {
//            currMatrix[name]( data.color );
//        }
//        else if ( name == 'showHeader') {
//            currMatrix[name]( data.val );
//        }
//        else if ( name == 'showSpecies') {
//            currMatrix[name]( data.val );
//        }
//        else if ( name == 'clusterSpp') {
//            currMatrix[name]( data.val );
//        }
//        else if ( name == 'clusterGenes') {
//            currMatrix[name]( data.val );
//        }
//    }
//
//    return;
//};

var plotSVG = function (OUTdiv, cfg) {
    console.log('plotting svg to %s', OUTdiv);
    var self = this;

    var el = document.getElementById(OUTdiv);
    el.innerHTML = '';

    this.divSlider = '#'+OUTdiv+'_slider';
    this.SVGdiv    = '#'+OUTdiv+'_graph';

    d3.select('#'+OUTdiv)
        .append('div')
            .attr('id', OUTdiv+'_slider')
    ;

    d3.select('#'+OUTdiv)
        .append('div')
            .attr('id', OUTdiv+'_graph')
            .style('overflow-x', 'hidden')
    ;


    this.cfg       = cfg;

    this.cfg.opts    = {
        paddingLeft :    0,
        paddingTop  :    0,
        cellWidth   :  0.5,
        cellHeight  :  0.5,
        fontHeight  : '1.5',
        scaleSplits :   10,
        scaleHeight :    2,
        labelHeight :  1.2
    };

    this.order = {
        rows: [
                Array.apply(null, Array(this.cfg.info.num_rows)).map(function(_,i){return i;}),
                //this.cfg.cluster.rows.rowsOrder
              ],
        cols: [
                Array.apply(null, Array(this.cfg.info.num_cols)).map(function(_,i){return i;}),
                //this.cfg.cluster.cols.colsOrder
              ],

        currRow: 0,

        currCol: 0
    };

    this.isShowingHeader     = false;
    this.isShowingSpecies    = false;
    this.isClusteringSpecies = false;
    this.isClusteringGenes   = false;


    console.log('DIV %s CFG %o', OUTdiv, cfg);
};

plotSVG.prototype.clean = function() {
    var self = this;

    return function() {
        console.log('cleaning svg');
        self.mySVGdiv
            .selectAll("rect")
                .data([])
                .on('click', null)
                .exit()
                .remove()
        ;

        self.mySVGdiv
            .selectAll('text')
                .data( [] )
                .exit()
                .remove()
        ;

        self.mySVGdiv
            .selectAll('g')
                .data( [] )
                .exit()
                .remove()
        ;

        self.mySVGdiv
            .selectAll('svg')
                .data( [] )
                .exit()
                .remove()
        ;

        self.heatmapRows
            .selectAll(".matrixrow")
            .data( [] )
            .exit()
            .remove()
        ;

        self.heatmapRects
            .selectAll("rect")
            .data([])
            .exit()
            .remove()
        ;

        self.myRowLabel
            .selectAll('.matrixheaderrowcell')
            .data( [] )
            .exit()
            .remove()
        ;

        self.myHeaderCol
            .selectAll('.matrixheadercolcell')
            .data( [] )
            .exit()
            .remove()
        ;

        self.myHeaderCol
            .selectAll('g')
            .remove();

        //$('#sliderW').remove();
        d3.select('#sliderW').remove();

        self.mySVGdiv.remove();
        self.myScaleLbl.remove();
        self.myScale.remove();
        self.mySVG.remove();
        self.myRows.remove();
        self.heatmapRow.remove();
        self.myRowLabel.remove();
        self.myHeaderCol.remove();
        self.heatmapRects.remove();
        self.heatmapRows.remove();

        delete self.order;
        delete self.slsW;
        delete self.myScaleLbl;
        delete self.myScale;
        delete self.mySVG;
        delete self.myRows;
        delete self.heatmapRow;
        delete self.heatmapRowG;
        delete self.heatmapRows;
        delete self.myRowLabel;
        delete self.rowsNames;
        delete self.myHeaderCol;
        delete self.heatmapRects;

        delete self.cfg.header;
        delete self.cfg.data;
        delete self.cfg.info;
        delete self.cfg.request;
        delete self.cfg;

        delete self.SVGdiv;
        delete self.divSlider;
        delete self.colorScale;
        delete self.expLab;
        delete self.myHeader;
        delete self.myHeaderCol;
        delete self.myHeaderRowCol;
        delete self.myRowLabel;
        delete self.myRows;
        delete self.myScale;
        delete self.mySVG;

        d3.select( self.SVGdiv ).remove();

        delete self.mySVGdiv;
        delete self.myGlobal;
    };
};

plotSVG.prototype.init = function() {
    //attach a SVG element to the document's body
    var self = this;


    this.changeStatus('info', '<span class="glyphicon glyphicon-picture">Plotting</span>');
    this.progresser(30);

    this.myGlobal = d3.select( this.SVGdiv );

    //console.log( this.mySVGdiv );

    this.width  = (self.cfg.opts.cellWidth  * self.cfg.info.num_cols) + self.cfg.opts.paddingLeft;
    this.height = (self.cfg.opts.cellHeight * self.cfg.info.num_rows) + self.cfg.opts.paddingTop ;

    this.mySVGdiv = this.myGlobal
        .append('svg')
            .attr("version"    , "1.2"                        )
            //.attr("xmlns"      ,"http://www.w3.org/2000/svg"  )
            //.attr("xmlns:xmlns:xlink","http://www.w3.org/1999/xlink")
    ;

    this.myScale  = this.mySVGdiv
        .append( "svg")
            .attr(   'width'              , this.width                + 'em')
            .attr(   'height'             , self.cfg.opts.scaleHeight + 'em')
            .attr(   "id"                 , "scale")
            //.classed('matrix',              true)
    ;


    this.mySVG    = this.mySVGdiv
        .append( "svg")
            .attr(   "width" , this.width + 'em') //400
            .attr(   "height", this.height+ 'em') //100
            .classed('matrix',              true)
            .attr(   "id"    ,        "outgraph")
    ;

    this.mySVG
        .append('filter')
            .attr("id", 'invert')
            .append('feColorMatrix')
                .attr('type', 'matrix')
                .attr('values', '-1 0 0 0 1 0 -1 0 0 1 0 0 -1 0 1 0 0 0 1 0')
    ;

    //define a color scale using the min and max expression values


    this.changeStatus('info', '<span class="glyphicon glyphicon-picture">Adding scale</span>');
    this.progresser(35);



    this.colors = {
        'blue'  : {
            'colors'   : ["blue"  , "white"    , "red"],
            'letter'   : 'b',
            'color'    : 'blue',
            'colorS'   : 'blue',
            'revColors': ["white" , "limegreen", "green"],
        },
        'green' : {
            'colors'   : ["white" , "limegreen", "green"],
            'letter'   : 'g',
            'color'    : 'limegreen',
            'colorS'   : 'green',
            'revColors': ["blue"  , "white"    , "red"],
        },
        'grey'  : {
            'colors'   : ["white" , "grey"     , "black"],
            'letter'   : 'g',
            'color'    : 'grey',
            'colorS'   : 'black',
            'revColors': ["blue"  , "white"    , "red"],
        },
        'red'   : {
            'colors'   : ["yellow", "orange"   , "red"],
            'letter'   : 'r',
            'color'    : 'red',
            'colorS'   : 'orange',
            'revColors': ["blue"  , "white"    , "red"],
        },
        'yellow': {
            'colors'   : ["white" , "yellow"   , "red"],
            'letter'   : 'y',
            'color'    : 'yellow',
            'colorS'   : 'red',
            'revColors': ["blue"  , "white"    , "red"],
        }
    };

    this.mapColor('red');

    this.updateColorScale();

    this.createScale();

    //generate heatmap rows
    this.myRows     = this.mySVG.append('svg')
        .classed('matrixrows', true)
        .attr(   'y'         , 0   )
        .attr(   'Oy'        , 0   )
    ;

    this.heatmapRow = this.myRows
        .append('svg')
            .classed('matrixcells', true)
    ;


    this.heatmapRowG = this.heatmapRow.append('g');



    this.changeStatus('info', '<span class="glyphicon glyphicon-picture">Adding squares</span>');
    this.progresser(40);

    this.heatmapRows = this.heatmapRowG
        .selectAll(".matrixrow")
            .data( self.cfg.data.ddata )
                .enter()
                    .append("svg")
                        .classed('matrixrow', true)
                        .attr(   'matrixrow', function(d, i) { return i; })
                        .attr(   "x"        ,                            0)
                        .attr(   "y"        , function(d, i) { return (i * self.cfg.opts.cellHeight) + self.cfg.opts.cellHeight + self.cfg.opts.paddingTop + 'em'; })
                        .attr(   "height"   ,                              self.cfg.opts.cellHeight  + 'em')
                        .attr(   "Oy"       , function(d, i) { return (i * self.cfg.opts.cellHeight) + self.cfg.opts.cellHeight + self.cfg.opts.paddingTop + 'em'; })
                        .attr(   "Oheight"  ,                              self.cfg.opts.cellHeight  + 'em')
    ;



    //generate heatmap columns
    this.heatmapRects = this.heatmapRows
        .selectAll("rect")
        .data(function(d) {
            return d;
        })
        .enter()
            .append("svg:rect")
                .attr(   'width'              ,self.cfg.opts.cellWidth  + 'em')
                .attr(   'height'             ,self.cfg.opts.cellHeight + 'em')
                .attr(   'Owidth'             ,self.cfg.opts.cellWidth  + 'em')
                .attr(   'Oheight'            ,self.cfg.opts.cellHeight + 'em')
                .classed('matrixcell', true)
                .style('fill',function(d, i) {
                    return self.colorScale(d[0]);
                })
                .attr('x', function(d, i) {
                    var v = (d[2] * self.cfg.opts.cellWidth) + self.cfg.opts.paddingLeft + 'em';
                    return v;
                })
                .attr('Ox', function(d, i) {
                    var v = (d[2] * self.cfg.opts.cellWidth) + self.cfg.opts.paddingLeft + 'em';
                    return v;
                })
                .attr('y', 0)
                .attr('matrixcol', function(d, i) {
                    return i;
                })
                .attr('title', '')
                .on('click', function(){
                    var cell     = this;
                    var colNum   = parseInt(cell.getAttribute('matrixcol'));

                    var reg      = self.getregister(null, colNum);
                    var cname    = reg['colname'];

                    console.log('CLICK. register %o', reg);

                    //self.getTree(  cname);
                    self.onClick(cname);
                })
                ;

    this.changeStatus('info', '<span class="glyphicon glyphicon-picture">Adding header</span>');
    this.progresser(70);

    this.addHeader();


    //expression value label
    this.expLab = this.myGlobal
        .append('div')
            .style('height'    ,        23)
            .style('position'  ,'absolute')
            .style('background',  'FFE53B')
            .style('opacity'   ,       0.8)
            .style('top'       ,         0)
            .style('padding'   ,        10)
            .style('left'      ,        40)
            .attr( 'id'        ,  'expLab')
            //.style('display','none');
    ;


    var getter = self.getCellTitle();

    //this.changeStatus('info', '<span class="glyphicon glyphicon-picture">Adding tooltip</span>');
    //this.progresser(80);


    this.changeStatus('info', '<span class="glyphicon glyphicon-picture">Creating slider</span>');
    this.progresser(80);

    this.createSlider();

    this.changeStatus('success', '<span class="glyphicon glyphicon-ok">Done</span>');
    this.progresser(90);


    //$('#outgraph').tooltip({
    //    content: function(callback){
    //        //$('.ui-tooltip').each(function(){ $(this).remove(); });
    //        var tools = document.getElementsByClassName('ui-tooltip');
    //
    //        for ( var i=0; i<tools.length; i++) {
    //            $(tools[i]).remove();
    //        }
    //
    //
    //        if ( $(this).is('#main_row .matrixcell') ) {
    //            callback( getter(this) );
    //        } else {
    //            callback( $(this).attr('title') ) ;
    //        }
    //    },
    //    show: { delay: 1300 }
    //});

    self.updateSize();
};

plotSVG.prototype.appendClustering = function(data) {
    console.log('appending cluster %o', data);
    this.order.rows.push( data.rows.rowsOrder );
    this.order.cols.push( data.cols.colsOrder );
    console.log('new order %o', this.order);
};

plotSVG.prototype.createSlider = function() {
    var self = this;

    console.log('adding slider');


    d3.select( this.divSlider )
        .append('div')
            .attr('id', 'sliderDivW')
            .append('div')
                .attr('id', 'sliderW')
    ;

    //$('<div>'       , { 'class': '', 'id': 'sliderDivW' } ).appendTo( this.divSlider );
    //$('<div>'       , {              'id': 'sliderW'    } ).appendTo( '#sliderDivW'  );

    self.sldW = $('#sliderW').slider({
        range : 'min',
        min   : 0,
        max   : 0,
        step  : 0,
        value : 0,
        slide : function( event, ui ) {
            var cMax = $(this).slider('option','max');
            var prop = (ui.value/cMax*100).toFixed(2);
            var t    = " - Pos "+prop+"%";
            self.myScaleLbl.text( t       );
            self.translateW(      ui.value);
        }
    });

    var cVal = $("#sliderW").slider("value");
    var cMax = $("#sliderW").slider("option", "max");
    var prop = (cVal / cMax*100).toFixed(2);
    var t    = " - Pos "+ prop + "%";

    self.myScaleLbl.text( t );

    self.updateSize();
};

plotSVG.prototype.updateSliderSize = function(w) {
    var self  = this;
    var wE    = w - $(this.SVGdiv).width();
    var wS    = 1; //math.floor(h / 1);

    var cVal  = $("#sliderW").slider("value");
    var cMax  = $("#sliderW").slider("option", "max");

    var cProp = cVal / cMax;

    if (cMax == 0) {
        cProp = 0;
    }

    var nVal  = Math.round(cProp * wE);

    //console.log("cvalue %d cmax %d cprop %f width %d nval %d", cVal, cMax, cProp, wE, nVal);

    self.sldW.slider('option', 'max' , wE  );
    self.sldW.slider('option', 'step', wS  );
    self.sldW.slider('value' ,         nVal);

    var prop = (nVal / wE * 100).toFixed(2);
    var t    = " - Pos "+prop+ "%";

    self.myScaleLbl.text( t );

    self.translateW( nVal );
};

plotSVG.prototype.translateW = function( v ) {
    var self = this;
    self.myHeaderCol.attr('transform', 'translate(-'+v+')');
    self.heatmapRowG.attr('transform', 'translate(-'+v+')');
};

plotSVG.prototype.changeStatus = function(status, msg) {
    console.log("%s %s", status, msg);
};

plotSVG.prototype.progresser = function(val) {
    console.log('progress %d', val);
};

plotSVG.prototype.onClick = function(cname) {
    console.log('clicked on gene %s', cname);
};

plotSVG.prototype.updateDraw = function () {
    var self = this;

    console.log( 'updating draw');

    var ff = function(d, i) {
                var val = d[0];
                var row = d[1];
                var col = d[2];
                //console.log('val %f row %d col %d', val, row, col);
                var reg = self.getregister( row, col );
                return self.colorScale( reg.distance );
            };

    this.heatmapRows
        .selectAll("rect")
            .style('fill', ff)
    ;

    this.myRowLabel.selectAll('.matrixheaderrowcell')
        .text( function(d,i) { return 'c '+self.getregister(i).rowname; } )
    ;


    var fr = function(d,i) {
                var val = self.getregister(null,i)[rowname];
                //console.log('h %d name %s val %s',i,rowname,val);
                return val;
            };

    for ( var j in self.rowsNames ) {
        //[ 'start' , 'start', self.cfg.header.line_starts  ],
        var rowdata = self.rowsNames[j];
        //console.log(rowdata);
        var rowname = rowdata[1];

        this.myHeaderCol.selectAll('.matrixheadercolcell'+rowname)
            .text( fr )
        ;
    }
};

plotSVG.prototype.getregister = function ( row, col ) {
    var self  = this;
    if ( typeof(row) == 'undefined') {
        row = null;
    }
    if ( typeof(col) == 'undefined' ) {
        col = null;
    }

    var res   = {};

    var nRow  = null;
    var nCol  = null;

    var order = self.order;

    //console.log(order);

    if ( row !== null ) {
        var cRow  = order.currRow;
        var rRow  = order.rows[cRow];
            nRow  = rRow[row];

        //console.log('getting row %d crow %d rrow %o', row, cRow, rRow);

        res['rowname'] = self.cfg.data.dnames[ nRow ];
    }

    if ( col !== null ) {
        var cCol   = order.currCol;
        var rCol   = order.cols[cCol];
            nCol   = rCol[col];

        //console.log('getting col %d ccol %d rcol %o', col, cCol, rCol);

        var header   = self.cfg.header;

        res['colname'] = header.line_names[   nCol ];
        res['start'  ] = header.line_starts[  nCol ];
        res['end'    ] = header.line_ends[    nCol ];
        res['unities'] = header.line_unities[ nCol ];
        res['snps'   ] = header.line_snps[    nCol ];
    }

    if (( row !== null ) && ( col !== null )) {
        //console.log('getting distance nrow %d ncol %o', nRow, nCol);
        res['distance'] = self.cfg.data.ddata[  nRow ] [ nCol ][ 0 ];
    }

    return res;
};

plotSVG.prototype.showHeader = function ( val ) {
    var self = this;

    console.log('showing header');

    self.isShowingHeader = val;

    if (val) {
        self.myHeader.style('visibility', 'visible');

        self.heatmapRects.each( function() {
            var s = d3.select(this);
            s
                .attr('width', s.attr('CNwidth'))
                .attr('x'    , s.attr('CNx'    ))
            ;
        });

        self.myRows.attr(    'y', self.myRows.attr('CNy'));
        self.heatmapRow.attr('x', self.maxHeaderRowWidth );

    } else {
        if (!self.isShowingSpecies) {
            self.heatmapRow.attr('x', 0);
        }

        self.myHeader.style('visibility', 'hidden');

        self.heatmapRects.each( function() {
            var s = d3.select(this);
            s.attr('width', s.attr('Owidth'));
            s.attr('x'    , s.attr('Ox'    ));
        });

        self.myRows.attr('y', self.myRows.attr('Oy'));
    }

    self.updateSize();
};

plotSVG.prototype.showSpecies = function ( val ) {
    var self = this;

    console.log('showing species');
    self.isShowingSpecies = val;

    if ( val ) {
        if (!self.isShowingHeader) {
            self.heatmapRow.attr('x', self.maxHeaderRowWidth);
        }

        self.heatmapRects.each( function() {
            var s = d3.select(this);
            s.attr('height', s.attr('RNheight'));
        });

        this.heatmapRows.each(function(){
            var s = d3.select(this);
            s.attr('height', s.attr('RNheight'));
            s.attr('y'     , s.attr('RNy'     ));
        });

        self.myRowLabel.style('visibility', 'visible');

    } else {
        if (!self.isShowingHeader) {
            self.heatmapRow.attr('x', 0);
        }

        self.heatmapRects.each( function() {
            var s = d3.select(this);
            s.attr('height', s.attr('Oheight'));
        });

        self.heatmapRows.each(function(){
            var s = d3.select(this);
            s.attr('height', s.attr('Oheight'));
            s.attr('y'     , s.attr('Oy'     ));
        });

        self.myRowLabel.style('visibility', 'hidden');
    }

    self.updateSize();
};

plotSVG.prototype.clusterSpp = function ( val ) {
    var self = this;

    console.log('svg clustering spp', val);

    self.isClusteringSpecies = val;

    //console.log( this.cfg.cluster.rows );

    self.order.currRow = val ? 1 : 0;

    self.updateDraw();
};

plotSVG.prototype.clusterGenes = function ( val ) {
    var self = this;

    console.log('svg clustering genes', val);

    self.isClusteringGenes = val;

    //console.log( this.cfg.cluster.cols )

    self.order.currCol = val ? 1 : 0;

    self.updateDraw();
};

plotSVG.prototype.toggleShowHeader   = function() { var self = this; return function () { self.showHeader(   ! self.isShowingHeader     ) } };

plotSVG.prototype.toggleShowSpecies  = function() { var self = this; return function () { self.showSpecies(  ! self.isShowingSpecies    ) } };

plotSVG.prototype.toggleClusterSpp   = function() { var self = this; return function () { self.clusterSpp(   ! self.isClusteringSpecies ) } };

plotSVG.prototype.toggleClusterGenes = function() { var self = this; return function () { self.clusterGenes( ! self.isClusteringGenes   ) } };

plotSVG.prototype.download = function( ) {
    var self = this;

    return function () {
        var srcDiv     = self.mySVG;
        //var srcDiv     = self.myScale;
        var ish = self.isShowingHeader;
        var iss = self.isShowingSpecies;

        self.showHeader( true);
        self.showSpecies(true);

        var srcDivNode = srcDiv.node();
        var doctype    = '<?xml version="1.0" encoding="utf-8" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n';


        if (!srcDivNode.hasAttributeNS(d3.ns.prefix.xmlns, "xmlns")) {
            srcDivNode.setAttributeNS(d3.ns.prefix.xmlns, "xmlns", d3.ns.prefix.svg);
        }

        if (!srcDivNode.hasAttributeNS(d3.ns.prefix.xmlns, "xmlns:xlink")) {
            srcDivNode.setAttributeNS(d3.ns.prefix.xmlns, "xmlns:xlink", d3.ns.prefix.xlink);
        }


        var source  = (new XMLSerializer()).serializeToString(srcDivNode);//.replace('</style>', '<![CDATA[' + styles + ']]></style>\n');
        var rect    = srcDivNode.getBoundingClientRect();

        srcDiv
            .attr('width' , rect.width )
            .attr('height', rect.height)
        ;

        var svgInfo = {
            //top              : rect.top,
            //left             : rect.left,
            //width            : rect.width,
            //height           : rect.height,
            'class'          : srcDiv.attr("class"),
            id               : srcDiv.attr("id"),
            childElementCount: srcDivNode.childElementCount,
            source           : [doctype + source]
        };

        var filename = 'image.csv';

        if (svgInfo.id) {
            filename = svgInfo.id;

        } else if (svgInfo['class']) {
            filename = svgInfo['class'];

        } else if (window.document.title) {
            filename = window.document.title.toLowerCase();
        }

        filename = filename.replace(/[^a-z0-9]/gi, '-');

        console.log('converting');

        //d3.text('/convert')
        d3.xhr('/convert')
            //.header('Content-type', 'application/svg\/xml')
            .header('Encode-type', 'multipart/form-data')
            //.mimeType('image/png')
            .responseType('blob')
            .post(svgInfo.source, function(error, res) {
                console.warn('convertion success');
                //console.warn(error);
                //console.warn(res );
                var img = res.response;
                //console.warn(img );

                //var url = window.URL.createObjectURL(new Blob(svgInfo.source, { "type" : "image/svg+xml" }));
                //var url = window.URL.createObjectURL(new Blob([img], { "type" : "image/png" }));
                var url = window.URL.createObjectURL(img);

                var a   = d3.select("body")
                    .append('a')
                        .attr( "class"   , "svg-crowbar"    )
                        .attr( "download", filename + ".png")
                        .attr( "href"    , url              )
                        .style("display" , "none"           );

                a.node().click();

                setTimeout(function () {
                    window.URL.revokeObjectURL(url);
                }, 10);

                a.remove();


                self.showHeader( ish);
                self.showSpecies(iss);
            })
        ;

    };

};

plotSVG.prototype.updateSize = function( ) {
    var self = this;
    var h    = 0;
    var w    = 0;

    this.myRows.selectAll('.matrixcells').each( function() {
        var b = d3.select(this).node().getBoundingClientRect();
        h += b.height;
        w += b.width;
        //h += this.getBBox().height;
        //w += this.getBBox().width;
    });

    //var gH = this.heatmapRowG[0][0].getBBox().height;
    //this.heatmapRow.attr(  'height' , Math.round(h*1.05) + 'px');


    if (self.isShowingHeader) {
        h += self.sumHeaderColHeight;
        w += self.sumHeaderRowWidth;
    } else {
        if ( self.isShowingSpecies) {
            w += self.sumHeaderRowWidth;
        }
    }

    h = Math.round(h*1.02);
    w = Math.round(w*1.02);

    this.mySVG
        .attr('height', h + 'px')
        .attr('width' , w + 'px')
    ;

    var headerHeight = parseInt( self.mySVGdiv.attr('headerHeight') );
    var hT = Math.round((h + headerHeight) * 1.01);

    this.mySVGdiv
        .attr('height', hT + 'px')
        .attr('width' , w  + 'px')
    ;

    self.updateSliderSize(w);
};

plotSVG.prototype.translate = function( x , y ) {
    var self = this;
    console.log('translating X %d Y %d cX %d cY %d', x, y, self.currXtrans, self.currYtrans);

    var self = this;

    self.currXtrans += x;
    self.currYtrans += y;

    console.log('translated cX %d cY %d', self.currXtrans, self.currYtrans);

    self.heatmapRow.attr('transform', 'translate('+this.currXtrans+','+this.currYtrans+')');
};

plotSVG.prototype.mapColor = function (color) {
    var self = this;

    self.cfg.opts.colors = self.colors[color].colors;

    self.updateColors();
};

plotSVG.prototype.updateColorScale = function () {
    var self = this;

    self.cfg.info.dmid = ((self.cfg.info.dmax - self.cfg.info.dmin) / 2.0).toFixed(2);

    this.colorScale = d3.scale.linear()
        .domain([self.cfg.info.dmin, self.cfg.info.dmid, self.cfg.info.dmax])
        .range(self.cfg.opts.colors);
};

plotSVG.prototype.updateColors = function () {
    var self = this;

    self.updateColorScale();

    if ( self.heatmapRects ) {
        self.heatmapRects.each( function() {
            d3.select(this).style('fill',function(d, i) {
                //console.log('F i %d D %o', i, d);
                return self.colorScale(d[0]);
            });
        });

        self.myScale.selectAll('rect').each( function() {
            d3.select(this).style('fill',function(d, i) {
                //console.log('F i %d D %o', i, d);
                return self.colorScale(d);
            });
        });
    }
};

plotSVG.prototype.createScale = function () {
    var self  = this;
    var dmin  = self.cfg.info.dmin;
    var dmid  = self.cfg.info.dmid;
    var dmax  = self.cfg.info.dmax;
    var dfrag = ((dmax - dmin) * 1.0) / (self.cfg.opts.scaleSplits-1);

    self.updateColorScale();

    console.log("mix %d max %d splits %d frag %f", dmin, dmax, self.cfg.opts.scaleSplits, dfrag);

    var samples = [];
    var stats   = [];
    for ( var i = dmin; i < dmax; i+=dfrag) {
        //console.log( i );
        samples.push( i.toFixed(2) );
        stats  .push( 0            );
    }
    //console.log(samples);



    var paddingLeft = self.cfg.opts.cellWidth * 5;
    var cellW       = self.cfg.opts.cellWidth * 3;

    var data     = self.cfg.data.ddata;
    var statsSum  = 0;
    for ( var r = 0; r < data.length; r++ ) {
        var cols = data[r];
        for ( var c = 0; c < cols.length; c++ ) {
            var v = cols[c];
            var d = v[0];
            var k = Math.round( d / dfrag );
            //console.log("d %f f %f k %f", d, dfrag, k);
            if ( k >= stats.length ) {
                k = stats.length - 1;
            }
            stats[ k ] += 1;
            statsSum   += 1;
        }
    }

    var statsPro = [];

    for ( var s = 0; s < stats.length; s++ ) {
        statsPro.push( stats[s] / statsSum);
    }


    self.myScaleTextLeft = self.myScale
        .append('text')
            .text(dmin.toFixed(1)                                     )
            .attr('x'          , 0                              + 'px')
            //.attr('y'          , self.cfg.opts.scaleHeight *.75 + 'em')
            .attr('fill'       , 'black'                              )
            .attr('font-family', 'sans-serif'                         )
            .attr('font-size'  , '1em'                                )
    ;

    var scaleTextLeftBox    = self.myScaleTextLeft[0][0].getBBox();
    var scaleTextLeftHeight = scaleTextLeftBox.height;
    var scaleTextLeftWidth  = scaleTextLeftBox.width;
    var scaleTextLeftEnd    = scaleTextLeftBox.width + scaleTextLeftBox.x;

    self.myScaleTextLeft.attr('y'           , scaleTextLeftHeight*1.5 + 'px');
    self.myScale.attr(        'height'      , scaleTextLeftHeight*2.0 + 'px');
    self.mySVG.attr(          'y'           , self.myScale.attr('height'));
    self.mySVGdiv.attr(       'headerHeight', scaleTextLeftHeight*2.0);

    //console.log(statsPro);

    var blockHeight        = function(i) { return (0.25+(statsPro[i]*0.75)) * (scaleTextLeftHeight * 2); };

    self.myScaleBars = self.myScale
        .append("g");

    self.myScaleBarsCells = self.myScaleBars
            .selectAll('.matrixcell')
                .classed('matrixscale', true)
                .data( samples )
                .enter()
                    .append("svg:rect")
                        .attr(   'width'              , scaleTextLeftWidth       + 'px')
                        .attr(   'height'             , function(d,i) { return blockHeight(i) + 'px' } )
                        .classed('matrixcell datacell', true)
                        .style('fill',function(d, i) {
                            //console.log('F i %d D %o', i, d);
                            return self.colorScale(d);
                        })
                        .attr('x', function(d, i) {
                            var v = (i * scaleTextLeftWidth) + (scaleTextLeftWidth*1.2);
                            //console.log('X i %d D %o v %d', i, d, v);
                            return v + 'px';
                        })
                        .attr('y', function(d, i) {
                            //console.log('Y i %d D %o d2 %d v %d', i, d, d[2], v);
                            return ((scaleTextLeftHeight*2) - blockHeight(i)) + 'px';
                        });

    var myScaleBarsBox   = self.myScaleBars[0][0].getBBox();
    var myScaleBarsWidth = myScaleBarsBox.width;
    var myScaleBarsEnd   = myScaleBarsBox.width + myScaleBarsBox.x;

    self.myScaleTextRight = self.myScale
        .append('text')
            .text(dmax.toFixed(1)                              )
            .attr('x'          , myScaleBarsEnd + (scaleTextLeftWidth*0.2) + 'px')
            .attr('y'          , scaleTextLeftHeight*1.5 + 'px')
            .attr('fill'       , 'black'                       )
            .attr('font-family', 'sans-serif'                  )
            .attr('font-size'  , '1em'                         )
    ;

    var scaleTextRightBox    = self.myScaleTextRight[0][0].getBBox();
    var scaleTextRightHeight = scaleTextRightBox.height;
    var scaleTextRightWidth  = scaleTextRightBox.width;
    var scaleTextRightEnd    = scaleTextRightBox.width + scaleTextRightBox.x;

    self.myScaleLbl = self.myScale
        .append('text')
            .text(' - Pos 100.00%  '                                                )
            .attr('x'          , scaleTextRightEnd + (scaleTextLeftWidth*0.2) + 'px')
            .attr('y'          , scaleTextLeftHeight*1.5                      + 'px')
            .attr('fill'       , 'black'                                            )
            .attr('font-family', 'sans-serif'                                       )
            .attr('font-size'  , '1em'                                              )
    ;

    var scaleLabelBox    = self.myScaleLbl[0][0].getBBox();
    var scaleLabelHeight = scaleLabelBox.height;
    var scaleLabelWidth  = scaleLabelBox.width;
    var scaleLabelEnd    = scaleLabelWidth + scaleLabelBox.x;

    var scaleColors = self.myScale
        .append('g')
            .attr('transform' , 'translate('+(scaleLabelEnd*1.05)+')')
            .attr('id', 'colorPicker')
    ;


    var lastEnd = 0;

    for (color in this.colors) {
        console.log(color);

        var data    = self.colors[color];
        var colors  = data.colors;
        var letter  = data.letter;
        var colorsB = data.color;
        var colorsS = data.colorS;

        (
            function (clr,ltr) {
                var g = scaleColors
                    .append('g')
                    .attr('transform' , 'translate('+(lastEnd+2)+')')
                ;

                g.append('rect')
                    .style('fill', clr)
                    .attr('width', 20)
                    .attr('height', scaleTextLeftHeight*2)
                    .attr('rx', 10)
                    .attr('ry', 10)
                    .on('click', function() { self.mapColor( clr ) } )
                ;

                g.append('text')
                    .text(ltr)
                    .style('fill', 'white')
                    .attr('x' ,  5)
                    .attr('y' , scaleTextLeftHeight*1.2)
                    .attr('font-weight', 'bold')
                    .on('click', function() { self.mapColor( clr ) } )
                ;

                var txtBox    = scaleColors[0][0].getBBox();
                var txtHeight = txtBox.height;
                var txtWidth  = txtBox.width;
                var txtEnd    = txtBox.width + txtBox.x;

                lastEnd = txtWidth + 2;
            }
        )(color, letter);
    }

    var txtBox    = scaleColors[0][0].getBBox();
    var txtHeight = txtBox.height;
    var txtWidth  = txtBox.width;
    var txtEnd    = txtWidth + txtBox.x;
    console.log('txt width %d x %d %o', txtWidth, txtBox.x, txtBox);

    var showers = [
        ['Show Species'   , self.toggleShowSpecies()   , true ],
        ['Show Header'    , self.toggleShowHeader()    , true ],
        ['Cluster Species', self.toggleClusterSpp()    , true ],
        ['Cluster Genes'  , self.toggleClusterGenes()  , true ],
        ['Download'       , self.download()            , false],
        ['Close'          , self.clean()               , false]
    ];


    var scaleShowers = self.myScale
        .append('g')
            .attr('transform' , 'translate('+((scaleLabelEnd+txtWidth)*1.05)+')')
            .attr('id', 'showers')
    ;


    var lastEnd = 0;

    for ( var d = 0; d < showers.length; d++) {
        var data = showers[d];

        (
            function(tx,fc, toggle) {
                var g = scaleShowers
                    .append('g')
                    .attr('transform' , 'translate('+(lastEnd+2)+')')
                ;

                var r = g.append('rect')
                    .style('fill', 'grey')
                    .attr('width', 20)
                    .attr('height', scaleTextLeftHeight*2)
                    .attr('rx', 10)
                    .attr('ry', 10)
                ;

                var t = g.append('text')
                    .text(tx)
                    .style('fill', 'white')
                    .attr('x' ,  5)
                    .attr('y' , scaleTextLeftHeight*1.2)
                    .attr('font-weight', 'bold')
                ;

                var fcc = function() {
                    if ( toggle ) {
                        var gf = g.attr('filter');

                        if ( gf ) {
                            g.attr('filter', null);
                        } else {
                            g.attr('filter', 'url(#invert)');
                        }
                    }

                    fc();
                };

                r.on('click', fcc);
                t.on('click', fcc);

                r.attr('width', t[0][0].getBBox().width * 1.15 + 5);

                var txtBox    = scaleShowers[0][0].getBBox();
                var txtHeight = txtBox.height;
                var txtWidth  = txtBox.width;
                var txtEnd    = txtBox.width + txtBox.x;

                lastEnd = txtWidth + 5;
            }
        )( data[0], data[1], data[2] );
    }
};

plotSVG.prototype.getCellTitle = function () {
    var self = this;

    return function(cell) {
        //console.log('getCellTitle');
        var prow     = cell.parentNode;
        var colNum   = parseInt( cell.getAttribute('matrixcol') );
        var rowNum   = parseInt( prow.getAttribute('matrixrow') );

        //console.log( 'tooltip cell %o prow %o', cell, prow);
        //console.log( 'tooltip row %d col %d', rowNum, colNum);

        var register = self.getregister(rowNum,colNum);

        var title =   '<p class="ptip"><b>Species:</b> ' + register.rowname
                    + '<p class="ptip"><b>Name:</b> '    + register.colname
                    + '<p class="ptip"><b>Start:</b> '   + register.start
                    + '<p class="ptip"><b>End:</b> '     + register.end
                    + '<p class="ptip"><b>Unities:</b> ' + register.unities
                    + '<p class="ptip"><b>SNPs:</b> '    + register.snps
                    + '<p class="ptip"><b>Distance:</b> '+ register.distance;
        // + ' Rownum ' + rownum + ' Colnum ' + colnum

        return title;
    };
};

plotSVG.prototype.addHeader = function () {
    this.addRowNames();
    this.addColNames();
};

plotSVG.prototype.addRowNames = function () {
    var self = this;
    this.rowLabelTransX =  0;
    this.rowLabelTransY =  0;

    this.myRowLabel     = this.myRows
        .append('svg')
            .classed('matrixheaderrowrow', true                                                        )
            .style(  'visibility'        , 'hidden'                                                    )
            //.attr(   "y"                 , "30")
            //.attr(   "transform"         , "translate("+self.rowLabelTransX+","+self.rowLabelTransY+")")
    ;


    this.myRowLabel.selectAll('.matrixheaderrowcell')
        .data( self.cfg.data.dnames )
        .enter()
            .append('text')
                .classed('matrixheaderrowcell', true                             )
                .attr(   'x'                  , 0 + 'em'                         )
                .attr(   'y'                  , function(d,i) { return ((i+1) * self.cfg.opts.labelHeight) + 'em'; } )
                .style(  'height'             , self.cfg.opts.labelHeight + 'em' )
                .text(   function(d,i) { return d;        }                      )
    ;


    this.maxHeaderRowWidth  = 0;
    this.maxHeaderRowHeight = 0;
    this.myRowLabel.selectAll('.matrixheaderrowcell').each( function() {
        var h = this.getBBox().height;
        var w = this.getBBox().width;
        self.maxHeaderRowHeight  = h > self.maxHeaderRowHeight ? h : self.maxHeaderRowHeight;
        self.maxHeaderRowWidth   = w > self.maxHeaderRowWidth  ? w : self.maxHeaderRowWidth ;
    });

    self.maxHeaderRowWidth  = Math.round((self.maxHeaderRowWidth  + 1) * 1.15);
    self.maxHeaderRowHeight = Math.round((self.maxHeaderRowHeight + 1) * 1.15);

    //set row names cell sizes
    this.myRowLabel.selectAll('.matrixheaderrowcell')
        .each( function(d,i) {
            var el = d3.select(this);
                el.style('width', self.maxHeaderRowWidth + 'px');
        })
    ;

    this.sumHeaderRowHeight = 0;
    this.sumHeaderRowWidth  = 0;
    this.mySVG.selectAll('.matrixheaderrowrow').each( function() {
        var h = this.getBBox().height;
        var w = this.getBBox().width ;
        self.sumHeaderRowHeight = h;
        self.sumHeaderRowWidth  = w;
    });


    self.sumHeaderRowHeight = Math.round(( self.sumHeaderRowHeight + 1 ) * 1.15);
    self.sumHeaderRowWidth  = Math.round(( self.sumHeaderRowWidth  + 1 ) * 1.15);

    console.log('maxHeaderRow Width %d Height %d sumHeight %d', this.maxHeaderRowWidth, this.maxHeaderRowHeight, this.sumHeaderRowHeight);

    this.myRowLabel
        .attr('height', self.sumHeaderRowHeight + 'px')
        .attr('width' , self.maxHeaderRowWidth  + 'px');

    this.heatmapRects.each( function() {
        d3.select(this).attr('RNheight', self.cfg.opts.labelHeight + 'em');
    });

    this.heatmapRows.each(function(){
        var s        = d3.select(this);
        var rowNum   = this.getAttribute('matrixrow');
        s.attr('RNheight',  self.cfg.opts.labelHeight                      + 'em');
        s.attr("RNy"     , (self.cfg.opts.labelHeight * rowNum).toFixed(2) + 'em');
    });

    //this.myRows
    //    .attr('height', self.sumHeaderRowHeight + 'px')
    //    .attr('width' , self.sumHeaderRowWidth  + 'px')
    //;
};

plotSVG.prototype.addColNames = function () {
    var self = this;

    self.rowsNames = [
        [ 'start' , 'start'  , self.cfg.header.line_starts  ],
        [ 'end'   , 'end'    , self.cfg.header.line_ends    ],
        [ '#genes', 'unities', self.cfg.header.line_unities ],
        [ '#SNPs' , 'snps'   , self.cfg.header.line_snps    ],
        [ 'name'  , 'colname', self.cfg.header.line_names   ]
    ];


    this.myHeader = this.mySVG
        .append('svg')
            .classed('matrixheader', true    )
            .style(  'visibility'  , 'hidden')
            //.attr(   "y"           , "20")
    ;

    this.myHeaderRowCol = this.myHeader
        .append('g')
            .classed('matrixheaderrowcol', true    )
    ;

    this.myHeaderColS = this.myHeader
        .append('svg')
    ;

    this.myHeaderCol = this.myHeaderColS
        .append('g')
            .classed('matrixheadercol', true    )
    ;


    for ( var r = 0; r < self.rowsNames.length; r++) {
        self.genHeader(self.rowsNames, r);
        var rowtitle = self.rowsNames[r][0];

        this.myHeaderRowCol
            .append('text')
                .text(rowtitle)
                .classed('matrixheadercell'           , true     )
                //.classed('matrixheadercolcell'        , true     )
                .classed('matrixheadercolrowcell'     , true     )
                //.classed('matrixheadercolcell'+rowname, true     )
                .attr(   'colnum'                     , -1       )
                .attr(   'x'                          , 0  + 'em')
                .attr(   'y'                          , (r+1) * self.cfg.opts.labelHeight + 'em')
                .style(  'height'                     ,         self.cfg.opts.labelHeight + 'em')
    }


    var mhrh = self.maxHeaderRowHeight;
    var mhrw = self.maxHeaderRowWidth ;
    this.myHeader.selectAll('.matrixheaderrowcol').each( function() {
        var h = this.getBBox().height;
        var w = this.getBBox().width ;
        mhrh = h > mhrh ? h : mhrh;
        mhrw = w > mhrw ? w : mhrw;
    });

    if (( mhrh != self.maxHeaderRowHeight ) || ( mhrw != self.maxHeaderRowWidth )) {
        console.log('updating row width');
        self.maxHeaderRowHeight = Math.round(( mhrh + 1 ) * 1.15);
        self.maxHeaderRowWidth  = Math.round(( mhrw + 1 ) * 1.15);

        this.myRowLabel
            .attr('width' , self.maxHeaderRowWidth  + 'px');

        this.myRowLabel.selectAll('.matrixheaderrowcell')
            .each( function(d,i) {
                var el = d3.select(this);
                    el.style('width', self.maxHeaderRowWidth + 'px');
            })
        ;
    }








    this.maxHeaderColWidth  = 0;
    this.maxHeaderColHeight = 0;
    this.myHeader.selectAll('.matrixheadercolcell').each( function() {
        var w = this.getBBox().width;
        var h = this.getBBox().height;
        self.maxHeaderColWidth  = w > self.maxHeaderColWidth  ? w : self.maxHeaderColWidth ;
        self.maxHeaderColHeight = h > self.maxHeaderColHeight ? h : self.maxHeaderColHeight;
    });

    self.maxHeaderColWidth  = Math.round((self.maxHeaderColWidth  + 1) * 1.15);
    self.maxHeaderColHeight = Math.round((self.maxHeaderColHeight + 1) * 1.15);

    //set header cell sizes
    this.myHeader.selectAll('.matrixheadercolcell')
        .each( function(d,i) {
            var el = d3.select(this);
            var cn = parseInt(el.attr('colnum'));
            var x  = self.maxHeaderColWidth * cn + self.maxHeaderRowWidth;

            el.attr( 'x'    ,  x  );
            el.style('width', self.maxHeaderColWidth + 'px');
        })
    ;

    this.mySVG.selectAll('.matrixheader').each( function() {
        self.sumHeaderColHeight = this.getBBox().height;
        self.sumHeaderColWidth  = this.getBBox().width ;
    });

    self.sumHeaderColHeight = Math.round(( self.sumHeaderColHeight + 1 ) * 1.15);
    self.sumHeaderColWidth  = Math.round(( self.sumHeaderColWidth  + 1 ) * 1.15);

    console.log('maxHeaderCol Width %d Height %d sum Width %d sum Height %d', this.maxHeaderColWidth, this.maxHeaderColHeight, self.sumHeaderColWidth, self.sumHeaderColHeight);

    this.myHeader.attr('height', self.sumHeaderColHeight).attr('width', self.sumHeaderColWidth);

    self.heatmapRects.each( function() {
        var s      = d3.select(this);
        var colNum = this.getAttribute('matrixcol');
        var x      = self.maxHeaderColWidth * colNum;
        s.attr('CNwidth', self.maxHeaderColWidth + 'px');
        s.attr('CNx'    , x                      + 'px');
    });

    self.myRows.attr('CNy', self.sumHeaderColHeight);

    this.myHeader
        .attr('height', self.sumHeaderColHeight + 'px')
        .attr('width' , self.sumHeaderColWidth  + 'px')
    ;

    this.myHeaderColS
        .append('defs')
            .append('clipPath')
                .attr('id', 'clipScroll')
                .append('rect')
                    .attr('x', self.maxHeaderRowWidth)
                    .attr('y', 0)
                    .attr('width' , self.sumHeaderColWidth - self.maxHeaderRowWidth)
                    .attr('height', self.sumHeaderColHeight)

    this.myHeaderColS.style('clip-path', 'url(#clipScroll)');
    //this.myHeaderCol.attr('viewBox', self.maxHeaderRowWidth+' 0 '+self.sumHeaderColHeight+' '+self.sumHeaderColWidth);
};

plotSVG.prototype.genHeader = function (rowsNames, r) {
    var self     = this;
    var rowtitle = rowsNames[r][0];
    var rowname  = rowsNames[r][1];
    var rowdata  = rowsNames[r][2];


    var fx = function(d,i) { return i; };
    var ft = function(d,i) { return d; };

    var g = this.myHeaderCol
        .append('g')
            .classed('matrixheadercolrow'        , true)
            .classed('matrixheadercolrow'+rowname, true)
    ;

    g.selectAll('.matrixheadercolcell'+rowname)
        .data( rowdata )
        .enter()
            .append('text')
                .classed('matrixheadercell'           , true     )
                .classed('matrixheadercolcell'        , true     )
                .classed('matrixheadercolcell'+rowname, true     )
                .attr(   'colnum'                     , fx       )
                .attr(   'x'                          , fx       )
                .attr(   'y'                          , (r+1) * self.cfg.opts.labelHeight + 'em')
                .style(  'height'                     ,         self.cfg.opts.labelHeight + 'em')
                .text(    ft                                     )
    ;
};
