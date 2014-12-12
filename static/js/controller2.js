var xmlns           = "http://www.w3.org/2000/svg";
var matrixFontSize  = 14;
var pixelPerLetterW = matrixFontSize / 2;
var pixelPerLetterH = matrixFontSize;

var canvasID        = "imgcanvas";


console.log('LOCATION', location         );
console.log('HOSTNAME', location.hostname);
console.log('PORT    ', location.port    );
console.log('PROTOCOL', location.protocol);

clusterURL   = location.protocol + '//' + location.hostname + ':' + ( parseInt( location.port ) + 1 );
converterURL = location.protocol + '//' + location.hostname + ':' + ( parseInt( location.port ) + 2 );
pdbURL       = location.protocol + '//' + location.hostname + ':' + ( parseInt( location.port ) + 3 );

console.log('URL cluster  ', clusterURL  );
console.log('URL converter', converterURL);
console.log('URL pdb      ', pdbURL      );



var colors = {
    'blue'  : {
        'colorsNames'   : ["blue"  , "white"    , "red"],
        'revColorsNames': ["white" , "limegreen", "green"],
        'letter'        : 'b',
        'color'         : 'blue',
        'colorS'        : 'white',
        'colorN'        : 'grey',
    },
    'green' : {
        'colorsNames'   : ["white" , "limegreen", "green"],
        'revColorsNames': ["blue"  , "white"    , "red"],
        'letter'        : 'g',
        'color'         : 'limegreen',
        'colorS'        : 'white',
        'colorN'        : 'grey',
    },
    'grey'  : {
        'colorsNames'   : ["white" , "grey"     , "black"],
        'revColorsNames': ["blue"  , "white"    , "red"],
        'letter'        : 'g',
        'color'         : 'grey',
        'colorS'        : 'white',
        'colorN'        : 'grey',
    },
    'red'   : {
        'colorsNames'   : ["yellow", "orange"   , "red"],
        'revColorsNames': ["blue"  , "white"    , "red"],
        'letter'        : 'r',
        'color'         : 'red',
        'colorS'        : 'white',
        'colorN'        : 'grey',
    },
    'yellow': {
        'colorsNames'   : ["red" , "orange"   , "yellow"],
        'revColorsNames': ["blue"  , "white"    , "red"],
        'letter'        : 'y',
        'color'         : 'yellow',
        'colorS'        : 'white',
        'colorN'        : 'grey',
    }
};



var setup = {
    colTextWidth    : 120,

    rowTextWidth    :  80, //number of letters / 2

    textHeight      :  pixelPerLetterH,

    cellWidth       :   5,
    cellHeight      :   5,
    introgressHeight:  40,

    scaleHeight     :  50,
    scaleTextWidth  :  20,
    scaleBlockHeight:  10,
    scaleBlockWidth :  10,
    scaleSplits     :   9,

    paddingTop      :   5,
    paddingLeft     :   0,

    colors          : colors,

    showHeader      : false,
    showRow         : false,

    headerConvKey   : {
                        'start'      : 'Start Position',
                        'end'        : 'End Position',
                        'num_unities': 'Number of components',
                        'num_snps'   : 'Number of SNPs',
                        'name'       : 'Fragment Name'
    }
};









function dataManager ( setup, vars, data ) {
    console.log( "INITIALIZING DATA MANAGER: setup %o vars %o data %o", setup, vars, data );
    this.setup     = setup;
    this.data      = data.data;
    this.vars      = vars;
    this.data_info = data.data_info;
    this.header    = data.header;
    this.request   = data.request;
    //console.log( "initializing data: setup %o vars %o data %o", this.setup, this.vars, this.data );
}

dataManager.prototype = {
    getColNum               : function ( col ) {
        return this.vars.order.cols[ this.vars.currColOrder ][ col ];
    },
    getRowNum               : function ( row ) {
        //console.log( this.vars.currRowOrder, this.vars.order );
        return this.vars.order.rows[ this.vars.currRowOrder ][ row ];
    },
    getColorValue           : function ( val ) {
        //console.log( 'getColorValue vars %o %o', this.vars, this.setup.colors, val );
        //console.log(  this.vars.currColor );
        //console.log( this.setup.colors[    this.vars.currColor    ]  );
        return this.setup.colors[    this.vars.currColor    ].colorScale(val);
    },
    getColorValueRev        : function (  val ) {
        return this.setup.colors[    this.vars.currColor    ].colorScaleRev(val);
    },
    getMatrix               : function () {
        return this.data.line;
    },
    getMatrixRow            : function (  row ) {
        var realRow = this.getRowNum( row );
        return this.data.line[realRow];
    },
    getMatrixVal            : function ( row, col ) {
        var realCol = this.getColNum( col );
        var realRow = this.getRowNum( row );
        return this.data.line[ realRow ][ realCol ][0];
    },
    getNames                : function () {
        try {
            return this.data.name;
        } catch(e) {
            return [];
        }
    },
    getNamesVal             : function ( row ) {
        var realRow = this.getRowNum( row );
        var name    = this.getNames()[ realRow ];
        //console.log("get names val: row %d real row %d val %s", row, realRow, name);
        return name;
    },
    getHeader               : function () {
        return this.header;
    },
    getMinVal               : function () {
        return this.data_info.minVal;
    },
    getMaxVal               : function () {
        return this.data_info.maxVal;
    },
    getDataInfo             : function () {
        return this.data_info;
    },
    getHeaderKeys           : function () {
        return Object.keys( this.getHeader() );
    },
    getHeaderRow            : function ( key ) {
        return this.getHeader()[key];
    },
    getHeaderVal            : function ( rowName, col ) {
        var realCol = this.getColNum( col );
        return this.getHeaderRow(rowName)[ realCol ];
    },
    getHeaderConvKey        : function ( key ) {
        return this.setup.headerConvKey[ key ];
    },
    getHeaderInfo           : function ( col ) {
        var res        = {};
        //var header     = this.getHeader();
        var headerKeys = this.getHeaderKeys();

        for ( var k = 0; k < headerKeys.length; k++ ) {
            var key      = headerKeys[k];
            //var row    = this.getHeaderRow(key);
            var val      = this.getHeaderVal( key, col);
            var convK    = this.getHeaderConvKey( key );
            res[ convK ] = val;
        }

        return res;
    }
};




function blockManager ( manager, matrixData, layer ) {
    console.log( 'INITIALIZING BLOCK MANAGER: manager %o matrixdata %o layer %o', manager, matrixData, layer );
    manager.matrixData = matrixData;
    manager.layer      = layer;
    manager.canvasData = manager.matrixData.canvasData;
    manager.scope      = manager.canvasData.scope;
    manager.setup      = manager.canvasData.setup;
    manager.species    = manager.canvasData.species;
    manager.data       = manager.canvasData.data;
    manager.canvas     = manager.canvasData.canvas;
    manager.vars       = manager.canvasData.vars;
    manager.element    = manager.canvasData.element;
}





function scaleManager (      matrixData, layer ) {
    console.log( 'INITIALIZING SCALE MANAGER: matrixdata %o layer %o', matrixData, layer );
    blockManager( this, matrixData, layer );
    this.init();
}

scaleManager.prototype = {
    update     : function () {
    },
    init       : function () {
        console.log('UPDATING MATRIX SCALE. data: %o info: %o setup: %o', this.data, this.data.getDataInfo(), this.setup);

        this.scope.working   = true;

        var scaleHeight      = this.setup.scaleHeight;
        var scaleSplits      = this.setup.scaleSplits;
        var scaleTextWidth   = this.setup.scaleTextWidth;
        //var scaleBlockHeight = this.setup.scaleBlockHeight;
        var scaleBlockWidth  = this.setup.scaleBlockWidth;

        var info             = this.data.getDataInfo();

        var dmin             = info.minVal;
        var dmax             = info.maxVal;
        var ddif             = dmax - dmin;
        var dfrag            = (ddif        * 1.0) / (scaleSplits);

        var labelYpos        = (scaleHeight / 2.0) + (matrixFontSize/2);


        //var paddingLeft      = scaleTextWidth;
        //var cellW            = scaleBlockWidth;

        console.log("scale height %o splits %o text width %o block width %o info %o dmin %o dmax %o ddif %o dfrag %o labelypos %o",
                    scaleHeight, scaleSplits, scaleTextWidth, scaleBlockWidth, info, dmin,
                    dmax, ddif, dfrag, labelYpos
                    );
        //console.log(labelYpos, scaleHeight, scaleSplits, scaleTextWidth, scaleBlockWidth);
        //console.log("mix %d max %d splits %d frag %f", dmin, dmax, scaleSplits, dfrag);



        var G        = this.layer;
            //G.destroyChildren();
        console.log( "this layer %o before", G );

        //
        // distance scale
        //
        var samples = [];
        var stats   = [];
        for ( var i = dmin; i <= dmax; i+=dfrag) {
            samples.push( i.toFixed(2) );
            stats  .push( 0            );
        }


        var data        = this.data.getMatrix();
        var statsSum    = 0;
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
            statsPro.push( stats[s] / statsSum );
        }
        //console.log(statsSum, stats.reduce(function(a,b){return a+b}), statsPro.reduce(function(a,b){return a+b}));

        var z  = this.data;
        var zx = function( v ) { z.getColorValue(v); };

        var txt2EndPos  = genbar(G, 'Distance', this.setup, zx, 0, labelYpos, dmin, dmax, samples, statsPro);
            txt2EndPos += scaleTextWidth;





        //
        // snps scale
        //
        var snps   = this.data.getHeaderRow('num_snps');
        samples    = [];
        stats      = [];
        statsPro   = [];
        statsSum   = 0;
        var smin   = Math.min.apply( null, snps );
        var smax   = Math.max.apply( null, snps );
        var sSlope = (dmax - dmin) / (smax - smin);
        var sInter = dmin - (sSlope * smin);
        //console.log(snps, dmin, dmax, smin, smax, sSlope, sInter)

        for ( var j = dmin; j <= dmax; j+=dfrag) {
            samples.push( j.toFixed(2) );
            stats  .push( 0            );
        }


        for ( var e = 0; e < snps.length; e++ ) {
            var w = snps[e];
            var f = ( w * sSlope ) + sInter;
            var l = Math.round( f / dfrag );
            //console.log(dmin, dmax, smin, smax, sSlope, sInter, v, d, k);
            //console.log("d %f f %f k %f", d, dfrag, k);
            if ( l >= stats.length ) {
                l = stats.length - 1;
            }
            stats[ l ] += 1;
            statsSum   += 1;
        }

        statsPro = [];

        for ( var t = 0; t < stats.length; t++ ) {
            statsPro.push( stats[t] / statsSum );
        }
        //console.log(statsSum, stats.reduce(function(a,b){return a+b}), statsPro.reduce(function(a,b){return a+b}));

        var zz = function( v ) { z.getColorValueRev(v); };

        txt2EndPos  = genbar(G, '#SNPs', this.setup, zz, txt2EndPos, labelYpos, smin, smax, samples, statsPro);
        txt2EndPos += scaleTextWidth;




        var graphTitle =
                            'Database '   + this.database   + '\n' +
                            'Chromosome ' + this.chromosome + ' '  +
                            'Species '    + this.specie
                        ;

        if (this.groupBy) {
            console.log( "group by: %o", this.groupBy );
            graphTitle += '; Grouping by ' + this.groupBy + ' every ' + this.groupByVal + ' ';
        }

        if (this.clusterSegments) {
            graphTitle += '; Clustering segments ';
        }

        if (this.clusterRows) {
            graphTitle += '; Clustering species ';
        }

        var txt3 = new Kinetic.Text({
            x         : txt2EndPos,
            y         : matrixFontSize * 1.5,
            text      : graphTitle,
            fontSize  : matrixFontSize,
            fontFamily: 'Calibri',
            fill      : 'black'
        });

        G.add( txt3 );
        console.log( "this layer %o after", G );

        //this.layer.draw();
        console.log( "layer drawn", this.layer );

        //this.matrixData.canvas.stage.add( this.layer );

        this.scope.working = false;

        console.log('UPDATING MATRIX SCALE FINISHED');
    }
};

function genbar( g, title, setup, colorFunc, Xpos, Ypos, vmin, vmax, samp, stats ) {
    console.log("GEN BAR: g %o title %o setup %o colorfunc %o xpos %o ypos %o vmin %o vmax %o samp %o stats %o", g, title, setup, colorFunc, Xpos, Ypos, vmin, vmax, samp, stats);

    var txt1txt = title + ': ' + vmin.toFixed(1);

    var txt1 = new Kinetic.Text({
        x         : Xpos,
        y         : Ypos,
        text      : txt1txt,
        fontSize  : matrixFontSize,
        fontFamily: 'Calibri',
        fill      : 'black'
    });

    g.add(txt1);

    var scaleHeight     = setup.scaleHeight;
    var scaleBlockWidth = setup.scaleBlockWidth;

    var textEndPos      = Xpos + (txt1txt.length * pixelPerLetterW);
    var blockHeight     = function(i) { return (0.25+(stats[i]*0.75)) * scaleHeight; };
    var gb              = new Kinetic.Group();

    for ( var s = 0; s < samp.length; s++) {
        var val    = samp[ s ];
        var height = blockHeight(s);
        var y      = scaleHeight - height;
        //console.log('s ',s,' val ',val,colorFunc( val ));

        var rec     = new Kinetic.Rect({
                x     : ( textEndPos + (s * scaleBlockWidth) ),
                y     : y,
                width : scaleBlockWidth,
                height: height,
                fill  : colorFunc( val )
            });


        gb.add(rec);
    }

    g.add(gb);

    var blockEndPos = textEndPos + (samp.length * scaleBlockWidth);

    var txt2txt = vmax.toFixed(1);

    var txt2 = new Kinetic.Text({
        x         : blockEndPos,
        y         : Ypos,
        text      : txt2txt,
        fontSize  : matrixFontSize,
        fontFamily: 'Calibri',
        fill      : 'black'
    });

    g.add(txt2);

    return blockEndPos + (txt2txt.length * pixelPerLetterW);
}




