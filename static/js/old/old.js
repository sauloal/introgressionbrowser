// little X under the image to close it
var closeImgDiv = ' <div class="pull-right">\
        <i class="icon-remove" id="hideimg"></i>(ESC)\
    </div>\
    ';




function setWindowsSize() {
    // gets current window size and, based on that, decide the maximum size of the graphic in a 16/9 proportion
    var window_height     = $(window).height();
    //window.max_img_height = window_height * 0.85;
    //window.max_img_width  = window_height * 1.30;

    //TODO: check mouse position
    window.max_img_height = Math.ceil( window_height         *  0.60 );
    window.max_img_width  = Math.ceil( window.max_img_height * (16/9));

    console.log("window " + window_height + " max height " + max_img_height + " max width " + max_img_width);
}


function resetDivGraph() {
    // change graphic div's size
    //console.log('reseting graph');
    var $divGraph = $("#graphDiv");

    setWindowsSize();

    $divGraph.css('width' , window.max_img_width);
    $divGraph.css('height', window.max_img_height);
    $divGraph.width( window.max_img_width);
    $divGraph.height(window.max_img_height);

    $divGraph.hide();
}


function resizeImage(){
    // resize image accoding to mouse position
    //console.log('resizing image');

    var $divGraph = $("#graphDiv");
    resetDivGraph();
    $divGraph.show();

    var $imgGraph = $('#divImg');

    if ( $imgGraph.size() == 0 ) {
        //console.log("empty");
        return;
    }

    var offset    = $divGraph.offset();
    var x         = window.mouseXPos - offset.left;
    var y         = window.mouseYPos - offset.top;

    //console.log($imgGraph)
    var ix        = $imgGraph.get(0).width;
    var iy        = $imgGraph.get(0).height;
    var ip        = ix / iy;

    if (( ix == 0) || (iy == 0 )) {
        //resizeImage();
        return;
    }

    $divGraph.width( ix);
    $divGraph.height(iy);

    //console.log("B X " + x + " Y " + y + " IX " + ix + " IY " + iy + " IP " + ip);

    if (( x < ( ix * 1.2 )) && ( y < iy * 1.2)){
        //console.log("fixing");
        var nx =  x * .8;
        var ny = nx * ip;
        $imgGraph.get(0).width  = nx;
        $imgGraph.get(0).height = ny;
        $divGraph.width( nx);
        $divGraph.height(ny);

        //var ix = $imgGraph.get(0).width;
        //var iy = $imgGraph.get(0).height;

       //console.log("A X " + x + " Y " + y + " IX " + ix + " IY " + iy + " IP " + ip);
    }
};


function graph_caller(dataHash){
    // from the JSON data received, call the resquested function sending the data

    //console.log('calling graph graph caller');
    resetDivGraph();
    // add little X button to close the window
    var $divGraph = $("#graphDiv");
    $divGraph.show();

    // function to which the data should be sent to
    var dst                = dataHash['_dst_func'];
    //console.log('calling graph :: dst: ' + dst);

    // append the name of the destination div
    dataHash['container'] = 'graphDiv';

    var graph_function     = window[dst];
    //console.log('calling graph :: fn: ' + fn);

    // call function
    graph_function(dataHash);

    $divGraph.append(closeImgDiv);
}


function hideallstatus(){
    $("div[class=statusDiv]").each(function(data){
        $(this).hide();
    });
}

function loadsetup(data){
    console.log('loading setup');

    // add little X button to close the window
    var tgtname = $("#statusbtnSetup").attr("tgt");
    console.log("setup target name" + tgtname);
    var $divTgt = $('#' + tgtname);

    $divTgt.show();
    $divTgt.html(data);
    //{{ parseSetup(g.setupDB)|safe }}
}


