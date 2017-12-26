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

    $scope.request = {
      node: 0
    };


    $scope.chartData = [];

    $scope.showChart = false;
    $scope.showGraph = true;


    function initGraph() {
      // create a network
      var container = document.getElementById('mynetwork');
      $scope.graph_nodes = new vis.DataSet([]);
      $scope.graph_edges = new vis.DataSet([]);
      $scope.graph_data = {
        nodes: $scope.graph_nodes,
        edges: $scope.graph_edges
      };
      $scope.graph_options = definitions.getGraphOptions();

      $scope.network = new vis.Network(container, $scope.graph_data, $scope.graph_options);

      $scope.network.on('click', function(properties) {
        console.log(properties);
        var flagClickedNode = false;
        var clickedNodes = $scope.graph_nodes.get(properties.nodes);
        var clickedEdges = $scope.graph_edges.get(properties.edges);
        var clickedNode = clickedNodes[0];
        var clickedEdge = clickedEdges[0];

        if (clickedNode !== undefined) {
          console.log('clicked node:', clickedNode);
          flagClickedNode = true;
        } else if (clickedEdge !== undefined) {
          console.log('clicked edge:', clickedEdge);
        } else {
          return;
        }

        if (!flagClickedNode) {
          return;
        }

        $scope.request.node = parseInt(clickedNode.id_consumer);
        if ($scope.request.node === -1) {
          return;
        }

        var request = {
          node: $scope.request.node,
          global_scale: true
        };

        httpModule.getRawData(request).then(function(data) {
          globalApi.plotData(data, $scope.chartData[0]);
        }).catch(function(data) {
          console.log("no data");
        });

        httpModule.httpGet("/api/machine-learning/clusters/node/first-stage", request).then(function(data) {
          globalApi.plotData(data, $scope.chartData[1]);
        }).catch(function(data) {
          console.log("no data");
        });
      });
    }


    function updateGraph() {
      // var newColor = '#' + Math.floor((Math.random() * 255 * 255 * 255)).toString(16);
      $scope.graph_nodes.clear();
      $scope.graph_edges.clear();
      $scope.graph_nodes.add($scope.networkData.nodes);
      $scope.graph_edges.add($scope.networkData.edges);

      $scope.network.fit();

    }

    $scope.fit = function() {
      $scope.network.fit();
    };



    function initChart() {
      for (let i = 0; i < 3; i++) {
        $scope.chartData[i] = angular.copy($scope.chartModel);
      }
    }



    function getNetworkData() {
      return httpModule.httpGet('/api/network/graph');
    }

    $scope.resetML = function() {
      return httpModule.httpGet('/api/machine-learning/init');
    };

    $scope.loadData = function(request) {
      $scope.display = false;
      if (request === undefined) {
        request = {
          range: null,
          global_scale: true,
          assign: true
        };
      }

      $scope.resetML().then(function() {
        httpModule.httpGet("/api/machine-learning/clusters/range/second-stage", request).then(function(data) {
          $scope.hasData = true;
          globalApi.plotData(data, $scope.chartData[2]);

          $scope.showGraph = false;
          getNetworkData().then(function(data) {
            $scope.networkData = angular.fromJson(data.data);
            console.log($scope.networkData);
            // console.log($scope.networkData.nodes);

            $scope.showGraph = true;
            $timeout(function() {
              updateGraph();
            }, 500);


          }, function(error) {
            console.log("no data");
          });

        }, function(error) {
          console.log("no data");
        });
      });

    };


    $scope.init = function() {
      $scope.chartModel = definitions.getChartModel();
      initChart();
      $timeout(function() {
        initGraph();
      }, 500);
      $scope.loadData();
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
