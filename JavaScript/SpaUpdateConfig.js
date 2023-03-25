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

    // spa_config.py clientId restApiUrl dpBasePath
    console.log('*** executing: ' + SPA_EXECUTEABLE + ' spa_config.py ' + clientId + " " + getRestApiUrl() + " " + dpBasePath);
    await execPythonAsync(SPA_EXECUTEABLE + ' spa_config.py ' + clientId + " " + getRestApiUrl() + " " + dpBasePath);

    // signal that there is no longer a script is running
    setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    console.log("end");
}
