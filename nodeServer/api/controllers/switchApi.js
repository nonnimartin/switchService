'use strict';

var fs         = require('fs');
var https      = require('https');
var url        = require('url');
var request    = require('request');
const serve    = require('serve');
let {PythonShell} = require('python-shell')
var globalResult;
//const SMS      = require('node-sms-send')



function runRequests(){
  setInterval(getTwitterImageUrl, 2000);
}

function stopRequests(){
  clearInterval(getTwitterImageUrl);
}

exports.startRequests = function(req,res){
  runRequests();
}

function getTwitterImageUrl() {

  let options = {
  mode: 'text',
  pythonPath: '/usr/local/bin/python'
  };

  PythonShell.run('get_latest_img_url.py', options, function (err, result) {
  if (err){
    throw err;
  }else{
    if (result == null || result == 'null'){
      console.log('result was null');
      globalResult = result;
    }else{
      console.log('result was ' + result);
      globalResult = result;
    }
    return result;
  }
  });
}

/*function sendSMSToNumber(phoneNumber, userName, password, message){
  const sms = new SMS(userName, password);
  sms.send(phoneNumber, message)

  .then(body => console.log('body error message = ' + body)) // returns { message_id: 'string' }
  .catch(err => console.log('error = ' + err.message))

}*/

//REST API functions
exports.run_test = function(req, res) {
  getTwitterImageUrl();
  return res;
};

exports.ready_status = function(req, res) {
  setStatus('ready', '');
}