function headerManager (     matrixData, layer ) {
    console.log("INITIALIZING HEADER MANAGER: matrixdata %o layer %o", matrixData, layer);
    blockManager( this, matrixData, layer );
    this.init();
}

headerManager.prototype = {
    update     : function () {
        this.scope.working     = true;

        console.log('UPDATING MATRIX HEADER');


        var axisX              = this.vars.axisX;
        var axisY              = this.vars.axisY;

        var axisTextHeight     = this.vars.axisTextHeight;
        var headerKeys         = this.data.getHeaderKeys();

        var headerX            = this.vars.headerX;
        //var headerY        = this.vars.headerY;

        var colTextHeight      = this.vars.colTextHeight;
        var colTextWidth       = this.vars.colTextWidth;


        var sizeHasChanged    = axisX          != axisX          ||
                                axisY          != axisY          ||
                                axisTextHeight != axisTextHeight ||
                                headerKeys     != headerKeys     ||
                                headerX        != headerX        ||
                                headerY        != headerY        ||
                                colTextHeight  != colTextHeight  ||
                                colTextWidth   != colTextWidth;


        if (sizeHasChanged) {
            console.log('UPDATING MATRIX HEADER - CHANGED - UPDATING');

            this.axisX              = this.vars.axisX;
            this.axisY              = this.vars.axisY;

            this.axisTextHeight     = this.vars.axisTextHeight;
            this.headerKeys         = this.data.getHeaderKeys();

            this.headerX            = this.vars.headerX;
            //var headerY        = this.vars.headerY;

            this.colTextHeight      = this.vars.colTextHeight;
            this.colTextWidth       = this.vars.colTextWidth;

            var header = this.layer;

            var Gaxis  = header.axis.getChildren();

            for ( var row = 0; row < Gaxis.length; row++) {
                var child   = Gaxis[ row ];
                child.x( 0                    );
                child.y( row * axisTextHeight );
            }


            var Gchildren = header.cols.getChildren();

            for ( var c = 0; c < Gchildren.length; c++ ) { //svg lines
                var Gchild = Gchildren[c];
                //Gchild.setAttributeNS(null, 'x'    , headerX           + 'em' );
                //Gchild.setAttributeNS(null, 'y'    , c * colTextHeight + 'em' );
                Gchild.x( headerX           );
                Gchild.y( c * colTextHeight );

                var grandchildren = Gchild.getChildren();

                var rowName       = headerKeys[ c ];

                for ( var gc = 0; gc < grandchildren.length; gc++ ) {
                    var grandchild = grandchildren[gc];
                    var realVal    = this.data.getHeaderVal( rowName, gc );
                    //console.log(c, gc, grandchild, realVal);

                    grandchild.text( realVal           );
                    grandchild.x(    gc * colTextWidth );
                    grandchild.y(    0                 );
                }
            }

            this.layer.draw();

            console.log('UPDATING MATRIX HEADER - CHANGED - UPDATED');

        } else { // no size change. ignore
            console.log('UPDATING MATRIX HEADER - NOT CHANGED - SKIPPING');
        }

        this.scope.working = false;
    },
    init       : function () {
        console.log('UPDATING MATRIX HEADER');

        this.scope.working     = true;

        this.axisX              = this.vars.axisX;
        this.axisY              = this.vars.axisY;

        this.axisTextHeight     = this.vars.axisTextHeight;
        this.headerKeys         = this.data.getHeaderKeys();

        this.headerX            = this.vars.headerX;
        //var headerY        = this.vars.headerY;

        this.colTextHeight      = this.vars.colTextHeight;
        this.colTextWidth       = this.vars.colTextWidth;


        var header             = this.layer;
        header.x(       this.axisX           );
        header.y(       this.axisY           );
        header.visible( this.vars.showHeader );

        //if ( $element.children().length && this.canvas && this.canvas.header && this.canvas.header.hasChildren() ) { //cells already exists

        console.log('UPDATING MATRIX HEADER - DOES NOT EXISTS - CREATING');
        var axis = new Kinetic.Group();
        var cols = new Kinetic.Group();

        header.add( axis );
        header.add( cols );

        header.axis = axis;
        header.cols = cols;

        for ( var row = 0; row < this.headerKeys.length; row++) {
            var val     = this.data.getHeaderConvKey( this.headerKeys[row] );

            var nel     = new Kinetic.Text({
                x         : 0,
                y         : row * this.axisTextHeight,
                text      : val,
                fontSize  : matrixFontSize,
                fontFamily: 'Calibri',
                fill      : 'black'
            });

            axis.add( nel );
        }


        for ( var row = 0; row < this.headerKeys.length; row++) {
            var nel    = new Kinetic.Group({
                x: this.headerX,
                y: row * this.colTextHeight
            });

            var rowName = this.headerKeys[ row ];
            var rowData = this.data.getHeaderRow(rowName);

            for ( var col = 0; col < rowData.length; col++ ) {
                var realVal = this.data.getHeaderVal( rowName, col);
                var txt     = new Kinetic.Text({
                    x         : col * this.colTextWidth,
                    y         : 0,
                    text      : realVal,
                    fontSize  : matrixFontSize,
                    fontFamily: 'Calibri',
                    fill      : 'black'
                });

                nel.add( txt );
            }

            cols.add( nel );
        }

        this.scope.working = false;
        this.layer.draw();

        console.log('UPDATING MATRIX HEADER FINISHED');
    }
};





function rowsManager(       matrixData, layer ) {
    console.log("INITIALIZING ROWS MANAGER: matrixdata %o layer %o", matrixData, layer);
    blockManager( this, matrixData, layer );
    this.init();
}

rowsManager.prototype = {
    update     : function () {
    },
    init       : function () {
        console.log('UPDATING MATRIX ROWS');

        this.scope.working = true;

        var rowNamesX      = this.vars.rowNamesX;
        var rowNamesY      = this.vars.rowNamesY;
        var rowTextHeight  = this.vars.rowTextHeight;

        var names          = this.data.getNames();

        var rep            = this.layer;
            rep.destroyChildren();
            rep.x(       rowNamesX         );
            rep.y(       rowNamesY         );
            //rep.visible( this.vars.showRow );

        console.log('UPDATING MATRIX ROWS CREATING', rowTextHeight);

        for ( var row = 0; row < names.length; row++) {
            var realVal = this.data.getNamesVal( row );
            //console.log("row %d val %o", row, realVal);

            var nel     = new Kinetic.Text({
                x         : 0,
                y         : row * rowTextHeight,
                text      : realVal,
                fontSize  : matrixFontSize,
                fontFamily: 'Calibri',
                fill      : 'black'
            });

            rep.add(nel);
        }

        this.scope.working = false;

        this.layer.draw();

        console.log('UPDATING MATRIX ROWS FINISHED');
    }
};




function bodyManager (       matrixData, layer ) {
    console.log("INITIALIZING BODY MANAGER: matrixdata %o layer %o", matrixData, layer);
    blockManager( this, matrixData, layer );
    this.init();
}

bodyManager.prototype = {
    update     : function () {
        this.scope.working     = true;

        //if ( this.element.children().length && this.canvas && this.canvas.body && this.canvas.body.hasChildren() ) { //cells already exists
        console.log('UPDATING MATRIX BODY EXISTS');
        //console.log('UPDATING MATRIX BODY. EXISTS %o %o %o', $element.children().length, this.svg, this.svg.matrix);


        var matrixx            = this.vars.matrixX;
        var matrixy            = this.vars.matrixY;
        var cellheight         = this.vars.cellHeight;
        var cellwidth          = this.vars.cellWidth;
        var matrixHeight       = this.vars.matrixHeight;

        var sizeHasChanged     = matrixx      != this.matrixx      ||
                                 matrixy      != this.matrixy      ||
                                 cellheight   != this.cellheight   ||
                                 cellwidth    != this.cellwidth    ||
                                 matrixHeight != this.matrixHeight;


        if ( sizeHasChanged ) {
            console.log('UPDATING MATRIX BODY. UPDATING DOM');

            var matrix    = this.layer;
            //var matrix2   = this.canvas.body2;
            var children  = matrix.getChildren();

            this.matrixx           = matrixX;
            this.matrixy           = matrixY;
            this.cellheight        = cellHeight;
            this.cellwidth         = cellWidth;
            this.matrixHeight      = matrixHeight;

            matrix.x(      matrixx      );
            matrix.y(      matrixy      );
            matrix.cw(     cellwidth    );
            matrix.ch(     cellheight   );
            matrix.height( matrixHeight );


            for ( var c = 0; c < children.length; c++ ) { //svg lines
                var child = children[c];
                //console.log(c, child);

                if ( sizeHasChanged ) {
                    child.x( 0              );
                    child.y( c * cellheight );
                }

                var grandchildren = child.getChildren();

                for ( var gc = 0; gc < grandchildren.length; gc++ ) {
                    var grandchild = grandchildren[gc];
                    //console.log(c, gc, grandchild);
                    var realVal = this.getMatrixVal(c, gc);

                    if ( sizeHasChanged ) {
                        grandchild.x(      gc * cellwidth );
                        grandchild.y(      0              );
                        grandchild.width(  cellwidth      );
                        grandchild.height( cellheight     );
                    }

                    grandchild.fill( this.data.getColorValue( realVal ) );
                }
            }

            this.layer.draw();

            console.log('UPDATING MATRIX BODY. UPDATING DOM');
        } else { // SIZE HAS NOT CHANGED. SKIPPING
            console.log('UPDATING MATRIX BODY. SKIPPING');
        }

        this.scope.working     = false;
    },
    init       : function () {
        console.log('INITIALIZING MATRIX BODY');

        //console.log('UPDATING MATRIX BODY %o %o %o', this, $element, attrs);

        this.scope.working     = true;

        this.matrixx           = this.vars.matrixX;
        this.matrixy           = this.vars.matrixY;
        this.cellheight        = this.vars.cellHeight;
        this.cellwidth         = this.vars.cellWidth;
        this.matrixHeight      = this.vars.matrixHeight;

        console.log( this.matrixx, this.matrixy );

        console.log('UPDATING MATRIX BODY DOES NOT EXISTS. EMPTYING');
        //console.log('UPDATING MATRIX BODY. EMPTYING %o %o %o', $element.children().length, this.svg, this.svg.matrix);

        //$element.empty();

        console.log('UPDATING MATRIX BODY. GETTING MATRIX');

        var line               = this.data.getMatrix();

        console.log('UPDATING MATRIX BODY. GOT MATRIX');


        console.log('UPDATING MATRIX BODY. SETTING SIZE');
        var matrix        = this.layer;
            matrix.x(       this.matrixx      );
            matrix.y(       this.matrixy      );
            matrix.height(  this.matrixHeight );
            matrix.cw     = this.cellwidth;
            matrix.ch     = this.cellheight;

            //var matrix2 = this.canvas.body2 = new Kinetic.Stage({
            //    x     :  matrixx     ,
            //    y     :  matrixy     ,
            //    height:  matrixHeight,
            //    containner: 'invi'
            //});

            //this.canvas.body2 = matrix2;


        for ( var row = 0; row < line.length; row++) {
            console.log('UPDATING MATRIX BODY. ADDING ROW ', row);
            var nel    = new Kinetic.Group({
                x: 0,
                y: (row+1) * this.cellheight
            });

            var rowData = this.data.getMatrixRow( row );
            var nels    = [];

            for ( var col = 0; col < rowData.length; col++ ) {
                //console.log('UPDATING MATRIX BODY. ADDING COL ', col);
                var realVal = this.data.getMatrixVal(  row, col );
                var fillC   = this.data.getColorValue( realVal  );

                var rec     = new Kinetic.Rect({
                        x     : col * this.cellwidth,
                        y     : 0,
                        width : this.cellwidth,
                        height: this.cellheight,
                        fill  : fillC
                    });

                //rec.onclick     = function(c  ) { return function(  ) { this.showCoord(c);        }; }(    col);
                //rec.onmouseover = function(r,c) { return function(ev) { this.showTooltip(ev, r, c)}; }(row,col);
                nel.add( rec );
            }
            matrix.add( nel );
        }


        //console.log('UPDATING MATRIX BODY. CONVERTING TO IMAGE');
        //matrix2.toDataURL({
        //    callback: function(dataURL){
        //        console.log('UPDATING MATRIX BODY. CONVERTED TO IMAGE');
        //        //matrix.clear();
        //        //
        //        //var img        = new Image();
        //        //    img.src    = dataURL;
        //        //    img.onload = function(){
        //        //console.log('UPDATING MATRIX BODY. IMAGE LOADED');
        //        //var matrixImg  = new Kinetic.Image();
        //        //matrixImg.setImage(img);
        //        //matrixImg.setX(matrixImg.getWidth()  >> 1);
        //        //matrixImg.setY(matrixImg.getheight() >> 1);
        //        //matrix.add(matrixImg);
        //        //console.log('UPDATING MATRIX BODY. IMAGE SET');
        //        //};
        //    }
        //});
        //console.log('UPDATING MATRIX BODY. ADDED LINE', row);

        console.log('UPDATING MATRIX BODY. APPENDDED TO DOM');

        this.layer.draw();

        this.scope.working = false;
    }
};




