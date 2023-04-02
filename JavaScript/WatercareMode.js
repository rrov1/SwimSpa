// Wasserpflegemodus setzen (regulärer Ausdruck um alle Zieltemperaturen im System zu steuern mit einer subscription)
on({id: /^javascript\.\d+\.Datenpunkte\.SwimSpa\.\d+\.WasserpflegeSwitch$/, change: "ne", ack: false}, function (obj) {
    setWatercareMode(obj);
});

async function setWatercareMode(obj) {
    var newWaterCareModeIdx = obj.state.val;
    console.log("start");
    var dpBasePath = BASE_ADAPTER + "." + BASE_FOLDER
    // get client id
    var clientId = getState(getParent(obj.id, 2) + ".ClientGUID").val;
    //console.log("*** clientId: " + clientId);
    // get spa id
    var spaId = getState(getParent(obj.id, 1) + ".ID").val;
    //console.log("*** spaId: " + spaId);
    // neuer Wasserpflegemodus Index
    //console.log("*** new watercare mode index: " + newWaterCareModeIdx);
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

    // spa_toggleLight.py clientId restApiUrl spaId lightKey lightChannel
    console.log('*** executing: ' + SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_setWatercareMode.py ' + clientId + " " + getRestApiUrl() + " " + spaId + " " + newWaterCareModeIdx + " " + getParent(obj.id, 1));
    await execPythonAsync(SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_setWatercareMode.py ' + clientId + " " + getRestApiUrl() + " " + spaId + " " + newWaterCareModeIdx + " " + getParent(obj.id, 1));

    // signal that there is no longer a script is running
    setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    console.log("end");
}
