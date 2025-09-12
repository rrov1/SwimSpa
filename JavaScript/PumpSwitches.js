// Pumpen ein-/ausschalten (regulärer Ausdruck um alle Pumpen aller Contoller im System zu steuern mit einer subscription)
on({id: /^javascript\.\d+\.Datenpunkte\.SwimSpa\.\d+\.Pumpen\.P\d+\.Switch$/, change: "any", ack: false}, function (obj) {
    switchPump(obj);
});

async function switchPump(obj) {
    var newState = obj.state.val;
    console.log("start");
    var dpBasePath = BASE_ADAPTER + "." + BASE_FOLDER;
    // get client id
    var clientId = getState(getParent(obj.id, 4) + ".ClientGUID").val;
    //console.log("*** clientId: " + clientId);
    // get spa id
    var spaId = getState(getParent(obj.id, 3) + ".ID").val;
    //console.log("*** spaId: " + spaId);
    //get spa IP
    var spaIP = getState(getParent(obj.id, 3) + ".IPAddresse").val;
    //console.log("*** spaIP: " + spaIP);

    // check if controller is enabled
    if (getState(getParent(obj.id, 3) + ".ControllerEnabled").val == false) {
        console.log("unable to execute: controller " + spaId + " is disabled.");
        return;
    }
    
    // get pump id
    var pumpId = parseInt(obj.channelId.substring(obj.channelId.lastIndexOf(".") + 2));
    pumpId--;
    //console.log("*** pump id: " + pumpId);
    //console.log("*** new pump state: " + newState);
    var pyScriptFolder = PY_SCRIPTS_FOLDER;
    if (!pyScriptFolder.endsWith("/")) {
        pyScriptFolder += "/";
    }
    //console.log("*** pyScriptFolder: " + pyScriptFolder);
    
    // reset if script runs longer than 5 minutes
    var diff = new Date(new Date() - new Date(getState(dpBasePath + ".scriptRunning").ts));
    if (Math.floor((diff/1000)/60) > 5) {
        console.log("resetting scriptRunning, because it's false since more than 5 minutes");
        setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    }
    // check if executable is running
    let maxWait = 32,
        startTime = Date.now();
    while (await getState(dpBasePath + ".scriptRunning").val) {
        await Sleep(500);
        if (Date.now() - startTime >= maxWait * 1000) {
            console.log("timeout waiting for an execution timeslot");
            return
        }
    }
    // signal that a script is running
    setState(dpBasePath + '.scriptRunning', {val: true, ack: true});

    // spa_switchPump.py clientId restApiUrl spaId pumpId newPumpState pumpChannel
    console.log('*** executing: ' + SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_switchPump.py ' + clientId + " " + getRestApiUrl() + " " + spaId + " " + spaIP + " " + pumpId + " " + newState + " " + obj.channelId);
    await execPythonAsync(SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_switchPump.py ' + clientId + " " + getRestApiUrl() + " " + spaId + " " + spaIP + " " + pumpId + " " + newState + " " + obj.channelId);

    // signal that there is no longer a script is running
    setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    console.log("end");
}
