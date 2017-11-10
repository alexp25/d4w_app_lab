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

    $scope.chartData = {
      columns: ['x', 'series 1'],
      rows: [
        [1, 10],
        [2, 20],
        [3, 30],
      ],
      timestamp: new Date()
    };

    $scope.chartSettings = {
      min: 0,
      max: 5000
    };

    function getModelData() {
      $scope.hasData = false;
      console.log('getModelData');
      $http.get('/api/machine-learning/clusters', {
        params: {
          param: 0
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

        let info = jsonObj.info;

        console.log(jsonObj);
        console.log(info);

        $scope.chartSettings.min = info.min;
        $scope.chartSettings.max = info.max;

        jsonObj = jsonObj.data;
        // $scope.displayData = false;

        let rows = [];
        let n_points = jsonObj[0].length;
        const NMAX = 15;
        console.log("series: " + jsonObj.length);
        let n_series_draw = (jsonObj.length < NMAX) ? (jsonObj.length) : NMAX;
        $scope.chartData.columns = ['x'];
        for (let i = 0; i < n_series_draw; i++) {
          $scope.chartData.columns.push('series ' + i + ": " + info.headers[i]);
        }
        for (let i = 0; i < n_points; i++) {
          // add timestamp
          // rows[i] = [new Date(jsonObj[i].Timestamp)];
          rows[i] = [i];
          for (let j = 0; j < n_series_draw; j++) {
            // add data from all clusters
            if (j < jsonObj[i].length) {
              rows[i].push(jsonObj[j][i]);
            }
          }
        }
        $scope.chartData.rows = rows;
        $scope.chartData.timestamp = new Date();

        $timeout(function() {
          $scope.displayData = true;
        });

        console.log('dataset updated ', $scope.chartData);


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
      $http.get('/api/database/sensors', {
        params: {
          param: params1
        }
      }).
      then(function(data) {
        var i;
        var jsonObj = angular.fromJson(data.data);
        $scope.jsonObj = jsonObj;

        if ($scope.jsonObj === false) {
          return;
        }
        if ($scope.jsonObj.result === 1) {
          return;
        }

        $scope.hasData = true;
        console.log($scope.jsonObj[0]);
        // $scope.displayData = false;


        if (jsonObj[0] !== undefined) {

          var rows = [];
          var uk, yk, rk;
          for (i = 0; i < jsonObj.length; i++) {
            uk = jsonObj[i].Value;

            rows[i] = [new Date(jsonObj[i].Timestamp), uk];
          }
          $scope.chartData.rows = rows;
          $scope.chartData.timestamp = new Date();

          $timeout(function() {
            $scope.displayData = true;
          });

          console.log('dataset updated ', $scope.chartData);
        }

      }).
      catch(function(data) {
        $scope.jsondata = 'error';
        $scope.hasData = true;
        //alert('error');
      });


    }

    function pollData() {
      $scope.timer[2] = $timeout(function() {
        // getRawData($scope.selected);
        getModelData();
        pollData();
      }, 5000);
    }

    $scope.init = function() {

      pollData();
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
