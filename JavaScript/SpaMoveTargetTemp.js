// Automatische Nachführung der Zieltemperatur
// kann ggf. auch den DP automaticTargetTemp auch deaktiviert werden

schedule("10,30,50 * * * *", function () {
    checkAndSetSpaTemp(BASE_ADAPTER + "." + BASE_FOLDER + ".0", 30);
    checkAndSetSpaTemp(BASE_ADAPTER + "." + BASE_FOLDER + ".1", 38);
});

function checkAndSetSpaTemp(spaDevice, maxTargetTemp) {
    //console.log("start");
    const MIN_SPA_TEMP = 12;
    var currentSpaTemp, targetTemp;

    if (!getState(getParent(spaDevice, 1) + ".automaticTargetTemp").val) {
        console.log("automatic temperature tracking deactivated");
        return;
    }

    currentSpaTemp = getState(spaDevice + '.AktuelleTemperatur').val;
    targetTemp = getState(spaDevice + '.ZielTemperatur').val;

    if (currentSpaTemp + 5 != targetTemp) {
        if (currentSpaTemp + 5 > MIN_SPA_TEMP && currentSpaTemp + 5 < maxTargetTemp) {
            console.log("changing target temp for \"" + getState(spaDevice + ".Name").val + "\" to " + (currentSpaTemp + 5));
            setState(spaDevice + '.ZielTemperatur', {val: currentSpaTemp + 5, ack: false});
        } else {
            if (currentSpaTemp + 5 > maxTargetTemp && targetTemp != maxTargetTemp) {
                setState(spaDevice + '.ZielTemperatur', {val: maxTargetTemp, ack: false});
            }
            if (currentSpaTemp + 5 < MIN_SPA_TEMP && targetTemp != MIN_SPA_TEMP) {
                setState(spaDevice + '.ZielTemperatur', {val: MIN_SPA_TEMP, ack: false});
            }
            console.log("automatic temperature tracking target with " + (currentSpaTemp + 5) + " exceeds the min (" + MIN_SPA_TEMP + ") or max (" + maxTargetTemp + ") value");
        }
    }

    //console.log("end");
}