angular.module('app').controller('monitorModelViewCtrl', ['$scope', 'socket', '$timeout', '$http', '$q', 'globalApi', 'httpModule', 'definitions',
  function($scope, socket, $timeout, $http, $q, globalApi, httpModule, definitions) {
    var numericDisplay;
    $scope.timer = [];
    $scope.viewMode = 'map';
    $scope.info = null;
    $scope.chartModel = {
      columns: ['x', 'series 1'],
      rows: [
        [1, 10],
        [2, 20],
        [3, 30],
      ],
      timestamp: new Date(),
      settings: {
        min: 0,
        max: 5000
      },
      info: "",
      disp: false
    };

    $scope.chartData = [];

    $scope.request = {
      new_node: 0
    };

    $scope.finalClusters = [];

    function initChart() {
      for (let i = 0; i < 3; i++) {
        $scope.chartData[i] = angular.copy($scope.chartModel);
      }
    }

    $scope.selected = [];

    //checkboxes
    $scope.toggle = function(item, list) {
      var idx = list.indexOf(item);
      if (idx > -1) {
        list.splice(idx, 1);
      } else {
        list.push(item);
      }
    };

    $scope.exists = function(item, list) {
      return list.indexOf(item) > -1;
    };


    $scope.isIndeterminate = function() {
      return ($scope.selected.length !== 0 &&
        $scope.selected.length !== $scope.items.length);
    };

    $scope.isChecked = function() {
      return $scope.selected.length === $scope.items.length;
    };

    $scope.toggleAll = function() {
      if ($scope.selected.length === $scope.items.length) {
        $scope.selected = [];
      } else if ($scope.selected.length === 0 || $scope.selected.length > 0) {
        $scope.selected = $scope.items.slice(0);
      }
    };

    function getRange(start, end) {
      var a = [];
      for (var i = start; i <= end; i++) {
        a.push(i);
      }
      return a;
    }

    function getIds(nodes) {
      a = [];
      for (var i = 0; i < nodes.length; i++) {
        a.push(nodes[i].id);
      }
      return a;
    }

    $scope.loadData = function(request) {
      var deferred = $q.defer();
      if (request === undefined) {
        request = {
          range: getIds($scope.selected),
          global_scale: false,
          assign: false
        };
      }
      httpModule.httpGet("/api/machine-learning/clusters/range/first-stage", request).then(function(data) {
        globalApi.plotData(data, $scope.chartData[0]);
      });
      httpModule.httpGet("/api/machine-learning/clusters/range/second-stage", request).then(function(data) {
        globalApi.plotData(data, $scope.chartData[1]);
        $scope.finalClusters = data.data;
        console.log(data);
      });
      deferred.resolve('done');

      return deferred.promise;
    };

    $scope.resetNode = function() {
      $scope.request.new_node = 0;
    };

    $scope.resetML = function() {
      return httpModule.httpGet('/api/machine-learning/init');
    };

    function pollData(first, tm = 5000) {
      let tm1 = tm;
      $scope.request.node = -1;

      if (first === true) {
        tm1 = 0;
        $scope.request.new_node = 5;
      }
      $scope.timer[2] = $timeout(function() {
        $scope.pendingRequest = $q.defer();
        $scope.loadData({
          new_node: $scope.request.new_node,
          global_scale: false,
          assign: false
        }).then(function() {
          $scope.request.new_node += 1;
          if ($scope.request.new_node > $scope.items[$scope.items.length - 1].id) {
            $scope.request.new_node = 5;
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
      // $scope.request = definitions.getRequestStructure();
      $scope.chartModel = definitions.getChartModel();
      $scope.mode = mode;

      initChart();
      httpModule.getInfo().then(function(data) {
        $scope.info = data;
        $scope.items = data.nodes;
        $scope.toggleAll();
        // $scope.loadData();
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
