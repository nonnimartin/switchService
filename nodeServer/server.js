var line      = "==================================================="
var express   = require('express'),
  app         = express(),
  port        = process.env.PORT || 3000,
  bodyParser  = require('body-parser');

var switchApi = require('./api/controllers/switchApi.js');
var serve     = require('serve');
var fs        = require('fs');
var exec      = require('child_process').exec;

function puts(error, stdout, stderr) { console.log(stdout) }

function closePort(port) {
  //kill process on reservrd ports
  exec("lsof -t -i tcp:" + port + " | xargs kill", puts);
}

function serveStartupStatus() {

    //Write current status to json file for Chrome to check
    var statusJSON = {
      "status" : "startup"
    };

    fs.writeFile(__dirname + "/status/status.json", JSON.stringify(statusJSON), function(err) {
    if (err) throw err;
    });
//serve the status.json location
    const server = serve(__dirname + "/status", {
      port: 3002
    })
    global.statusServed = true;
}

closePort("3001");
closePort("3002");

serveStartupStatus();

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