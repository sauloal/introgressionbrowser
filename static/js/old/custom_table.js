
var plotTable = function (OUTdiv, cfg) {
    console.log('plotting table');
    var self = this;

    console.log('DIV %s CFG %o', OUTdiv, cfg);

    //this.cols_length = cols_length;
    //this.rows_length = rows_length;
    //this.minData     = minData;
    //this.maxData     = maxData;
    //this.data        = data;
    //this.cols        = cols;
    //this.rows        = rows;
    //this.SVGdiv      = SVGdiv;
    this.OUTdiv      = OUTdiv;
    this.cfg         = cfg;

    if ( this.cfg.request.page   !== null ) { this.cfg.request.page   = this.cfg.request.page + 1; } else { this.cfg.request.page = 1; };

    if ( this.cfg.request.maxNum  == null ) { console.log('getting default max number'); this.cfg.request.maxNum = this.cfg.info.maxNumDefault };

    this.cfg.info.maxPage = this.cfg.info.num_cols_total / this.cfg.request.maxNum;

    if ( this.cfg.info.maxPage > Math.floor( this.cfg.info.maxPage ) ) {
        this.cfg.info.maxPage  = Math.floor( this.cfg.info.maxPage ) + 1;
    } else {
        this.cfg.info.maxPage  = Math.floor( this.cfg.info.maxPage );
    }


    this.cfg.opts = {
        color: {
            // GRAPH COLOR SCHEME: RED
            yr : 253, //red
            yg :  32, //green
            yb : 117 //blue
        }
    };

    this.cfg.info.resStr   += 'page: '+this.cfg.request.page+' (out of '+this.cfg.info.maxPage+') max registers: '+this.cfg.request.maxNum;

    this.init();

};

