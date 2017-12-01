angular.module('app').controller('monitorNetworkCtrl', ['$scope', 'socket', '$timeout', '$http', '$q',
  function($scope, socket, $timeout, $http, $q) {
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

    $scope.showChart = false;


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

    // var options = {
    //
    // };
    var network = new vis.Network(container, data, options);

    $scope.request = {
      node: -1,
      dual_clustering: 0
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
      // cutn: 10,
      info: "",
      disp: false
    };

    $scope.chartData = [];


    function initChart() {
      for (let i = 0; i < 2; i++) {
        $scope.chartData[i] = angular.copy($scope.chartModel);
      }
    }


    function plotData(data, chart) {
      let info = data.info;
      let tsdata = data.data;

      // console.log(data);
      // console.log(info);
      chart.settings.min = data.info.min;
      chart.settings.max = data.info.max;
      chart.info = data.info;

      let rows = [];
      let columns = [];
      let n_points = tsdata[0].length;
      const NMAX = 100;
      // console.log("series: " + tsdata.length);
      // console.log("n_points: " + n_points);
      let n_series_draw = (tsdata.length < NMAX) ? (tsdata.length) : NMAX;
      columns = ['x'];
      for (let i = 0; i < n_series_draw; i++) {
        columns.push(info.headers[i]);
      }

      for (let i = 0; i < n_points; i++) {
        rows[i] = [i];
        for (let j = 0; j < n_series_draw; j++) {
          rows[i][j + 1] = tsdata[j][i];
        }
      }

      // chart.disp = false; // refresh anyway

      if (!angular.equals(columns, chart.columns)) {
        // chart.disp = false;
        chart.columns = columns;
      }
      chart.rows = rows;
      chart.timestamp = new Date();

      $timeout(function() {
        chart.disp = true;
      });

      // console.log('dataset updated ', chart);

    }

    function getRawData(params1) {
      $scope.hasData = false;
      var deferred = $q.defer();

      console.log('getRawData: ', params1);
      $http.get('/api/machine-learning/raw', {
        params: {
          param: params1
        }
      }).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);

        if (jsonObj === false) {
          // deferred.reject('error');
          deferred.resolve('error');
          return deferred.promise;
        }
        if (jsonObj.result === 1) {
          deferred.resolve('error');
          return deferred.promise;
        }

        $scope.hasData = true;
        plotData(jsonObj, $scope.chartData[0]);

        deferred.resolve('done');

      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        deferred.reject(data);
      });

      return deferred.promise;
    }


    function getModelData(params1) {
      $scope.hasData = false;
      var deferred = $q.defer();

      console.log('getModelData: ', params1);
      $http.get('/api/machine-learning/clusters', {
        params: {
          param: params1
        }
      }).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);


        if (jsonObj === false) {
          deferred.resolve('error');
          return deferred.promise;
        }
        if (jsonObj.result === 1) {
          deferred.resolve('error');
          return deferred.promise;
        }

        $scope.hasData = true;
        if (params1.dual_clustering === 0) {
          plotData(jsonObj, $scope.chartData[1]);
        } else if (params1.dual_clustering === 1) {
          plotData(jsonObj, $scope.chartData[2]);
        }

        deferred.resolve('done');
        // console.log($scope.chartData2);
      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        deferred.reject('error');
      });
      return deferred.promise;
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


      getRawData($scope.request).then(function() {
        console.log("ok");
      }).catch(function(data) {
        console.log("error: " + data);
      });

      getModelData($scope.request).then(function() {
        console.log("ok");
      }).catch(function(data) {
        console.log("error: " + data);
      });


    });


    function updateNetwork() {
      // var newColor = '#' + Math.floor((Math.random() * 255 * 255 * 255)).toString(16);
      nodes.clear();
      edges.clear();
      nodes.add($scope.networkData.nodes);
      edges.add($scope.networkData.edges);
    }




    function getNetworkData(params1) {
      $scope.hasData = false;
      console.log('getNetworkData: ', params1);
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
      getNetworkData(0);
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
      // pollData(true);
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
      socket.emit('disconnect_request', '');
    });
  }
]);
