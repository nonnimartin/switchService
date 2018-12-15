'use strict';
module.exports = function(app) {
  var switchApi = require('../controllers/switchApi.js');

//server api routes
  app.route('/run_test')
      .get(switchApi.run_test);

  app.route('/urls/ready_status/')
      .get(switchApi.ready_status);
};


