angular.module('app').controller('controlDetailsCtrl', ['$scope', 'socket', '$timeout', '$http',
  function($scope, socket, $timeout, $http) {

    $scope.timer = [];
    $scope.viewMode = 'map';
    $scope.selected = {
      reqtype: 'control'
    };
    $scope.data_init = false;

    $scope.control = {
      pump: 0,
      ref: 0,
      mode: 0,
      supervisor: 0,
      controller_selection: 0,
      controller_selection_id: 1
    };

    $scope.test = function() {
      console.log("test");
    };


    var startPolling = function(delay) {
      $scope.timer[1] = $timeout(function() {
        if (socket.isConnected || true) {
          socket.emit('get_data', $scope.selected);
          // socket.emit('get_data', $scope.selected, function(data) {
          //   startPollingWs_socketio();
          // });
          startPolling(delay);
        }
      }, delay);
    };

    $scope.send = function(data) {
      socket.emit('post_data', data);
      console.log(data);
    };


    $scope.init = function() {
      $scope.timer[0] = $timeout(function() {

        socket.connect();
        socket.on('connect', function() {
          console.log('connect event');
          $scope.data_init = false;
          socket.emit('message', 'connection');
        });

        socket.on('disconnect', function() {
          console.log('disconnect event');
        });

        socket.on('get_data', function(msg) {
          $scope.jsondata = angular.fromJson(msg);
          if (!$scope.data_init) {
            $scope.data_init = true;
            $scope.control.pump = $scope.jsondata.info.pump;
            $scope.control.ref = $scope.jsondata.info.ref;
            $scope.control.mode = $scope.jsondata.info.mode.toString();
            $scope.control.supervisor = $scope.jsondata.info.supervisor.toString();
          }

          if ($scope.jsondata.info.mode >= 1) {
            $scope.control.pump = $scope.jsondata.info.pump;
          }
          if ($scope.jsondata.info.mode === 5) {
            $scope.control.ref = $scope.jsondata.info.ref;
          }
        });
        startPolling(100);

      }, 500);
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