function introgressManager (      matrixData, layer ) {
    console.log("INITIALIZING INTROGRESS MANAGER: matrixdata %o layer %o", matrixData, layer);
    blockManager( this, matrixData, layer );
    this.init();
}

introgressManager.prototype = {
    update                  : function () {
        this.scope.working            = true;

        var introgressWidth           = this.vars.introgressWidth;
        var introgressHeight          = this.vars.introgressHeight;
        var introgressLineHeight      = this.vars.introgressLineHeight;
        var cellWidth                 = this.vars.cellWidth;

        var valids                    = this.canvasData.getSelectedIntrogress();

        var sizeHasChanged            = this.introgressHeight     != introgressHeight     ||
                                        this.introgressWidth      != introgressWidth      ||
                                        this.introgressLineHeight != introgressLineHeight ||
                                        this.cellWidth            != cellWidth;


        if ( sizeHasChanged ) {
            this.introgressHeight         = introgressHeight;
            this.introgressWidth          = introgressWidth;
            this.introgressLineHeight     = introgressLineHeight;
            this.cellWidth                = cellWidth; //}
        }

        //this.svg.introgress.attr('ih'   , introgressHeight + 'em' );
        //this.svg.introgress.attr('iw'   , introgressWidth  + 'em' );


        for ( var l = 0 ; l < valids.length; l++ ) {
            var linedata = valids[l];

            //console.log("SPP %d %s %o %o", l, spp, linedata, linedata.checked);

            if ( linedata.checked ) { // button checked
                if ( ! linedata.svg1 ) { // button checked but html does not exists
                    console.log("SPP %d %s CHECKED %o", l, linedata.name, linedata);
                    this.plot( l, linedata );

                } else { // button checked and html exists
                    console.log("SPP %d %s HTML EXISTS", l, linedata.name);

                    if ( sizeHasChanged ) { //size has changed
                        console.log("SPP %d %s HTML EXISTS. SIZE HAS CHANGED. UPDATING", l, linedata.name);
                        this.setPos( linedata.svg1, linedata.svg2, linedata.name );
                    } else {
                        console.log("SPP %d %s HTML EXISTS. SIZE HAS NOT CHANGED. SKIPPING", l, linedata.name);
                    }
                }
            } else { // not selected
                console.log("SPP %d %s NOT CHECKED %o", l, linedata.name, linedata);
                if ( linedata.svg1 ) { // not selected but showing
                    console.log("SPP %d %s HTML EXISTS. DELETING", l, linedata.name);
                    linedata.el.parent.removeChild( linedata.el ); // delete
                    console.log("SPP %d %s HTML EXISTS. DELETED", l, linedata.name);
                } else { // nothig to do
                    console.log("SPP %d %s HTML DOES NOT EXISTS. SKIPPING", l, linedata.name);
                }
            }
        }

        if (sizeHasChanged) {
            this.layer.draw();
        }

        this.scope.working    = false;
    },
    init                    : function () {
        console.log('UPDATING MATRIX INTROGRESS');

        this.scope.working            = true;

        var introgressHeight          = this.vars.introgressHeight;
        var introgressWidth           = this.vars.introgressWidth;
        var introgressLineHeight      = this.vars.introgressLineHeight;
        var cellWidth                 = this.vars.cellWidth;

        this.introgressHeight         = introgressHeight;
        this.introgressWidth          = introgressWidth;
        this.introgressLineHeight     = introgressLineHeight;
        this.cellWidth                = cellWidth;

        var valids                    = this.canvasData.getSelectedIntrogress();

        for ( var l = 0 ; l < valids.length; l++ ) {
            var linedata = valids[l];

            //console.log("SPP %d %s %o %o", l, spp, linedata, linedata.checked);

            if ( linedata.checked ) {
                this.plot( l, linedata );
            }
        }

        this.layer.draw();

        this.scope.working = false;

        console.log('UPDATING MATRIX INTROGRESS DONE');
    },
    pathmouseover           : function ( ev ) {
        console.log( ev   );
        //console.log( this );

        var bbox        = this.getBoundingClientRect();
        //console.log(bbox);
        //console.log(this.getBoundingClientRect());
        //console.log(this.parentNode.getBoundingClientRect());
        //console.log(this.parentNode.parentNode.getBoundingClientRect());
        //console.log(this.parentNode.parentNode.parentNode.getBoundingClientRect());
        //console.log(this.parentNode.parentNode.parentNode.parentNode.getBoundingClientRect());

        var spp         = this.getAttribute( 'spp' );
        var sppPos      = this.getNames().indexOf( spp );
        var paddingLeft = this.getBoundingClientRect().left - this.parentNode.parentNode.getBoundingClientRect().left;
        var pX          = ev.pageX;
        var pY          = ev.pageY;
        var x           = ev.x;
        var y           = ev.y;
        var xpos        = pX - paddingLeft;
        var max         = this.vars.numCols - 1;
        var width       = bbox.width;
        var pxperx      = (width / max);
        var pos         = Math.round(xpos/pxperx) - 1;

        console.log("paddingLeft %d x %d xpos %d max %d width %d pxperx %d pos %d spp %s", paddingLeft, pX, xpos, max, width, pxperx, pos, spp);

        this.showCommonAncestor(spp, pX, pY, x, y, pos);
    },
    pathmouseout            : function ( ev ) {
        console.log('mouse out');
        var $sel = $('#tree_render_small');
        if ( $sel.length > 0 ) {
            $sel.remove();
        }
    },
    showCommonAncestor      : function ( spp, pX, pY, x, y, pos ) {
        console.log("showing common ancestor pX %d pY %d x %d y %d pos %d", pX, pY, x, y, pos);

        var ancesterTree = this.getCommonAncerstorTree(spp, pos);

        var numSpps = ancesterTree.split(',').length;

        var width   = (($(window).width() - x) - 20) * 0.6;
        var height  = (y - 20                      ) * 0.8;

        var effX    = pX          + 10;
        var effY    = pY - height - 10;

        console.log( "width %d height %d effX %d effY %d", width, height, effX, effY );

        this.pathmouseout(null);

        $('<div>', {'id': 'tree_render_small'})
            .css( 'top'     ,       effY )
            .css( 'left'    ,       effX )
            .css( 'height'  ,     height )
            .css( 'width'   ,      width )
            .css( 'position', 'absolute' )
            .css( 'z-index' ,        200 )
                .appendTo( $('body') )
        ;

        console.log('spps %d h %d w %d (%d)', numSpps, height, width, $(window).width());

        var svgSrc = insertTree( ancesterTree, 'tree_render_small', width-20, height-20);
    },
    getCommonAncerstorTree  : function ( spp, pos ) {
        console.log("getting common ancestor tree for spp %s pos %d", spp, pos);
        var data  = this.introgressData[ spp ].data;
        var k1    = Object.keys( data  )[ 0 ];
        var data1 = data[  k1 ];
        var k2    = Object.keys( data1 )[ 0 ];
        var data2 = data1[ k2 ];
        console.log(data );
        console.log(k1   );
        console.log(data1);
        console.log(k2   );
        console.log(data2);
        var tree = data2[ pos ].tree;
        //console.log(tree);
        return tree;
    },
    setPos                  : function ( svg1, svg2, name ) {
            svg1.setAttributeNS(null, 'x'                  , 0                         + 'em' );
            svg1.setAttributeNS(null, 'y'                  , y                         + 'em' );
            svg1.setAttributeNS(null, 'height'             , this.introgressLineHeight + 'em' );
            svg1.setAttributeNS(null, 'width'              , this.introgressWidth      + 'em' );

            svg2.setAttributeNS(null, 'x'                  , this.cellWidth            + 'em' );
            svg2.setAttributeNS(null, 'y'                  , 0                         + 'em' );
            svg2.setAttributeNS(null, 'height'             , this.introgressLineHeight + 'em' );
            svg2.setAttributeNS(null, 'width'              , this.introgressWidth      + 'em' );
            svg2.setAttributeNS(null, 'preserveAspectRatio',                            'none');
            svg2.setAttributeNS(null, 'spp'                ,                             name );

            svg2.onmouseout  = this.pathmouseout;
            svg2.onmouseover = this.pathmouseover;


            //linedata.html = data2path( linedata.data       );
            //for ( var d = 0; d < data.length; d++) {
            //    data[d] = data[d] * (l+2);
            //}

            //$element.attr('width' , this.vars.svgWidth       + 'px');
            //$element.attr('height', validCount * introgressheight + 'px');
    },
    plot                    : function ( l, linedata ) {
        console.log("SPP %d %s CHECKED %o", l, linedata.name, linedata);
        console.log("SPP %d %s CREATING HTML", l, linedata.name);

        var svg1 = document.createElementNS( xmlns, 'svg' );

        var svg2 = document.createElementNS( xmlns, 'svg' );

        this.setPos( svg1, svg2, linedata.name );

        var txt1 = document.createElementNS( xmlns, 'text' );
            txt1.setAttributeNS(null, 'x'                  , 0+'em'                           );
            txt1.setAttributeNS(null, 'y'                  , 1+'em'                           );
            txt1.setAttributeNS(null, 'font-size'          ,   '12'                           );
            txt1.appendChild(   document.createTextNode( linedata.name ) );

        svg1.appendChild(txt1);
        svg1.appendChild(svg2);


        (
            function( C, R, D, S, numCols ) {
                var tgt = D.name;
                //var pbd = pdbURL+'/pbd/'+C+'/'+R+'/'+tgt+'/Median%20-%201MAD/PhyloSor';
                var pbds = pdbURL+'/pbds/'+C+'/'+R+'/'+tgt;
                console.log( pbds );
                $http.get(pbds)
                    .success(
                        function(Ddata) {
                            var data = Ddata.pbds;

                            console.log(data);
                            D.data   = data;

                            var distsG       = [];
                            var selectorKeys = Object.keys( data );
                            console.log("selectorKeys", selectorKeys);

                            for ( var selectorPos = 0; selectorPos < selectorKeys.length; selectorPos++ ) {
                                var selector = selectorKeys[ selectorPos ];
                                console.log("selector", selector);

                                var methods     = data[ selector ];
                                var methodsKeys = Object.keys( methods );

                                for ( var methodPos = 0; methodPos < methodsKeys.length; methodPos++ ) {
                                    var method = methodsKeys[ methodPos ];
                                    console.log("method", method);
                                    var dists   = methods[ method ];

                                    for ( var d = 0; d < dists.length; d++ ) {
                                        var dist = dists[d].dist;
                                        distsG.push( dist );
                                    }
                                }
                            }




                            var datamax = Math.max.apply(null, distsG);
                            var datamin = Math.min.apply(null, distsG);
                            var datadif = datamin + datamax;

                            if (datamin < 0) {     //-5
                                if (datamax < 0) { // -5 -3
                                    datadif = Math.abs(datamin  - datamax); // -5 - -3 = -5 + 3 = abs(-2) = 2
                                } else {           // -5  3
                                    datadif = Math.abs(datamin) - datamax; // abs(-5) +  3 = 5 + 3 = 8
                                }
                            } else { // 5 3
                                    datadif = datamax - datamin;
                            }

                            console.log(datamin, datamax, datadif);

                            var vb      = "0 0 " + numCols + " " + datadif;

                            S.setAttributeNS(null, 'viewBox', vb);



                            var lineNum    =  0;
                            var lWidth     =  0.10;
                            var lineColors = ["red", "blue", "green", "black"];

                            for ( var selectorPos = 0; selectorPos < selectorKeys.length; selectorPos++ ) {
                                var selector = selectorKeys[ selectorPos ];
                                console.log("selector", selector);

                                var methods     = data[ selector ];
                                var methodsKeys = Object.keys( methods );

                                for ( var methodPos = 0; methodPos < methodsKeys.length; methodPos++ ) {
                                    var method = methodsKeys[ methodPos ];
                                    console.log("method", method);
                                    var dists   = methods[ method ];
                                    //console.log('pdb got data C %o R %o D %o S %o tgt %o Ddata %o data %o', C, R, D, S, tgt, Ddata, data);
                                    var distsL  = [];

                                    for ( var d = 0; d < dists.length; d++ ) {
                                        var dist  = dists[d].dist;
                                        var rDist = datadif - dist; // min= 1 max=5 dif=4 val=3 dif-val=4-3=1 val=1 4-1=4
                                        //if ( datamin < 0) {         // min=-1 max=5 dif=6 val=3 dif-val=6-
                                            //code
                                        //}
                                        distsL.push( rDist );
                                    }
                                    console.log(distsL);

                                    var lColor = lineColors[ lineNum ];
                                    var path   = data2path( distsL, lColor, lWidth );

                                    S.appendChild( path );
                                    lineNum += 1;

                                    //var box = document.createElementNS( xmlns,  'rect');
                                    //box.setAttributeNS( null, "x"           ,      "0");
                                    //box.setAttributeNS( null, "y"           ,      "0");
                                    //box.setAttributeNS( null, "width"       ,  numCols);
                                    //box.setAttributeNS( null, "height"      ,  datamax);
                                    //box.setAttributeNS( null, "fill"        ,  "green");
                                    //
                                    //S.appendChild( box               );
                                }
                            }
                        }
                    );
            }
        )(this.chromosome, this.specie, linedata, svg2, this.vars.numCols);

        linedata.svg1    = svg1;
        linedata.svg2    = svg2;
        linedata.el      = this.element.append( linedata.svg1 );
    }
};











      function getRandomColor() {
            var colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple'];
            var val = Math.random() * 5;
            return colors[Math.round(val)];
      }