plotTable.prototype.init = function() {
    var self = this;


    $('<span>'      , { 'class': "label label-success pull-center lblstatus", 'id': "lbl_resstatus"   } ).html( this.cfg.info.resStr ).appendTo( '#status_row_1_1' );
    $('<span>'      , { 'class': "label"                          , 'id': "lbl_qrystatus"             } ).html( this.cfg.info.qryStr ).appendTo( '#status_row_1_1' );

    $('<div>'       , { 'class': 'pull-center'                    , 'id': 'posControl'                } ).appendTo( '#status_row_2_1' );

    $('<i>'         , { 'class': 'iconControl icon-refresh'       , 'title': 'Whole Genome'           } ).data('dst', 'refresh' ).appendTo( '#posControl' );
    $('<i>'         , { 'class': 'iconControl icon-fast-backward' , 'title': 'First Block'            } ).data('dst', 'first'   ).appendTo( '#posControl' );
    $('<i>'         , { 'class': 'iconControl icon-step-backward' , 'title': 'Previous Block'         } ).data('dst', 'previous').appendTo( '#posControl' );

    $('<input>'     , { 'class': 'col-md-3'                          , 'id': 'sliderLbl', 'type': 'text' } ).appendTo( '#posControl' );

    $('<i>'         , { 'class': 'iconControl icon-step-forward'  , 'title': 'Next Block'             } ).data('dst', 'next'    ).appendTo( '#posControl' );
    $('<i>'         , { 'class': 'iconControl icon-fast-forward'  , 'title': 'Last Block'             } ).data('dst', 'last'    ).appendTo( '#posControl' );
    $('<i>'         , { 'class': 'iconControl icon-play'          , 'title': 'Go to Selection'        } ).data('dst', 'read'    ).appendTo( '#posControl' );

    $('<div>'       , { 'class': ''                               , 'id': 'sliderDiv'                 } ).appendTo( '#status_row_3_1' );

    $('<div>'       , { 'id': 'slider'}).data({'minPosDefault': this.cfg.info.dminPosAbs, 'maxPosDefault': this.cfg.info.dmaxPosAbs}).appendTo( '#sliderDiv' );


    console.log('adding slider');
    $('#slider').slider({
        range: true,
        min: this.cfg.info.dminPosAbs,
        max: this.cfg.info.dmaxPosAbs,
        step: 1,
        values: [this.cfg.info.dminPos, this.cfg.info.dmaxPos],
        slide: function( event, ui ) {
            var page = $('#data').data('request')['page'] || null;

            if ( page !== null ) { page = page + 1; } else { page = 1; };

            lengAbs = $('#data').data('data_info')["length_abs"];
            //console.log('length abs '+lengAbs);
            step    = Math.floor( lengAbs / 100 );
            //console.log('step '+step);
            ui.step = step;

            $("#sliderLbl").val("From "+ui.values[0]+ " To "+ui.values[1] + " Page " + page );
        }
    });


    $("#sliderLbl")
        .val("From "+$("#slider").slider("values", 0)+ " To "+$("#slider").slider("values", 1) + " Page " + self.cfg.request.page)
        .attr('disabled', true)
        .attr('title', 'Show only this range');


    console.log('NO D3');
    console.log('adding table');
    //metadata['id'] = "data";

    this.$tbl = $('<table>', { 'id': "data" });

    this.requestF = {};
    $.each(self.cfg.request, function(k,v){
        if (( v !== null ) && ( v !== false )) {
            console.log('table adding k: '+k+' v '+v);
            self.requestF[k] = v;
        }
    });

    this.$tbl.data('request'  , this.requestF);
    this.$tbl.data('data_info', this.cfg.info);

    console.log('adding header');
    var $trStart = this.addRowHeader( 'Start Position', 'play'    , this.cfg.header.line_names, this.cfg.header.line_starts  );
    var $trEnd   = this.addRowHeader( 'End   Position', 'stop'    , this.cfg.header.line_names, this.cfg.header.line_ends    );
    var $trUnit  = this.addRowHeader( '# Unities'     , 'th-large', this.cfg.header.line_names, this.cfg.header.line_unities );
    var $trSnp   = this.addRowHeader( '# SNPs'        , 'star'    , this.cfg.header.line_names, this.cfg.header.line_snps    );
    var $trName  = this.addRowHeader( 'Unity Name'    , 'user'    , this.cfg.header.line_names, this.cfg.header.line_names   );

    var rows = new Array(this.cfg.data.ddata.length + 5);
    rows[0] = $trStart;
    rows[1] = $trEnd;
    rows[2] = $trUnit;
    rows[3] = $trSnp;
    rows[4] = $trName;

    console.log('adding rows');

    $.each(self.cfg.data.ddata, function(dindex) {
        var $tr   = self.addRowData(  dindex, this );
        rows[dindex + 5 ] = $tr;
    });

    console.log('adding to table');
    this.$tbl.append( rows );
    this.$tbl.appendTo(this.OUTdiv)

    console.log('coloring');
    this.heatMap();
    console.log('done');





    $(document).on('click',      '#data .datacell' , function(){
        var request  = $('#data').data('request');
        var evenly   = request[ 'evenly'  ] || null;
        var every    = request[ 'every'   ] || null;
        var nclasses = request[ 'nclasses'] || null;
        var chrom    = request[ 'chrom'   ] || null;


        if ( (!evenly)  && every === null && nclasses === null ) {
            var gene  = $(this).data(  'cname');
            var href = '/tree/'+chrom+'/'+gene;
            console.log('getting tree: '+href);
            $.getJSON(href, self.cfg.funcs.showTreePopUp);

        } else {
            var actstr = ""
            if ( evenly            ) { actstr += ' evenly' };
            if ( every    !== null ) { actstr += ' every ' + every    + ' bp'      };
            if ( nclasses !== null ) { actstr += ' in '    + nclasses + ' classes' };
            alert('I can only show tree without concatenations (evenly, every or classes). Currently you have '+actstr+' active');
        }
    });


    $(document).on('mouseenter', '#data td.datatd'   , self.colorCrux());


    $(document).on('mouseleave', '#data td.datatd'   , self.colorCrux());


    $(document).on('click'     , '.iconControl'      , self.posChanger());


    //TOOLTIP
    $('body').tooltip({
        content: function(callback){
            //$('.ui-tooltip').each(function(){ $(this).remove(); });
            var tools = document.getElementsByClassName('ui-tooltip');
            for ( var i=0; i<tools.length; i++) {
                $(tools[i]).remove();
            }

            if ( $(this).is('#data .datacell') ) {
                callback( self.getCellTitle(this) );
            } else {
                callback( $(this).attr('title') ) ;
            }
        },
        show: { delay: 1300 }
    });


};

