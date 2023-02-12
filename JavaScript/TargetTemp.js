// Zieltemperatur setzen (regulärer Ausdruck um alle Zieltemperaturen im System zu steuern mit einer subscription)
on({id: /^javascript\.\d+\.Datenpunkte\.SwimSpa\.\d+\.ZielTemperatur$/, change: "ne", ack: false}, function (obj) {
    setTargetTemp(obj);
});

function setTargetTemp(obj) {
    var newState = obj.state.val;
    
    // get client id
    var clientId = getState(getParent(obj.id, 2) + ".ClientGUID").val;
    console.log("*** clientId: " + clientId);
    // get spa id
    var spaId = getState(getParent(obj.id, 1) + ".ID").val;
    console.log("*** spaId: " + spaId);
    
    
    // spa_toggleLight.py clientId spaId lightKey lightChannel
    //console.log('python3 spa_setTargetTemp.py ' + clientId + " " + spaId + " " + newState + " " + obj.id);
    exec('python3 spa_setTargetTemp.py ' + clientId + " " + spaId + " " + newState + " " + obj.id, function (error, stdout, stderr) {
        console.log('*** stdout: ' + stdout);
        if (error !== null) {
            console.log('*** stderr: ' + error);
            setState(obj.id, {val: obj.oldState.val, ack: true});
            console.log("*** setting state of:" + obj.id + " to old value: " + obj.oldState.val);
        }
    });
}

function getParent(id, num) {
    var idParent = id;
    for (var min = 0; min < num; min++) {
        idParent = idParent.substring(0, idParent.lastIndexOf("."));
    }
    return idParent;
}
