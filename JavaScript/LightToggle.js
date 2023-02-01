// Licht ein-/ausschalten
on({id: "javascript.0.Datenpunkte.SwimSpa.0.Lichter.LI.Switch", change: "any", ack: false}, function (obj) {
    toggleLight(obj);
});

function toggleLight(obj) {
    var newState = obj.state.val;
    
    // get client id
    var clientId = getState(getParent(obj.id, 4) + ".ClientGUID").val;
    console.log("*** clientId: " + clientId);
    // get spa id
    var spaId = getState(getParent(obj.id, 3) + ".ID").val;
    console.log("*** spaId: " + spaId);
    // get light key
    var lightKey = obj.channelId.substring(obj.channelId.lastIndexOf(".") + 1);
    console.log("*** light key: " + lightKey);
    
    // spa_toggleLight.py clientId spaId lightKey lightChannel
    exec('python3 spa_toggleLight.py ' + clientId + " " + spaId + " " + lightKey + " " + obj.channelId, function (error, stdout, stderr) {
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