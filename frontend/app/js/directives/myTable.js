angular.module('app').directive('myTable', function() {
  return {
    restrict: 'E',
    templateUrl: 'templates/directives/my-table.html',
    scope: {
      caption: '@',
      header: '=?',
      keys: '=',
      data: '=',
      options: '=?'
    },
    link: function(scope) {
      if (scope.options === undefined) {
        scope.options = {
          disp_mode: 1
        };
      }
    }

  };
});
