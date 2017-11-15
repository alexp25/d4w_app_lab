angular.module('app').controller('monitorNetworkCtrl', ['$scope', 'socket', '$timeout', '$http',
  function($scope, socket, $timeout, $http) {
    var numericDisplay;
    $scope.timer = [];
    $scope.viewMode = 'map';
    $scope.selected = {
      reqtype: 'sensors',
      type: 1,
      id: 4,
      n: 10
    };

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


    var nodes = new vis.DataSet([{
        id: 1,
        label: 'node\none',
        shape: 'box',
        color: '#97C2FC'
      },
      {
        id: 2,
        label: 'node\ntwo',
        shape: 'circle',
        color: '#FFFF00'
      },
      {
        id: 3,
        label: 'node\nthree',
        shape: 'diamond',
        color: '#FB7E81'
      },
      {
        id: 4,
        label: 'node\nfour',
        shape: 'dot',
        size: 10,
        color: '#7BE141'
      },
      {
        id: 5,
        label: 'node\nfive',
        shape: 'ellipse',
        color: '#6E6EFD'
      },
      {
        id: 6,
        label: 'node\nsix',
        shape: 'star',
        color: '#C2FABC'
      },
      {
        id: 7,
        label: 'node\nseven',
        shape: 'triangle',
        color: '#FFA807'
      },
      {
        id: 8,
        label: 'node\neight',
        shape: 'triangleDown',
        color: '#6E6EFD'
      }
    ]);

    // create an array with edges
    var edges = new vis.DataSet([{
        from: 1,
        to: 8,
        color: {
          color: 'red'
        },
        label: "labeled edge"
      },
      {
        from: 1,
        to: 3,
        color: 'rgb(20,24,200)'
      },
      {
        from: 1,
        to: 2,
        color: {
          color: 'rgba(30,30,30,0.2)',
          highlight: 'blue'
        }
      },
      {
        from: 2,
        to: 4,
        color: {
          inherit: 'to'
        }
      },
      {
        from: 2,
        to: 5,
        color: {
          inherit: 'from'
        }
      },
      {
        from: 5,
        to: 6,
        color: {
          inherit: 'both'
        }
      },
      {
        from: 6,
        to: 7,
        color: {
          color: '#ff0000',
          opacity: 0.3
        }
      },
      {
        from: 6,
        to: 8,
        color: {
          opacity: 0.3
        }
      },
    ]);

    // create a network
    var container = document.getElementById('mynetwork');
    var data = {
      nodes: nodes,
      edges: edges
    };
    // var options = {
    //   physics: {
    //     stabilization: true,
    //   },
    //   nodes: {
    //     borderWidth: 4,
    //     size: 10,
    //     //fixed:true,
    //     physics: false,
    //     color: {
    //       border: '#222222',
    //       background: '#666666'
    //     },
    //     font: {
    //       color: '#000000'
    //     }
    //   },
    //   edges: {
    //     color: 'lightgray'
    //   },
    //   layout: {
    //     randomSeed: 0
    //   }
    // };

    var options = {

    };
    var network = new vis.Network(container, data, options);


    function getData(params1) {
      $scope.hasData = false;
      console.log('getData: ', params1);
      $http.get('/api/network/graph', {
        params: {
          param: params1
        }
      }).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data.data);

        if (jsonObj === false) {
          return;
        }
        if (jsonObj.result === 1) {
          return;
        }

        $scope.hasData = true;
        $scope.networkData = jsonObj;

        function updateNetwork() {
          // var newColor = '#' + Math.floor((Math.random() * 255 * 255 * 255)).toString(16);
          nodes.clear();
          edges.clear();
          nodes.add($scope.networkData.nodes);
          edges.add($scope.networkData.edges);
        }

        updateNetwork();

        console.log(jsonObj);

      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        //alert('error');
      });


    }

    $scope.loadData = function() {
      getData(0);
    };

    function pollData(first) {
      let tm = 5000;
      if (first === true) {
        tm = 0;
      }
      $scope.timer[2] = $timeout(function() {
        $scope.loadData();
        pollData(false);
      }, tm);
    }

    $scope.init = function() {
      // pollData(true);
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
      socket.emit('disconnect_request', '');
    });
  }
]);
