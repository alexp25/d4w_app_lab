angular.module('app').controller('monitorModelViewCtrl', ['$scope', 'socket', '$timeout', '$http',
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

    $scope.chartData1 = {
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
      disp: false
    };

    $scope.chartData2 = {
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
      disp: false
    };

    $scope.chartData3 = {
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
      disp: false
    };


    function plotData(data, chart) {
      let info = data.info;
      let tsdata = data.data;

      console.log(data);
      console.log(info);

      chart.settings.min = data.info.min;
      chart.settings.max = data.info.max;


      let rows = [];
      let columns = [];
      let n_points = tsdata[0].length;
      const NMAX = 100;
      console.log("series: " + tsdata.length);
      console.log("n_points: " + n_points);
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

      if (!angular.equals(columns, chart.columns)) {
        chart.disp = false;
        chart.columns = columns;
      }
      chart.rows = rows;
      chart.timestamp = new Date();

      $timeout(function() {
        chart.disp = true;
      });

      console.log('dataset updated ', chart);

    }

    function getModelData(plot) {
      $scope.hasData = false;
      console.log('getModelData');
      $http.get('/api/machine-learning/clusters', {
        params: {
          param: {
            "plot": plot
          }
        }
      }).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);

        if (jsonObj === false) {
          return;
        }
        if (jsonObj.result === 1) {
          return;
        }

        $scope.hasData = true;
        if (plot === 0) {
          plotData(jsonObj, $scope.chartData2);
        } else if (plot === 1) {
          plotData(jsonObj, $scope.chartData3);
        }
        // console.log($scope.chartData2);
      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        //alert('error');
      });

    }

    function getRawData(params1) {
      $scope.hasData = false;
      console.log('getRawData: ', params1);
      $http.get('/api/machine-learning/raw', {
        params: {
          param: params1
        }
      }).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);

        if (jsonObj === false) {
          return;
        }
        if (jsonObj.result === 1) {
          return;
        }

        $scope.hasData = true;
        plotData(jsonObj, $scope.chartData1);

      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        //alert('error');
      });


    }

    function pollData(first) {
      let tm = 5000;
      if (first === true) {
        tm = 0;
      }
      $scope.timer[2] = $timeout(function() {
        getRawData($scope.selected);
        getModelData(0);
        getModelData(1);

        pollData(false);
      }, tm);
    }

    $scope.init = function() {
      pollData(true);
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
