pgApp.controller('PgController',function($scope,$http) {

  $scope.validate = function(element, ctrl) {
    console.log("elelemtn in pg.js" + element);
    var fieldName = $(element).attr('ng-model');

    // Sanitize the received value depending on field type.
    var sanitizedValue = element.html();
     console.log('field is' + fieldName);
     console.log('value is' + sanitizedValue);
     $scope[fieldName] = sanitizedValue;
     
     // Update view, show sanitized value.
    ctrl.$render(sanitizedValue);
    $scope.$apply(function() {
      ctrl.$setViewValue(sanitizedValue);
    });

    // Send post request to app engine.
    $scope.save(element, fieldName);
  }
  
   $scope.save = function(element, fieldName) {
    var postData = {};
    postData[fieldName] = $scope[fieldName];
    $http({
      method: 'POST',
      url: '/pg-edit/' + $scope.pgSlugInit,
      data: postData
    })
    .success(function(data, status) {
      console.log(status);
      $scope.status = status;

      $(element).addClass('confirm');
      setTimeout(function() {
        $(element).removeClass('confirm');
      }, 1500);
    })
    .error(function(data, status) {
      console.log(status);
      $scope.data = data || "Request failed";
      $(element).addClass('error');
      setTimeout(function() {
        $(element).removeClass('error');
      }, 1500);
    });
  };

  $scope.sanitizeSimpleString = function(value) {
    value = $('#sanitizer-div').html(value.trim()).text();  // stripping tags
    value = value.replace(new RegExp('[\t\r\n]', 'ig'), ' ');
    value = value.replace(new RegExp('[ ]+', 'ig'), ' ');
    return value.trim();
  }

});

  
pgApp.controller('RequestUserCtrl', function($scope,$http) {
          
  $scope.saveUser = function(user_key, sharing) {
    $scope.requestUser = user_key;
    $scope.sharing = sharing;
    $scope.save($('#sanitizer-div'), 'requestUser', 'sharing');  // dummy element
  }
  
  $scope.removeUser = function(user_key, sharing) {
    console.log(user_key);
    $scope.removeuser = user_key;
    $scope.sharing = sharing;
    $scope.save($('#sanitizer-div'), 'removeuser', 'sharing');  // dummy element
  }
  
  $scope.save = function(element, fieldName, sharing) {
    var postData = {};
    postData[fieldName] = $scope[fieldName];
    postData[sharing] = $scope[sharing];

    // Without explicit indicator, the back-end
    // could not distinguish empty and non-existent array.
    if (fieldName == 'requestUser') {
      postData['containsAddUser'] = true;
    }
    if (fieldName == 'removeuser') {
      postData['containsRemoveUser'] = true;
    }
    
     
    $http({
      method: 'POST',
      url: '/request-user/' + $scope.pgIdInit,
      data: postData
    })
    .success(function(data, status) {
      console.log(status);
      $scope.status = status;

    })
    .error(function(data, status) {
      console.log(status);
      $scope.data = data || "Request failed";
      $(element).addClass('error');
    });
  };
 });   