var xmlns           = "http://www.w3.org/2000/svg";
var matrixFontSize  = 14;
var pixelPerLetterW = matrixFontSize / 2;
var pixelPerLetterH = matrixFontSize;
var blockQuanta     = 20;
var CANVAS_EL       = 'imgcanvas';

console.log('LOCATION', location         );
console.log('HOSTNAME', location.hostname);
console.log('PORT    ', location.port    );
console.log('PROTOCOL', location.protocol);





//http://tobyho.com/2012/07/27/taking-over-console-log/
function takeOverConsole(){
    var console = window.console
    if (!console) return
    function intercept(method){
        var original = console[method]
        console[method] = function(){
            // do sneaky stuff
            if (original.apply){
                // Do this for normal browsers
                original.apply(console, arguments)
            }else{
                // Do this for IE
                var message = Array.prototype.slice.apply(arguments).join(' ')
                original(message)
            }
        }
    }
    function ignore(method){
        var original = console[method]
        console[method] = function(){
            // do sneaky stuff
        }
    }

    var methods = [['log', ignore], ['warn', intercept], ['error', intercept]]
    for (var i = 0; i < methods.length; i++)
        methods[i][1](methods[i][0])
}


function isInList(lst, val) {
    return (lst.indexOf(val) != -1 );
}




console.log("QUANTA", blockQuanta);

var sharedService = function () {
    var sharedData = {};

    return sharedData;
};



function formatValStr( cellVal ) {
    var v = null;
    var u = null;
    if      (cellVal > 1000000000) { //1G
        v = cellVal / 1000000000.0;
        u = 'G';
    }
    else if (cellVal > 1000000) { //1M
        v = cellVal / 1000000.0;
        u = 'M';
    }
    else if (cellVal > 1000) { //1K
        v = cellVal / 1000.0;
        u = 'K';
    } else {
        v = cellVal;
        u = '';
    }
    var x = v.toFixed(1).toLocaleString({minimumFractionDigits: 1, maximumFractionDigits: 1});

    return x + ' ' + u + 'bp';
}