plotTable.prototype.addRowHeader = function(name, icon, line_names, data) {
    var $tr  = $('<tr>');

    var $tdh  = $('<th>', { 'class': 'datablock datath dataHeader'} ).data('rname', name).text(name);
    var cells = new Array(data.length+1);
    if ( ! $("#chk_printHeader").is(':checked') ) {
        $tdh.addClass('thinvisible');
    }
    cells[0] = $tdh;

    $.each(data, function(index) {
        var cname  = line_names[   index ];
        var val    = data[ index ];
        var $td    = $('<th>', { 'class': 'datablock datath dataHeaderCell', 'title': this}).data('cname', cname).text(val);

        //$td.append( $('<i>').attr('class', 'icon-'+icon) )

        if ( ! $("#chk_printHeader").is(':checked') ) {
            $td.addClass('thinvisible');
        }

        cells[index + 1] = $td;
    });

    $tr.append( cells );
    return $tr;
}

plotTable.prototype.addRowData   = function (dindex, data) {
    var self  = this;
    var rname = self.cfg.data.dnames[dindex];

    var $tr   = $('<tr>').attr('class', 'datatr dataRow').attr('rname', rname).data('rname', rname);

    var cells = new Array(data.length + 1);
    var $td   = $('<td>').attr('class', 'datablock datatd dataRowHeader').data('rname', rname).text(rname);

    if ( ! $("#chk_printSpp").is(':checked') ) {
        $td.addClass('tdinvisible');
    }

    cells[0] = $td;

    for (var index=0; index < data.length; ++index){
        var datal    = data[index];
        var distance = datal[0];
        var rownum   = datal[1];
        var colnum   = datal[2];

        var cstart   = self.cfg.header.line_starts[  index ];
        var cend     = self.cfg.header.line_ends[    index ];
        var cuni     = self.cfg.header.line_unities[ index ];
        var csnp     = self.cfg.header.line_snps[    index ];
        var cname    = self.cfg.header.line_names[   index ];

        var $tdd      = $('<td>')
            .data({
                        'rname'  : rname   ,
                        'cname'  : cname   ,
                        'value'  : distance,

                        'start'  : cstart  ,
                        'end'    : cend    ,
                        'unities': cuni    ,
                        'snps'   : csnp    ,
                        'name'   : cname
                    });
        $($tdd)[0].setAttribute('class', 'datablock datatd datacell');
        $($tdd)[0].setAttribute('cname', cname            );
        $($tdd)[0].setAttribute('title', ''               );

        cells[index + 1] = $tdd;
    }

    $tr.append( cells );

    return $tr;
};

plotTable.prototype.heatMap = function () {
    var self  = this;
    //var max = $('#data').data('data_info')["maxVal"];
    var min   = this.cfg.info.dmin;
    var max   = this.cfg.info.dmax;
    var dif   = max - min;



    var xr = 255;
    var xg = 255;
    var xb = 255;
    //n  = 100;

    // add classes to cells based on nearest 10 value
    var pieces = document.getElementsByClassName('datacell');
    for ( var i=0; i<pieces.length; i++) {
    //$('#data td.datacell').each(function(){
        var piece = pieces[i];
        var val   = $.data(piece, 'value');
        var tval  = (val - min) / dif * 100;
        //var val   = $.data(this, 'value');

        var pos   = parseInt((Math.round(tval).toFixed(0)));
        var red   = parseInt((xr + (( pos * (self.cfg.opts.color.yr - xr)) / (num_groups-1))).toFixed(0));
        var green = parseInt((xg + (( pos * (self.cfg.opts.color.yg - xg)) / (num_groups-1))).toFixed(0));
        var blue  = parseInt((xb + (( pos * (self.cfg.opts.color.yb - xb)) / (num_groups-1))).toFixed(0));
        var clr   = 'rgb('+red+','+green+','+blue+')';

        //console.log('val ' + val + ' max ' + max + ' pos ' + pos + ' R ' + red + ' G ' + green + ' B ' + blue + ' clr ' + clr);

        piece.style.backgroundColor = clr;
    }
};