$(document).ready(function(){
    // store mouse position
    $(document).mousemove(function(e){
        window.mouseXPos = e.pageX;
        window.mouseYPos = e.pageY;
        //console.log("X " + window.mouseXPos + " Y " + window.mouseYPos);
     });


    // HIDE/SHOW COLUMNS
    $(document).on('click', ".icon-chevron-right", function(){
        var tgt = $(this).attr("tgt");
        $("." + tgt).each(function(data){
            $(this).show();
        });
        //$(this).attr("class", "icon-chevron-left");
        $(this).toggleClass("icon-chevron-left");
        $(this).toggleClass("icon-chevron-right");
    });


    // HIDE/SHOW COLUMNS
    $(document).on('click', ".icon-chevron-left", function(){
        var tgt = $(this).attr("tgt");
        $("." + tgt).each(function(data){
            $(this).hide();
        });
        $(this).toggleClass("icon-chevron-left");
        $(this).toggleClass("icon-chevron-right");
    });


    //SHOW STATUS
    $(document).on('click', "button[class=statusbtn]", function(){
        //TODO: separate setup in global and project setup
        var tgt = $(this).attr("tgt");

        hideallstatus();

        $("#" + tgt).each(function(data){
            $(this).show();
        });
    });


    $(document).on('click', 'button[id=statusbtnSetup]', function(e){

        var href = window.url_for_setup;
        $.get(href, loadsetup);
    });






    //SHOW PNG IMAGES
    $(document).on('mouseenter', "a[class=graphimg]", function(e){
        var href = $(this).attr("lnk");
        $("#graphDiv").html('<img src="'+href+'" id="divImg" onload="resizeImage()"/>');
        $("#graphDiv").append(closeImgDiv);
    });

    //$(document).on('mouseleave', "a[class=graphimg]", function(){
        //$("#graphDiv").html('');
        //$("#graphDiv").hide();
    //});


    //SHOW JSON IMAGES
    $(document).on('mouseenter', "a[class=graphjson]", function(e){
        var href = $(this).attr("lnk");
        console.log('getting '+href);
        $.getJSON(href, graph_caller);
    });

    //$(document).on('mouseleave', "a[class=graphjson]", function(){
    //    $("#graphDiv").html('');
    //    $("#graphDiv").hide();
    //});




    //hide image div
    $(document).on('click', "#hideimg", resetDivGraph);

    // if pressed ESC, close image
    $(document).bind('keydown', function(e) {
        //var al = "which " + e.which + " key code " + e.keyCode;
        e = e || window.event;

        //al += " which2 " + e.which + " kcode2 " + e.keyCode;
        //alert(al);

        if (e.keyCode == 27) { // hide div if ESC is pressed
            $("#graphDiv").html('');
            $('#graphDiv').hide();
            //$('#graphDiv').show();
        };
    });




    //ROW COLORING
    $(document).on('mouseenter', ".dataline", function(){
        var id = $(this).attr("id");
        $(this).toggleClass("colored");
    });

    $(document).on('mouseleave', ".dataline", function(){
        var id = $(this).attr("id");
        $(this).toggleClass("colored");
    });


    //COLUMN COLORING
    $(document).on('mouseenter', ".dataCol", function(){
        var col = $(this).attr("col");
        $("[col=" + col+"]").each(function(data){
            $(this).toggleClass("colored");
        });
    });

    $(document).on('mouseleave', ".dataCol", function(){
        var col = $(this).attr("col");
        $("[col=" + col+"]").each(function(data){
            $(this).toggleClass("colored");
        });
    });


    //TITLEBAR
    var val = $('#projectNameSelector').val(0);
    $("#projectNameSelector").change(function(){
        var val = $('#projectNameSelector').val();
        if ( val != "" ) {
            var dst = window.url_for_query + "?projectName=" + val;
            //window.location.replace(dst);
            $('#result').html("<h4>Getting " + val + "...</h4>");
            $.get(dst, function(data){
                $('#result').html(data);
            });
        };
    });

    hideallstatus();

    resetDivGraph();
});
