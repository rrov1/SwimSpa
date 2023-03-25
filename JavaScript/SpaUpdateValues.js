// Achtung dieses Script benötigt: SpaGlobal.js im Ordner global (Expert Mode!)
// Das Script aktualisiert sich häufig ändernde Werte, das kürzeste Intervall ist minütlich.

schedule("* * * * *", function () {
    updateSpaValues();
});

//updateSpaValues();

async function updateSpaValues() {
    console.log("start");
    var dpBasePath = BASE_ADAPTER + "." + BASE_FOLDER
    // get client id
    var clientId = await getState(dpBasePath + ".ClientGUID").val;
    //console.log("*** clientId: " + clientId);
    // alle spa id's (wir gehen mal davon aus, das sie immer sortiert sind)
    var spaIdList = "";
    $('state[id=' + BASE_ADAPTER + "." + BASE_FOLDER + '*.ID]').each(function(id, i) {
        spaIdList = spaIdList + getState(id).val + ",";
    });
    if (spaIdList.endsWith(",")) {
        spaIdList = spaIdList.substring(0, spaIdList.length - 1);
    }
    //console.log("*** spaIdList: " + spaIdList);

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
    console.log('*** executing: ' + SPA_EXECUTEABLE + ' spa_updateBulk.py ' + clientId + " " + getRestApiUrl() + " " + spaIdList + " " + dpBasePath);
    await execPythonAsync(SPA_EXECUTEABLE + ' spa_updateBulk.py ' + clientId + " " + getRestApiUrl() + " " + spaIdList + " " + dpBasePath);

    // signal that there is no longer a script is running
    setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    console.log("end");
}