plotTable.prototype.getCellTitle = function (cell) {
    var rname    = $(cell).data('rname'  );
    var cname    = $(cell).data('cname'  );
    var distance = $(cell).data('value'  );

    var cstart   = $(cell).data('start'  );
    var cend     = $(cell).data('end'    );
    var cuni     = $(cell).data('unities');
    var csnp     = $(cell).data('snps'   );
    var cname    = $(cell).data('name'   );

    var title = '<p class="ptip"><b>Species:</b> ' + rname + '<p class="ptip"><b>Name:</b> ' + cname + '<p class="ptip"><b>Start:</b> ' + cstart + '<p class="ptip"><b>End:</b> ' + cend + '<p class="ptip"><b>Unities:</b> ' + cuni + '<p class="ptip"><b>SNPs:</b> ' + csnp + '<p class="ptip"><b>Distance:</b> '+ distance; // + ' Rownum ' + rownum + ' Colnum ' + colnum

    return title;
};

plotTable.prototype.posChanger = function () {
    var self = this;

    return function() {
        var dst   = $(this).data('dst');

        var qry   = self.cfg.request;
        var spp   = qry['ref'  ] || null;
        var chrom = qry['chrom'] || null;

        switch(dst)
        {
            case 'refresh':
                resetSlider();
                return;
                break;
            case 'first':
                qry['page'] = 0;
                break;
            case 'previous':
                if ( 'page' in qry ) {
                    qry['page'] -=  1;
                } else {
                    qry['page']  = 0;
                }
                break;
            case 'next':
                if ( 'page' in qry ) {
                    qry['page'] += 1;
                } else {
                    qry['page']  = 1;
                }
                break;
            case 'last':
                var maxPage = getMaxPage();
                qry['page'] = maxPage;
                break;
            case 'read':
                var slvals  = self.getSliderValue();
                var slmin   = slvals[0];
                var slmind  = slvals[1];
                var slmax   = slvals[2];
                var slmaxd  = slvals[3];
                var changed = slvals[4];
                console.log('got: min ',slmin,' mind ',slmind,' max ',slmax, ' maxd ',slmaxd, ' changed ', changed);

                if ( changed ) {
                    console.log('changed');
                    if (slmin != slmind) {
                        console.log('sending start ', slmin);
                        qry['startPos'] = slmin;
                    }
                    if (slmax != slmaxd) {
                        console.log('sending end '  , slmax);
                        qry['endPos'  ] = slmax;
                    }
                }
                break;
            default:
                return;
                break;
        }

        if (qry['page'] < -1 ) {
            qry['page'] = -1;
        }

        self.cfg.funcs.submitDataQuery(spp, chrom, qry);
    };
};

plotTable.prototype.mapColor = function (color) {
    var self = this;
    switch(color)
        {
            case 'blue':
                self.cfg.opts.color.yr = 52;
                self.cfg.opts.color.yg = 119;
                self.cfg.opts.color.yb = 220;
                break;
            case 'yellow':
                self.cfg.opts.color.yr = 250;
                self.cfg.opts.color.yg = 237;
                self.cfg.opts.color.yb = 37;
                break;
            case 'green':
                self.cfg.opts.color.yr = 118;
                self.cfg.opts.color.yg = 246;
                self.cfg.opts.color.yb = 68;
                break;
            case 'grey':
                self.cfg.opts.color.yr = 100;
                self.cfg.opts.color.yg = 100;
                self.cfg.opts.color.yb = 100;
                break;
            case 'red':
                self.cfg.opts.color.yr = 253;
                self.cfg.opts.color.yg =  32;
                self.cfg.opts.color.yb = 117;
                break;
            default:
                self.cfg.opts.color.yr = 243;
                self.cfg.opts.color.yg = 32;
                self.cfg.opts.color.yb = 117;
                break;
        }
    self.heatMap();
};

