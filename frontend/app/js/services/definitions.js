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

  var graph_options = {
    physics: {
      stabilization: true,
    },
    nodes: {
      borderWidth: 1,
      borderWidthSelected: 2,
      // size: 100,
      fixed: true,
      font: {
        color: '#343434',
        size: 14, // px
        face: 'arial',
        background: 'none',
        strokeWidth: 0, // px
        strokeColor: '#ffffff',
        align: 'center',
        multi: false,
        vadjust: 0,
        bold: {
          color: '#343434',
          size: 14, // px
          face: 'arial',
          vadjust: 0,
          mod: 'bold'
        },
        ital: {
          color: '#343434',
          size: 14, // px
          face: 'arial',
          vadjust: 0,
          mod: 'italic',
        },
        boldital: {
          color: '#343434',
          size: 14, // px
          face: 'arial',
          vadjust: 0,
          mod: 'bold italic'
        },
        mono: {
          color: '#343434',
          size: 15, // px
          face: 'courier new',
          vadjust: 2,
          mod: ''
        }
      },
      labelHighlightBold: true,
      mass: 1,
      scaling: {
        min: 30,
        max: 100,
        label: {
          enabled: false,
          min: 14,
          max: 30,
          maxVisible: 30,
          drawThreshold: 5
        }
      },
      shadow: {
        enabled: true,
        color: 'rgba(0,0,0,0.5)',
        size: 10,
        x: 5,
        y: 5
      },
      shape: 'dot',
      // ellipse, circle, database, box, text.
      // image, circularImage, diamond, dot, star, triangle, triangleDown, hexagon, square, icon
      shapeProperties: {
        borderDashes: false, // only for borders
        borderRadius: 6, // only for box shape
        interpolation: false, // only for image and circularImage shapes
        useImageSize: false, // only for image and circularImage shapes
        useBorderWithImage: false // only for image shape
      }
    },

    edges: {
      color: 'lightgray',
      scaling: {
        min: 1,
        max: 15,
        label: {
          enabled: false,
          min: 14,
          max: 30,
          maxVisible: 30,
          drawThreshold: 5
        }
      }
    },
    layout: {
      randomSeed: 0
    }
  };

  return {
    getRequestStructure: function() {
      return {
        node: -1,
        dual_clustering: 0,
        new_node: null,
        global_scale: true,
        assign: true
      };
    },
    getChartModel: function(){
      return chartModel;
    },
    getGraphOptions: function(){
      return graph_options;
    }
  };
});
