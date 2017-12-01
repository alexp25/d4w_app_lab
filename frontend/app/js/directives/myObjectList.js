angular.module('app').directive('myObjectList', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/my-object-list.html',
    scope: {
      caption: '@',
      data: '='
    },
    link: function(scope) {

    }

  };
});