function matrixManager( canvasData ) {
    console.log("INITIALIZING MATRIX MANAGER: canvasdata %o", canvasData);

    this.canvasData = canvasData;
    this.scope      = canvasData.scope;
    this.setup      = canvasData.setup;
    this.species    = canvasData.species;
    this.data       = canvasData.data;
    this.canvas     = canvasData.canvas;
    this.vars       = canvasData.vars;
    this.element    = document.getElementById( canvasID );

    this.init();
}

matrixManager.prototype = {
    init            : function () {
        console.log('matrix manager INIT. canvas ID %s', canvasID);

        var stageConf = {
            container : canvasID,
            width     : this.vars.svgWidth  + 'px',
            height    : this.vars.svgHeight + 'px',
            //scaleX    : this.vars.svgWidthScale,
            //scaleY    : this.vars.svgHeightScale,
            draggable : false
        };

        console.log('HAS UPDATE IN CANVAS - NO CANVAS - CREATING: conf: %o', stageConf);

        this.canvas.stage = new Kinetic.Stage(stageConf);

        //this.canvas.eventLayer = new Kinetic.Layer();
        //this.canvas.eventLayer.add(
        //    new Kinetic.Rect({
        //        x     : 0,
        //        y     : 0,
        //        width : this.vars.svgHeightMax,
        //        height: this.vars.svgWidthMax
        //    })
        //);

        this.canvas.scale      = new Kinetic.Layer();
        this.canvas.header     = new Kinetic.Layer();
        this.canvas.rows       = new Kinetic.Layer();
        this.canvas.body       = new Kinetic.Layer();
        this.canvas.introgress = new Kinetic.Layer();

      var layer = new Kinetic.Layer();

      for(var n = 0; n < 10; n++) {
        var radius   = Math.random() * 100 + 20;
        var colornum = getRandomColor();
        var color    = Kinetic.Util.getRGB(colornum);
        var shape    = new Kinetic.RegularPolygon({
          x: Math.random() * this.canvas.stage.getWidth(),
          y: Math.random() * this.canvas.stage.getHeight(),
          sides: Math.ceil(Math.random() * 5 + 3),
          radius: radius,
          fillRed: color.r,
          fillGreen: color.g,
          fillBlue: color.b,
          opacity: (radius - 20) / 100,
          draggable: true
        });

        layer.add(shape);
      }



        //this.scaleManager      = new scaleManager(      this, this.canvas.scale      );
        //this.headerManager     = new headerManager(     this, this.canvas.header     );
        //this.rowsManager       = new rowsManager(       this, this.canvas.rows       );
        //this.bodyManager       = new bodyManager(       this, this.canvas.body       );
        //this.introgressManager = new introgressManager( this, this.canvas.introgress );

        console.log('HAS UPDATE IN CANVAS - ADDING LAYERS');
        this.canvas.stage
            //.add( this.canvas.scale      )
            .add( layer     )
            //.add( this.canvas.rows       )
            //.add( this.canvas.body       )
            //.add( this.canvas.introgress )
            //.add( this.canvas.eventLayer )
        ;

        console.log('HAS UPDATE IN CANVAS - ADDING LAYERS FINISHED');


        this.canvas.stage.draw();

        console.log('HAS UPDATE IN CANVAS - CALLING');


        //if (this.hasUpdatesScale) {
        //    this.funcs.matrix.scale(this, $element, attrs);
        //    if (!doFullRedraw) {
        //        console.log('HAS UPDATE IN CANVAS - NO NEED TO FULL REDRAW - ONLY SCALE');
        //        this.canvas.scale.draw();
        //    }
        //}
        //
        //if (this.hasUpdatesHeader) {
        //    this.funcs.matrix.header(this, $element, attrs);
        //    if (!doFullRedraw) {
        //        console.log('HAS UPDATE IN CANVAS - NO NEED TO FULL REDRAW - ONLY HEADER');
        //        this.canvas.header.draw();
        //    }
        //}
        //
        //if (this.hasUpdatesRows) {
        //    this.funcs.matrix.rows(this, $element, attrs);
        //    if (!doFullRedraw) {
        //        console.log('HAS UPDATE IN CANVAS - NO NEED TO FULL REDRAW - ONLY ROWS');
        //        this.canvas.rows.draw();
        //    }
        //}
        //
        //if (this.hasUpdatesBody) {
        //    this.funcs.matrix.body(this, $element, attrs);
        //    if (!doFullRedraw) {
        //        console.log('HAS UPDATE IN CANVAS - NO NEED TO FULL REDRAW - ONLY BODY');
        //        this.canvas.body.draw();
        //    }
        //}
        //
        //if (this.hasUpdatesIntrogress) {
        //    //this.funcs.matrix.introgress(this, $element, attrs);
        //    if (!doFullRedraw) {
        //        console.log('HAS UPDATE IN CANVAS - NO NEED TO FULL REDRAW - ONLY INTROGRESS');
        //        this.canvas.introgress.draw();
        //    }
        //}
        //
        //
        //
        //if (doFullRedraw) {
        //    console.log('HAS UPDATE IN CANVAS - FULL REDRAW');
        //
        //    this.controller.reset();
        //    this.canvas.stage.draw();
        //
        //    console.log('HAS UPDATE IN CANVAS - FULL REDRAW FINISHED');
        //}

        console.log('HAS UPDATE IN CANVAS - CALLED');

        //<g svgmatrix hasupdates='hasUpdatesScale'  func='funcs.matrix.scale'></g>
        //
        //<svg class="matrixbody" x="0em" data-ng-attr-y="{{ vars.scaleHeight || 0 }}em">
        //    <g svgmatrix hasupdates='hasUpdatesHeader' func='funcs.matrix.header' show='vars.showHeader'></g>
        //
        //    <g svgmatrix hasupdates='hasUpdatesRows'   func='funcs.matrix.rows'   show='vars.showRow'></g>
        //
        //    <g svgmatrix hasupdates='hasUpdatesBody'   func='funcs.matrix.body'></g>
        //</svg>
        //
        //<svg class="introgressbody" data-ng-attr-x="{{ vars.introgressX || 0 }}em" data-ng-attr-y="{{ vars.introgressY || 0}}em" data-ng-attr-width="{{ vars.introgressWidth || 0 }}em" data-ng-attr-height="{{ vars.introgressHeight || 0}}em">
        //    <g svgmatrix hasupdates='hasUpdatesIntrogress' func='funcs.matrix.introgress'></g>
        //</svg>-->

        console.log('matrix manager INITED');
    },
    update          : function () {
        console.log('matrix manager UPDATE');



        console.log('matrix manager UPDATED');
    }
};




var canvasManager = function ( $scope, data ) {
    console.log("INITIALIZING CANVAS MANAGER: scope %o data %o", $scope, data);

    this.scope            = $scope;
    this.setup            = $scope.setup;
    this.species          = $scope.species;

    this.vars             = {};
    this.vars.currColor   = 'red';
    this.vars.scaleHeight = this.setup.scaleHeight;
    this.initiated        = true;
    this.cluster          = null;
    this.report           = null;
    this.svg              = {};
    this.canvas           = {};
    this.introgressData   = {};

    console.log( 'creating data: scope %o setup %o species %o', this.scope, this.setup, this.species );

    this.data             = new dataManager( $scope.setup, this.vars, data );
    this.updateSizes();

    console.log( 'plotting data %o', this.data );
    console.log( 'plotting' );
    this.plot();
    console.log( 'plotted' );
};

