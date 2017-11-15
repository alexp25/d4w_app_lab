// angular.module('app').config(['esri.map']);
angular.module('app').config(['$stateProvider', '$urlRouterProvider', '$httpProvider', '$locationProvider', '$mdThemingProvider',
  function($stateProvider, $urlRouterProvider, $httpProvider, $locationProvider, $mdThemingProvider) {
    $httpProvider.defaults.withCredentials = true;
    $urlRouterProvider.otherwise(function($injector, $location) {
      var $state = $injector.get("$state");
      $state.go("home");
    });
    // $mdThemingProvider.theme('altTheme')
    //   .primaryPalette('teal') // specify primary color, all
    //   // other color intentions will be inherited
    //   // from default
    //   .accentPalette('green')
    //
    //
    //   .backgroundPalette('grey', {
    //     'default': '50' // use shade 200 for default, and keep all other shades the same
    //   });


    // $mdThemingProvider.setDefaultTheme('teal');
    // $mdThemingProvider
    //   .theme('default')
    //   .primaryPalette('blue')
    //   .accentPalette('teal')
    //   .warnPalette('red')
    //   .backgroundPalette('grey');
    // https://material.angularjs.org/1.1.0/demo/colors


    $mdThemingProvider.theme('default')
      .primaryPalette('blue-grey', {
        'default': '600', // by default use shade 400 from the pink palette for primary intentions
        'hue-1': '100', // use shade 100 for the <code>md-hue-1</code> class
        'hue-2': '600', // use shade 600 for the <code>md-hue-2</code> class
        'hue-3': 'A100' // use shade A100 for the <code>md-hue-3</code> class
      })
      .accentPalette('blue-grey', {
        'default': '400' // use shade 200 for default, and keep all other shades the same
      })

      // .backgroundPalette('grey', {
      //   'default': 'A100'
      // })

      .warnPalette('blue-grey');

    $stateProvider
      .state('root', {
        url: '',
        abstract: true,
        access: {
          restricted: false
        },
        views: {
          /*'header': {
            templateUrl: 'static/templates/header.html'
          }*/
        }
      })

      .state('login', {
        url: '/login',
        access: {
          restricted: false
        },
        views: {
          /*'header': {
              templateUrl: 'static/templates/header.html'
            },*/
          'content': {
            templateUrl: 'templates/login.html',
            controller: 'loginCtrl'
          }
        }
      })
      .state('register', {
        url: '/register',
        access: {
          restricted: false
        },
        views: {
          /*'header': {
              templateUrl: 'static/templates/header.html'
            },*/
          'content': {
            templateUrl: 'templates/register.html',
            controller: 'registerCtrl'
          }
        }
      })

      .state('home', {
        url: '/home',
        access: {
          restricted: true
        },
        views: {
          /*  'header': {
              templateUrl: 'static/templates/header.html'
            },
            'navigation': {
              templateUrl: 'static/templates/navigation.html',
              controller: 'navigationCtrl'
            },*/
          'content': {
            templateUrl: 'templates/home.html',
            controller: 'homeCtrl'
          }
        }
      })


      .state('settings', {
        url: '/settings',
        access: {
          restricted: true
        },
        views: {

          'content': {
            templateUrl: 'templates/settings.html',
            controller: 'settingsCtrl'
          }
        }
      })

      .state('monitor-overview', {
        url: '/monitor/overview',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/monitor/overview.html',
            controller: 'monitorOverviewCtrl'
          }
        }
      })
      .state('monitor-model-view', {
        url: '/monitor/model-view',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/monitor/model-view.html',
            controller: 'monitorModelViewCtrl'
          }
        }
      })
      .state('monitor-network', {
        url: '/monitor/network',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/monitor/network.html',
            controller: 'monitorNetworkCtrl'
          }
        }
      })
      .state('control-main', {
        url: '/control/main',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/control/main.html',
            controller: 'controlMainCtrl'
          }
        }
      })
      .state('control-details', {
        url: '/control/details',
        access: {
          restricted: true
        },
        views: {
          'content': {
            templateUrl: 'templates/control/details.html',
            controller: 'controlDetailsCtrl'
          }
        }
      });
  }
]);
