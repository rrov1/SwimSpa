// Automatische Nachführung der Zieltemperatur
// kann ggf. auch den DP automaticTargetTemp auch deaktiviert werden

schedule("10,40 * * * *", function () {
    checkAndSetSpaTemp(BASE_ADAPTER + "." + BASE_FOLDER + ".0", 28);
    checkAndSetSpaTemp(BASE_ADAPTER + "." + BASE_FOLDER + ".1", 37);
});

function checkAndSetSpaTemp(spaDevice, maxTargetTemp) {
    //console.log("start");
    var currentSpaTemp, targetTemp;

    if (!getState(getParent(spaDevice, 1) + ".automaticTargetTemp").val) {
        console.log("automatic temperature tracking deactivated");
        return;
    }

    currentSpaTemp = getState(spaDevice + '.AktuelleTemperatur').val;
    targetTemp = getState(spaDevice + '.ZielTemperatur').val;

    if (currentSpaTemp + 5 != targetTemp) {
        if (currentSpaTemp + 5 > 12 && currentSpaTemp + 5 < maxTargetTemp) {
            console.log("changing target temp for \"" + getState(spaDevice + ".Name").val + "\" to " + (currentSpaTemp + 5));
            setState(spaDevice + '.ZielTemperatur', {val: currentSpaTemp + 5, ack: false});
        } else {
            console.log("automatic temperature tracking hit with " + (currentSpaTemp + 5) + " the min or max value");
        }
    }

    //console.log("end");
}