canvasManager.prototype = {
    controller: {
        moveX        : function ( x ) {
            console.log('moving from X ', this.canvas.stage.x(), ' TO X ', x);
            if ( this.canvas.stage.x() != x ) {
                this.canvas.stage.x( x );
                this.controller.update();
            }
        },
        moveY        : function ( y, u ) {
            console.log('moving from Y ', this.canvas.stage.y(), ' TO Y ', y);
            if ( this.canvas.stage.y() != y ) {
                this.canvas.stage.y( y );
                this.controller.update();
            }
        },
        zoom         : function ( x, y ) {
            console.log('zoom from X ', this.canvas.stage.scaleX(), ' Y ', this.canvas.stage.scaleY(), ' TO X ', x, ' Y ', y);
            if (this.canvas.stage.scaleX() != x || this.canvas.stage.scaleY() != y) {
                this.canvas.stage.scaleX( x );
                this.canvas.stage.scaleY( y );
                this.controller.update();
            }
        },
        update       : function () {
            this.canvas.stage.draw();
        },
        moveRight    : function () {
            var oX = this.canvas.stage.x();
            var oW = this.canvas.stage.width();
            var x  = oX - (oW*0.1);
            this.controller.moveX( x );
        },
        moveLeft     : function () {
            var oX = this.canvas.stage.x();
            var oW = this.canvas.stage.width();
            var x  = oX + (oW*0.1);
            this.controller.moveX( x );
        },
        moveDown     : function () {
            var oY = this.canvas.stage.y();
            var oH = this.canvas.stage.height();
            var y  = oY - (oH*0.1);
            this.controller.moveY( y );
        },
        moveUp       : function () {
            var oY = this.canvas.stage.y();
            var oH = this.canvas.stage.height();
            var y  = oY + (oH*0.1);
            this.controller.moveY( y );
        },
        moveDownFull : function () {
            this.controller.moveY( 0 );
        },
        moveUpFull   : function () {
            var oH = this.canvas.stage.height();
            this.controller.moveY( oH );
        },
        moveLeftFull : function () {
            this.controller.moveX( 0 );
        },
        moveRightFull: function () {
            var oW = this.canvas.stage.width();
            this.controller.moveX( oW );
        },
        zoomOut      : function () {
            var cs = this.canvas.stage.scale();
            var x  = cs.x * 0.9;
            var y  = cs.y * 0.9;
            this.controller.zoom( x, y );
        },
        zoomIn       : function () {
            var cs = this.canvas.stage.scale();
            var x  = cs.x * 1.1;
            var y  = cs.y * 1.1;
            this.controller.zoom( x, y );
        },
        zoomReset    : function () {
            this.controller.zoom( this.vars.svgWidthScale, this.vars.svgHeightScale );
        },
        reset        : function () {
            console.log('reseting', this.canvas.stage.scale(), this.canvas.stage.offset(), this.canvas.stage.x(), this.canvas.stage.y() );
            this.controller.zoomReset();
            this.controller.moveLeftFull();
            this.controller.moveDownFull();
            console.log('resetted', this.canvas.stage.scale(), this.canvas.stage.offset(), this.canvas.stage.x(), this.canvas.stage.y() );
        }
    },
    plot                    : function () {
        for ( var s = 0; s < this.species.length; s++ ) {
            var spp = this.species[s];
            //console.log('adding spp', s, spp);
            this.introgressData[ spp ] = {
                'checked': false,
                'data'   : null,
                'html'   : null,
                'name'   : spp
            };
        }


        console.log('data %o', this.data);

        this.chromosome         = this.chromosomeQry;
        this.specie             = this.specieQry;
        this.database           = this.databaseQry;

        this.vars.showHeader    = this.setup.showHeader;
        this.vars.showRow       = this.setup.showRow;

        this.vars.currColOrder  = 0;
        this.vars.currRowOrder  = 0;

        this.clusterSegments    = false;
        this.clusterRows        = false;

        var header              = this.data.getHeader();
        console.log( 'HEADER', header );
        this.vars.numHeaderRows = Object.keys( header ).length;

        this.vars.numMatrixRows = this.data.getNames().length;

        this.vars.numCols       = this.data.getDataInfo().num_cols;
        this.vars.numRows       = this.data.getDataInfo().num_rows;


        console.log('numHeaderRows %d', this.vars.numHeaderRows);
        console.log('numMatrixRows %d', this.vars.numMatrixRows);
        console.log('numCols       %d', this.vars.numCols      );

        //console.log( 'VARS', this.vars );

        this.vars.order = {
            cols: [
                Array.apply(null, Array(this.vars.numCols)).map(function(_,i){return i;})
            ],
            rows: [
                Array.apply(null, Array(this.vars.numRows)).map(function(_,i){return i;})
            ]
        };

        this.vars.names = this.data.getNames();
        var maxRowNameSize = 0;
        for ( var n = 0; n < this.vars.names.length; n++ ) {
            var nS = this.vars.names[ n ].length;
            maxRowNameSize = nS > maxRowNameSize ? nS : maxRowNameSize;
        }


        this.vars.header = this.data.getHeader();
        var maxColNameSize = 0;
        for ( var k in this.vars.header ) {
            var v = this.vars.header[ k ];

            var nC = k.length;
            maxRowNameSize = nC > maxRowNameSize ? nC : maxRowNameSize;

            for ( var n = 0; n < v.length; n++ ) {
                var nS = String(v[ n ]).length;
                maxColNameSize = nS > maxColNameSize ? nS : maxColNameSize;
            }
        }

        this.setup.rowTextWidth = maxRowNameSize * pixelPerLetterW;
        this.setup.colTextWidth = maxColNameSize * pixelPerLetterW;

        console.log('data: compiling colors');
        this.compileColors();

        console.log('data: updating width and height');
        this.updateWidthHeight();

        console.log('data: compiling cells');
        this.matrix = new matrixManager( this );

        if (this.clusterAlive) {
            console.log('data: asking cluster');
            this.getCluster();
        }
    },
    updateSizes             : function () {
        this.H            = Math.floor($(window).height() * 0.99);
        this.W            = Math.floor($(window).width()  * 0.99);
        this.maxH         = Math.floor(this.H             * 0.95);
        this.maxW         = Math.floor(this.W             * 0.95);
    },
    compileColors           : function () {
        var minV  = this.data.getMinVal();
        var maxV  = this.data.getMaxVal();

        for ( var color in this.setup.colors ) {
            console.log("compiling color ", color);

            this.setup.colors[ color ].colorScale    = getColors( minV, maxV, this.setup.colors[ color ].colorsNames    );
            this.setup.colors[ color ].colorScaleRev = getColors( minV, maxV, this.setup.colors[ color ].revColorsNames );
        }
    },
    updateWidthHeight       : function () {
        this.updateSizes();

        this.vars.axisTextWidth = this.setup.rowTextWidth;

        if (this.vars.showHeader) {
            this.vars.colTextWidth   = this.setup.colTextWidth;
            this.vars.colTextHeight  = this.setup.textHeight;
            this.vars.cellWidth      = this.setup.colTextWidth;
            this.vars.axisTextHeight = this.setup.textHeight;

        } else {
            this.vars.colTextWidth   = 0;
            this.vars.colTextHeight  = 0;
            this.vars.cellWidth      = this.setup.cellWidth;
            this.vars.axisTextHeight = 0;

        }



        if (this.vars.showRow) {
            this.vars.rowTextWidth   = this.setup.rowTextWidth;
            this.vars.rowTextHeight  = this.setup.textHeight;
            this.vars.cellHeight     = this.setup.textHeight;

        } else {
            this.vars.rowTextWidth   = 0;
            this.vars.rowTextHeight  = 0;
            this.vars.cellHeight     = this.setup.cellHeight;

        }

        console.log( 'cellHeight ', this.vars.cellHeight );


        if (this.vars.showHeader || this.vars.showRow) {
            this.vars.axisTextWidth  = this.setup.rowTextWidth;
        } else {
            this.vars.axisTextWidth  = 0;
        }


        this.vars.introgressLineHeight = this.setup.introgressHeight;
        var axixHeight     = this.vars.numHeaderRows              * this.vars.colTextHeight;
        var headerHeight   = this.vars.colTextHeight;
            headerHeight   = this.vars.colTextHeight > axixHeight ? this.vars.colTextHeight : axixHeight;

        var matrixColWidth = this.vars.showHeader ? this.vars.cellHeight * this.vars.numHeaderRows : this.vars.cellWidth;


        this.vars.axisX                = this.setup.paddingLeft;
        this.vars.axisY                = this.setup.scaleHeight;
        this.vars.axisWidth            = this.setup.axisTextWidth;
        this.vars.axisHeight           = headerHeight;

        this.vars.headerX              = this.setup.paddingLeft              + this.vars.axisTextWidth;
        this.vars.headerY              = this.setup.scaleHeight;
        this.vars.headerHeight         = headerHeight;
        //this.vars.numHeaderRows             * this.vars.colTextHeight;

        this.vars.rowNamesX            = this.setup.paddingLeft;
        this.vars.rowNamesY            = this.vars.headerY                   + this.vars.headerHeight;

        this.vars.matrixX              = this.setup.paddingLeft              + this.vars.axisTextWidth;
        this.vars.matrixY              = this.vars.headerHeight              + this.setup.scaleHeight;
        this.vars.matrixHeight         = this.vars.numMatrixRows             * this.vars.cellHeight                + this.vars.cellHeight;
        //this.vars.matrixWidth          = this.vars.numCols                   * this.vars.cellWidth;
        this.vars.matrixWidth          = this.vars.numCols                   * matrixColWidth;

        this.vars.introgressY          = this.setup.scaleHeight              + this.vars.matrixY                   + this.vars.matrixHeight;
        this.vars.introgressX          = this.vars.matrixX;
        this.vars.introgressHeight     = this.getSelectedIntrogress().length * this.vars.introgressLineHeight;
        this.vars.introgressWidth      = this.vars.matrixWidth;

        //MAX WIDTH 32767
        //this.vars.svgHeight            = this.setup.scaleHeight              + this.vars.headerHeight              + this.vars.matrixHeight + this.vars.introgressHeight;
        //this.vars.svgWidth             = this.vars.axisTextWidth             + this.vars.matrixWidth;

        this.vars.svgHeight            = this.maxH;
        this.vars.svgWidth             = this.maxW;

        this.vars.svgHeightMax         = this.setup.scaleHeight              + this.vars.headerHeight              + this.vars.matrixHeight   + this.vars.introgressHeight;
        this.vars.svgWidthMax          = this.vars.axisTextWidth             + this.vars.matrixWidth;

        var scaleH = Math.floor( this.vars.svgHeight / ( this.vars.svgHeightMax * 1.01 ) );
        var scaleW = Math.floor( this.vars.svgWidth  / ( this.vars.svgWidthMax  * 1.01 ) );
        var scale  = scaleH < scaleW ? scaleW : scaleH;

        this.vars.svgHeightScale       = scale;
        this.vars.svgWidthScale        = scale;



        //console.log( this.getSelectedIntrogress().length, this.vars.introgressLineHeight     , this.vars.introgressHeight, this.getSelectedIntrogress().length * this.vars.introgressLineHeight );
        //console.log( this.setup.scaleHeight             , this.vars.headerHeight             , this.vars.matrixHeight    , this.vars.introgressHeight );
        //console.log( 'screen size ', this.vars.svgHeight                , this.vars.svgWidth      );
        //console.log( 'image max   ', this.vars.svgHeightMax             , this.vars.svgWidthMax   );
        //console.log( 'image scale ', this.vars.svgHeightScale           , this.vars.svgWidthScale );
        //console.log( this.vars.introgressY              , this.vars.matrixY                  , this.vars.matrixHeight    , this.vars.scaleHeight);
        //console.log( this.vars.introgressHeight         , this.getSelectedIntrogress().length, this.vars.introgressHeight);
    },
    updateColors            : function ( colorName ) {
        this.vars.currColor       = colorName;
        this.update();
    },
    changeColOrder          : function ( currColOrder ) {
        this.currColOrder = currColOrder;
        this.update();
    },
    changeRowOrder          : function ( currRowOrder ) {
        this.currRowOrder = currRowOrder;
        this.update();
    },
    updateIntrogress        : function ( spp ) {
        console.log('updating introgression');
        this.man.updateIntrogress( spp );
        this.introgressData[ spp ].checked = true;
        this.update();
    },
    getSelectedIntrogress   : function () {
        var names      = this.data.getNames();
        var valids     = [];

        for ( var l = 0 ; l < names.length; l++ ) {
            var spp      = names[l];
            var linedata = this.introgressData[ spp ];

            //console.log("SPP %d %s %o %o", l, spp, linedata, linedata.checked);

            if ( linedata.checked ) {
                console.log("SPP %d %s CHECKED %o", l, spp, linedata);
                valids.push( linedata );

            } else {
                if ( linedata.html1 ) {

                }
            }
        }

        return valids;
    },
    clearVars               : function () {
        this.data           = null;
        this.svg            = {};
        this.canvas         = {};
        this.introgressData = {};
    },
    updateTooltip           : function ( tip ) {
        //$scope.tooltip.appendChild( document.createTextNode( tip ) );
        //console.log('tip', tip);
        this.tooltip.html(tip);
        //$scope.tooltip.text(tip);
    },
    showTooltip             : function ( event, row, col ) {
        //console.log('showing tooltip for ', row, col);
        var nfo = this.getHeaderInfo(col);
        var val = this.getMatrixVal(row, col);
        var spp = this.getNamesVal(row);
        nfo.Distance     = val;
        nfo.Specie       = spp;
        //console.log(spp, nfo, val);

        var tip = "";
        for ( var key in nfo ) {
            tip += "<b>" + key + "</b>: " + nfo[ key ] + " ";
        }

        $scope.updateTooltip( tip );
    },
    update                  : function () {
        this.updateWidthHeight();
        this.matrix.update();
    }
};




