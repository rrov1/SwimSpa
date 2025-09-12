// Achtung dieses Script benötigt: SpaGlobal.js im Ordner global (Expert Mode!)
// Das Script aktualisiert sich häufig ändernde Werte, das kürzeste Intervall ist minütlich.

schedule("* * * * *", function () {
    updateSpaValues();
});

async function updateSpaValues() {
    console.log("start");
    var dpBasePath = BASE_ADAPTER + "." + BASE_FOLDER
    // get client id
    var clientId = await getState(dpBasePath + ".ClientGUID").val;
    //console.log("*** clientId: " + clientId);
    // alle spa id's (wir gehen mal davon aus, das sie immer sortiert sind)
    var spaIdList = "", spaIPList = "";
    $('state[id=' + BASE_ADAPTER + "." + BASE_FOLDER + '*.ID]').each(function(id, i) {
        spaIdList = spaIdList + getState(id).val + ",";
        if (getState(id.replace(".ID", ".ControllerEnabled")).val == true) {
            spaIPList = spaIPList + getState(id.replace(".ID", ".IPAddresse")).val + ",";
        } else {
            spaIPList = spaIPList + "0.0.0.0" + ",";
        }
    });
    if (spaIdList.endsWith(",")) {
        spaIdList = spaIdList.substring(0, spaIdList.length - 1);
    }
    if (spaIPList.endsWith(",")) {
        spaIPList = spaIPList.substring(0, spaIPList.length - 1);
    }
    //console.log("*** spaIdList: " + spaIdList);
    //console.log("*** spaIPList: " + spaIPList);
    
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
    let maxWait = 20,
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

    // spa_updateBulk.py clientId restApiUrl spaIdList dpBasePath
    console.log('*** executing: ' + SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_updateBulk.py ' + clientId + " " + getRestApiUrl() + " " + spaIdList + " " + spaIPList + " " + dpBasePath);
    await execPythonAsync(SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_updateBulk.py ' + clientId + " " + getRestApiUrl() + " " + spaIdList + " " + spaIPList + " " + dpBasePath);

    // signal that there is no longer a script is running
    setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    console.log("end");
}
