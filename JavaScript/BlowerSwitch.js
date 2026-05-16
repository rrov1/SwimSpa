// Blower ein-/ausschalten (regulärer Ausdruck um alle Blower aller Controller im System zu steuern mit einer subscription)
on({id: /^javascript\.\d+\.Datenpunkte\.SwimSpa\.\d+\.Blower\.BL\.Switch$/, change: "any", ack: false}, function (obj) {
    switchBlower(obj);
});

async function switchBlower(obj) {
    var newState = obj.state.val;
    console.log("start");
    var dpBasePath = BASE_ADAPTER + "." + BASE_FOLDER;
    // get client id
    var clientId = getState(getParent(obj.id, 4) + ".ClientGUID").val;
    // get spa id
    var spaId = getState(getParent(obj.id, 3) + ".ID").val;
    // get spa IP
    var spaIP = getState(getParent(obj.id, 3) + ".IPAddresse").val;

    // check if controller is enabled
    if (getState(getParent(obj.id, 3) + ".ControllerEnabled").val == false) {
        console.log("unable to execute: controller " + spaId + " is disabled.");
        return;
    }

    // get blower key (e.g. "BL")
    var blowerKey = obj.channelId.substring(obj.channelId.lastIndexOf(".") + 1);
    var pyScriptFolder = PY_SCRIPTS_FOLDER;
    if (!pyScriptFolder.endsWith("/")) {
        pyScriptFolder += "/";
    }

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
            return;
        }
    }
    // signal that a script is running
    setState(dpBasePath + '.scriptRunning', {val: true, ack: true});

    // spa_switchBlower.py clientId restApiUrl spaId spaIP blowerKey newBlowerState blowerChannel
    const switchBlowerCommand = buildShellCommand([
        SPA_EXECUTEABLE,
        pyScriptFolder + 'spa_switchBlower.py',
        clientId,
        getRestApiUrl(),
        spaId,
        spaIP,
        blowerKey,
        newState,
        obj.channelId
    ]);
    console.log('*** executing: ' + switchBlowerCommand);

    try {
        await execPythonAsync(switchBlowerCommand);
    } finally {
        // signal that there is no longer a script running
        setState(dpBasePath + '.scriptRunning', {val: false, ack: true});
    }
    console.log("end");
}