plotTable.prototype.getSliderValue = function () {
    if ( $("#slider").length > 0 ) {
        console.log('has slider');
        var slider = $("#slider");
        var slmin  = $(slider).slider("values", 0);
        var slmax  = $(slider).slider("values", 1);
        var slmind = $(slider).data('minPosDefault');
        var slmaxd = $(slider).data('maxPosDefault');


        var changed = true;
        if ((slmin == slmind) && (slmax == slmaxd)){
            changed = false;
        }

        console.log('getting value: min ',slmin,' mind ',slmind,' max ',slmax, ' maxd ',slmaxd, ' changed ', changed);

        return [slmin, slmind, slmax, slmaxd, changed];
    } else {
        return [null, null, null, null, false]
    }
};

plotTable.prototype.resetSlider = function () {
    if ( $("#slider").length > 0 ) {
        console.log('has slider');
        var slider = $("#slider");
        var slmind = $(slider).data('minPosDefault');
        var slmaxd = $(slider).data('maxPosDefault');

        $(slider).slider("values", 0, slmind);
        $(slider).slider("values", 1, slmaxd);

        var slmin  = $(slider).slider("values", 0);
        var slmax  = $(slider).slider("values", 1);

        console.log('min ',slmin,' mind ',slmind,' max ',slmax, ' maxd ',slmaxd);

    }
};

plotTable.prototype.getMaxPage = function () {
    var req            = $('#data').data('request');
    var nfo            = $('#data').data('data_info');

    var maxNum         = req['maxNum'  ];
    var page           = req['page'    ];
    var num_cols_total = nfo[ 'num_cols_total' ];


    if ( page   !== null ) { page = page + 1; } else { page = 1; };

    if ( maxNum !== null ) { console.log('getting max num from default'); maxNum = $('#maxNumber').data('maxNumberDefault'); };

    var maxPage        = num_cols_total / maxNum;

    maxPage = Math.floor( maxPage );

    return maxPage;
};

plotTable.prototype.showHeader = function ( val ) {
    $('.datath').each(function(){
        $(this).toggleClass('thinvisible');
    });
};

plotTable.prototype.showSpecies = function ( val ) {
    $('.dataRowHeader').each(function(){
        $(this).toggleClass('tdinvisible');
    });
};

plotTable.prototype.clusterSpp = function ( val ) { }

plotTable.prototype.clusterGenes = function ( val ) { }

plotTable.prototype.colorCrux = function () {
    var self  = this;

    return function () {
            var rname = $.data(this, 'rname');
            var cname = $.data(this, 'cname');

        ////rnames = document.querySelectorAll('#data tr.dataRow[rname="'+rname+'"]');
        ////for (var i = 0; i<rnames.length; ++i){
        ////    rnames[i].classList.toggle('coloredRow');
        ////}
        //rnames = document.getElementsByTagName('tr');
        //for (var i = 0; i<rnames.length; ++i){
        //    rel = rnames[i];
        //    if ( rel.hasAttribute('rname' ) ) {
        //        if ( rel.getAttribute('rname') == rname ) {
        //            rel.classList.toggle('coloredRow');
        //        }
        //    }
        //}
        //
        ////cnames = document.querySelectorAll('#data td.datacell[cname="'+cname+'"]');
        ////for (var i = 0; i<cnames.length; ++i){
        ////    cnames[i].classList.toggle('coloredCol');
        ////}
        //cnames = document.getElementsByTagName('td');
        //for (var i = 0; i<cnames.length; ++i){
        //    cel = cnames[i];
        //    if ( cel.hasAttribute('cname' ) ) {
        //        if ( cel.getAttribute('cname') == cname ) {
        //            cel.classList.toggle('coloredCol');
        //        }
        //    }
        //}
        //
        //var tools = document.getElementsByClassName('ui-tooltip');
        //for ( var i=0; i<tools.length; i++) {
        //    $(tools[i]).remove();
        //}
    };
};
