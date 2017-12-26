angular.module('app').controller('monitorModelViewOneNodeCtrl', ['$scope', 'socket', '$timeout', '$http', '$q', 'globalApi', 'httpModule', 'definitions',
  function($scope, socket, $timeout, $http, $q, globalApi, httpModule, definitions) {
    var numericDisplay;
    $scope.timer = [];
    $scope.viewMode = 'map';
    $scope.info = null;
    $scope.request = {
      node: 0,
      new_node: 0
    };

    $scope.chartData = [];

    function initChart() {
      for (let i = 0; i < 2; i++) {
        $scope.chartData[i] = angular.copy($scope.chartModel);
      }
    }

    $scope.loadData = function(request) {

      if (request === undefined) {
        request = {
          node: $scope.request.node,
          global_scale: false,
          assign: false
        };
      }
      var deferred = $q.defer();
      httpModule.getRawData(request).then(function(data) {
        globalApi.plotData(data, $scope.chartData[0]);
      }, function(error) {
        console.log("no data");
      });
      httpModule.httpGet("/api/machine-learning/clusters/node/first-stage", request).then(function(data) {
        globalApi.plotData(data, $scope.chartData[1]);
      }, function(error) {
        console.log("no data");
      });
      deferred.resolve('done');
      return deferred.promise;
    };

    $scope.loadDataSelected = function(request) {
      if (request === undefined) {
        request = {
          node: $scope.request.node,
          global_scale: false,
          assign: false
        };
      }
      httpModule.getRawData(angular.copy($scope.request)).then(function(data) {
        globalApi.plotData(data, $scope.chartData[0]);
      }, function(error) {
        console.log("no data");
      });

      httpModule.httpGet("/api/machine-learning/clusters/node/first-stage", request).then(function(data) {
        globalApi.plotData(data, $scope.chartData[1]);
      }, function(error) {
        console.log("no data");
      });

    };

    $scope.init = function(mode = 1) {

      $scope.mode = mode;
      $scope.request.dual_clustering = 0;
      $scope.request.global_scale = false;
      $scope.chartModel = definitions.getChartModel();
      initChart();
      httpModule.getInfo().then(function(data) {
        $scope.info = data;
        $scope.loadData();
      }, function() {
        console.log("no data");
      });
    };

    var clearTimers = function() {
      $timeout.cancel($scope.timer[2]);
      for (var i = 0; i < $scope.timer.length; i++) {
        $timeout.cancel($scope.timer[i]);
      }
    };

    $scope.$on("$destroy", function() {
      clearTimers();
      console.log('disconnect');
      // socket.emit('disconnect_request', '');
    });
  }
]);
