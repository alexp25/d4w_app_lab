angular.module("app").factory('httpModule', function($rootScope, $timeout, $http, $q) {
  return {
    httpGet: function(url, params) {
      if (params === undefined) {
        params = null;
      }
      var deferred = $q.defer();
      $http.get(url, {
        params: {
          param: params
        }
      }).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);
        deferred.resolve(jsonObj);
      }).
      catch(function(data) {
        deferred.reject('error');
      });
      return deferred.promise;
    },
    getRawData: function(params1) {
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
          deferred.resolve(null);
          return deferred.promise;
        }
        if (jsonObj.result === 1) {
          deferred.resolve(null);
          return deferred.promise;
        }
        deferred.resolve(jsonObj);
      }).
      catch(function(data) {
        deferred.reject('error');
      });
      return deferred.promise;
    },
    getModelData: function(params1) {
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
          deferred.resolve(null);
          return deferred.promise;
        }
        if (jsonObj.result === 1) {
          deferred.resolve(null);
          return deferred.promise;
        }
        deferred.resolve(jsonObj);
      }).
      catch(function(data) {
        deferred.reject('error');
      });
      return deferred.promise;
    },
    getInfo: function() {
      var deferred = $q.defer();
      console.log('getInfo:');
      $http.get('/api/machine-learning/info', {}).
      then(function(data) {
        var jsonObj = angular.fromJson(data.data);
        if (jsonObj === false) {
          deferred.resolve(null);
          return deferred.promise;
        }
        if (jsonObj.result === 1) {
          deferred.resolve(null);
          return deferred.promise;
        }
        deferred.resolve(jsonObj.info);
      }).
      catch(function(data) {
        deferred.reject('error');
      });
      return deferred.promise;
    }
  };
});
