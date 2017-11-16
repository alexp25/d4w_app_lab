angular.module('app').controller('monitorModelViewCtrl', ['$scope', 'socket', '$timeout', '$http', '$q',
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


    function initChart() {
      for (let i = 0; i < 3; i++) {
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

      if (!angular.equals(columns, chart.columns)) {
        chart.disp = false;
        chart.columns = columns;
      }
      chart.rows = rows;
      chart.timestamp = new Date();

      $timeout(function() {
        chart.disp = true;
      });

      // console.log('dataset updated ', chart);

    }

    function getModelData(plot) {
      $scope.hasData = false;
      var deferred = $q.defer();

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
          deferred.resolve('error');
          return deferred.promise;
        }
        if (jsonObj.result === 1) {
          deferred.resolve('error');
          return deferred.promise;
        }

        $scope.hasData = true;
        if (plot === 0) {
          plotData(jsonObj, $scope.chartData[1]);
        } else if (plot === 1) {
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
        deferred.reject('error');
      });

      return deferred.promise;
    }

    $scope.loadData = function() {
      var deferred = $q.defer();
      getRawData($scope.selected).then(function() {
        getModelData(0).then(function() {
          getModelData(1).then(function() {
            deferred.resolve('done');
          });
        });
      });
      return deferred.promise;
    };


    function pollData(first, tm = 1000) {
      let tm1 = tm;
      if (first === true) {
        tm1 = 0;
      }
      $scope.timer[2] = $timeout(function() {
        $scope.loadData().then(function() {
          pollData(false, tm);
        });
      }, tm1);
    }

    $scope.startLoop = function(tm) {
      pollData(true, tm);
    };

    $scope.stopLoop = function() {
      $timeout.cancel($scope.timer[2]);
    };

    $scope.init = function() {
      initChart();
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
