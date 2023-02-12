// Pumpen ein-/ausschalten (regulärer Ausdruck um alle Pumpen im System zu steuern mit einer subscription)
on({id: /^javascript\.\d+\.Datenpunkte\.SwimSpa\.\d+\.Pumpen\.P\d+\.Switch$/, change: "any", ack: false}, function (obj) {
    switchPump(obj);
});

function switchPump(obj) {
    var newState = obj.state.val;
    
    // get client id
    var clientId = getState(getParent(obj.id, 4) + ".ClientGUID").val;
    console.log("*** clientId: " + clientId);
    // get spa id
    var spaId = getState(getParent(obj.id, 3) + ".ID").val;
    console.log("*** spaId: " + spaId);
    // get pump id
    var pumpId = parseInt(obj.channelId.substring(obj.channelId.lastIndexOf(".") + 2));
    pumpId--;
    console.log("*** pump id: " + pumpId);
    console.log("*** new pump state: " + newState);
    
    // spa_switchPump.py clientId spaId pumpId newPumpState pumpChannel
    exec('python3 spa_switchPump.py ' + clientId + " " + spaId + " " + pumpId + " " + newState + " " + obj.channelId, function (error, stdout, stderr) {
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
