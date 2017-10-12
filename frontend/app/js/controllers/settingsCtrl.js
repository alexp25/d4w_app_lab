angular.module('app').controller('settingsCtrl', ['$scope', '$timeout',
  '$log', '$http',
  function($scope, $timeout, $log, $http) {
    $scope.settings = {};
    $scope.hasData = true;


    $scope.postSettings = function() {
      console.log($scope.settings.data);
    };

    $scope.getSettings = function() {
      $scope.hasData = false;
      var config = {
        method: 'GET',
        url: '/api/settings'
      };
      $http(config).

      then(function(response) {
        $scope.hasData = true;
        var responseData = angular.fromJson(response.data);
        console.log(responseData);
        $scope.settings = responseData.data;
      }, function(err) {});
    };

    $scope.reloadConfig = function() {
      console.log("reload server config");
      var config = {
        method: 'GET',
        url: '/api/reload'
      };
      $http(config).
      then(function(response) {

      }, function(err) {});
    };


    $scope.init = function() {
      $scope.getSettings();
    };


    /**
 dropzone
 **/

    //Set options for dropzone
    //Visit http://www.dropzonejs.com/#configuration-options for more options
    $scope.dzOptions = {
      url: '/api/file/settings',
      paramName: 'file',
      maxFilesize: '10',
      maxFiles: 1,
      params: {
        id: 0
      },
      // acceptedFiles: 'image/jpeg, images/jpg, image/png',
      addRemoveLinks: true,
      dictDefaultMessage: 'Drop new configuration file here',
      createImageThumbnails: false,
      thumbnailHeight: 60,
      thumbnailWidth: 60,
      clickable: true
    };

    //Handle events for dropzone
    //Visit http://www.dropzonejs.com/#events for more events
    $scope.dzCallbacks = {
      'addedfile': function(file) {
        // $scope.dzMethods.removeFile(file);
        console.log(file);
        if ($scope.prevFile !== undefined) {
          console.log("replacing file");
          $scope.dzMethods.removeFile($scope.prevFile);
        }
        $scope.newFile = file;
      },
      'removedfile': function(file) {
        console.log(file);
        $scope.prevFile = undefined;
      },
      'success': function(file, xhr) {
        $scope.prevFile = file;
        $scope.$apply(function() {
          $scope.responseData = angular.fromJson(xhr);
          console.log($scope.responseData);
          if ($scope.responseData.result !== 0) {
            alert("Error: File format error. " + $scope.responseData.msg);
            $scope.dzMethods.removeFile(file);
          } else {
            $scope.getSettings();
          }
        });
      }
    };

    //Apply methods for dropzone
    //Visit http://www.dropzonejs.com/#dropzone-methods for more methods
    $scope.dzMethods = {};

    $scope.removeNewFile = function() {
      $scope.dzMethods.removeFile($scope.newFile); //We got $scope.newFile from 'addedfile' event callback
    };


    $scope.$on('$destroy', function(event) {});
  }
]);
