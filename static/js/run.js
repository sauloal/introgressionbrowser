//<div id="controls"/>
//<div id="projects"/>
//<div id="logs"/>

var CONTROLS_ID = "controls";
var PROJECTS_ID = "projects";
var LOGS_ID     = "logs";

function relayMessage(msg) {
    console.warn(msg);
}

var Projects    = function($scope, $http) {
    this.$scope       = $scope;
    this.$http        = $http;

    this.projects     = null;
    this.reqSerial    = 0;

    this.el_controls  = $("#"+CONTROLS_ID);
    this.el_projects  = $("#"+PROJECTS_ID);
    this.el_logs      = $("#"+LOGS_ID    );

    console.log("Projects");
    console.log("Projects :: el controls", this.el_controls);
    console.log("Projects :: el projects", this.el_projects);
    console.log("Projects :: el logs    ", this.el_logs    );
};


Projects.prototype.update = function() {
    // TODO: query server for project data
    
    var self    = this;

    console.log("Projects :: update");
    
    var req = { "action": "get", "data": { "serial": self.reqSerial }, "noonce": noonce };

    self.reqSerial += 1;
    
    self.$http.post('run', req)
            .success(
                function(data, status, headers, config) {
                    console.log('got data %o', data);
                    self.display(data);
                }
            )
            .error(
                function(data, status, headers, config) {
                    console.warn("Error getting data. Status: ", status, " Message: ", data, " Headers: ", headers, " Config: ", config);
                }
            );
    };


Projects.prototype.display = function(data) {
    console.log("Projects :: display");
    console.log("Projects :: displaying %o", data);
};





var Project = function(projects, name) {
    this.projects = projects;
    thi.name      = name;

    console.log("Project");

};

Project.prototype.display = function() {
    console.log("Project :: display");
    
};





var mainController = function ( $scope, $http ) {
    $scope.projects = new Projects($scope, $http);

    $scope.projects.update();
};


var app = angular.module('myApp', [])
    .controller('mainController'  , ['$scope', '$http', mainController  ])
;

//http://lorenhoward.com/blog/how-to-get-angular-to-work-with-jinja/
app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{[');
  $interpolateProvider.endSymbol(']}');
}]);