var mainController = function ( $scope, $http ) {
    console.log("INITIALIZING MAIN CONTROLLER: scope %o http %o", $scope, $http);

    this.scope                     = $scope;

    $scope.working                 = true;

    $scope.setup                   = setup;



    //
    // GETTERS
    //
    $scope.getMtime                = function () {
        $http.get('/mtime/'+$scope.databaseQry)
            .success(
                function(data) {
                    console.log('mtime %o', data);
                    $scope.dbmtime = data.mtime;
                }
            );
    };

    $scope.getSpecies              = function () {
        $http.get('/spps/'+$scope.databaseQry)
            .success(
                function(data) {
                    console.log('spps %o', data);
                    $scope.species = data.spps;
                }
            );
    };

    $scope.getChromosomes          = function () {
        $http.get('/chroms/'+$scope.databaseQry)
            .success(
                function(data) {
                    console.log('chromosomes %o', data);
                    $scope.chromosomes = data.chroms;
                }
            );
    };

    $scope.getGenes                = function () {
        $http.get('/genes/'+$scope.databaseQry+'/'+$scope.chromosomeQry)
            .success(
                function(data) {
                    console.log('genes %o', data);
                    $scope.genes = data.genes;
                }
            );
    };

    $scope.getReport               = function () {
        $scope.working = true;

        $http.get('/report/'+$scope.databaseQry+'/'+$scope.chromosomeQry+'/'+$scope.geneQry)
            .success(
                function(data) {
                    console.log('report %o', data);
                    $scope.report  = data;
                    $scope.loadReport(data);
                    $scope.working = false;
                }
            );
    };






    //
    // CANVAS FUNCTIONS
    //
    $scope.getData                 = function () {
        if (
                typeof($scope.specieQry    ) != null &&
                typeof($scope.chromosomeQry) != null &&
                typeof($scope.databaseQry  ) != null
            ){
                console.log("submitting spp %s schr %s db %s", $scope.specieQry, $scope.chromosomeQry, $scope.databaseQry);

                $scope.working = true;

                console.log('REQUESTING DATA');

                $http.get('/data/'+$scope.databaseQry+'/'+$scope.specieQry+'/'+$scope.chromosomeQry)
                    .success( $scope.receiveData );

                console.log('DATA REQUESTED');
        }
    };

    $scope.receiveData             = function ( data ) {
        console.log('DATA RECEIVED');
        if ( $scope.man ) {
            delete $scope.man;
        }

        $scope.man        = new canvasManager( $scope, data );

        $scope.controller = $scope.man.controller;
        console.log('CANVAS INITIATED');
    };

    $scope.changeColOrder          = function () {
        var currColOrder = 1;
        if ( $scope.clusterSegments ) {
            currColOrder = 1;
        } else {
            currColOrder = 0;
        }
        //$scope.hasUpdates(true);
        if ( $scope.man ) {
            $scope.man.changeColOrder( currColOrder );
        }
    };

    $scope.changeRowOrder          = function () {
        var currRowOrder = 1;
        if ( $scope.clusterRows ) {
            currRowOrder = 1;
        } else {
            currRowOrder = 0;
        }
        //$scope.hasUpdates(true);
        if ( $scope.man ) {
            $scope.man.changeRowOrder( currRowOrder );
        }
    };

    $scope.showCoord               = function ( col ) {
        var ordercol = $scope.vars.order.cols[ this.vars.currColOrder ];
        var realCol  = ordercol[ col ];
        var header   = $scope.data.header;
        var gene     = header.name[realCol];
        console.log('showing coord ',col, realCol, gene);
        $scope.gene  = gene;
        $scope.showGene(gene);
    },






    //
    // INDEPENDENT GETTERS
    //
    $scope.getDatabases            = function () {
        $http.get('/dbs')
            .success(
                function(data) {
                    console.log('dbs %o', data);
                    $scope.databases        = data.databases;

                    // sample database
                    $scope.specieQry        = "ref";
                    $scope.databaseQry      = "Solanum 84 50 Kbp window";
                    $scope.chromosomeQry    = "SL2.40ch06";
                    $scope.updateFields();

                    $scope.initiated        = true;
                }
        );
    };

    $scope.getUsername             = function () {
        $http.get('/username')
            .success(
                function(data) {
                    console.log('username %o', data);
                    $scope.username = data.username;
                }
        );
    };

    $scope.getAlives               = function () {
        $http.get(clusterURL+'/alive')
            .success(
                function(data) {
                    console.log('cluster alive %o', data);
                    $scope.clusterAlive = true;

                    if ( $scope.data ) {
                        console.log('cluster alive and data already loaded. delayed getting cluster');
                        $scope.getCluster();
                    }
                }
            );

        $http.get(converterURL+'/alive')
            .success(
                function(data) {
                    console.log('converter alive %o', data);
                    $scope.converterAlive = true;
                }
            );


        $http.get(pdbURL+'/alive')
            .success(
                function(data) {
                    console.log('pdb alive %o', data);
                    $scope.pdbAlive = true;
                }
            );

    };

    $scope.getCluster              = function () {
        payload = {
            'data'    : $scope.getMatrix(),
            'rownames': $scope.getNames(),
            'colnames': $scope.getHeaderRow('name')
        };

        $http({
                method : 'POST',
                url    : clusterURL,
                data   : $.param( { 'table': JSON.stringify( payload ) } ),
                headers: {
                    //'Content-Type'                : 'application/json',
                    'Content-Type'                : 'application/x-www-form-urlencoded'
                    //'Access-Control-Allow-Headers': "Origin, X-Requested-With, Content-Type, Accept",
                    //'Access-Control-Allow-Origin' : "*",
                    //'Access-Control-Allow-Methods': "OPTIONS,GET,POST,PUT,DELETE"
                }
            })
            .success(
                function(data) {
                    console.log( typeof(data) );
                    console.log('cluster %o', data);

                    $scope.cluster = data;

                    $scope.vars.order.cols.push( data.cols.colsOrder );
                    $scope.vars.order.rows.push( data.rows.rowsOrder );
                }
            );
    };

    $scope.loadReport              = loadReport;

    $scope.showGeneQry             = function () {
        console.log("showing gene QRY");

        if (
                typeof($scope.chromosomeQry) !== null &&
                typeof($scope.databaseQry  ) !== null &&
                typeof($scope.geneQry      ) !== null
            ){
                console.log("showing gene QRY: chr %s db %s gene %s", $scope.chromosomeQry, $scope.databaseQry, $scope.geneQry);

                $scope.man.updateSizes();
                $scope.getReport();
            }
    };

    $scope.showGene                = function ( gene ) {
        console.log("showing gene");

        if (
                typeof($scope.chromosome) !== null &&
                typeof($scope.database  ) !== null &&
                typeof(gene             ) !== null
            ){
                console.log("showing gene: chr %s db %s gene %s", $scope.chromosome, $scope.database, $scope.gene);
                $scope.databaseQry   = $scope.database;
                $scope.chromosomeQry = $scope.chromosome;
                $scope.geneQry       = gene;
                $scope.showGeneQry();
            }
    };

    $scope.showHelp                = function () {
        console.log('show help');
        showhelp();
    };





    //
    // FUNCTIONS
    //
    $scope.clearVars               = function () {
        $scope.databaseQry    = null;
        $scope.specieQry      = null;
        $scope.chromosomeQry  = null;
        $scope.geneQry        = null;
        $scope.groupByQry     = null;
        $scope.groupByValQry  = null;

        $scope.database       = null;
        $scope.specie         = null;
        $scope.chromosome     = null;
        $scope.gene           = null;
        $scope.groupBy        = null;
        $scope.groupByVal     = null;

        $scope.cluster        = null;
        $scope.report         = null;

        $scope.databases      = null;
        $scope.username       = null;

        $scope.dbmtime        = null;

        $scope.species        = null;
        $scope.chromosomes    = null;

        $scope.genes          = null;

        if ( $scope.man ) {
            $scope.man.clearVars();
        }

        $scope.startup();
    };

    $scope.updateFields            = function () {
        console.log('database changed %o', $scope.databaseQry);
        if ($scope.databaseQry) {
            console.log(' getting database info');
            $scope.getMtime();
            $scope.getSpecies();
            $scope.getChromosomes();
            $scope.getGenes();

        } else {
            console.log(' cleaning vars');
            $scope.clearVars();
        }
    };

    $scope.startup                 = function () {
        console.log('starting up');
        $scope.getDatabases();
        $scope.getUsername();
        console.log('started up');
    };







    //
    // GETTERS
    //
    $scope.getSvg                  = function () {
        var doctype  = '<?xml version="1.0" standalone="yes"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n';
        var svgSrc   = $('#wrap').html();
            svgSrc   = svgSrc.replace(/\<\!--.*?--\>/g, '');
            svgSrc   = svgSrc.replace(/data-ng\S+?\".+?\"/g, '');
            svgSrc   = svgSrc.replace(/\s+\n/g, '');
            svgSrc   = doctype + svgSrc;
        var ofile    = $scope.database + '_' + $scope.chromosome + '_' + $scope.specie;
        return [ofile, svgSrc];
    };

    $scope.downloadAsSvg           = function () {
        var res    = $scope.getSvg();
        var ofile  = res[0];
        var svgSrc = res[1];

        downloadDataNfo (ofile + '.svg', svgSrc, 'image/xml+svg');
    };

    $scope.downloadAsPng           = function () {
        var res    = $scope.getSvg();
        var ofile  = res[0];
        var svgSrc = res[1];

        svgtopng(ofile + '.png', svgSrc);
    };

    $scope.downloadAsPdf           = function () {
        var res    = $scope.getSvg();
        var ofile  = res[0];
        var svgSrc = res[1];

        svgtopdf(ofile + '.pdf', svgSrc);
    };

    $scope.updateConfig            = function () {
        if ( $scope.man ) {
            $scope.man.update();
        }
    };

    $scope.updateIntrogress        = function ( spp ) {
        console.log('updating introgression');
        if ( $scope.man ) {
            $scope.man.updateIntrogress( spp );
        }
    };






    //
    // INITIALIZING
    //
    $scope.clearVars();

    $scope.clusterAlive     = false;
    $scope.converterAlive   = false;
    $scope.pdbAlive         = false;
    $scope.getAlives();


    $scope.tooltip          = $('#tooltip');

    $scope.working          = false;
};




var app = angular.module('myApp', [])
    .controller('mainController'  , ['$scope', '$http', mainController  ])
;


app.filter('iff', function () {
    return function(input, truevalue, falsevalue) {
        //console.log(" input %o true %o false %o", input, truevalue, falsevalue);
        return input ? truevalue : falsevalue;
    };
});













function getColors (vmin, vmax, scheme) {
    var sLen   = scheme.length;
    var vPiece = (vmax - vmin) / sLen;
    //var vmid   = ((vmax - vmin) / 2.0).toFixed(4);
    var vals   = [];

    for ( var val = vmin; val <= vmax; val += vPiece ) {
        vals.push( val );
    }

    var colorScale = d3.scale.linear()
        .domain( vals   )
        .range(  scheme );

    return colorScale;
}


function showhelp () {
    window.open('/static/help.html', '_blank');
}


var lineF = d3.svg.line()
            .x( function(d,i) { return i; } )
            .y( function(d,i) { return d; } )
            .interpolate("linear")
;


function data2path (data, sColor, sWidth) {
    var line = document.createElementNS( xmlns, 'path');
        line.setAttributeNS( null, "d"           , lineF( data ));
        line.setAttributeNS( null, "stroke"      , sColor       );
        line.setAttributeNS( null, "stroke-width", sWidth       );
        line.setAttributeNS( null, "fill-opacity", 0            );
        //line.setAttributeNS( null, "fill"        , "black"      );

    return line;
}

























var TreeDiv = 'tree';
function loadReport (data) {
    console.log('load report: got report data %o', data);

    //TREE DIV
    $('#'+TreeDiv).empty();

    var $TreeDiv = $('<div>'      , { 'class': 'tree'   , 'id': TreeDiv+'_tree'  } ).appendTo('#'+TreeDiv);
    //$('#'+TreeDiv).dialog({ autoOpen: false, 'maxWidth': maxW, 'width': maxW, 'maxHeight': maxH, 'height': maxH });

    console.log('width ', $(window).width());

    $TreeDiv.dialog({
        'autoOpen': false,
        //'maxWidth': maxW,
        //'maxHeight': maxH,
        //'width': maxW,
        //'height': maxH,
        'height': Math.round($(window).height()*0.95),
        'width': "99%",
        'close': function() {
            //$TreeDiv.dialog("destroy");
            $TreeDiv.remove();
        }
    });


    $TreeDiv.html('');

    console.log('load report: separating data');

    //console.log('reposrt', data);

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

    var db_name = data['db_name'];

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
        var pval  = pairs[ppos];
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
    var filename  = db_name + '_' + chrom + '_' + start + '_' + end + '_' + gene;
    var desc      = db_name + '_' + chrom + '_' + start + '_' + end + '_' + gene;

    console.log('load report: adding data');

    showTree(      filename, treeStr,       treeDst);
    showMatrix(    filename,          spps, matrix, matrixDst );
    showAlignment( filename, desc,    spps, aln   , alnDst    );

    console.log('load report: opening');

    $TreeDiv.dialog('open');

    console.log('load report: done');
}


function showTree (filename, treeStr, dst) {
    console.log('show tree');

    var $dst    = $('#'+dst);

    $dst.html('');


    console.log('showtree: creating');

    var numSpps = treeStr.split(',').length;
    var width   = Math.round($(window).width() *0.7);
    var height  = numSpps * 14;


    $('<div>', {'id': 'tree_render'}).appendTo($dst);
    console.log('spps %d h %d w %d (%d)', numSpps, height, width, $(window).width());

    var doctype = '<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n';
    var nfile       = filename + '_TREE.newick';
    var ofile       = filename + '_TREE.svg';
    var pfile       = filename + '_TREE.png';
    var ffile       = filename + '_TREE.pdf';
    var svgSrc      = insertTree( treeStr, 'tree_render', width*1.1, height*1.1);
        svgSrc      = doctype + svgSrc;
    var downloadPNG = function(){ svgtopng(pfile, svgSrc); };
    var downloadPDF = function(){ svgtopdf(ffile, svgSrc); };

    $('<a>', {'class': 'downloadlink'}).text('Download PNG'      ).click(downloadPNG).insertAfter('#tree_render');
    $('<a>', {'class': 'downloadlink'}).text('Download PDF //'   ).click(downloadPDF).insertAfter('#tree_render');
    $('<a>', {'class': 'downloadlink'}).data('ofile', ofile).data('src', svgSrc ).data('filetype', "image/svg+xml").text('Download SVG //'   ).click(downloadData).insertAfter('#tree_render');
    $('<a>', {'class': 'downloadlink'}).data('ofile', nfile).data('src', treeStr).data('filetype', "text/plain"   ).text('Download Newick //').click(downloadData).insertAfter('#tree_render');

    console.log('show tree: finished');
}


function showMatrix (    filename, spps, matrix, matrixDst ) {
    var $dst = $('#'+matrixDst);
    var $tbl = $('<table>', { 'class': 'matrixTable' }).appendTo($dst);
    console.log("show matrix");
    //console.log(spps);
    //console.log(matrix);
    var omtrx = '';

    $.each( spps, function (k,v) {
        //console.log('matrix k '+k+' v '+v);
        var $tr  = $('<tr>', {'class': 'matrixLine'             }).appendTo($tbl);
        $tr.append($('<td>', {'class': 'matrixCell matrixHeader'}).append(   v ));
        omtrx += v;

        $.each( matrix[k], function (l,col) {
            omtrx += "\t" + col;
            var cVal  = col.toFixed(2);
            var tclass;

            if ( l == k ) {
                tclass = {'class': 'matrixCell matrixVal matrixDiagonal'}
            } else if ( l > k ) {
                tclass = {'class': 'matrixCell matrixVal matrixParallel'};
            } else {
                tclass = {'class': 'matrixCell matrixVal matrixMain'    };
            }

            $td = $('<td>', tclass).append(cVal).appendTo($tr);
            //console.log('aln '+k+' v '+v);
        });
        omtrx += "\n";
    });

    var nfile  = filename + '_MATRIX.tsv';
    $('<a>', {'class': 'downloadlink'}).data('ofile', nfile).data('src', omtrx).data('filetype', "text/plain").text('Download Matrix').click(downloadData).insertAfter($dst);

    console.log("show matrix done");
}


function showAlignment ( filename, desc, spps, aln, alnDst ) {
    var self  = this;
    var $dst  = $('#'+alnDst);
    var $tbl  = $('<table>', { 'class': 'alignmentTable'}).appendTo($dst);
    var fasta = "";
    console.log("show alignment");

    console.log("show alignment: creating table");
    $.each( spps, function (k,v) {
        var seq  = aln[v];
        fasta   += '>' + desc + v + '\n' + seq + '\n';

        //console.log('aln    k '+k+' v '+v+' seq '+seq);
        var $tr  =  $('<tr>', { 'class': 'alignmentCell alignmentLine'         })
            .append($('<td>', { 'class': 'alignmentCell alignmentHead'         }).append(v  ))
            .append($('<td>', { 'class': 'monospace alignmentCell alignmentVal'}).append(seq))
            .appendTo($tbl);
        //console.log('aln '+k+' v '+v);
    });


    console.log("show alignment: creating cells");
    //$('.alignmentVal').each(function(){
    //    var message = $(this).html();
    //    var chars   = new Array( message.length );
    //    for (var i  = 0; i < message.length; i++) {
    //        var mchar = message[i];
    //        chars[i] = "<div class='dnaNuc dna"+mchar+"'>" + mchar + "</div>";
    //    }
    //    $(this).html(chars);
    //});

    console.log("show alignment: adding data");

    var nfile  = filename+'_ALIGNMENT.fasta';
    $('<a>', {'class': 'downloadlink'}).data('ofile', nfile).data('src', fasta).data('filetype', "text/plain").text('Download Alignment').click(downloadData).insertAfter($dst);

    console.log("show alignment done");
}


function insertTree ( treeStr, id_to_render, width, height) {
    //Smits.PhyloCanvas.Render.Style['text']['font-size'] = 10;
    //Smits.PhyloCanvas.Render.Style['Rectangular']['bufferX'] = 200;
    //Smits.PhyloCanvas.Render.Parameters.Rectangular.showScaleBar = true;
    //Smits.PhyloCanvas.Render.Style.text['font-size'] = 16;
    Smits.PhyloCanvas.Render.Style.bootstrap = { 'font-size': 0 };

    var numSpps          = treeStr.split(',').length;
    var heightS          = numSpps * 12;
    var widthS           = heightS;

    var phylocanvas = new Smits.PhyloCanvas(
        { 'newick': treeStr }, // Newick or XML string
        id_to_render,         // div id where to render
        widthS,
        heightS,
        'rectangular'
    );

    console.log('show tree: created');

    var el = document.getElementById(id_to_render).getElementsByTagName('svg')[0];
    //console.log( el.getAttribute('height') );
    el.setAttribute('viewBox'            , '0 0 '+widthS+' '+(heightS + 12) );
    el.setAttribute('preserveAspectRatio',                          'none' );
    el.setAttribute('width'              ,                          width  );
    el.setAttribute('height'             ,                          height );
    //console.log( el.getAttribute('height') );

    return phylocanvas.getSvgSource();
}


function downloadData () {
    var ofile     = $(this).data('ofile'   );
    var dataobj   = $(this).data('src'     );
    var datatype  = $(this).data('filetype');
    //console.log('downloading',ofile,dataobj,datatype);
    console.log('downloading',ofile,datatype);
    downloadDataNfo (ofile, dataobj, datatype);
}


function downloadDataNfo (ofile, dataobj, datatype) {
    var blob      = new Blob([dataobj], {type: datatype});
    downloadBlob(ofile, blob);
}


function downloadBlob (ofile, blob) {
    saveAs(blob, ofile);
}


function svgtopng (pfile, svgSrc) {
    svgtoimage('png', pfile, svgSrc);
}


function svgtopdf (pfile, svgSrc) {
    svgtoimage('pdf', pfile, svgSrc);
}


function svgtoimage (fmt, pfile, svgSrc) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function(){
        console.log('ready');
        if (this.status == 200) {
            console.log('success');
            var b64    = this.response;
            var img    = atob(b64);

            var length = img.length;
            var ab     = new ArrayBuffer(length);
            var ua     = new Uint8Array(ab);
            for (var i = 0; i < length ; i++) {
                ua[i] = img.charCodeAt(i);
            }

            if      (fmt == 'png') {
                downloadDataNfo(pfile, ab, "image/png");
            }
            else if (fmt == 'pdf') {
                downloadDataNfo(pfile, ab, "application/pdf");
            }
        }
    };
    var curl = converterURL + '/' + fmt;
    xhr.open('POST', curl, true);
    xhr.setRequestHeader('Content-Type', 'text/plain;charset=UTF-8');
    xhr.send(svgSrc);
};



















