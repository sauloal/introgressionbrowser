self.addEventListener('message', function(e) {
    var data = e.data;
    //console.log('WORKER RECEIVED DATA %o %o', e, data);
    self.postMessage({ 'cmd': data.cmd, 'data': data.data });
    //self.y
    //self.nelp
    //self.rowData
    //self.$scope
    //self.matrix

    //var nel     = self.nelp.clone( { y: (row+1) * cellheight } );
    //
    //for ( var col = 0; col < self.rowData.length; col++ ) {
    //    var block     = $scope.getBlockRC( row, col ).clone({ x: col * cellwidth });
    //    nel.add( block );
    //}
    //self.matrix.add( nel );

}, false);
