angular.module("app").factory('definitions', function($rootScope, $timeout) {
  var chartModel = {
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
    info: null,
    extra: null,
    disp: false
  };
  return {
    requestStructure: function() {
      return {
        node: -1,
        dual_clustering: 0,
        new_node: null,
        global_scale: true,
        assign: true
      };
    },
    chartModel: function(){
      return chartModel;
    }
  };
});
