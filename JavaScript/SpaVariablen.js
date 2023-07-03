// Achtung dieses Script benötigt: SpaGlobal.js im Ordner global (Expert Mode!)

// Datenpunkte erstellen (2 SpaController, 3 Pumpen, mit Wasserfall)
createDatapoints(2, 3, true);


function createDatapoints(nDevCnt, nPumpCnt, createWaterfall) {
    const VERSION = "0.2.4"
    console.log("*** start: createDatapoints(nDevCnt: " + nDevCnt + ", nPumpCnt: " + nPumpCnt + ", createWaterfall: " + createWaterfall + ") v" + VERSION);
    var objectId, objectData;

    // globale Datenpunkte
    let spaStates = {};
    for (let nCurDev = 0; nCurDev < nDevCnt; nCurDev++) {
        spaStates[nCurDev.toString()] = nCurDev.toString();
    }

    objectId = BASE_ADAPTER + "." + BASE_FOLDER + ".preferredHeating";
    if (!existsState(objectId)) {
        createState(objectId, {
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
    } else {
        // Korrektur Attribute
        objectData = getObject(objectId);
        objectData.common.name = "preferredHeating";
        setObject(objectId, objectData, function (err) {
            if (err) log('cannot write object: ' + err);
        });
    }

    objectId = BASE_ADAPTER + "." + BASE_FOLDER + ".preferredHeatingName";
    if (!existsState(objectId)) {
        createState(objectId, {
            read: true, 
            write: false, 
            name: "preferredHeatingName",
            type: "string", 
            role: "info.name",
            desc: "Name des Gerätes das bevorzugt beheizt wird",
            def: ""
        });
    } else {
        // Korrektur Attribute
        objectData = getObject(objectId);
        objectData.common.name = "preferredHeatingName";
        setObject(objectId, objectData, function (err) {
            if (err) log('cannot write object: ' + err);
        });
    }

    objectId = BASE_ADAPTER + "." + BASE_FOLDER + ".automaticHeating";
    if (!existsState(objectId)) {
        createState(objectId, {
            read: true, 
            write: true, 
            name: "automaticHeating",
            type: "boolean", 
            role: "switch.enable",
            desc: "Automatisches Heizen aktiv/inaktiv",
            def: true
        });
    } else {
        // Korrektur Attribute
        objectData = getObject(objectId);
        objectData.common.name = "automaticHeating";
        setObject(objectId, objectData, function (err) {
            if (err) log('cannot write object: ' + err);
        });
    }

    objectId = BASE_ADAPTER + "." + BASE_FOLDER + ".automaticTargetTemp";
    if (!existsState(objectId)) {
        createState(objectId, {
            read: true, 
            write: true, 
            name: "automaticTargetTemp",
            type: "boolean", 
            role: "switch.enable",
            desc: "Automatisches nachführen der Zieltemperatur aktiv/inaktiv",
            def: true
        });
    }
    
    objectId = BASE_ADAPTER + "." + BASE_FOLDER + ".scriptRunning";
    if (!existsState(objectId)) {
        createState(objectId, {
            read: true, 
            write: true, 
            name: "scriptRunning",
            type: "boolean", 
            role: "switch",
            desc: "Ein Python Script läuft gerade",
            def: false
        });
    }

    // remove DP because no longer needed (energiefluss adapter 3.5.x now supports kW to W conversion)
    objectId = BASE_ADAPTER + "." + BASE_FOLDER + ".actualPowerConsumption";
    if (existsObject(objectId)) {
        deleteState(objectId);
    }
    
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
            console.log("*** leaving guid unchanged");
        }
    });

    // Variablen pro SpaController
    for (let nCurDev = 0; nCurDev < nDevCnt; nCurDev++) {
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev, {
            "type" : "device",
            "common" : {"name": "SpaController-" + nCurDev, "desc": "SpaController", "role": "SpaController"}
        });

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".ID";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "ID", 
                type: "string", 
                role: "info.address",
                desc: "Geräte ID",
                def: ""
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".U_ID";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "U_ID", 
                type: "string", 
                role: "info.address",
                desc: "Geräte U_ID",
                def: ""
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Name";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "Name", 
                type: "string", 
                role: "info",
                desc: "Name",
                def: ""
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }
        
        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Temperatureinheit";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "Temperatureinheit", 
                type: "string", 
                role: "info",
                desc: "Temperatureinheit",
                def: "°C"
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".AktuelleTemperatur";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "AktuelleTemperatur", 
                type: "number", 
                role: "value.temperature",
                desc: "Aktuelle Temperatur",
                def: -1
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }
        
        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".ZielTemperatur";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: true, 
                name: "ZielTemperatur", 
                type: "number", 
                role: "value.temperature",
                desc: "Zieltemperatur",
                def: 35,
                min: 15,
                max: 40
            });
        } else {
            // Korrektur Attribute
            objectData = getObject(objectId);
            objectData.common.def = 35;
            objectData.common.min = 15;
            objectData.common.max = 40;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".EchteZielTemperatur";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "EchteZielTemperatur", 
                type: "number", 
                role: "value.temperature",
                desc: "Echte Zieltemperatur",
                def: -1
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Heizer";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "Heizer", 
                type: "string", 
                role: "info.status",
                desc: "Aktivität Heizer",
                def: ""
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        // remove obsolete dp (use dp: WasserpflegeSwitch instead and use vis widget like basic - ValueList Text to display a text in the desired language)
        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Wasserpflege";
        if (existsObject(objectId)) {
            deleteState(objectId);
        }

        // remove obsolete dp (use dp: WasserpflegeSwitch instead)
        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".WasserpflegeIndex"
        if (existsObject(objectId)) {
            deleteState(objectId);
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".WasserpflegeModi";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: true, 
                name: "WasserpflegeModi", 
                type: "string", 
                role: "text",
                desc: "Auswählbare Wasserpflegemodi",
                def: ""
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".WasserpflegeSwitch";
        if (!existsState(objectId)) {
            createState(objectId, {
                read: true, 
                write: true, 
                name: "Wasserpflegemodusschalter",
                type: 'number',
                role: 'indicator',
                states: {
                    0: "Abwesend",
                    1: "Standard",
                    2: "Energiesparen",
                    3: "Energiesparen Plus",
                    4: "Wochenende"
                },
                desc: "Auswahl des aktiven Wasserpflegemodus",
                def: 0
            });
        } else {
            // Korrektur type Attribut
            objectData = getObject(objectId);
            objectData.common.type = "number";
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }
        
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
            
            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Name";
            if (!existsState(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Name", 
                    type: "string", 
                    role: "info.name",
                    desc: "Name der Pumpe",
                    def: ""
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Modus";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Modus", 
                    type: "string", 
                    role: "state",
                    desc: "Aktueller Modus",
                    def: ""
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.P" + nCurPump + ".Modi";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Modi", 
                    type: "string", 
                    role: "text",
                    desc: "Auswählbare Modi",
                    def: ""
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }
            
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

        // Wasserfall
        if (createWaterfall) {
            setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.Waterfall", {
                "type" : "channel",
                "common" : {"name": "Waterfall"}
            });
            
            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.Waterfall" + ".Name";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Name", 
                    type: "string", 
                    role: "info.name",
                    desc: "Name der Pumpe",
                    def: ""
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.Waterfall" + ".Modus";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Modus", 
                    type: "string", 
                    role: "state",
                    desc: "Aktueller Modus",
                    def: ""
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Pumpen.Waterfall" + ".Modi";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Modi", 
                    type: "string", 
                    role: "text",
                    desc: "Auswählbare Modi",
                    def: ""
                });
            }
            
            createState(BASE_FOLDER + "." + nCurDev + ".Pumpen.Waterfall" + ".Switch", {
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

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Name";
        if (!existsObject(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "Name", 
                type: "string", 
                role: "info.name",
                desc: "Name des Lichts",
                def: ""
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Is_On";
        if (!existsObject(objectId)) {
            createState(objectId, {
                read: true, 
                write: false, 
                name: "Is_On", 
                type: "boolean", 
                role: "state",
                desc: "Aktueller Status",
                def: false
            });
        } else {
            // Korrektur write Attribut
            objectData = getObject(objectId);
            objectData.common.write = false;
            objectData.common.def = false;
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Lichter.LI.Switch";
        if (!existsObject(objectId)) {
            createState(objectId, {
                read: true, 
                write: true, 
                name: "Switch", 
                type: "boolean", 
                role: "button",
                desc: "Lichtschalter",
                def: false
            });
        } else {
            // Korrektur role Attribut
            objectData = getObject(objectId);
            objectData.common.role = "button";
            setObject(objectId, objectData, function (err) {
                if (err) log('cannot write object: ' + err);
            });
        }

        // Sensoren: Boolean
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
            
            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Name", 
                    type: "string", 
                    role: "info.name",
                    desc: "Name des Sensors",
                    def: ""
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "State", 
                    type: "boolean", 
                    role: "state",
                    desc: "Sensorstatus",
                    def: false
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                objectData.common.def = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }
        }

        // Sensoren: String
        sSensors = ["CIRCULATING PUMP", "OZONE", "Last Ping", "Status", "SMART WINTER MODE:RISK"];
        for (let i = 0; i < sSensors.length; i++) {
            setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_"), {
                "type" : "channel",
                "common" : {"name": sSensors[i]}
            });

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Name", 
                    type: "string", 
                    role: "info.name",
                    desc: "Name des Sensors",
                    def: ""
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "State", 
                    type: "string", 
                    role: "state",
                    desc: "Sensorstatus",
                    def: ""
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }
        }

        // Sensoren: number
        sSensors = ["RF Channel"];
        for (let i = 0; i < sSensors.length; i++) {
            setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_"), {
                "type" : "channel",
                "common" : {"name": sSensors[i]}
            });

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Name", 
                    type: "string", 
                    role: "info.name",
                    desc: "Name des Sensors",
                    def: ""
                });
            } else {
                // Korrektur write Attribut & type
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "State", 
                    type: "number", 
                    role: "state",
                    desc: "Sensorstatus"
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                objectData.common.type = "number";
                objectData.common.def = -1;                
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }
        }

        // Sensoren: percent
        sSensors = ["RF Signal"];
        for (let i = 0; i < sSensors.length; i++) {
            setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_"), {
                "type" : "channel",
                "common" : {"name": sSensors[i]}
            });

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".Name";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "Name", 
                    type: "string", 
                    role: "info.name",
                    desc: "Name des Sensors",
                    def: ""
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }

            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Sensoren." + sSensors[i].replace(/ /g, "_").replace(/:/g, "_") + ".State";
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: "State", 
                    type: "number", 
                    role: "level",
                    unit: "%",
                    desc: "Sensorstatus",
                    def: 0
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.write = false;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }
        }

        // remove previuosly created buttons for functions
        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".enableHeating";
        if (existsObject(objectId)) {
            deleteState(objectId);
        }
        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".disableHeating";
        if (existsObject(objectId)) {
            deleteState(objectId);
        }

        // Reminder
        setObject(BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Erinnerungen", {
            "type" : "channel",
            "common" : {"name": "Erinnerungen"}
        });

        // Reminder: string - löschen wir nicht mehr benötigt
        objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Erinnerungen.Time";
        if (existsObject(objectId)) {
            deleteState(objectId);
        }
        // Reminder: number
        var sReminders = ["RinseFilter", "CleanFilter", "ChangeWater", "CheckSpa"];
        var sReminderDesc = ["Filter spülen", "Filter reinigen", "Wasser wechseln", "Spa prüfen"];
        for (let i = 0; i < sReminders.length; i++) {
            objectId = BASE_ADAPTER + "." + BASE_FOLDER + "." + nCurDev + ".Erinnerungen." + sReminders[i].replace(/ /g, "_").replace(/:/g, "_");
            if (!existsObject(objectId)) {
                createState(objectId, {
                    read: true, 
                    write: false, 
                    name: sReminders[i].replace(/ /g, "_").replace(/:/g, "_"), 
                    type: "number", 
                    role: "info",
                    desc: sReminderDesc[i], 
                    def: 0
                });
            } else {
                // Korrektur write Attribut
                objectData = getObject(objectId);
                objectData.common.type = "number";
                objectData.common.name = sReminders[i].replace(/ /g, "_").replace(/:/g, "_");
                objectData.common.def = 0;
                setObject(objectId, objectData, function (err) {
                    if (err) log('cannot write object: ' + err);
                });
            }
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
