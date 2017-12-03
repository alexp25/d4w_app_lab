angular.module('app').controller('monitorNetworkCtrl', ['$scope', 'socket', '$timeout', '$http', '$q', 'globalApi', 'httpModule', 'definitions',
  function($scope, socket, $timeout, $http, $q, globalApi, httpModule, definitions) {
    var numericDisplay;
    $scope.timer = [];
    $scope.viewMode = 'map';
    $scope.selected = {
      reqtype: 'sensors',
      type: 1,
      id: 4,
      n: 10
    };


    $scope.chartData = [];

    $scope.showChart = false;


    var nodes = new vis.DataSet([]);

    // create an array with edges
    var edges = new vis.DataSet([]);

    // create a network
    var container = document.getElementById('mynetwork');
    var data = {
      nodes: nodes,
      edges: edges
    };
    var options = {
      physics: {
        stabilization: true,
      },
      nodes: {
        borderWidth: 4,
        size: 100,
        fixed: true,
        // physics: false,
        // color: {
        //   border: '#222222',
        //   background: '#666666'
        // },
        // font: {
        //   color: '#000000'
        // }
      },
      edges: {
        color: 'lightgray'
      },
      layout: {
        randomSeed: 0
      }
    };


    var network = new vis.Network(container, data, options);

    function initChart() {
      for (let i = 0; i < 3; i++) {
        $scope.chartData[i] = angular.copy($scope.chartModel);
      }
    }

    network.on('click', function(properties) {
      var ids = properties.nodes;
      var clickedNodes = nodes.get(ids);
      var clickedNode = clickedNodes[0];
      console.log('clicked node:', clickedNode);
      if (clickedNode === undefined) {
        return;
      }
      $scope.request.node = parseInt(clickedNode.id_consumer);
      if ($scope.request.node === -1) {
        return;
      }
      httpModule.getRawData($scope.request).then(function(data) {
        globalApi.plotData(data, $scope.chartData[0]);
      }).catch(function(data) {
        console.log("no data");
      });
      $scope.request.dual_clustering = 0;
      httpModule.getModelData($scope.request).then(function(data) {
        globalApi.plotData(data, $scope.chartData[1]);
      }).catch(function(data) {
        console.log("no data");
      });
    });

    function updateNetwork() {
      // var newColor = '#' + Math.floor((Math.random() * 255 * 255 * 255)).toString(16);
      nodes.clear();
      edges.clear();
      nodes.add($scope.networkData.nodes);
      edges.add($scope.networkData.edges);
    }

    function getNetworkData() {
      return httpModule.httpGet('/api/network/graph');
    }

    $scope.resetML = function() {
      return httpModule.httpGet('/api/machine-learning/init');
    };

    $scope.loadData = function() {
      getNetworkData().then(function(data) {
        $scope.networkData = angular.fromJson(data.data);
        console.log($scope.networkData);
        updateNetwork();
      }, function(error) {
        console.log("no data");
      });
      $scope.resetML().then(function() {
        $scope.request.node = -1;
        $scope.request.dual_clustering = 1;
        $scope.request.new_node = null;
        $scope.request.global_scale = true;
        httpModule.getModelData(angular.copy($scope.request)).then(function(data) {
          $scope.hasData = true;
          globalApi.plotData(data, $scope.chartData[2]);
        }, function(error) {
          console.log("no data");
        });
      });

    };

    function pollData(first, tm = 1000) {
      let tm1 = tm;
      if (first === true) {
        tm1 = 0;
      }
      $scope.timer[2] = $timeout(function() {
        $scope.loadData();
        pollData(false, tm);
      }, tm1);
    }

    $scope.init = function() {
      $scope.request = globalApi.requestStructure();
      $scope.chartModel = definitions.chartModel();
      initChart();
      $scope.loadData();
    };

    $scope.startLoop = function(tm) {
      pollData(true, tm);
    };

    $scope.stopLoop = function() {
      $timeout.cancel($scope.timer[2]);
    };

    var clearTimers = function() {
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