var mainController = function ( $scope, $http, mySharedService ) {
    $scope.working                 = true;

    $scope.setup                   = {
        colTextWidth    : 120,

        rowTextWidth    :  80, //number of letters / 2

        textHeight      :  pixelPerLetterH,

        cellWidth       :   5,
        cellHeight      :   5,
        //introgressHeight:  40,

        scaleHeight     :  50,
        scaleTextWidth  :  20,
        scaleBlockHeight:  10,
        scaleBlockWidth :  10,
        scaleSplits     :   9,

        paddingTop      :   5,
        paddingLeft     :   0,

        colors          : colors,

        full_size       : true,

        //showHeader      : false,
        //showRow         : false,

        headerConvKey   : {
                            'start'      : 'Start Position',
                            'end'        : 'End Position',
                            'num_unities': 'Number of components',
                            'num_snps'   : 'Number of SNPs',
                            'name'       : 'Fragment Name'
        }
    };

    $scope.isInList = isInList;


    //
    // GETTERS
    //
    $scope.getMtime                = function () {
        $http.get('api/mtime/'+$scope.databaseQry)
            .success(
                function(data) {
                    console.log('mtime %o', data);
                    $scope.dbmtime = data.mtime;
                }
            );
    };

    $scope.getSpecies              = function () {
        $http.get('api/spps/'+$scope.databaseQry)
            .success(
                function(data) {
                    console.log('spps %o', data);
                    $scope.species = list_to_utf(data.spps);
                }
            );
    };

    $scope.getClusterList          = function () {
        $http.get('api/clusterlist/'+$scope.databaseQry)
            .success(
                function(data) {
                    console.log('clusterlist %o', data);
                    $scope.clusterlist      = data;
                    $scope.clusterlistchrom = [];
                    for ( var chrom in data ) {
                        console.log('cluster chrom', chrom);
                        if ( chrom == '__global__' || chrom == $scope.chromosomeQry) {
                            for ( var c in data[chrom]) {
                                var v = data[chrom][c];
                                console.log('cluster chrom', chrom, 'c', v);
                                if ( $scope.clusterlistchrom.indexOf( v ) < 0) {
                                    $scope.clusterlistchrom.push( v );
                                }
                            }
                        }
                    }
                    console.log('clusterlistchrom' , $scope.clusterlistchrom );
                }
            );
    };

    $scope.getChromosomes          = function () {
        $http.get('api/chroms/'+$scope.databaseQry)
            .success(
                function(data) {
                    console.log('chromosomes %o', data);
                    $scope.chromosomes = data.chroms;
                }
            );
    };

    $scope.getGenes                = function () {
        if (
                $scope.databases     !== null                       &&
                $scope.databaseQry   !== null                       &&
                $scope.chromosomes   !== null                       &&
                $scope.chromosomeQry !== null                       &&
                isInList($scope.databases  , $scope.databaseQry   ) &&
                isInList($scope.chromosomes, $scope.chromosomeQry )
            ) {

            $http.get('api/genes/'+$scope.databaseQry+'/'+$scope.chromosomeQry)
                .success(
                    function(data) {
                        console.log('genes %o', data);
                        $scope.genes = data.genes;
                    }
                );
        } else {
            alert( "chromosome " + $scope.chromosomeQry + " is not in " + $scope.chromosomes + " for database " + $scope.databaseQry + " in " + ($scope.chromosomes.indexOf($scope.chromosomeQry) != -1 ));
        }
    };

    $scope.getReport               = function () {
        $scope.working = true;

        $http.get('api/report/'+$scope.databaseQry+'/'+$scope.chromosomeQry+'/'+$scope.geneQry)
            .success(
                function(data, status, header, config) {
                    console.log('report success %o status %o header %o config %o', data, status, header, config);
                    //console.log('report %o', data);
                    $scope.report  = data;
                    $scope.loadReport(data);
                    $scope.working = false;
                }
            )
            .error(
                function(data, status, header, config) {
                    console.log('report error %o status %o header %o config %o', data, status, header, config);
                    $scope.working = false;
                    alert('error loading report');
                }
            )
            ;
    };

    $scope.getData                 = function () {
        if (
                $scope.databases     !== null                       &&
                $scope.databaseQry   !== null                       &&
                $scope.chromosomes   !== null                       &&
                $scope.chromosomeQry !== null                       &&
                $scope.species       !== null                       &&
                $scope.specieQry     !== null                       &&
                isInList($scope.databases  , $scope.databaseQry   ) &&
                isInList($scope.chromosomes, $scope.chromosomeQry ) &&
                isInList($scope.species    , $scope.specieQry     )
            ){
                console.log("submitting spp %s schr %s db %s", $scope.specieQry, $scope.chromosomeQry, $scope.databaseQry);

                $scope.working = true;

                delete $scope.data;
                delete $scope.cluster;
                delete $scope.report;
                delete $scope.canvas;
                delete $scope.svg;

                $scope.data           = null;
                $scope.cluster        = null;
                $scope.report         = null;
                $scope.canvas         = null;
                $scope.svg            = {};
                if ( $scope.canvas && $scope.canvas.stage) {
                    $scope.canvas.scale     .destroy();
                    //$scope.canvas.header    .destroy();
                    $scope.canvas.rows      .destroy();
                    $scope.canvas.body      .destroy();
                    $scope.canvas.ruler     .destroy();
                    //$scope.canvas.introgress.destroy();
                    $scope.canvas.stage     .destroy();
                }
                delete $scope.canvas;
                $scope.canvas = {};


                $scope.updateSizes();

                console.log('REQUESTING DATA', $scope.databaseQry, $scope.specieQry, $scope.chromosomeQry);
                //console.log(encodeURIComponent($scope.specieQry), encodeURIComponent(encodeURIComponent($scope.specieQry)));
                var q = encodeURIComponent(escape(encodeURIComponent(escape($scope.specieQry))));

                $http.get('api/data/'+$scope.databaseQry+'/'+q+'/'+$scope.chromosomeQry)
                    .success( $scope.receiveData      )
                    .error(   $scope.receiveDataError );

                console.log('DATA REQUESTED');
        } else {
            alert( "invalid combination of database ("+$scope.databaseQry+"), chromosome ("+$scope.chromosomeQry+") and reference ("+$scope.specieQry+")" );
        }
    };



    //
    // INDEPENDENT GETTERS
    //
    $scope.getDatabases            = function () {
        $http.get('api/dbs')
            .success(
                function(data) {
                    console.log('dbs %o', data);
                    $scope.databases = data.databases;
                    $scope.databases.sort();
                }
        );
    };

    $scope.getUsername             = function () {
        $http.get('username')
            .success(
                function(data) {
                    console.log('username %o', data);
                    $scope.username = data.username;
                }
        );
    };

    $scope.getAlives               = function () {
    };

    $scope.loadReport              = loadReport;

    $scope.receiveDataError        = function ( status, headers, config ) {
        //console.log('DATA RECEIVE ERROR: data    %o', data   );
        console.log('DATA RECEIVE ERROR: status  %o', status );
        console.log('DATA RECEIVE ERROR: headers %o', headers);
        console.log('DATA RECEIVE ERROR: config  %o', config );

        alert( "combination of database, chromosome and reference does not exists" );

        console.log('working');
        $scope.working = false;

        console.log("DATA NOT RECEIVED AND PROCESSED");
    };

    $scope.receiveData             = function ( data, status, headers, config ) {
        console.log('DATA RECEIVE SUCCESS: data    %o', data   );
        console.log('DATA RECEIVE SUCCESS: status  %o', status );
        console.log('DATA RECEIVE SUCCESS: headers %o', headers);
        console.log('DATA RECEIVE SUCCESS: config  %o', config );

        $scope.canvas             = {};
        $scope.chromosome         = $scope.chromosomeQry;
        $scope.specie             = $scope.specieQry;
        $scope.database           = $scope.databaseQry;

        $scope.vars.numHeaderRows = Object.keys( data.header ).length;

        $scope.vars.numMatrixRows = data.data.name.length;

        $scope.vars.numCols       = data.data_info.num_cols;

        console.log('numHeaderRows %d', $scope.vars.numHeaderRows);
        console.log('numMatrixRows %d', $scope.vars.numMatrixRows);
        console.log('numCols       %d', $scope.vars.numCols      );

        var maxRowNameSize = 0;
        for ( var n = 0; n < data.data.name.length; n++ ) {
            var nS = data.data.name[ n ].length;
            maxRowNameSize = nS > maxRowNameSize ? nS : maxRowNameSize;
        }


        var maxColNameSize = 0;
        for ( var k in data.header ) {
            var v = data.header[ k ];

            var nC = k.length;
            maxRowNameSize = nC > maxRowNameSize ? nC : maxRowNameSize;

            for ( var n = 0; n < v.length; n++ ) {
                var nS = String(v[ n ]).length;
                maxColNameSize = nS > maxColNameSize ? nS : maxColNameSize;
            }
        }

        $scope.setup.rowTextWidth = maxRowNameSize * pixelPerLetterW;
        $scope.setup.colTextWidth = maxColNameSize * pixelPerLetterW;

        console.log( typeof(data.clusters) );
        console.log('cluster %o', data.clusters);

        $scope.cluster            = data.clusters;

        $scope.clusterNames = [ $scope.defaultClusterName ];
        var dfn = $scope.defaultClusterName;
        console.log('DFN', dfn);

        $scope.vars.order           = {};
        $scope.vars.order.cols      = {};
        $scope.vars.order.rows      = {};
        $scope.vars.order.cols[dfn] = Array.apply(null, Array(data.data_info.num_cols)).map(function(_,i){return i;});
        $scope.vars.order.rows[dfn] = Array.apply(null, Array(data.data_info.num_rows)).map(function(_,i){return i;});


        if ( $scope.cluster !== null ) {
            console.log('cluster keys', Object.keys($scope.cluster));

            for ( var c in $scope.cluster ) {
                console.log('adding cluster', c);
                $scope.clusterNames.push( c );
                $scope.vars.order.rows[ c ] = $scope.cluster[ c ].rows.rowsOrder;
                $scope.vars.order.cols[ c ] = $scope.cluster[ c ].cols.colsOrder;
            }
        }

        console.log($scope.vars.order.cols);

        if ( $scope.clusterNames.indexOf( $scope.vars.nextRowOrder) < 0 ) {
            $scope.vars.currRowOrder = dfn;
        } else {
            $scope.vars.currRowOrder = $scope.vars.nextRowOrder;
        }

        console.log('data: updating width and height');
        $scope.updateWidthHeightTransparent();

        console.log('data: linking data');
        $scope.data = data;

        console.log('data: compiling colors');

        $scope.compileColors( data.data_info, $scope.receiveData2 );
    };

    $scope.receiveData2            = function() {
        console.log('data: updating dom');
        $scope.hasUpdates(true);

        console.log('working');
        $scope.working = false;

        console.log( 'end %o', $scope );

        console.log("DATA RECEIVED AND PROCESSED");
    };

    $scope.showGeneQry             = function () {
        console.log("showing gene QRY");

        if (
                $scope.databases     !== null                       &&
                $scope.databaseQry   !== null                       &&
                $scope.chromosomes   !== null                       &&
                $scope.chromosomeQry !== null                       &&
                $scope.genes         !== null                       &&
                $scope.geneQry       !== null                       &&
                isInList($scope.databases  , $scope.databaseQry   ) &&
                isInList($scope.chromosomes, $scope.chromosomeQry ) &&
                isInList($scope.genes      , $scope.geneQry       )
            ){
                console.log("showing gene QRY: chr %s db %s gene %s", $scope.chromosomeQry, $scope.databaseQry, $scope.geneQry);

                $scope.updateSizes();
                $scope.getReport();
            }
    };

    $scope.showGene                = function ( gene ) {
        console.log("showing gene");

        if (
                $scope.databases     !== null                    &&
                $scope.database      !== null                    &&
                $scope.chromosomes   !== null                    &&
                $scope.chromosome    !== null                    &&
                $scope.genes         !== null                    &&
                gene                 !== null                    &&
                isInList($scope.databases  , $scope.database   ) &&
                isInList($scope.chromosomes, $scope.chromosome ) &&
                isInList($scope.genes      , gene              )
            ){
                console.log("showing gene: chr %s db %s gene %s", $scope.chromosome, $scope.database, gene);
                $scope.databaseQry   = $scope.database;
                $scope.chromosomeQry = $scope.chromosome;
                $scope.geneQry       = gene;
                $scope.showGeneQry();
            } else {
                console.log("not able to show gene");
                alert("not able to show gene");

                console.log('databases       ', $scope.databases   );
                console.log('database        ', $scope.database    );
                console.log('chromosomes     ', $scope.chromosomes );
                console.log('chromosome      ', $scope.chromosome  );
                console.log('genes           ', $scope.genes       );
                console.log('gene            ', gene               );
                console.log('valid database  ', isInList($scope.databases  , $scope.database   ) );
                console.log('valid chromosome', isInList($scope.chromosomes, $scope.chromosome ) );
                console.log('valid gene      ', isInList($scope.genes      , gene              ) );
            }

    };

    $scope.showHelp                = function () {
        console.log('show help');
        showhelp();
    };

    $scope.changeRowOrder          = function (clustername) {
        console.log('changeRowOrder', $scope.vars.currRowOrder, clustername);

        $scope.vars.currRowOrder = clustername;

        if ( $scope.clusterlistchrom.indexOf( clustername ) >= 0 ) {
            $scope.vars.nextRowOrder = clustername;
        }

        $scope.hasUpdates(true);
    };

    $scope.toggleShowRow            = function() {
        $scope.showRow = !$scope.showRow;
        if ( $scope.canvas ) {
          $scope.updateWidthHeight();
        }
    };

    //
    // FUNCTIONS
    //
    $scope.cleanVars                    = function () {
        $scope.zeroeVars();
        $scope.startup();
    };

    $scope.zeroeVars                    = function () {
        $scope.databaseQry      = null;
        $scope.specieQry        = null;
        $scope.chromosomeQry    = null;
        $scope.geneQry          = null;
        $scope.groupByQry       = null;
        $scope.groupByValQry    = null;

        $scope.database         = null;
        $scope.specie           = null;
        $scope.chromosome       = null;
        $scope.gene             = null;
        $scope.groupBy          = null;
        $scope.groupByVal       = null;

        $scope.data             = null;
        $scope.cluster          = null;
        $scope.report           = null;
        $scope.svg              = {};
        $scope.canvas           = null;

        $scope.databases        = null;
        $scope.username         = null;

        $scope.dbmtime          = null;

        $scope.species          = null;
        $scope.chromosomes      = null;
        $scope.clusterlist      = null;
        $scope.clusterlistchrom = null;
        $scope.clusterNames     = null;
        $scope.genes            = null;
    };

    $scope.updateFields                 = function () {
        console.log('database changed %o', $scope.database);
        if ($scope.databaseQry) {
            $scope.specieQry        = null;
            $scope.chromosomeQry    = null;
            $scope.geneQry          = null;
            $scope.groupByQry       = null;
            $scope.groupByValQry    = null;

            $scope.getMtime();
            $scope.getSpecies();
            $scope.getChromosomes();
            $scope.getClusterList();

        } else {
            $scope.cleanVars();
        }
    };

    $scope.updateSizes                  = function () {
        $scope.H            = Math.round($(window).height() *0.99);
        $scope.W            = Math.round($(window).width()  *0.99);
        $scope.maxH         = Math.round($scope.H           *0.95);
        $scope.maxW         = Math.round($scope.W           *0.95);
    };

    $scope.startup                      = function () {
        $scope.getDatabases();
        $scope.getUsername();
    };

    $scope.updateWidthHeightTransparent = function () {
        $scope.vars.axisTextWidth = $scope.setup.rowTextWidth;

        if ($scope.showHeader) {
            $scope.vars.colTextWidth   = $scope.setup.colTextWidth;
            $scope.vars.colTextHeight  = $scope.setup.textHeight;
            $scope.vars.cellWidth      = $scope.setup.colTextWidth;
            $scope.vars.axisTextHeight = $scope.setup.textHeight;
        } else {
            $scope.vars.colTextWidth   = 0;
            $scope.vars.colTextHeight  = 0;
            $scope.vars.cellWidth      = $scope.setup.cellWidth;
            $scope.vars.axisTextHeight = 0;
        }



        if ($scope.showRow) {
            $scope.vars.rowTextWidth   = $scope.setup.rowTextWidth;
            $scope.vars.rowTextHeight  = $scope.setup.textHeight;
            $scope.vars.cellHeight     = $scope.setup.textHeight;
        } else {
            $scope.vars.rowTextWidth   = 0;
            $scope.vars.rowTextHeight  = 0;
            $scope.vars.cellHeight     = $scope.setup.cellHeight;
        }

        console.log( 'cellHeight %o', $scope.vars.cellHeight );




        if ($scope.showHeader || $scope.showRow) {
            $scope.vars.axisTextWidth  = $scope.setup.rowTextWidth;
        } else {
            $scope.vars.axisTextWidth  = 0;
        }


        var axixHeight     = $scope.vars.numHeaderRows              * $scope.vars.colTextHeight;
        var headerHeight   = $scope.vars.colTextHeight;
            headerHeight   = $scope.vars.colTextHeight > axixHeight ? $scope.vars.colTextHeight : axixHeight;

        var matrixColWidth = $scope.showHeader ? $scope.vars.cellHeight * $scope.vars.numHeaderRows : $scope.vars.cellWidth;


        $scope.vars.axisX                = $scope.setup.paddingLeft;
        $scope.vars.axisY                = $scope.setup.scaleHeight;
        $scope.vars.axisWidth            = $scope.setup.axisTextWidth;
        $scope.vars.axisHeight           = headerHeight;

        $scope.vars.headerX              = $scope.setup.paddingLeft              + $scope.vars.axisTextWidth;
        $scope.vars.headerY              = $scope.setup.scaleHeight;
        $scope.vars.headerHeight         = headerHeight;

        var matrixY                      = $scope.vars.rulerY                    + $scope.vars.rulerHeight; // $scope.vars.headerY                   + $scope.vars.headerHeight
        $scope.vars.rowNamesX            = $scope.setup.paddingLeft;
        $scope.vars.rowNamesY            = matrixY                               + $scope.vars.cellHeight;

        $scope.vars.rulerHeight          = Math.ceil(matrixFontSize*1.0);
        $scope.vars.rulerX               = $scope.setup.paddingLeft              + $scope.vars.axisTextWidth;
        $scope.vars.rulerY               = $scope.vars.headerHeight              + $scope.setup.scaleHeight;

        $scope.vars.matrixX              = $scope.vars.rulerX;
        $scope.vars.matrixY              = matrixY;
        $scope.vars.matrixHeight         = ($scope.vars.numMatrixRows+1)         * $scope.vars.cellHeight;//                + $scope.vars.cellHeight;
        $scope.vars.matrixWidth          = $scope.vars.numCols                   * matrixColWidth;

        //MAX WIDTH 32.767
        $scope.vars.svgHeight            = $scope.setup.scaleHeight              + $scope.vars.headerHeight              + $scope.vars.matrixHeight + $scope.vars.rulerHeight;//    + $scope.vars.introgressHeight;
        if ( $scope.setup.full_size ) {
            $scope.vars.svgWidth         = $scope.vars.axisTextWidth             + $scope.vars.matrixWidth;
        } else {
            $scope.vars.svgWidth         = $scope.maxW;
        }

        $scope.vars.svgHeightMax         = $scope.setup.scaleHeight              + $scope.vars.headerHeight              + $scope.vars.matrixHeight + $scope.vars.rulerHeight;//   + $scope.vars.introgressHeight;
        $scope.vars.svgWidthMax          = $scope.vars.axisTextWidth             + $scope.vars.matrixWidth;

        $scope.vars.defaultMatrixWidthScale  = 1.0;
        $scope.vars.defaultMatrixHeightScale = 1.0;

        if ( $scope.canvas.body ) {
            if ( $scope.setup.full_size ) {
                $scope.vars.svgWidth       = $scope.vars.axisTextWidth + ( $scope.vars.matrixWidth * $scope.canvas.body.scaleX() );
            } else {
                $scope.vars.svgWidth       =                             ( $scope.vars.matrixWidth * $scope.canvas.body.scaleX() );

            }

            $scope.vars.svgHeight          =                             ( $scope.vars.svgHeight   * $scope.canvas.body.scaleY() );
        }

        console.log('svgHeight %o scaleHeight %o headerHeight %o introgressHeight %o matrixHeight %o', $scope.vars.svgHeight, $scope.setup.scaleHeight, $scope.vars.headerHeight, 0, $scope.vars.matrixHeight);
        console.log('svgWidth  %o scaleWidth  %o headerWidth  %o introgressWidth  %o matrixWidth  %o', $scope.vars.svgWidth , $scope.setup.scaleWidth , $scope.vars.headerWidth , 0, $scope.vars.matrixWidth );
    };

    $scope.updateWidthHeight            = function () {
        $scope.updateWidthHeightTransparent();
        $scope.hasUpdates(true);
    };

    $scope.controller                   = {
        update        : function(noup) {
            $scope.updateWidthHeightTransparent();
            $scope.controller.resize(noup);
        },
        resize        : function(noup) {
            console.log('size UPDATE');
            $scope.canvas.stage.width(  $scope.vars.svgWidth      );
            $scope.canvas.stage.height( $scope.vars.svgHeight     );
            $scope.canvas.body.height(  $scope.vars.matrixHeight  );
            $scope.canvas.body.width(   $scope.vars.matrixWidth   );
            $scope.redoRuler();
            if (!noup) {
                console.log('size UPDATE DRAW');
                $scope.canvas.stage.draw();
            }
        },
        moveX         : function(x, noup) {
            console.log('moving from X ', $scope.canvas.body.x(), ' TO X ', x);
            if ( $scope.canvas.body.x() != x ) {
                $scope.canvas.body.x( x );
                if (!noup) {
                    console.log('move X UPDATE');
                    $scope.controller.update();
                }
            }
        },
        moveY         : function(y, noup) {
            console.log('moving from Y ', $scope.canvas.body.y(), ' TO Y ', y);
            if ( $scope.canvas.body.y() != y ) {
                $scope.canvas.body.y( y );
                if (!noup) {
                    console.log('move Y UPDATE');
                    $scope.controller.update();
                }
            }
        },
        moveLeft      : function(noup) {
            var oX = $scope.canvas.body.x();
            var oW = $scope.canvas.body.width();
            var x  = oX - (oW*0.1);
            $scope.controller.moveX( x, noup );
        },
        moveRight     : function(noup) {
            var oX = $scope.canvas.body.x();
            var oW = $scope.canvas.body.width();
            var x  = Math.floor(oX + (oW*0.1));
            $scope.controller.moveX( x, noup );
        },
        moveUp        : function(noup) {
            var oY = $scope.canvas.body.y();
            var oH = $scope.canvas.body.height();
            var y  = oY - (oH*0.1);
            $scope.controller.moveY( y, noup );
        },
        moveDown      : function(noup) {
            var oY = $scope.canvas.body.y();
            var oH = $scope.canvas.body.height();
            var y  = oY + (oH*0.1);
            $scope.controller.moveY( y, noup );
        },
        moveUpFull    : function(noup) {
            $scope.controller.moveY( $scope.vars.matrixY, noup );
        },
        moveDownFull  : function(noup) {
            var oH = $scope.canvas.body.height();
            $scope.controller.moveY( oH - $scope.vars.matrixY, noup );
        },
        moveLeftFull  : function(noup) {
            var oW = $scope.canvas.body.width();
            $scope.controller.moveX( (oW + $scope.vars.svgWidth)*-1, noup );
        },
        moveRightFull : function(noup) {
            $scope.controller.moveX( $scope.vars.matrixX, noup );
        },
        zoomX         : function(x,    noup) {
            console.log('zoom from X ', $scope.canvas.body.scaleX(), ' TO X ', x, $scope.canvas.body);
            if ($scope.canvas.body.scaleX() != x) {
                $scope.canvas.body.scaleX( x );
                if (!noup) {
                    console.log('zoom from X UPDATE');
                    $scope.controller.update();
                }
            }
        },
        zoomY         : function(   y, noup) {
            console.log('zoom from Y ', $scope.canvas.body.scaleY(), ' TO Y ', y);
            if ($scope.canvas.body.scaleY() != y) {
                $scope.canvas.body.scaleY( y );
                if (!noup) {
                    console.log('zoom from Y UPDATE');
                    $scope.controller.update();
                }
            }
        },
        zoom          : function(x, y, noup) {
            $scope.controller.zoomX(x, true);
            $scope.controller.zoomY(y, true);
            if (!noup) {
                console.log('zoom UPDATE');
                $scope.controller.update();
            }
        },
        zoomOut       : function(noup) {
            $scope.controller.zommOutX(true);
            $scope.controller.zommOutY(true);
            if (!noup) {
                console.log('zoom out UPDATE');
                $scope.controller.update();
            }
        },
        zoomIn        : function(noup) {
            $scope.controller.zommInX(true);
            $scope.controller.zommInY(true);
            if (!noup) {
                console.log('zoom in UPDATE');
                $scope.controller.update();
            }
        },
        zoomOutX      : function(noup) {
            var cs = $scope.canvas.body.scale();
            var x  = cs.x * 0.9;
            $scope.controller.zoomX( x, noup );
        },
        zoomInX       : function(noup) {
            var cs = $scope.canvas.body.scale();
            var x  = cs.x * 1.1;
            $scope.controller.zoomX( x, noup );
        },
        zoomOutY      : function(noup) {
            var cs = $scope.canvas.body.scale();
            var y  = cs.y * 0.9;
            $scope.controller.zoomY( y, noup );
        },
        zoomInY       : function(noup) {
            var cs = $scope.canvas.body.scale();
            var y  = cs.y * 1.1;
            $scope.controller.zoomY( y, noup );
        },
        zoomReset     : function(noup) {
            $scope.controller.zoom( $scope.vars.defaultMatrixWidthScale, $scope.vars.defaultMatrixHeightScale, noup );
        },
        reset         : function(noup) {
            console.log('reseting', $scope.canvas.body.scale(), $scope.canvas.body.offset(), $scope.canvas.body.x(), $scope.canvas.body.y() );
            $scope.controller.zoomReset(     true );
            $scope.controller.moveRightFull( true );
            $scope.controller.moveUpFull(    true );
            $scope.controller.update(noup);
            console.log('resetted', $scope.canvas.body.scale(), $scope.canvas.body.offset(), $scope.canvas.body.x(), $scope.canvas.body.y() );
        }
    };

    $scope.compileColors           = function ( data_info, callback ) {
        console.log("CONPILING COLORS. INFO %o", data_info);
        var minV      = data_info.minVal;
        var maxV      = data_info.maxVal;
        var fcount    = 0;
        var numcolors = Object.keys( $scope.setup.colors ).length;

        var snps      = $scope.getHeaderRow('num_snps');
        var minS      = Math.min.apply( null, snps );
        var maxS      = Math.max.apply( null, snps );


        var clb       = function() {
            fcount += 1;
            if (fcount == (numcolors*2)) {
                $scope.$apply( callback );
            }
        };

        for (var color in $scope.setup.colors) {
            console.log("compiling color ", color);

            var cdata = $scope.setup.colors[ color ];

            cdata.colorScale     = getColors(            minV, maxV, cdata.colors             );
            cdata.colorScaleRev  = getColors(            minS, maxS, cdata.revColors          );
            cdata.colorBlocks    = $scope.genBlockColor( minV, maxV, cdata.colorScale,    clb );
            cdata.colorBlocksRev = $scope.genBlockColor( minS, maxS, cdata.colorScaleRev, clb );
        }

        console.log("compiling color finished", $scope.setup.colors);
    };

    $scope.updateColors            = function ( colorName ) {
        $scope.vars.currColor       = colorName;
        if ( $scope.canvas ) {
          $scope.hasUpdatesBody       = true;
          $scope.hasUpdatesScale      = true;
          $scope.hasUpdatesG          = true;
        }
    };

    $scope.getColorValue           = function ( val ) {
        return $scope.setup.colors[    $scope.vars.currColor    ].colorScale(val);
    };

    $scope.getColorValueRev        = function (  val ) {
        return $scope.setup.colors[    $scope.vars.currColor    ].colorScaleRev(val);
    };

    $scope.getBlockRowCol          = function ( row, col  ) {
        var realVal = $scope.getMatrixVal(  row, col );
        return $scope.getBlock( realVal );
    };

    $scope.getBlockColRev          = function ( col  ) {
        var snps    = $scope.getHeaderRow('num_snps');
        var realVal = snps[ col ];

        return $scope.getBlockRev( realVal );
    };

    $scope.getBlock                = function ( val  ) {
        var block = $scope.setup.colors[    $scope.vars.currColor    ].colorBlocks( val );
        return block;
    };

    $scope.getBlockRev             = function ( val  ) {
        var block = $scope.setup.colors[    $scope.vars.currColor    ].colorBlocksRev( val );
        return block;
    };

    $scope.genBlockColor           = function ( vmin, vmax, colors, callback ) {
        var vPiece    = (vmax.toFixed(20) - vmin.toFixed(20)) / (blockQuanta);
        var vals      = [];
        var l         = new Kinetic.Layer();
        var c         = 0;
        var e         = 0;
        var clb       = function(d) {
                            return function(img) {
                                vals[d] = img;
                                e += 1;
                                if (e == blockQuanta) {
                                    callback();
                                }
                            };
                        };

        console.log( 'genblockcolor started: min %d max %d colors %o piece %d', vmin, vmax, colors, vPiece);
        for ( var p = 0; p < blockQuanta; p+=1) {
            var val = vmin + (p * vPiece);

            var rect = new Kinetic.Rect({
                x     : 0,
                y     : 0,
                width : $scope.setup.cellWidth,
                height: $scope.setup.cellHeight,
                fill  : colors( val )
            });

            l.add(rect);

            rect.toImage({
                    callback: clb(c)
                });

            vals.push( null );

            c += 1;
        }

        var valF = function( val ) {
            var valn = val - vmin;
            var vali = Math.floor(valn / vPiece);
            if (vali == vals.length) {
                vali = vals.length - 1;
            }
            var valr = vals[ vali ];
            return valr;
        };

        return valF;
    };

    $scope.hasUpdates              = function ( val ) {
        console.log('changing HAS UPATES to', val);
        $scope.hasUpdatesHeader     = val;
        $scope.hasUpdatesRows       = val;
        $scope.hasUpdatesBody       = val;
        $scope.hasUpdatesScale      = val;
        $scope.hasUpdatesIntrogress = val;
        $scope.hasUpdatesG          = val;

    };

    $scope.showCoord               = function ( col ) {
        var ordercol = $scope.vars.order.cols[ $scope.vars.currColOrder ];
        var realCol  = ordercol[ col ];
        var header   = $scope.data.header;
        var gene     = header.name[realCol];
        console.log('showing coord ',col, realCol, gene);
        $scope.gene  = gene;
        $scope.showGene(gene);
    };

    $scope.getColNum               = function ( col ) {
        return $scope.vars.order.cols[ $scope.vars.currColOrder ][ col ];
    };

    $scope.getRowNum               = function ( row ) {
        return $scope.vars.order.rows[ $scope.vars.currRowOrder ][ row ];
    };

    $scope.getMatrix               = function () {
        return $scope.data.data.line;
    };

    $scope.getMatrixRow            = function (  row ) {
        var realRow = $scope.getRowNum( row );
        return $scope.data.data.line[realRow];
    };

    $scope.getMatrixVal            = function ( row, col ) {
        var realCol = $scope.getColNum( col );
        var realRow = $scope.getRowNum( row );
        if (realRow < $scope.data.data.line.length) {
            var cols = $scope.data.data.line[ realRow ];
            if (realCol < cols.length) {
                return cols[ realCol ][0];
            } else {
                return null;
            }
        } else {
            return null;
        }
    };

    $scope.getNames                = function () {
        try {
            return $scope.data.data.name;
        } catch(e) {
            return [];
        }
    };

    $scope.getNamesVal             = function ( row ) {
        var realRow = $scope.getRowNum( row );
        return $scope.getNames()[ realRow ];
    };

    $scope.getHeader               = function () {
        return $scope.data.header;
    };

    $scope.getHeaderKeys           = function () {
        return Object.keys( $scope.getHeader() );
    };

    $scope.getHeaderRow            = function ( key ) {
        return $scope.getHeader()[key];
    };

    $scope.getHeaderVal            = function ( rowName, col ) {
        var realCol = $scope.getColNum( col );
        return $scope.getHeaderRow(rowName)[ realCol ];
    };

    $scope.getHeaderConvKey        = function ( key ) {
        return $scope.setup.headerConvKey[ key ];
    };

    $scope.getHeaderInfo           = function ( col ) {
        var res        = {};
        var headerKeys = $scope.getHeaderKeys();

        for ( var k = 0; k < headerKeys.length; k++ ) {
            var key    = headerKeys[k];
            var val    = $scope.getHeaderVal( key, col);
            var convK  = $scope.getHeaderConvKey( key );
            res[ convK ] = val;
        }

        return res;
    };

    $scope.getInfo                 = function () {
        return $scope.data.data_info;
    };

    $scope.updateTooltip           = function ( tip ) {
        $scope.tooltip.html(tip);
    };

    $scope.showTooltip             = function ( row, col ) {
        var nfo = $scope.getHeaderInfo(col);
        var val = $scope.getMatrixVal( row, col);
        var spp = $scope.getNamesVal(  row);
        nfo.Distance     = val;
        nfo.Specie       = spp;

        var tip = "";
        for ( var key in nfo ) {
            var val = nfo[ key ];
            if (( val !== null ) && ( val !== undefined)){
                if (!isNaN(val)){
                    if (val % 1 === 0) {
                        val = val.toLocaleString();
                    } else {
                        val = val.toFixed(5).toLocaleString({minimumFractionDigits: 5, maximumFractionDigits: 5});
                    }
                }
                tip += "<b>" + key + "</b>: " + val + " ";
            }
        }

        $scope.updateTooltip( tip );
    };

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
        $scope.updateWidthHeight();
        $scope.hasUpdates(true);
    };

    $scope.pathmouseover           = function ( ev ) {
        console.log( ev   );

        var bbox        = this.getBoundingClientRect();
        var spp         = this.getAttribute( 'spp' );
        var sppPos      = $scope.getNames().indexOf( spp );
        var paddingLeft = this.getBoundingClientRect().left - this.parentNode.parentNode.getBoundingClientRect().left;
        var pX          = ev.pageX;
        var pY          = ev.pageY;
        var x           = ev.x;
        var y           = ev.y;
        var xpos        = pX - paddingLeft;
        var max         = $scope.vars.numCols - 1;
        var width       = bbox.width;
        var pxperx      = (width / max);
        var pos         = Math.round(xpos/pxperx) - 1;

        console.log("paddingLeft %d x %d xpos %d max %d width %d pxperx %d pos %d spp %s", paddingLeft, pX, xpos, max, width, pxperx, pos, spp);

        $scope.showCommonAncestor(spp, pX, pY, x, y, pos);
    };

    $scope.pathmouseout            = function ( ev ) {
        console.log('mouse out');
        var $sel = $('#tree_render_small');
        if ( $sel.length > 0 ) {
            $sel.remove();
        }
    };

    $scope.downloadCanvasAsImage   = function ( fmt ) {

        console.log('saving file: fmt', fmt);

        if (fmt == 'jpeg') {
            $scope.canvas.stage.add( $scope.canvas.background );
            $scope.canvas.background.moveToBottom();
        }

        var rh = $scope.canvas.ruler.height();
        $scope.controller.update();
        console.warn($scope.canvas.background.children[0]);
        $scope.canvas.background.width(             $scope.vars.svgWidth  );
        $scope.canvas.background.children[0].width( $scope.vars.svgWidth  );
        $scope.canvas.body.width(                   $scope.vars.svgWidth  );
        $scope.canvas.body.height(                  $scope.vars.svgHeight );
        $scope.canvas.ruler.height(                 $scope.vars.svgHeight );
        $scope.canvas.ruler.draw();
        $scope.canvas.stage.draw();
        $scope.canvas.background.draw();

        $scope.canvas.stage.toDataURL({
            callback: function(imageURL) {
                console.log('OPENING URL');

                if (fmt == 'jpeg') {
                    $scope.canvas.background.remove();
                }
                $scope.canvas.ruler.height( rh );

                window.open(imageURL);
            },
            mimeType: 'image/'+fmt,
            quality: 1.0,
            height: $scope.vars.svgHeight,
            width:  $scope.vars.svgWidth
        });
        console.log( $scope.canvas.stage );
    };

    $scope.getMousePos             = function (canvas, evt ) {
        var rect = canvas.canvas._canvas.getBoundingClientRect();
        return {
            x: ( evt.evt.clientX - rect.left - $scope.vars.matrixX ) / canvas.scaleX(),
            y: ( evt.evt.clientY - rect.top  - $scope.vars.matrixY ) / canvas.scaleY()
        };
    };

    $scope.mousePosToCoord         = function ( mousePos ) {
        var message1 = 'mousePosToVar: Mouse position: ' + mousePos.x + ',' + mousePos.y;
        console.log(message1);

        var colNum   = Math.floor( mousePos.x / $scope.vars.cellWidth  );
        var rowNum   = Math.floor( mousePos.y / $scope.vars.cellHeight ) - 1;

        var message2 = 'mousePosToVar: Matrix position: ' + colNum + ',' + rowNum;
        console.log(message2);

        return {
            x: colNum,
            y: rowNum
        };
    };




    //
    // MATRIX
    //
    $scope.funcs                   = {};
    $scope.funcs.matrix            = {};

    $scope.funcs.matrix.scale      = function ( $scope, $element, attrs ) {
        console.log('UPDATING MATRIX SCALE');

        var info             = $scope.getInfo();
        var scaleHeight      = $scope.setup.scaleHeight;
        var scaleSplits      = $scope.setup.scaleSplits;
        var scaleTextWidth   = $scope.setup.scaleTextWidth;
        var scaleBlockWidth  = $scope.setup.scaleBlockWidth;

        var dmin             = info.minVal;
        var dmax             = info.maxVal;
        var ddif             = dmax - dmin;
        var dfrag            = (ddif        * 1.0) / (scaleSplits);

        var labelYpos        = (scaleHeight / 2.0) + (matrixFontSize/2);

        var tip              = document.getElementById('tooltip');

        function genbar(g, title, colorFunc, Xpos, Ypos, vmin, vmax, samp, stats) {
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

            var textEndPos  = Xpos + (txt1txt.length * pixelPerLetterW);
            var blockHeight = function(i) { return (0.25+(stats[i]*0.75)) * scaleHeight; };
            var gb          = new Kinetic.Group();

            for ( var s = 0; s < samp.length; s++) {
                var val    = samp[ s ];
                var height = blockHeight(s);
                var y      = scaleHeight - height;

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


        var G        = $scope.canvas.scale;
            G.destroyChildren();


        //
        // distance scale
        //
        var samples = [];
        var stats   = [];
        for ( var i = dmin; i <= dmax; i+=dfrag) {
            samples.push( i.toFixed(2) );
            stats  .push( 0            );
        }


        var data        = $scope.getMatrix();
        var statsSum    = 0;
        for ( var r = 0; r < data.length; r++ ) {
            var cols = data[r];
            for ( var c = 0; c < cols.length; c++ ) {
                var v = cols[c];
                var d = v[0];
                var k = Math.round( d / dfrag );
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

        var txt2EndPos  = genbar(G, 'Distance', $scope.getColorValue, 0, labelYpos, dmin, dmax, samples, statsPro);
        txt2EndPos     += scaleTextWidth;





        //
        // snps scale
        //
        var snps  = $scope.getHeaderRow('num_snps');
        samples   = [];
        stats     = [];
        statsPro  = [];
        statsSum  = 0;
        var smin  = Math.min.apply( null, snps );
        var smax  = Math.max.apply( null, snps );
        var sdif  = smax - smin;
        var sfrag = (sdif        * 1.0) / (scaleSplits);

        for ( var i = smin; i <= smax; i+=sfrag) {
            samples.push( i.toFixed(2) );
            stats  .push( 0            );
        }

        for ( var c = 0; c < snps.length; c++ ) {
            var v = snps[c];
            var k = Math.round( v / sfrag );
            if ( k >= stats.length ) {
                k = stats.length - 1;
            }
            stats[ k ] += 1;
            statsSum   += 1;
        }

        statsPro = [];

        for ( var s = 0; s < stats.length; s++ ) {
            statsPro.push( stats[s] / statsSum );
        }

        txt2EndPos  = genbar(G, '#SNPs', $scope.getColorValueRev, txt2EndPos, labelYpos, smin, smax, samples, statsPro);
        txt2EndPos += scaleTextWidth;




        var graphTitle =
                            'Database '   + $scope.database   + '\n' +
                            'Chromosome ' + $scope.chromosome + ' ' +
                            'Species '    + $scope.specie
                        ;

        if ($scope.groupBy) {
            console.log($scope.groupBy);
            graphTitle += '; Grouping by ' + $scope.groupBy + ' every ' + $scope.groupByVal + ' ';
        }

        if ($scope.clusterSegments) {
            graphTitle += '; Clustering segments ';
        }

        if ($scope.clusterRows) {
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

        console.log('UPDATING MATRIX SCALE FINISHED');
    };

    $scope.funcs.matrix.header     = function ( $scope, $element, attrs ) {
        console.log('UPDATING MATRIX HEADER');

        var axisX          = $scope.vars.axisX;
        var axisY          = $scope.vars.axisY;

        var axisTextHeight = $scope.vars.axisTextHeight;
        var headerKeys     = $scope.getHeaderKeys();

        var headerX        = $scope.vars.headerX;

        var colTextHeight  = $scope.vars.colTextHeight;
        var colTextWidth   = $scope.vars.colTextWidth;


        var header         = $scope.canvas.header;
        header.x(       axisX             );
        header.y(       axisY             );
        header.visible( $scope.showHeader );


        if ( $element.children().length && $scope.canvas && $scope.canvas.header && $scope.canvas.header.hasChildren() ) { //cells already exists
            console.log('UPDATING MATRIX HEADER - EXISTS - UPDATING');


            var Gaxis = header.axis.getChildren();
            for ( var row = 0; row < Gaxis.length; row++) {
                var child   = Gaxis[ row ];
                child.x( 0                    );
                child.y( row * axisTextHeight );
            }

        } else {
            console.log('UPDATING MATRIX HEADER - DOES NOT EXISTS - CREATING');
            var axis = new Kinetic.Group();
            var cols = new Kinetic.Group();

            header.add( axis );
            header.add( cols );

            header.axis = axis;
            header.cols = cols;

            console.time("header name");
            for ( var row = 0; row < headerKeys.length; row++) {
                var val     = $scope.getHeaderConvKey( headerKeys[row] );

                var nel     = new Kinetic.Text({
                    x         : 0,
                    y         : row * axisTextHeight,
                    text      : val,
                    fontSize  : matrixFontSize,
                    fontFamily: 'Calibri',
                    fill      : 'black'
                });

                axis.add( nel );
            }
            console.timeEnd("header name");

        }

        console.log('UPDATING MATRIX HEADER FINISHED');
    };

    $scope.funcs.matrix.rows       = function ( $scope, $element, attrs ) {
        console.log('UPDATING MATRIX ROWS');

        var rowNamesX     = $scope.vars.rowNamesX;
        var rowNamesY     = $scope.vars.rowNamesY;
        var rowTextHeight = $scope.vars.rowTextHeight;

        var names         = $scope.getNames();

        var rep           = $scope.canvas.rows;
            rep.destroyChildren();
            rep.x(       rowNamesX      );
            rep.y(       rowNamesY      );
            rep.visible( $scope.showRow );

        var nelp          = new Kinetic.Text({
            x         : 0,
            y         : 0,
            fontSize  : matrixFontSize,
            fontFamily: 'Calibri',
            fill      : 'black'
        });

        console.log('UPDATING MATRIX ROWS CREATING', rowTextHeight);
        for ( var row = 0; row < names.length; row++) {
            var realVal = $scope.getNamesVal( row );
            var y       = row * rowTextHeight;
            var nel     = nelp.clone({
                text: realVal,
                y   : y
                });
            rep.add(nel);
        }

        console.log('UPDATING MATRIX ROWS FINISHED');
    };

    $scope.funcs.matrix.body       = function ( $scope, $element, attrs, callback ) {
        console.log('UPDATING MATRIX BODY scope %o element %o attrs %o', $scope, $element, attrs);

        var matrixx       = $scope.vars.matrixX;
        var matrixy       = $scope.vars.matrixY;

        var matrixHeight  = $scope.vars.matrixHeight;
        var matrixWidth   = $scope.vars.matrixWidth;

        var cellheight    = $scope.vars.cellHeight;
        var cellwidth     = $scope.vars.cellWidth;

        var numbered      = false;

        var br = new Kinetic.Rect({
                    x     : 0,
                    y     : 0,
                    width : $scope.vars.svgWidth,
                    height: $scope.vars.svgHeight,
                    fill  : 'white'
                });
        $scope.canvas.background.removeChildren();
        $scope.canvas.background.add( br );


        $scope.canvas.body.removeChildren();

        console.log('UPDATING MATRIX BODY. GETTING MATRIX');

        var line          = $scope.getMatrix();

        console.log('UPDATING MATRIX BODY. GOT MATRIX');

        console.log( "MATRIX X %o Y %o MH %o MW %o CH %o CW %o", matrixx, matrixy, matrixHeight, matrixWidth, cellheight, cellwidth );

        console.time("body iter");

        var cellC         = 0;
        var cvans         = document.createElement('canvas');
            cvans.height  = matrixHeight;
            cvans.width   = matrixWidth;
            cvans.cw      = cellwidth;
            cvans.ch      = cellheight;
        var ctx           = cvans.getContext("2d");
            ctx.imageSmoothingEnabled = false;

        var totaly        = line.length;


        var addImg       = function() {
            console.log('addImg');

            var imgo = new Image();
            imgo.onload = function() {
                console.timeEnd("convertion");

                var kimg = new Kinetic.Image({
                    image: this
                });

                $scope.$apply ( function() {
                    console.time("insertion");
                    $scope.canvas.body.x(       matrixx      );
                    $scope.canvas.body.y(       matrixy      );
                    $scope.canvas.body.height(  matrixHeight );
                    $scope.canvas.body.width(   matrixWidth  );
                    $scope.canvas.body.add(     kimg         );
                    console.timeEnd("insertion");
                    console.timeEnd("body iter");
                    callback();
                    console.log("cells", cellC);
                } );
            };
            console.time("convertion");
            imgo.src = cvans.toDataURL("image/jpeg", 1.0);

        };

        var workerfc = 0;
        var workerf  = function(e) {
            var data = e.data;
            wrc = this;

            if (data.cmd) {
                if (data.cmd == 'log') {
                }
                else if (data.cmd == 'dorow') {
                    var row     = data.data;
                    var d = new Date();
                    var n = d.getTime();
                    var y       = (row+1) * cellheight;
                    var rowData = $scope.getMatrixRow( row );

                    for ( var col = 0; col < rowData.length; col++ ) {
                        var x      = col * cellwidth;
                        var block  = $scope.getBlockRowCol( row, col );
                        cellC     += 1;
                        ctx.drawImage( block, x, y, cellwidth, cellheight);

                        if ( row === 0 ) {
                            var blockS  = $scope.getBlockColRev( col );
                            ctx.drawImage( blockS, x, 0, cellwidth, cellheight);
                        }
                    }

                    workerfc += 1;
                    d = new Date();
                    n = d.getTime();
                    if ( workerfc == line.length ) {
                        addImg();
                        console.log('TERMINATING MATRIX WORKER');
                        wrc.terminate();
                    } else {
                        console.log('PROCESSED MATRIX WORKER', workerfc, '/', line.length);
                    }
                }
            }
        };


        var worker  = new Worker('static/js/controller_webworker.js?matrix');
            worker.addEventListener('message', workerf, false);

        for ( var row = 0; row < line.length; row++) {
            worker.postMessage({ 'cmd': 'dorow', 'data': row});
        }
    };

    $scope.funcs.matrix.ruler       = function ( $scope, $element, attrs ) {
        console.log('UPDATING MATRIX RULER scope %o element %o attrs %o', $scope, $element, attrs);

        $scope.redoRuler();
    };

    $scope.funcs.matrix.canvas     = function ( $scope, $element, attrs ) {
        console.log('HAS UPDATE IN CANVAS');
        $scope.working    = true;

        $scope.updateWidthHeight();

        var doFullRedraw = false;
        var addLayers    = false;

        if ((!$scope.canvas) || (!$scope.canvas.stage)) {
            console.log('HAS UPDATE IN CANVAS - NO CANVAS - CREATING');

            $scope.canvas.stage = new Kinetic.Stage({
                container : $element.attr('id'),
                width     : $scope.vars.svgWidth,
                height    : $scope.vars.svgHeight,
                draggable : false
            });

            addLayers                = true;
            doFullRedraw             = true;

            $scope.canvas.background = new Kinetic.Layer({ 'id': 'canvas_background' });
            $scope.canvas.scale      = new Kinetic.Layer({ 'id': 'canvas_scale'      });
            $scope.canvas.rows       = new Kinetic.Layer({ 'id': 'canvas_rows'       });
            $scope.canvas.ruler      = new Kinetic.Layer({ 'id': 'canvas_ruler'      });

            var bdycfg = {
                    'id'      : 'canvas_body',
                    scaleX    : $scope.vars.matrixWidthScale
                };
            if (!$scope.setup.full_size) {
                    bdycfg.draggable     = true;
                    bdycfg.dragBoundFunc = function(pos) {
                        return {
                            x: pos.x,
                            y: this.getAbsolutePosition().y
                        };
                    };
            }
            $scope.canvas.body       = new Kinetic.Layer( bdycfg );





            $scope.canvas.body.listening(true);

            $scope.canvas.body.on('click', function(evt) {
                evt.cancelBubble = true;
                var mousePos     = $scope.getMousePos($scope.canvas.body, evt);
                var message      = 'Mouse position: ' + mousePos.x + ',' + mousePos.y;
                console.log(message);
                var matrixPos    = $scope.mousePosToCoord( mousePos );
                $scope.showTooltip( matrixPos.y, matrixPos.x );
            }, false);

            $scope.canvas.body.on('dblclick', function(evt) {
                evt.cancelBubble = true;
                var mousePos     = $scope.getMousePos($scope.canvas.body, evt);
                var message      = 'Mouse position: ' + mousePos.x + ',' + mousePos.y;
                console.log(message);
                var matrixPos    = $scope.mousePosToCoord( mousePos );
                $scope.showCoord( matrixPos.x );
            }, false);

        } else {
            console.log('HAS UPDATE IN CANVAS - RESIZING - W', $scope.vars.svgWidth, " H ", $scope.vars.svgHeight );
            if ( $scope.canvas.stage.width != $scope.vars.svgWidth  ) {
                doFullRedraw = true;
            }

            if ( $scope.canvas.stage.height != $scope.vars.svgHeight) {
                doFullRedraw = true;
            }
        }

        console.log('HAS UPDATE IN CANVAS - CALLING');

        var cmds       = ['doscale', 'dorows', 'doruler', 'dobody']; //'doheader',
        var cmdrun     = 0;
        var fullRedraw = function( wrk ) {
            cmdrun += 1;
            if (cmdrun == cmds.length) {
                if (doFullRedraw) {
                    console.log( "HAS UPDATE IN CANVAS - FULL REDRAW");
                    console.time("full redraw");

                    console.time(   "reset controller");
                    $scope.controller.reset(true);
                    console.timeEnd("reset controller");

                    console.time(   "drawing");
                    $scope.controller.resize();
                    console.timeEnd("drawing");

                    console.log(    "HAS UPDATE IN CANVAS - FULL REDRAW FINISHED");
                    console.timeEnd("full redraw");
                    console.timeEnd("adding");
                }

                console.log('TERMINATING CANVAS UPDATE WORKER');
                $scope.working = false;
                wrk.terminate();
            }
        };

        console.log('HAS UPDATE IN CANVAS - CALLED');

        var workerfc = 0;
        var workerf = function(e){
            var data  = e.data;
            var wrk   = this;

            if (data.cmd) {
                workerfc += 1;

                if (data.cmd == 'log') {
                    //console.log('worker received:', data.data );
                }
                else if (data.cmd == 'doscale') {
                    console.time("adding scale");
                    if ($scope.hasUpdatesScale) {
                        console.time("adding scale calc");
                        $scope.funcs.matrix.scale($scope, $element, attrs);
                        console.timeEnd("adding scale calc");
                        console.time("adding scale append");
                        $scope.canvas.stage.add( $scope.canvas.scale      );
                        $scope.canvas.scale.batchDraw();
                        console.timeEnd("adding scale append");
                        fullRedraw( wrk );
                    }
                    console.timeEnd("adding scale");
                }
                else if (data.cmd == 'doheader') {
                    console.time("adding header");
                    if ($scope.hasUpdatesHeader) {
                        console.time("adding header calc");
                        $scope.funcs.matrix.header($scope, $element, attrs);
                        console.timeEnd("adding header calc");
                        console.time("adding header append");
                        $scope.canvas.stage.add( $scope.canvas.header      );
                        console.timeEnd("adding header append");
                        $scope.canvas.header.batchDraw();
                        fullRedraw( wrk );
                    }
                    console.timeEnd("adding header");
                }
                else if (data.cmd == 'dorows') {
                    console.time("adding rows");
                    if ($scope.hasUpdatesRows) {
                        console.time("adding rows calc");
                        $scope.funcs.matrix.rows($scope, $element, attrs);
                        console.timeEnd("adding rows calc");
                        console.time("adding rows append");
                        $scope.canvas.stage.add( $scope.canvas.rows      );
                        $scope.canvas.rows.batchDraw();
                        console.timeEnd("adding rows append");
                        fullRedraw( wrk );
                    }
                    console.timeEnd("adding rows");
                }
                else if (data.cmd == 'dobody') {
                    console.time("adding body");
                    if ($scope.hasUpdatesBody) {
                        console.time("adding body calc");
                        $scope.funcs.matrix.body($scope, $element, attrs, function(){
                            console.timeEnd("adding body calc");
                            console.time("adding body append");
                            $scope.canvas.stage.add( $scope.canvas.body      );
                            $scope.canvas.body.batchDraw();
                            console.timeEnd("adding body append");
                            fullRedraw( wrk );
                            console.timeEnd("adding body");
                        });
                    }
                }
                else if (data.cmd == 'doruler') {
                    console.time("adding ruler calc");
                    if ($scope.hasUpdatesBody) {
                        console.time("adding ruler");
                        $scope.funcs.matrix.ruler($scope, $element, attrs);
                        console.timeEnd("adding ruler calc");
                        console.time("adding ruler append");
                        $scope.canvas.stage.add( $scope.canvas.ruler      );
                        $scope.canvas.ruler.batchDraw();
                        console.timeEnd("adding ruler append");
                        fullRedraw( wrk );
                    }
                    console.timeEnd("adding ruler");
                }

                console.log('PROCESSED CANVAS WORKER', workerfc, '/', cmds.length);
            }
        };


        console.time("adding");
        var worker  = new Worker('static/js/controller_webworker.js?canvas');
            worker.addEventListener('message', workerf, false);
        for ( var cmdN in cmds ) {
            var cmd = cmds[cmdN];
            console.log('calling %s worker', cmd);
            worker.postMessage({ 'cmd': cmd, 'data': null});
        }

    };

    $scope.redoRuler                = function() {
        var scale         = 1.0;
        var matrixx       = $scope.vars.matrixX;
        var matrixy       = $scope.vars.matrixY;

        if ($scope.canvas.body) {
            scale = $scope.canvas.body.scaleX();
        }

        //var matrixHeight  = $scope.vars.matrixHeight;
        var matrixWidth   = $scope.vars.matrixWidth;

        var cellheight    = $scope.vars.cellHeight;
        var cellwidth     = $scope.vars.cellWidth;

        var rulerHeight   = $scope.vars.rulerHeight;
        var rulerWidth    = matrixWidth * scale;
        var rulerx        = $scope.vars.rulerX;
        var rulery        = $scope.vars.rulerY;

        $scope.canvas.ruler.removeChildren();

        console.log('UPDATING MATRIX RULER. X', rulerx, 'Y', rulery, 'W', rulerWidth, 'H', rulerHeight, 'cW', cellwidth, 'ch', cellheight);
        console.log('UPDATING MATRIX RULER. GETTING MATRIX');

        var line          = $scope.getMatrix();
        var totaly          = line.length;
        var doney           = 0;


        var starts          = $scope.getHeaderRow('start');
        var smin            = Math.min.apply(null, starts);
        var smax            = Math.max.apply(null, starts);
        var sdiff           = smax - smin;
        var rowLen          = rulerWidth;
        var maxRulerNameLen = 9 * (matrixFontSize / 2);              // position name has, at most, 9 chars
        var barWidth        = Math.floor( matrixFontSize  / 4     ); // vertical bar is 1/4th of the width of a letter
        var rulerPieceSize  = Math.floor( maxRulerNameLen * 2     ); // each bar accomodates 3 times the size of the text
        var rulerStep       = Math.floor( rulerPieceSize  / 5     ); // each sub-step appears at 1/5th of the length of the bar
        var numRulerPieces  = Math.floor( rowLen / rulerPieceSize ) - 1; // number of bars in total
        //console.warn("starts %o smin %d smax %d sdiff %d rowLen %d maxRulerNameLen %d rulerPieceSize %d rulerStep %d numRulerPieces %d",
                     //starts, smin, smax, sdiff, rowLen, maxRulerNameLen, rulerPieceSize, rulerStep, numRulerPieces );


        var rulerF = new Kinetic.Group({
            x           : 0,
            y           : 0,
            width       : rowLen,
            height      : rulerHeight
        });

        var rulerPiece = new Kinetic.Group({
            x           : 0,
            y           : 0,
            width       : rulerPieceSize,
            height      : rulerHeight
        });

        var rulerLongLine = new Kinetic.Rect({
            x           : rulerPieceSize,
            y           : 0,
            width       : barWidth,
            height      : Math.floor( matrixFontSize * 1 ),
            fill        : '#093',
            cornerRadius: 2
        });

        rulerPiece.add( rulerLongLine );

        var nelp          = new Kinetic.Text({
            x         : rulerPieceSize + barWidth,
            y         : 0,//ph,
            fontSize  : matrixFontSize,
            fontFamily: 'Calibri',
            fill      : 'black'
        });

        for ( var q = 0; q < numRulerPieces; q++ ) {
            var piecex  = (q * rulerPieceSize);
            //console.log('piecex', piecex);
            var piece   = rulerPiece.clone({
                x: piecex
            });

            if (q === 0) {
                var cellVal0 = starts[ 0 ];
                var nel0     = nelp.clone({
                    text: formatValStr( cellVal0 ),
                    x   : barWidth
                });

                piece.add( nel0 );
                piece.add( rulerLongLine.clone({ x: 0 }) );

                var cellVal1    = starts[ starts.length -1 ];
                var cellVal1Txt = formatValStr( cellVal1 );
                console.log('cellVal1', cellVal1, 'cellVal1Txt', cellVal1Txt, 'cellVal1Txt.length', cellVal1Txt.length, 'x', rulerWidth - barWidth - (cellVal1Txt.length * (matrixFontSize / 2)));
                var nel1     = nelp.clone({
                    text: cellVal1Txt,
                    x   : rulerWidth - barWidth - (cellVal1Txt.length * (matrixFontSize / 2))
                });

                piece.add( nel1  );
                piece.add( rulerLongLine.clone({ x: rulerWidth - barWidth }) );
            }

            var cellId  = Math.floor( ((piecex + rulerPieceSize)/scale) / cellwidth );
            var cellVal = starts[ cellId ];
            //console.log('q', q, 'piecex', piecex, 'cellId', cellId, 'cellval', cellVal);
            if (cellVal) {
                var nel     = nelp.clone({
                    text: formatValStr( cellVal )
                });

                piece.add(  nel  );
            }
            rulerF.add( piece );
        }

        $scope.canvas.ruler.add(    rulerF      );
        $scope.canvas.ruler.x(      rulerx      );
        $scope.canvas.ruler.y(      rulery      );
        $scope.canvas.ruler.height( rulerHeight );
        $scope.canvas.ruler.width(  rulerWidth  );
        $scope.canvas.ruler.draw();
        $scope.canvas.stage.draw();
        console.log('UPDATING MATRIX RULER. FINISHED');
    };

    $scope.onMouseWheel            = function(layer, e, delta, deltaX, deltaY) {
      //http://codepen.io/netgfx/pen/CKFLu

      // mozilla fix...
        if (e.originalEvent.detail){
            delta = e.originalEvent.detail;
        }
        else{
            delta = e.originalEvent.wheelDelta;
        }

		if (delta !== 0) {
			e.preventDefault();
		}

        var scales    = layer.scale();
        var scaleX    = scales.x;
        var scaleY    = scales.y;

		var cur_scaleX;
		var cur_scaleY;
		if (delta > 0) {
			cur_scaleX = scaleX + Math.abs(delta / 640);
			cur_scaleY = scaleY + Math.abs(delta / 640);
		} else {
			cur_scaleX = scaleX - Math.abs(delta / 640);
			cur_scaleY = scaleY - Math.abs(delta / 640);
		}

        console.log('>>>>',e,delta,e.detail);
		//check for minimum scale limit
        //console.log(cur_scale, min_scale);
		//if (cur_scale > min_scale) {
			var d        = document.getElementById('graph');
            var cnvsPos  = $scope.getPos(d);
			var Apos     = layer.getAbsolutePosition();
			var mousePos = layer.getPosition();

            console.log(d,cnvsPos,Apos,mousePos);
			var smallCalcX = (e.originalEvent.pageX - Apos.x - cnvsPos.x) / scaleX;
			var smallCalcY = (e.originalEvent.pageY - Apos.y - cnvsPos.y) / scaleY;

			var endCalcX   = (e.originalEvent.pageX          - cnvsPos.x) - (cur_scaleX * smallCalcX);
			var endCalcY   = (e.originalEvent.pageY          - cnvsPos.y) - (cur_scaleY * smallCalcY);

			//scale = cur_scale;

            console.log( "X %d Y %d sX %d sY %d", endCalcX, endCalcY, cur_scaleX, cur_scaleY );
			layer.setPosition({ x: endCalcX, y: endCalcY });

			layer.scaleX( cur_scaleX );
            layer.scaleY( cur_scaleY );
            layer.draw();
		//}
	};

	$scope.getPos                  = function (el) {
		for (var lx=0, ly=0;
            el != null;
            lx += el.offsetLeft, ly += el.offsetTop, el = el.offsetParent);
    	return {x: lx,y: ly};
	};


    //
    // INITIALIZING
    //
    $scope.cleanVars();
    $scope.updateSizes();


    $scope.clusterSegments   = false;
    $scope.clusterRows       = false;

    $scope.clusterAlive      = false;
    $scope.converterAlive    = false;
    $scope.showHeader        = false;
    $scope.showRow           = false;
    $scope.canvas            = null;

    $scope.pdbAlive          = false;
    $scope.getAlives();

    $scope.defaultClusterName = 'Alphabetical';

    $scope.vars              = {};
    $scope.vars.currColor    = 'red';
    $scope.vars.currColOrder = $scope.defaultClusterName;
    $scope.vars.currRowOrder = $scope.defaultClusterName;
    $scope.vars.nextColOrder = $scope.defaultClusterName;
    $scope.vars.nextRowOrder = $scope.defaultClusterName;

    $scope.vars.scaleHeight  = $scope.setup.scaleHeight;
    $scope.initiated         = true;
    $scope.hasUpdates(false);

    $scope.tooltip           = $('#tooltip');



    //$scope.specieQry         = "ref";
    //$scope.databaseQry      = "Tomato 84 - 10Kb";
    //$scope.databaseQry       = "Tomato 84 - 50Kb";
    //$scope.chromosomeQry     = "SL2.40ch06";

    //$scope.specieQry        = "ref";
    //$scope.databaseQry      = "Arabidopsis 50k";
    //$scope.databaseQry      = "Arabidopsis 50k - Chr 4 - Xianwen";
    //$scope.chromosomeQry    = "Chr4";


    $scope.updateFields();

    //$scope.element          = document.getElementById(CANVAS_EL);

    //setTimeout(function(){document.getElementById('btn_send').click();}, 3000);

    $scope.working          = false;
};


function numeric_to_unicode(s) {
	return s.replace(/&#(\d+);/g, function (m, n) { return String.fromCharCode(n); });
}

function list_to_utf(lst) {
	return lst;
	var l = $.map( lst, numeric_to_unicode );
	//console.log('list_to_utf', lst, l);
	return l;
}




var app = angular.module('myApp', [])
    .service(   'sharedService'   , [sharedService                              ])
    .controller('mainController'  , ['$scope', '$http', 'sharedService', mainController  ])
;

//http://lorenhoward.com/blog/how-to-get-angular-to-work-with-jinja/
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

app.filter('iff', function () {
    return function(input, truevalue, falsevalue) {
        //console.log(" input %o true %o false %o", input, truevalue, falsevalue);
        return input ? truevalue : falsevalue;
    };
});

app.directive('canvasmatrix', function () {
    function updateField($scope, $element, attrs) {
        //console.log('calling svgmatrix lnk field update');

        var hasupdates = $scope.$eval( attrs.hasupdates );

        if (!hasupdates) {
            //console.log('svgmatrix already updated');
            return;
        } else {
            //console.log('svgmatrix running update');
        }


        if (attrs.show) {
            var show = $scope.$eval(attrs.show);

            if (!show) {
                //console.log('svgmatrix no show');
                $scope.$eval( attrs.hasupdates + ' = false');
                $element.empty();
                return;
            }
        }

        if (attrs.func) {
            var func = $scope.$eval(attrs.func);
            if (func) {
                func($scope, $element, attrs);
            } else {
                console.log("NO FUNCTION");
                return;
            }
        }

        $scope.$eval( attrs.hasupdates + ' = false');
    }

    function lnk($scope, $element, attrs) {
        console.log('calling svgmatrix lnk');
        $scope.$watch(attrs.hasupdates, function() { updateField($scope, $element, attrs); });
    }

    return {
        restrict: 'A',
        transclude: true,
        link: lnk
    };
});







var colors = {
    'rainbow'  : {
        'colors'   : ["white", "blue"  , "cyan"    , "green", "yellow", "red", "pink"],
        'letter'   : 'r',
        'color'    : 'white',
        'colorS'   : 'black',
        'revColors': ["white", "grey"],
    },
    'blue'  : {
        'colors'   : ["blue"  , "white"    , "red"],
        'letter'   : 'b',
        'color'    : 'cyan',
        'colorS'   : 'white',
        'revColors': ["lime", "forestgreen"],
    },
    'green' : {
        'colors'   : ["white" , "limegreen", "green"],
        'letter'   : 'g',
        'color'    : 'lime',
        'colorS'   : 'white',
        'revColors': ["yellow", "orange"   , "red"],
    },
    'grey'  : {
        'colors'   : ["white" , "grey"     , "black"],
        'letter'   : 'g',
        'color'    : 'gainsboro',
        'colorS'   : 'white',
        'revColors': ["yellow", "orange"   , "red"],
    },
    'red'   : {
        'colors'   : ["yellow", "orange"   , "red"],
        'letter'   : 'r',
        'color'    : 'red',
        'colorS'   : 'white',
        'revColors': ["white" , "limegreen", "green"],
    },
    'yellow': {
        'colors'   : ["red" , "orange"   , "yellow"],
        'letter'   : 'y',
        'color'    : 'yellow',
        'colorS'   : 'white',
        'revColors': ["white" , "limegreen", "green"],
    }
};



function getColors (vmin, vmax, scheme) {
    var sLen   = scheme.length;
    var vPiece = (vmax - vmin) / sLen;
    //var vmid   = ((vmax - vmin) / 2.0).toFixed(4);
    var vals   = [];

    for ( var val = vmin; val <= vmax; val += vPiece ) {
        vals.push( val );
    }
    console.log("getColors: vmin %o vmax %o scheme %o slen %o vpiece %o vals %o", vmin, vmax, scheme, sLen, vPiece, vals);

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

function data2path(data, sColor, sWidth) {
    var line = document.createElementNS( xmlns, 'path');
        line.setAttributeNS( null, "d"           , lineF( data ));
        line.setAttributeNS( null, "stroke"      , sColor       );
        line.setAttributeNS( null, "stroke-width", sWidth       );
        line.setAttributeNS( null, "fill-opacity", 0            );
        //line.setAttributeNS( null, "fill"        , "black"      );

    return line;
}

























var TreeDiv = 'tree';
function loadReport(data) {
    //register[ DB_TREE    ] = { 'newick': tree_str, 'png'   : tree_img  }
    //register[ DB_FASTA   ] = { 'fasta' : snpSeq  , 'coords': coords    }
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

    var spps    = list_to_utf(data['spps'   ]);
    var matrix  = data['LINE'   ];

    var treeStr = data['TREE'   ].newick;
    var treePng = data['TREE'   ].png;

    var aln     = data['FASTA'  ].fasta;
    var coords  = data['FASTA'  ].coords;

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

    console.time('report header');
    for ( ppos = 0; ppos < pairs.length; ++ppos ) {
        var pval  = pairs[ppos];
        trs[ppos] = $('<tr>', {'class': 'reportLine'})
                    .append( $('<td>', { 'class': 'reportCell reportHeader' }).html( pval[0] ) )
                    .append( $('<td>', { 'class': 'reportCell reportVal'    }).html( pval[1] ) );
    }
    console.timeEnd('report header');


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

    console.time('report tree');
    showTree(      filename, treeStr, treePng,              treeDst   );
    console.timeEnd('report tree');

    console.time('report matrix');
    showMatrix(    filename,          spps, matrix,         matrixDst );
    console.timeEnd('report matrix');

    console.time('report alignment');
    showAlignment( filename, desc,    spps, aln   , coords, alnDst    );
    console.timeEnd('report alignment');

    console.log('load report: opening');

    console.time('report open');
    $TreeDiv.dialog('open');
    console.timeEnd('report open');

    console.log('load report: done');
}


function showTree(filename, treeStr, treePng, dst) {
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
    //var downloadPNG = function(){ svgtopng(pfile, svgSrc); };
    var downloadPDF = function(){ svgtopdf(ffile, svgSrc); };

    console.log( treePng );
    var downloadPNG = function(){ b64toimg(treePng, pfile, 'png') }

    $('<a>', {'class': 'downloadlink'}).text('Download PNG //'      ).click(downloadPNG).insertAfter('#tree_render');
    //$('<a>', {'class': 'downloadlink'}).text('Download PDF //'   ).click(downloadPDF).insertAfter('#tree_render');
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
                //tclass = {'class': 'matrixCell matrixVal matrixParallel'};
                tclass = {'class': 'matrixCell matrixVal matrixMain'    };
            } else {
                tclass = {'class': 'matrixCell matrixVal matrixMain'    };
            }

            if ( l > k ) {
                $td = $('<td>', tclass).appendTo($tr);
            } else {
                $td = $('<td>', tclass).append(cVal).appendTo($tr);
            }
            //console.log('aln '+k+' v '+v);
        });
        omtrx += "\n";
    });

    var nfile  = filename + '_MATRIX.tsv';
    $('<a>', {'class': 'downloadlink'}).data('ofile', nfile).data('src', omtrx).data('filetype', "text/plain").text('Download Matrix').click(downloadData).insertAfter($dst);

    console.log("show matrix done");
}


function showAlignment ( filename, desc, spps, aln, coords, alnDst ) {
    var self  = this;
    var $dst  = $('#'+alnDst);
    var $tbl  = $('<table>', { 'class': 'alignmentTable'}).appendTo($dst);
    var fasta = "";
    console.log("show alignment");




    console.log(aln);
    console.log("show alignment: creating table");
    $.each( spps, function (k,v) {
        var seq  = aln[v];
        fasta   += '>' + desc + v + '\n' + seq + '\n';

        //console.log('aln    k '+k+' v '+v+' seq '+seq);
        var $tr =  $('<tr>', { 'class': 'alignmentCell alignmentLine'         });
        $tr.append($('<td>', { 'class': 'alignmentCell alignmentHead'         }).append(v  ));


        $tr.append($('<td>', { 'class': 'monospace alignmentCell alignmentVal'}).append(seq))

        $tr.appendTo($tbl);
        //console.log('aln '+k+' v '+v);
    });


    console.log("show alignment: creating cells");

    console.log("show alignment: adding data");

    var nfile  = filename+'_ALIGNMENT.fasta';
    $('<a>', {'class': 'downloadlink'}).data('ofile', nfile).data('src', fasta).data('filetype', "text/plain").text('Download Alignment').click(downloadData).insertAfter($dst);

    console.log("show alignment done");
}


function insertTree( treeStr, id_to_render, width, height) {
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
    el.setAttribute('viewBox'            , '0 0 '+widthS+' '+(heightS + 12) );
    el.setAttribute('preserveAspectRatio',                          'none' );
    el.setAttribute('width'              ,                          width  );
    el.setAttribute('height'             ,                          height );

    return phylocanvas.getSvgSource();
}


function downloadData () {
    var ofile     = $(this).data('ofile'   );
    var dataobj   = $(this).data('src'     );
    var datatype  = $(this).data('filetype');
    console.log('downloading',ofile,datatype);
    downloadDataNfo (ofile, dataobj, datatype);
}


function downloadDataNfo (ofile, dataobj, datatype) {
    var blob      = new Blob([dataobj], {type: datatype});
    downloadBlob(ofile, blob);
}


function downloadBlob(ofile, blob) {
    saveAs(blob, ofile);
}


function svgtopng(pfile, svgSrc) {
    svgtoimage('png', pfile, svgSrc);
}


function svgtopdf(pfile, svgSrc) {
    svgtoimage('pdf', pfile, svgSrc);
}


function svgtoimage(fmt, pfile, svgSrc) {
    var xhr = new XMLHttpRequest();
    xhr.onload = function(){
        console.log('ready');
        if (this.status == 200) {
            console.log('success');
            var b64    = this.response;
            b64toimg(b64, pfile, fmt);
        }
    };
    var curl = converterURL + '/' + fmt;
    xhr.open('POST', curl, true);
    xhr.setRequestHeader('Content-Type', 'text/plain;charset=UTF-8');
    xhr.send(svgSrc);
}


function b64toimg(b64, pfile, fmt) {
            var img    = atob(b64);
            //console.log( 'img', img );
            var length = img.length;
            var ab     = new ArrayBuffer(length);
            var ua     = new Uint8Array(ab);

            for (var i = 0; i < length ; i++) {
                ua[i] = img.charCodeAt(i);
            }
            //console.log( 'ua', ua );

            if      (fmt == 'png') {
                downloadDataNfo(pfile, ab, "image/png");
            }
            else if (fmt == 'pdf') {
                downloadDataNfo(pfile, ua, "application/pdf");
            }
}
