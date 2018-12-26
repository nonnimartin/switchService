var line      = "==================================================="
var express   = require('express'),
  app         = express(),
  port        = process.env.PORT || 3000,
  bodyParser  = require('body-parser');

var switchApi = require('./api/controllers/switchApi.js');
var fs        = require('fs');
var exec      = require('child_process').exec;

function puts(error, stdout, stderr) { console.log(stdout) }

function closePort(port) {
  //kill process on reservrd ports
  exec("lsof -t -i tcp:" + port + " | xargs kill", puts);
}

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());


var routes = require('./api/routes/switchRoutes');
routes(app);


app.listen(port);

console.log('');
console.log(line);
console.log('| Switch image SMS service serving on port: ' + port + '  |');
console.log(line);
console.log('');

switchApi.startRequests();