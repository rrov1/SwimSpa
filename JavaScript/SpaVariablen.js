// Pfade für die Datenpunkablage
const BASE_FOLDER = "Datenpunkte.SwimSpa";
const BASE_ADAPTER = "javascript.0";

// Datenpunkte erstellen (1 SpaController, 3 Pumpen)
createDatapoints(1, 3);


function createDatapoints(nDevCnt, nPumpCnt) {
    console.log("*** start: createDatapoints(nDevCnt: " + nDevCnt + ", nPumpCnt: " + nPumpCnt +")");

    // globale Datenpunkte
    createState(BASE_FOLDER + ".actualPowerConsumption", {
        read: true, 
        write: true, 
        name: "actualPowerConsumption",
        unit: 'W', 
        type: "number", 
        role: "value.power.consumption",
        desc: "Momentanverbrauch in W",
        def: 0,
        min: 0
    });
    
    let spaStates = {};
    for (let nCurDev = 0; nCurDev < nDevCnt; nCurDev++) {
        spaStates[nCurDev.toString()] = nCurDev.toString();
    }
    createState(BASE_FOLDER + ".preferredHeating", 0, {
        read: true, 
        write: true, 
        name: "preferredHeating", 
        type: 'number',
        min: 0,
        max: nDevCnt-1,
        role: 'value',
        states: spaStates,
        desc: "ID des Whirlpool/SwimSpa der (bevorzugt) beheizt werden soll."
    });

    createState(BASE_FOLDER + ".preferredHeatingName", {
        read: true, 
        write: false, 
        name: "preferredHeatingName",
        type: "string", 
        role: "info.name",
        desc: "Name des Gerätes das bevorzugt beheizt wird",
        def: ""
    });

    createState(BASE_FOLDER + ".automaticHeating", {
        read: true, 
        write: true, 
        name: "automaticHeating",
        type: "boolean", 
        role: "switch.enable",
        desc: "Automatisches Heizen aktiv/inaktiv",
        def: true
    });

    // GUID
    createState(BASE_FOLDER + ".ClientGUID", {
        read: true, 
        write: false, 
        name: "ClientGUID",
        type: "string", 
        role: "text",
        desc: "Client GUID für Gecko Kommunikation",
        def: ""
    }, function() {
        if (getState(BASE_FOLDER + ".ClientGUID").val == "") {
            let guid = create_UUID();
            console.log("*** created guid: " + guid);
            setState(BASE_FOLDER + ".ClientGUID", guid, true);
        } else {
            console.log("*** leving guid unchanged");
        }
    });

    // Variablen pro SpaController
    for (let nCurDev = 0; nCurDev < nDevCnt; nCurDev++) {
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev, {
            "type" : "device",
            "common" : {"name": "0", "desc": "SpaController"}
        });

        createState(BASE_FOLDER + "." + nCurDev + ".ID", {
            read: true, 
            write: true, 
            name: "ID", 
            type: "string", 
            role: "info.address",
            desc: "Geräte ID",
            def: ""
        });

        createState(BASE_FOLDER + "." + nCurDev + ".U_ID", {
            read: true, 
            write: true, 
            name: "U_ID", 
            type: "string", 
            role: "info.address",
            desc: "Geräte U_ID",
            def: ""
        });

        createState(BASE_FOLDER + "." + nCurDev + ".Name", {
            read: true, 
            write: true, 
            name: "Name", 
            type: "string", 
            role: "info",
            desc: "Name",
            def: ""
        });
        
        createState(BASE_FOLDER + "." + nCurDev + ".Temperatureinheit", {
            read: true, 
            write: true, 
            name: "Temperatureinheit", 
            type: "string", 
            role: "info",
            desc: "Temperatureinheit",
            def: "°C"
        });

        createState(BASE_FOLDER + "." + nCurDev + ".AktuelleTemperatur", {
            read: true, 
            write: true, 
            name: "AktuelleTemperatur", 
            type: "number", 
            role: "value.temperature",
            desc: "Aktuelle Temperatur",
            def: -1
        });

        createState(BASE_FOLDER + "." + nCurDev + ".ZielTemperatur", {
            read: true, 
            write: true, 
            name: "ZielTemperatur", 
            type: "number", 
            role: "value.temperature",
            desc: "Zieltemperatur",
            def: -1
        });

        createState(BASE_FOLDER + "." + nCurDev + ".EchteZielTemperatur", {
            read: true, 
            write: true, 
            name: "EchteZielTemperatur", 
            type: "number", 
            role: "value.temperature",
            desc: "Echte Zieltemperatur",
            def: -1
        });

        createState(BASE_FOLDER + "." + nCurDev + ".Heizer", {
            read: true, 
            write: true, 
            name: "Heizer", 
            type: "string", 
            role: "info.status",
            desc: "Aktivität Heizer",
            def: ""
        });

        createState(BASE_FOLDER + "." + nCurDev + ".Wasserpflege", {
            read: true, 
            write: true, 
            name: "Wasserpflege", 
            type: "string", 
            role: "info.status",
            desc: "Status Wasserpflege",
            def: ""
        });

        createState(BASE_FOLDER + "." + nCurDev + ".WasserpflegeIndex", {
            read: true, 
            write: true, 
            name: "WasserpflegeIndex", 
            type: "number", 
            role: "info.status",
            desc: "Status Wasserpflege (Index)",
            def: -1
        });

        createState(BASE_FOLDER + "." + nCurDev + ".WasserpflegeModi", {
            read: true, 
            write: true, 
            name: "WasserpflegeModi", 
            type: "string", 
            role: "text",
            desc: "Auswählbare Wasserpflegemodi",
            def: ""
        });

        // Pumpen
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen", {
            "type" : "folder",
            "common" : {"name": "Pumpen"}
        });
        for (let nCurPump = 1; nCurPump < nPumpCnt+1; nCurPump++) {
            setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump, {
                "type" : "channel",
                "common" : {"name": "Pumpe"}
            });
            
            createState(BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Name", {
                read: true, 
                write: false, 
                name: "Name", 
                type: "string", 
                role: "info.name",
                desc: "Name der Pumpe",
                def: ""
            });
            // Korrektur write Attribut
            extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Name", {common: {write: false}});

            createState(BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Modus", {
                read: true, 
                write: false, 
                name: "Modus", 
                type: "string", 
                role: "state",
                desc: "Aktueller Modus",
                def: ""
            });
            // Korrektur write Attribut
            extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Modus", {common: {write: false}});

            createState(BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Modi", {
                read: true, 
                write: false, 
                name: "Modi", 
                type: "string", 
                role: "text",
                desc: "Auswählbare Modi",
                def: ""
            });
            // Korrektur write Attribut
            extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Modi", {common: {write: false}});
            
            createState(BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Switch", {
                read: true, 
                write: true, 
                name: "Switch",
                type: 'number',
                min: 0,
                max: 2,
                role: 'level',
                states: {
                    0: 'OFF',
                    1: 'LO',
                    2: 'HI'
                },
                desc: "Geschwindigkeitsstufe der Pumpe",
                def: 0
            });
        }

        // Licht
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Lichter", {
            "type" : "folder",
            "common" : {"name": "Beleuchtung"}
        });
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Lichter.LI", {
            "type" : "channel",
            "common" : {"name": "Beleuchtung"}
        });

        createState(BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Name", {
            read: true, 
            write: false, 
            name: "Name", 
            type: "string", 
            role: "info.name",
            desc: "Name des Lichts",
            def: ""
        });
        // Korrektur write Attribut
        extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Name", {common: {write: false}});

        createState(BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Is_On", {
            read: true, 
            write: false, 
            name: "Is_On", 
            type: "boolean", 
            role: "state",
            desc: "Aktueller Status"
        });
        // Korrektur write Attribut
        extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Is_On", {common: {write: false}});

        createState(BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Switch", {
            read: true, 
            write: true, 
            name: "Switch", 
            type: "boolean", 
            role: "switch",
            desc: "Lichtschalter",
            def: false
        });

        // Sensoren
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren", {
            "type" : "folder",
            "common" : {"name": "Sensoren"}
        });
        // Sensoren: Boolean
        var sSensors = ["FILTER STATUS:CLEAN", "FILTER STATUS:PURGE", "SMART WINTER MODE:ACTIVE"];
        for (let i = 0; i < sSensors.length; i++) {
            setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_"), {
                "type" : "channel",
                "common" : {"name": sSensors[i]}
            });
            
            createState(BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name", {
                read: true, 
                write: false, 
                name: "Name", 
                type: "string", 
                role: "info.name",
                desc: "Name des Sensors",
                def: ""
            });
            // Korrektur write Attribut
            extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name", {common: {write: false}});

            createState(BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State", {
                read: true, 
                write: false, 
                name: "State", 
                type: "boolean", 
                role: "state",
                desc: "Sensorstatus"
            });
            // Korrektur write Attribut
            extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State", {common: {write: false}});
        }

        // Sensoren: String
        sSensors = ["CIRCULATING PUMP", "OZONE"];
        for (let i = 0; i < sSensors.length; i++) {
            setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_"), {
                "type" : "channel",
                "common" : {"name": sSensors[i]}
            });

            createState(BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name", {
                read: true, 
                write: true, 
                name: "Name", 
                type: "string", 
                role: "info.name",
                desc: "Name des Sensors",
                def: ""
            });
            // Korrektur write Attribut
            extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name", {common: {write: false}});

            createState(BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State", {
                read: true, 
                write: true, 
                name: "State", 
                type: "string", 
                role: "state",
                desc: "Sensorstatus",
                def: ""
            });
            // Korrektur write Attribut
            extendObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State", {common: {write: false}});
        }

        // buttons for functions
        createState(BASE_FOLDER + "." + nCurDev + ".enableHeating", {
            read: true, 
            write: true, 
            name: "enableHeating", 
            type: "boolean", 
            role: "button",
            desc: "Heizen aktivieren",
            def: false
        });

        createState(BASE_FOLDER + "." + nCurDev + ".disableHeating", {
            read: true, 
            write: true, 
            name: "disableHeating", 
            type: "boolean", 
            role: "button",
            desc: "Heizen deaktivieren",
            def: false
        });

        // Reminder
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Erinnerungen", {
            "type" : "channel",
            "common" : {"name": "Erinnerungen"}
        });

        // Reminder: String
        var sReminders = ["Time", "RinseFilter", "CleanFilter", "ChangeWater", "CheckSpa"];
        var sReminderDesc = ["Auslesezeitpunkt Erinnerung", "Filter spülen", "Filter reinigen", "Wasser wechseln", "Spa prüfen"];
        for (let i = 0; i < sReminders.length; i++) {
            createState(BASE_FOLDER + "." + nCurDev + ".Erinnerungen." + sReminders[i].replace(/ /g, "_").replace(/:/g, "_"), {
                read: true, 
                write: false, 
                name: "Name", 
                type: "string", 
                role: "info",
                desc: sReminderDesc[i], 
                def: ""
            });
        }
    }
    console.log("*** end: createDatapoints");
}

function create_UUID() {
    var dt = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-xxxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}
