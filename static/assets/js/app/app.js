/*
 * jQuery File Upload Plugin Angular JS Example 1.2.1
 * https://github.com/blueimp/jQuery-File-Upload
 *
 * Copyright 2013, Sebastian Tschan
 * https://blueimp.net
 *
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 */

/* jshint nomen:false */
/* global window, angular */

    console.log("app loaded");

    var pgApp = angular.module('pgApp', [
        'blueimp.fileupload',
        'ngAnimate',
        'ui.bootstrap',
        'ngRoute'
    ], function ($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    })
        pgApp.config([
            '$httpProvider', 'fileUploadProvider',
            function ($httpProvider, fileUploadProvider) {
                $httpProvider.defaults.transformRequest = function(data) {
                    if (data === undefined) {
                        return data;
                    }
                    return $.param(data);
                }
                $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
                delete $httpProvider.defaults.headers.common['X-Requested-With'];
                fileUploadProvider.defaults.redirect = window.location.href.replace(
                    /\/[^\/]*$/,
                    '/cors/result.html?%s'
                );
               
                    // Demo settings:
                    angular.extend(fileUploadProvider.defaults, {
                        // Enable image resizing, except for Android and Opera,
                        // which actually support image resizing, but fail to
                        // send Blob objects via XHR requests:
                        disableImageResize: /Android(?!.*Chrome)|Opera/
                            .test(window.navigator.userAgent),
                        maxFileSize: 5000000,
                        acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i
                    });
                }
            
        ])
    

        pgApp.controller('DemoFileUploadController', [
            '$scope', '$http', '$filter', '$window',
            function ($scope, $http) {
                $scope.options = {
                    url: url
                };
               
                    $scope.loadingFiles = true;
                    $http.get(url)
                        .then(
                            function (response) {
                                $scope.loadingFiles = false;
                                $scope.queue = response.data.files || [];
                            },
                            function () {
                                $scope.loadingFiles = false;
                            }
                        );
                }
            
        ])

        pgApp.controller('FileDestroyController', [
            '$scope', '$http',
            function ($scope, $http) {
                var file = $scope.file,
                    state;
                if (file.url) {
                    file.$state = function () {
                        return state;
                    };
                    file.$destroy = function () {
                        state = 'pending';
                        return $http({
                            url: file.deleteUrl,
                            method: file.deleteType
                        }).then(
                            function () {
                                state = 'resolved';
                                $scope.clear(file);
                            },
                            function () {
                                state = 'rejected';
                            }
                        );
                    };
                } else if (!file.$cancel && !file._index) {
                    file.$cancel = function () {
                        $scope.clear(file);
                    };
                }
            }
        ]);
        
        pgApp.controller('FileDeleteAfterRefresh', function($scope,$http) {
                     $scope.destroy = function (url, type, div_id) {
                        console.log('app.js url is' + url);
                        return $http({
                            method: 'POST',
                            url: url + '&_method=' + type
                            
                        }).then(
                            function () {
                                 $("#"+div_id).hide();
                            });
                    };
        });


        // Directive to make html elements editable for admin/moderation purposes.
        pgApp.directive('contenteditable', function() {
            return {
               require: 'ngModel',
               link: function(scope, element, attributes, ctrl) {
                   // view -> model
                   element.on('blur', function() {
                       console.log("element is" + element);
                       scope.validate(element, ctrl);
                   });

                   // Unless the element has the explicit class "allow-linebreaks",
                   // we'll suppress Enter key presses and exit focus (triggering save).
                   if (attributes.class === undefined ||
                       attributes.class.indexOf('allow-linebreaks') == -1) {
                       $(element).keypress(function(event) {
                           if (event.which == 13) {
                               event.preventDefault();
                               $(element).blur();
                            }
                        });
                    }

                    // model -> view
                    ctrl.$render = function(value) {
                        element.html(value);
                    };

                    // load init value from DOM
                    ctrl.$setViewValue(element.html()); 
                }
            };
        });
