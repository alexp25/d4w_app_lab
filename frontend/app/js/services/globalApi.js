angular.module("app").factory('globalApi', function($rootScope, $timeout) {
  return {
    plotData: function(data, chart) {
      let info = data.info;
      let tsdata = data.data;

      // console.log(data);
      // console.log(info);
      chart.settings.min = data.info.details.min;
      chart.settings.max = data.info.details.max;
      chart.info = data.info;
      chart.extra = data.extra;

      let rows = [];
      let columns = [];
      let n_points = tsdata[0].length;
      const NMAX = 100;
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
      // chart.disp = false; // refresh anyway
      if (!angular.equals(columns, chart.columns)) {
        // chart.disp = false;
        chart.columns = columns;
      }
      chart.rows = rows;
      chart.timestamp = new Date();

      $timeout(function() {
        chart.disp = true;
      });
      // console.log('dataset updated ', chart);
    }
  };
});
