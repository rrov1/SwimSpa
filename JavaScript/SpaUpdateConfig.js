// Achtung dieses Script benötigt: SpaGlobal.js im Ordner global (Expert Mode!)
// Es muss initial 1x aufgerufen werden, danach sollte es aller 6h laufen, es werden eher selten geänderte Konfigurationswerte aktualisiert

schedule("0 */6 * * *", function () {
    updateSpaConfig();
});

updateSpaConfig();

async function updateSpaConfig() {
    console.log("start");
    var dpBasePath = BASE_ADAPTER + "." + BASE_FOLDER
    // get client id
    var clientId = await getState(dpBasePath + ".ClientGUID").val;
    //console.log("*** clientId: " + clientId);
    var pyScriptFolder = PY_SCRIPTS_FOLDER;
    if (!pyScriptFolder.endsWith("/")) {
        pyScriptFolder += "/";
    }
    //console.log("*** pyScriptFolder: " + pyScriptFolder);
    var discoverIPs = getState(dpBasePath + ".discoverIP").val;
    if (discoverIPs != "") {
        discoverIPs = discoverIPs.split(",");
        console.log("*** IP(s) to disover: " + discoverIPs);
    }
    
    // reset if script runs longer than 5 minutes
    var diff = new Date(new Date() - new Date(getState(dpBasePath + ".scriptRunning").ts));
    if (Math.floor((diff/1000)/60) > 5) {
        console.log("resetting scriptRunning, because it's false since more than 5 minutes");
        setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    }
    // check if executable is running
    let maxWait = 35,
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

    // discover SpaControler
    if (discoverIPs != "") {
        // by given IP
        for (let i = 0; i < discoverIPs.length; i++) {
            console.log("*** discovering IP: " + i + " => " + discoverIPs[i]);
            // spa_config.py clientId restApiUrl dpBasePath spaNum spaIP
            console.log('*** executing: ' + SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_config.py ' + clientId + " " + getRestApiUrl() + " " + dpBasePath + " " + i + " " + discoverIPs[i]);
            await execPythonAsync(SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_config.py ' + clientId + " " + getRestApiUrl() + " " + dpBasePath + " " + i + " " + discoverIPs[i]);
        }
    } else {
        // by broadcast 
        // spa_config.py clientId restApiUrl dpBasePath
        console.log('*** executing: ' + SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_config.py ' + clientId + " " + getRestApiUrl() + " " + dpBasePath);
        await execPythonAsync(SPA_EXECUTEABLE + ' ' + pyScriptFolder + 'spa_config.py ' + clientId + " " + getRestApiUrl() + " " + dpBasePath);
    }

    // signal that there is no longer a script is running
    setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    console.log("end");
}