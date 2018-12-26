'use strict';

var fs         = require('fs');
var https      = require('https');
var url        = require('url');
var request    = require('request');
var {PythonShell} = require('python-shell')
var resolve = require('path').resolve
var globalResult;
var isRunning  = false;

// Load the AWS SDK for Node.js
var AWS = require('aws-sdk');

//get absolute path for config file
var filePath = resolve('./config.json');
AWS.config.loadFromPath(filePath);

function runRequests(){
  setInterval(getTwitterImageUrl, 10000);
}

function stopRequests(){
  clearInterval(getTwitterImageUrl);
}

exports.startRequests = function(req,res){
  runRequests();
}

function getTwitterImageUrl() {

  if (!isRunning) {
      isRunning    = true;
      var filePath = resolve('./config.json');
      var configMap;

      fs.readFile(filePath, 'utf8', function (err, data) {
          if (err) throw err;
             configMap = JSON.parse(data);
      });

      var options = {
      mode: 'text',
      pythonPath: '/usr/local/bin/python'
      };

      PythonShell.run('get_last_tweet.py', options, function (err, result) {
      if (err){
        throw err;
      }else{
        console.log('result = ' + result);
        if (result == 'None' || result == null){
          console.log('Result was None');
          globalResult = result;
        }else{
          console.log('Result was sent and ' + result);
          globalResult = result;
          sendSMSToNumber(configMap.phoneNumber, result);
        }
        isRunning = false;
        return result;
      }
    });
  }
}

function sendSMSToNumber(phoneNumber, message){

    // Create publish parameters
    var params = {
      Message: message.toString(),
      PhoneNumber: phoneNumber,
    };
    // Create promise and SNS service object
    var publishTextPromise = new AWS.SNS({apiVersion: '2010-03-31'}).publish(params).promise();
    // Handle promise's fulfilled/rejected states
    publishTextPromise.then(
      function(data) {
        console.log("MessageID is " + data.MessageId);
      }).catch(
        function(err) {
        console.error(err, err.stack);
    });
}

//REST API functions
exports.run_test = function(req, res) {
  getTwitterImageUrl();
  return res;
};

exports.ready_status = function(req, res) {
  setStatus('ready', '');
}


