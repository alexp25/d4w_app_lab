angular.module('app').controller('monitorModelViewOneNodeCtrl', ['$scope', 'socket', '$timeout', '$http', '$q', 'globalApi', 'httpModule', 'definitions',
  function($scope, socket, $timeout, $http, $q, globalApi, httpModule, definitions) {
    var numericDisplay;
    $scope.timer = [];
    $scope.viewMode = 'map';


    $scope.info = null;



    $scope.chartData = [];


    function initChart() {
      for (let i = 0; i < 2; i++) {
        $scope.chartData[i] = angular.copy($scope.chartModel);
      }
    }

    $scope.loadData = function() {
      var deferred = $q.defer();
      httpModule.getRawData(angular.copy($scope.request)).then(function(data) {
        globalApi.plotData(data, $scope.chartData[0]);
      }, function(error) {
        console.log("no data");
      });
      $scope.request.dual_clustering = 0;
      httpModule.getModelData(angular.copy($scope.request)).then(function(data) {
        globalApi.plotData(data, $scope.chartData[1]);
      }, function(error) {
        console.log("no data");
      });
      deferred.resolve('done');
      return deferred.promise;
    };

    $scope.resetNode = function() {
      $scope.request.new_node = null;
    };

    $scope.loadDataSelected = function() {
      $scope.request.new_node = null;
      httpModule.getRawData(angular.copy($scope.request)).then(function(data) {
        globalApi.plotData(data, $scope.chartData[0]);
      }, function(error) {
        console.log("no data");
      });

      httpModule.getModelData(angular.copy($scope.request)).then(function(data) {
        globalApi.plotData(data, $scope.chartData[1]);
      }, function(error) {
        console.log("no data");
      });

    };


    function pollData(first, tm = 5000) {
      let tm1 = tm;
      if (first === true) {
        tm1 = 0;
        $scope.request.new_node = 5;
      }
      $scope.timer[2] = $timeout(function() {
        $scope.pendingRequest = $q.defer();
        $scope.loadData().then(function() {
          $scope.request.new_node += 1;
          if ($scope.request.new_node > 21) {
            $scope.request.new_node = null;
            return;
          }
          // console.log(tm);
          pollData(false, tm);
        });
      }, tm1);
    }

    $scope.startLoop = function(tm) {
      pollData(true, tm);
    };

    $scope.stopLoop = function() {
      $timeout.cancel($scope.timer[2]);
      $scope.pendingRequest.resolve();
    };

    $scope.init = function(mode = 1) {
      $scope.request = definitions.requestStructure();
      $scope.mode = mode;
      $scope.request.dual_clustering = 0;
      $scope.request.global_scale = false;
      $scope.chartModel = definitions.chartModel();
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