//    $scope.onMouseWheel            = function(layer, e, delta, deltaX, deltaY) {
//      //http://codepen.io/netgfx/pen/CKFLu
//
//      // mozilla fix...
//        if (e.originalEvent.detail){
//            delta = e.originalEvent.detail;
//        }
//        else{
//            delta = e.originalEvent.wheelDelta;
//        }
//
//		if (delta !== 0) {
//			e.preventDefault();
//		}
//
//        var scales    = layer.scale();
//        var scaleX    = scales.x;
//        var scaleY    = scales.y;
//
//		var cur_scaleX;
//		var cur_scaleY;
//		if (delta > 0) {
//			cur_scaleX = scaleX + Math.abs(delta / 640);
//			cur_scaleY = scaleY + Math.abs(delta / 640);
//
//		} else {
//			cur_scaleX = scaleX - Math.abs(delta / 640);
//			cur_scaleY = scaleY - Math.abs(delta / 640);
//
//		}
//
//        console.log('>>>>',e,delta,e.detail);
//		//check for minimum scale limit
//        //console.log(cur_scale, min_scale);
//		//if (cur_scale > min_scale) {
//        var d        = document.getElementById('graph');
//        var cnvsPos  = $scope.getPos(d);
//        var Apos     = layer.getAbsolutePosition();
//        var mousePos = layer.getPosition();
//
//        console.log(d,cnvsPos,Apos,mousePos);
//        var smallCalcX = (e.originalEvent.pageX - Apos.x - cnvsPos.x) / scaleX;
//        var smallCalcY = (e.originalEvent.pageY - Apos.y - cnvsPos.y) / scaleY;
//
//        var endCalcX   = (e.originalEvent.pageX          - cnvsPos.x) - (cur_scaleX * smallCalcX);
//        var endCalcY   = (e.originalEvent.pageY          - cnvsPos.y) - (cur_scaleY * smallCalcY);
//
//        //scale = cur_scale;
//
//        console.log( "X %d Y %d sX %d sY %d", endCalcX, endCalcY, cur_scaleX, cur_scaleY );
//        layer.setPosition({ x: endCalcX, y: endCalcY });
//
//        layer.scaleX( cur_scaleX );
//        layer.scaleY( cur_scaleY );
//        layer.draw();
//		//}
//	};
//
//	$scope.getPos                  = function (el) {
//		for (var lx=0, ly=0;
//            el != null;
//            lx += el.offsetLeft, ly += el.offsetTop, el = el.offsetParent);
//    	return {x: lx,y: ly};
//	};










//// http://www.html5rocks.com/en/tutorials/canvas/performance/
//no pre-rendering:
//
//// canvas, context are defined
//function render() {
//  drawMario(context);
//  requestAnimationFrame(render);
//}
//
//pre-rendering:
//
//var m_canvas = document.createElement('canvas');
//m_canvas.width = 64;
//m_canvas.height = 64;
//var m_context = m_canvas.getContext(‘2d’);
//drawMario(m_context);
//
//function render() {
//  context.drawImage(m_canvas, 0, 0);
//  requestAnimationFrame(render);
//}

//Avoid floating point coordinates
//// With a bitwise or.
//rounded = (0.5 + somenum) | 0;
//// A double bitwise not.
//rounded = ~~ (0.5 + somenum);
//// Finally, a left bitwise shift.
//rounded = (0.5 + somenum) << 0;




//translate3d(x,y,z)



//http://cacodaemon.de/index.php?id=33
//.fifty {
//    transform: scale(1.5, 1.5);
//    -ms-transform: scale(1.5, 1.5);
//    -webkit-transform: scale(1.5, 1.5);
//    -o-transform: scale(1.5, 1.5);
//    -moz-transform: scale(1.5, 1.5);
//}
//.hundred {
//    transform: scale(2, 2);
//    -ms-transform: scale(2, 2);
//    -webkit-transform: scale(2, 2);
//    -o-transform: scale(2, 2);
//    -moz-transform: scale(2, 2);
//}
//.reset-origin {
//    transform-origin: 0% 0%;
//    -ms-transform-origin: 0% 0%;
//    -webkit-transform-origin: 0% 0%;
//    -o-transform-origin: 0% 0%;
//    -moz-transform-origin: 0% 0%;
//}





//http://blogs.msdn.com/b/davrous/archive/2012/04/06/modernizing-your-html5-canvas-games-with-offline-apis-file-apis-css3-amp-hardware-scaling.aspx
//window.addEventListener("resize", OnResizeCalled, false);
//
//function OnResizeCalled() {
//    canvas.style.width = window.innerWidth + 'px';
//    canvas.style.height = window.innerHeight + 'px';
//}
//
//Or even simpler via a CSS rule like:
//
//#canvas
//{
//    width: 100%;
//    height: 100%;
//}
//
//But you’ll understand later on why I’m registering to the resize event of the window.
//
//And that’s it! With hardware accelerated browsers, this operation will be done by your GPU at no cost! You will even have anti-aliasing enabled. Indeed, the scaling operation is done by the GPU thanks to the 100% applied to the width & height properties. Recent browsers also automatically apply an anti-aliasing algorithm for you. That’s why, David Catuhe was mentioning it in his canvas performance article.



//var gameWidth = window.innerWidth;
//var gameHeight = window.innerHeight;
//var scaleToFitX = gameWidth / 800;
//var scaleToFitY = gameHeight / 480;
//
//var currentScreenRatio = gameWidth / gameHeight;
//var optimalRatio = Math.min(scaleToFitX, scaleToFitY);
//
//if (currentScreenRatio >= 1.77 && currentScreenRatio <= 1.79) {
//    canvas.style.width = gameWidth + "px";
//    canvas.style.height = gameHeight + "px";
//}
//else {
//    canvas.style.width = 800 * optimalRatio + "px";
//    canvas.style.height = 480 * optimalRatio + "px";
//}






//http://blogs.msdn.com/b/eternalcoding/archive/2012/03/22/unleash-the-power-of-html-5-canvas-for-gaming-part-1.aspx
//The code for this technique is the following (used in the 2D tunnel effect to read the tunnel’s texture data):
//
//var loadTexture = function (name, then) {
//    var texture = new Image();
//    var textureData;
//    var textureWidth;
//    var textureHeight;
//    var result = {};
//
//    // on load
//    texture.addEventListener('load', function () {
//        var textureCanvas = document.createElement('canvas'); // off-screen canvas
//
//        // Setting the canvas to right size
//        textureCanvas.width = this.width; //<-- "this" is the image
//        textureCanvas.height = this.height;
//
//        result.width = this.width;
//        result.height = this.height;
//
//        var textureContext = textureCanvas.getContext('2d');
//        textureContext.drawImage(this, 0, 0);
//
//        result.data = textureContext.getImageData(0, 0, this.width, this.height).data;
//
//        then();
//    }, false);
//
//    // Loading
//    texture.src = name;
//
//    return result;
//};
//
//To use this code, you have to take in account that the load of the texture is asynchronous and so you have to use the then parameter to transmit a function to continue your code:
//
//// Texture
//var texture = loadTexture("soft.png", function () {
//    // Launching the render
//    QueueNewFrame();
//});


//JavaScript provides Math.round, Math.floor or even parseInt to convert number to integer. But this function makes some extra works (for instance to check ranges or to check if the value is effectively a number. parseInt even first converts its parameter to string!). And inside my rendering loop, I need to have a quick way to perform this conversion.
//
//Remembering my old assembler code, I used a small trick: Instead of using parseInt, you just have to shift your number to the right with a value of 0. The runtime will move the floating value from a floating register to an integer register and use an hardware conversion. Shifting this value to the right with a 0 value will let it unchanged and so you can get back your value casted to integer.
//
//The original code was:
//
//u = parseInt((u < 0) ? texture.width + (u % texture.width) : (u >= texture.width) ? u % texture.width : u);
//
//And the new one is the following:
//
//u = ((u < 0) ? texture.width + (u % texture.width) : (u >= texture.width) ? u % texture.width : u) >> 0;
//
//Of course this solution requires that you are sure the value is a correct number Sourire






//http://gamedev.stackexchange.com/questions/32221/huge-performance-difference-when-using-drawimage-with-img-vs-canvas
//dest.drawImage(src, x, y) // bad
//dest.drawImage(src, x, y, w, h, destX, destY, w, h) // good
//drawImage(image, sx, sy, sWidth, sHeight, dx, dy, dWidth, dHeight)






//http://www.w3schools.com/tags/canvas_getimagedata.asp
//var c=document.getElementById("myCanvas");
//var ctx=c.getContext("2d");
//ctx.fillStyle="red";
//ctx.fillRect(10,10,50,50);
//
//function copy()
//{
//var imgData=ctx.getImageData(10,10,50,50);
//ctx.putImageData(imgData,10,70);
//}




//http://useallfive.com/thoughts/javascript-tool-detect-if-a-dom-element-is-truly-visible/
//var my_element = document.getElementById('my-element');
////-- Returns true/false
//my_element.isVisible(my_element);





//http://stackoverflow.com/questions/6554760/finding-whether-an-svg-element-is-visible-in-the-viewport
//var tile; // this is your SVG tile node
//
//var svgroot = tile.ownerSVGElement;
//var scale = svgroot.currentScale;
//var vbParts = svgroot.getAttribute("viewBox").split(" ");
//var vbx = parseInt(vbParts[0]);
//var vby = parseInt(vbParts[1]);
//var vbxu = parseInt(vbParts[2]);
//var vbyu = parseInt(vbParts[3]);
//var tx = svgroot.currentTranslate.x;
//var ty = svgroot.currentTranslate.y;
//var svgWidth = parseInt(svgroot.getAttribute("width"));
//var svgHeight = parseInt(svgroot.getAttribute("height"));
//var svgzoomfactor = vbxu / svgWidth;
//
//var vpRect = svgroot.createSVGRect();
//vpRect.x = parseFloat(vbx + (-tx) * (svgzoomfactor) / scale);
//vpRect.y = parseFloat(vby + (-ty) * (svgzoomfactor) / scale);
//vpRect.width = parseFloat(svgWidth * svgzoomfactor / scale);
//vpRect.height = parseFloat(svgHeight * svgzoomfactor / scale);
//
//if (svgroot.checkIntersection(tile, vpRect)) {
//    // the tile intersects the viewport!
//}





//http://stackoverflow.com/questions/10244944/how-to-hide-controls-when-it-gets-outside-a-canvas-in-wp7
//You should use the Clip property.
//
//The following will show a Button that will show outside of the Canvas because button width > canvas width:
//
//<Canvas Width="200" Height="200">
//    <Button>My button with a lot of text</Button>
//</Canvas>
//Now if I add the Clip property, what goes outside of the clip region gets hidden:
//
//<Canvas Width="200" Height="200">
//    <Canvas.Clip>
//        <RectangleGeometry Rect="0,0,200,200" />
//    </Canvas.Clip>
//
//    <Button>My button with a lot of text</Button>
//</Canvas>







