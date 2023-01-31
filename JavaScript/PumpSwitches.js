// Pumpe 1 ein-/ausschalten
on({id: "javascript.0.Datenpunkte.SwimSpa.0.Pumpen.P1.Switch", change: "any", ack: false}, function (obj) {
    switchPump(obj);
});

// Pumpe 2 ein-/ausschalten
on({id: "javascript.0.Datenpunkte.SwimSpa.0.Pumpen.P2.Switch", change: "any", ack: false}, function (obj) {
    switchPump(obj);
});

// Pumpe 3 ein-/ausschalten
on({id: "javascript.0.Datenpunkte.SwimSpa.0.Pumpen.P3.Switch", change: "any", ack: false}, function (obj) {
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
