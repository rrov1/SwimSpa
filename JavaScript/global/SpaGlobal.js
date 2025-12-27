// Pfade für die Datenpunkablage
const BASE_ADAPTER = "javascript.0";
const BASE_FOLDER = "Datenpunkte.SwimSpa";
const SPA_EXECUTEABLE = "python3"
const PY_SCRIPTS_FOLDER = "/SpaController"

function execPythonAsync(command) {
    return new Promise((resolve, reject) => {
        exec(command, function (error, stdout, stderr) {
            //console.log('*** stdout: ' + stdout);
            if (error) {
                console.error('*** command failed with error code: ' + error.code + " - " + error.message);
            }
            resolve();
        });
    })
}

function Sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function getRestApiUrl() {
    //console.log("*** hostname: " + require("os").hostname());
    // get host ip (wir gehen mal davon aus, das Simple Rest API auch auf dem gleichen ioBroker läuft, Multihost ignorieren wir mal)
    var objectData = getObject("system.host."+ require("os").hostname());
    var ioBrIpAddress = "";
    for (var i = 0; i <= objectData.common.address.length - 1; i++) {
        ioBrIpAddress = objectData.common.address[i]
        if (ioBrIpAddress.match(/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/)) {
            break
        }
    }
    //console.log("*** ioBroker IPv4 address: " + ioBrIpAddress);
    // erste Instanz von Rest API
    objectData = getObject("system.adapter.simple-api.0");
    if (objectData.native.bind != "0.0.0.0") {
        console.log("Simple Rest API has different ip address configured: " + objectData.native.bind);
        ioBrIpAddress = objectData.native.bind;
    }
    //console.log("*** Simple Rest API port: " + objectData.native.port);
    //console.log("*** Simple Rest API uses https: " + objectData.native.secure);
    // URL zusammenbauen
    let simpleRestApiUrl = "http"
    if (objectData.native.secure) {
        simpleRestApiUrl += "s"
    }
    simpleRestApiUrl += "://" + ioBrIpAddress + ":" + objectData.native.port;
    //console.log("*** Simple Rest API URL: " + simpleRestApiUrl);
    return simpleRestApiUrl
}

function getParent(id, num) {
    var idParent = id;
    for (var min = 0; min < num; min++) {
        idParent = idParent.substring(0, idParent.lastIndexOf("."));
    }
    return idParent;
}