//http://stackoverflow.com/questions/21844451/render-a-tile-map-using-javascript
//// assuming images are already loaded properly
//// and have fired onload events, which you've listened for
//// so that there are no surprises, when your engine tries to
//// paint something that isn't there, yet
//
//
//// this should all be wrapped in a module that deals with
//// loading tile-maps, selecting the tile to "paint" with,
//// and generating the data-format for the tile, for you to put into the array
//// (or accepting plug-in data-formatters, to do so)
//var selected_tile = null,
//    selected_tile_map = get_tile_map(), // this would be an image with your tiles
//    tile_width  = 64, // in image-pixels, not canvas/screen-pixels
//    tile_height = 64, // in image-pixels, not canvas/screen-pixels
//
//    num_tiles_x = selected_tile_map.width  / tile_width,
//    num_tiles_y = selected_tile_map.height / tile_height,
//
//    select_tile_num_from_map = function (map_px_X, map_px_Y) {
//        // there are *lots* of ways to do this, but keeping it simple
//        var tile_y = Math.floor(map_px_Y / tile_height), // 4 = floor(280/64)
//            tile_x = Math.floor(map_px_X / tile_width ),
//
//            tile_num = tile_y * num_tiles_x + tile_x;
//            // 23 = 4 down * 5 per row + 3 over
//
//        return tile_num;
//    };
//
//    // won't go into event-handling and coordinate-normalization
//    selected_tile_map.onclick = function (evt) {
//        // these are the coordinates of the click,
//        //as they relate to the actual image at full scale
//        map_x, map_y;
//        selected_tile = select_tile_num_from_map(map_x, map_y);
//    };
//
//Then, for "painting", you just need to listen to a canvas click, figure out what the X and Y were, figure out where in the world that is, and what array spot that's equal to.
//From there, you just dump in the value of selected_tile, and that's about it.
//
//// this might be one long array, like I did with the tile-map and the number of the tile
//// or it might be an array of arrays: each inner-array would be a "row",
//// and the outer array would keep track of how many rows down you are,
//// from the top of the world
//var world_map = [],
//
//    selected_coordinate = 0,
//
//    world_tile_width  = 64, // these might be in *canvas* pixels, or "world" pixels
//    world_tile_height = 64, // this is so you can scale the size of tiles,
//                            // or zoom in and out of the map, etc
//
//    world_width  = 320,
//    world_height = 320,
//
//
//    num_world_tiles_x = world_width  / world_tile_width,
//    num_world_tiles_y = world_height / world_tile_height,
//
//    get_map_coordinates_from_click = function (world_x, world_y) {
//        var coord_x = Math.floor(world_px_x / num_world_tiles_x),
//            coord_y = Math.floor(world_px_y / num_world_tiles_y),
//
//            array_coord = coord_y * num_world_tiles_x + coord_x;
//
//        return array_coord;
//    },
//
//    set_map_tile = function (index, tile) {
//        world_map[index] = tile;
//    };
//
//    canvas.onclick = function (evt) {
//        // convert screen x/y to canvas, and canvas to world
//        world_px_x, world_px_y;
//        selected_coordinate = get_map_coordinates_from_click(world_px_x, world_px_y);
//
//        set_map_tile(selected_coordinate, selected_tile);
//    };
//As you can see, the procedure for doing one is pretty much the same as the procedure for doing the other (because it is -- given an x and y in one coordinate-set, convert it to another scale/set).







//http://blog.sklambert.com/create-a-canvas-tileset-background/
//Lastly, we need to draw the 32×32 tile to the canvas. Conveniently, the canvas  API provides the ability to do this in the drawImage()  function. By defining the clipping area, we can draw only the section of the image that we want and not the entire image.
//
//To translate the row and column of the tile into an x and y coordinate of the image, we just multiply each by the size of a tile. When we draw the image to the canvas, we do the same thing for r and c to draw the tile at the correct position on the background.
//var tilesetImage = new Image();
//tilesetImage.src = ‘path/to/image.png’;
//tilesetImage.onload = drawImage;
//var canvas = document.getElementById(‘main’);
//var ctx = canvas.getContext(’2d’);
//var tileSize = 32;       // The size of a tile (32×32)
//var rowTileCount = 20;   // The number of tiles in a row of our background
//var colTileCount = 32;   // The number of tiles in a column of our background
//var imageNumTiles = 16;  // The number of tiles per row in the tileset image
//function drawImage () {
//   for (var r = 0; r < rowTileCount; r++) {
//      for (var c = 0; c < colTileCount; c++) {
//         var tile = ground[ r ][ c ];
//         var tileRow = (tile / imageNumTiles) | 0; // Bitwise OR operation
//         var tileCol = (tile % imageNumTiles) | 0;
//         ctx.drawImage(tilesetImage, (tileCol * tileSize), (tileRow * tileSize), tileSize, tileSize, (c * tileSize), (r * tileSize), tileSize, tileSize);
//      }
//   }
//}




//http://www.akademy.co.uk/software/canvaszoom/
//https://bitbucket.org/akademy/canvaszoom





//https://www.inkling.com/read/html5-canvas-fulton-fulton-1st/chapter-4/zooming-and-panning-an-image
//context.drawImage(photo, windowX, windowY, windowWidth, windowHeight,
//    0,0,windowWidth*currentScale,windowHeight*currentScale);
//document.onkeydown = function(e){
//   e = e?e:window.event;
//}
//case 38:
//      //up
//      windowY-=10;
//      if (windowY<0){
//         windowY = 0;
//      }
//      break;
//case 40:
//      //down
//      windowY+=10;
//      if (windowY>photo.height - windowHeight){
//         windowY = photo.height - windowHeight;
//      }
//      break;
//case 37:
//      //left
//      windowX-=10;
//      if (windowX<0){
//         windowX = 0;
//      }
//      break;
//case 39:
//       //right
//      windowX+=10;
//      if (windowX>photo.width - windowWidth){
//         windowX = photo.width - windowWidth;
//      }
//      break;
//We also need to add in two cases for the + and - keys to perform zoom in and zoom out actions:
//
//case 109:
//       //-
//       currentScale-=scaleIncrement;
//       if (currentScale<minScale){
//          currentScale = minScale;
//       }
//       break;
//case 107:
//       //+
//       currentScale+=scaleIncrement;
//       if (currentScale>maxScale){
//          currentScale = maxScale;
//       }
//When the user presses the + or - key, the currentScale variable is either incremented or decremented by the scaleIncrement value. If the new value of currentScale is greater than maxScale or lower than minScale, we set it to maxScale or minScale, respectively.
//
//Example 4-15 puts this entire application together. It doesn’t take many lines of code to create the simple interactions.
//


//var request        = dataP['request'  ];
//var header         = dataP['header'   ];
//var data_line      = dataP['data'     ];
//var data_info      = dataP['data_info'];
//
//var cfg = {
//    'header': {
//        line_starts    : header[    'start'          ],
//        line_ends      : header[    'end'            ],
//        line_unities   : header[    'num_unities'    ],
//        line_snps      : header[    'num_snps'       ],
//        line_names     : header[    'name'           ],
//    },
//    'data':{
//        ddata          : data_line[ 'line'           ],
//        dnames         : data_line[ 'name'           ],
//    },
//    'info': {
//        dminPos        : data_info[ 'minPos'         ],
//        dmaxPos        : data_info[ 'maxPos'         ],
//        dminPosAbs     : data_info[ 'minPosAbs'      ],
//        dmaxPosAbs     : data_info[ 'maxPosAbs'      ],
//        dmin           : data_info[ 'minVal'         ],
//        dmax           : data_info[ 'maxVal'         ],
//        num_rows       : data_info[ 'num_rows'       ],
//        num_cols       : data_info[ 'num_cols'       ],
//        num_cols_total : data_info[ 'num_cols_total' ],
//        qryStr         : qryStr,
//        resStr         : resStr
//    },
//    'request': {
//        evenly         : request[   'evenly'         ],
//        group          : request[   'group'          ],
//        classes        : request[   'classes'        ],
//        chrom          : request[   'chrom'          ],
//        ref            : request[   'ref'            ],
//        maxNum         : request[   'maxNum'         ],
//        page           : request[   'page'           ],
//    }
//};


//http://stackoverflow.com/questions/14777841/angularjs-inputplaceholder-directive-breaking-with-ng-model


//http://www.htmlgoodies.com/html5/client/using-web-workers-to-improve-performance-of-image-manipulation.html


//http://stackoverflow.com/questions/13448455/bootstrap-buttons-radio-toggle-with-angularjs
//app.directive('buttonsRadio', function() {
//    return {
//        restrict: 'E',
//        scope: { model: '=', options:'='},
//        controller: function($scope){
//            $scope.activate = function(option){
//                $scope.model = option;
//            };
//        },
//        template: "<button type='button' class='btn' "+
//                    "ng-class='{active: option == model}'"+
//                    "ng-repeat='option in options' "+
//                    "ng-click='activate(option)'>{{option}} "+
//                  "</button>"
//    };
//});
//
//app.directive('matrixrow', function() {
//    return {
//        restrict: 'E',
//        scope: { matrixx:"=", matrixy:"=", cellheight:"=", cellwidth:"=", vars:'=', line:'=', color:"=", orderrow:'=', ordercol:'=' },
//        transclude: true,
//        replace: true,
//        template:   ''+
//                    '<svg class="matrix"       data-ng-attr-x="{{ matrix }}em"               data-ng-attr-y="{{ matrixY }}em">' +
//                    '   <svg class="matrixrow" data-ng-attr-x="0em"                          data-ng-attr-y="{{ ($index) * cellheight }}em" data-ng-repeat="(rowNum, rowData) in line">'+
//                    '       <rect              data-ng-attr-x="{{ ($index * cellwidth) }}em" data-ng-attr-y="0em"                           data-ng-repeat="cellVal in rowData"         data-ng-attr-width="{{ cellwidth }}em" data-ng-attr-height="{{ cellheight }}em" fill="{{ color.colorScale( line[ orderrow[ rowNum ] ][ ordercol[ $index ] ][ 0 ] ) }}"></rect>'+
//                    '   </svg>' +
//                    '</svg>'
//    };
//});
//
//app.directive('matrixrow2', function() {
//    function updateStr(key, newval, oldval, $scope, $element, attrs) {
//        if (!$scope.hasUpdates) {
//            return;
//        }
//
//        //matrixx="vars.matrixX" matrixy="vars.matrixY" cellheight="vars.cellHeight" cellwidth="vars.cellWidth" line="data.data.line" color="setup.colors[ vars.currColor ]" orderrow="vars.order.rows[ vars.currRowOrder ]" ordercol="vars.order.cols[ vars.currColOrder ]"
//        //console.log('update str ', key, newval, oldval, $scope, $element, attrs);
//        if (newval && oldval !== newval) {
//            var vars     = {};
//            var numAttrs = 0;
//            for ( var k in attrs ) {
//                if (k[0] !== '$' && k != 'matrixrow2') {
//                    var v  = attrs[k];
//                    var vv = $scope.$eval(v);
//
//                    numAttrs += 1;
//
//                    //console.log(k,v,vv,typeof(vv));
//                    if ( typeof(vv) !== 'undefined') {
//                        vars[k] = vv;
//                    }
//                }
//            }
//
//            if ( numAttrs == Object.keys(vars).length ) {
//                console.log('ALL VARS SET');
//                var xmlns = "http://www.w3.org/2000/svg";
//                var rep = document.createElementNS( xmlns, 'svg');
//                rep.setAttributeNS(null, 'class', "matrix"           );
//                rep.setAttributeNS(null, 'x'    , vars.matrixx + 'em');
//                rep.setAttributeNS(null, 'y'    , vars.matrixy + 'em');
//
//                for ( var row = 0; row < vars.line.length; row++) {
//                    var nel    = document.createElementNS( xmlns, 'svg');
//                    nel.setAttributeNS(null, 'class', 'matrixrow');
//                    nel.setAttributeNS(null, 'x'    , '0em');
//                    nel.setAttributeNS(null, 'y'    , row * vars.cellheight + 'em');
//
//                    var rowData = vars.line[row];
//
//                    for ( var col = 0; col < rowData.length; col++ ) {
//                        var realRow = vars.orderrow[ row ];
//                        var realCol = vars.ordercol[ col ];
//                        var realVal = vars.line[ realRow ][ realCol ][0];
//                        var rec     = document.createElementNS( xmlns, 'rect');
//                        rec.setAttributeNS(null, 'x'     , col * vars.cellwidth + 'em'     );
//                        rec.setAttributeNS(null, 'y'     , '0em'                           );
//                        rec.setAttributeNS(null, 'fill'  , vars.color.colorScale( realVal ));
//                        rec.setAttributeNS(null, 'width' , vars.cellwidth  + 'em'          );
//                        rec.setAttributeNS(null, 'height', vars.cellheight + 'em'          );
//
//                        nel.appendChild( rec );
//                    }
//
//                    rep.appendChild(nel);
//                }
//
//                //console.log( rep );
//                $element.empty();
//                $element.append( rep );
//                $scope.hasUpdates = false;
//            }
//        }
//    }
//
//    function lnk($scope, $element, attrs) {
//        console.log('calling lnk');
//        for ( var k in attrs ) {
//            if (k[0] !== '$' && k != 'matrixrow2') {
//                console.log('adding key', k);
//                var v = attrs[k];
//                (
//                    function(k, s, e, a) {
//                        $scope.$watch(v, function(n,o) { updateStr(k, n, o, s, e, a) });
//                    }
//                )(k, $scope, $element, attrs);
//            }
//        }
//    };
//
//    return {
//        restrict: 'A',
//        //scope: { cellheight:"=", cellwidth:"=", vars:'=', line:'=', color:"=", orderrow:'=', ordercol:'=' },
//        transclude: true,
//        //replace: true,
//        link: lnk
//    };
//});
