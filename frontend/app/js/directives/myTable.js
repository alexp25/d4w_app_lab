angular.module('app').directive('myTable', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/my-table.html',
    scope: {
      caption: '@',
      header: '=?',
      keys: '=',
      data: '='
    },
    link: function(scope) {

    }

  };
});
