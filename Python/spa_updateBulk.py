import requests
import urllib.parse

from geckolib import GeckoLocator

CLIENT_ID = "<<any_guid>>"
lSpas = ["SPA68:aa:bb:cc:dd:ee"]
IOBROKER_BASE_URL = "http://<<iobroker_ip_address>>:8087/setBulk"

dictEn2De = {'Away From Home': 'Abwesend',
          'Standard': 'Standard', 
          'Energy Saving': 'Energiesparen',
          'Super Energy Saving': 'Energiesparen Plus',
          'Weekender': 'Wochenende'
}

def cutModeName(modeString):
    # correct mode string in case geckolib returns longer strings than in modes collection
    if modeString == "OFF":
        return "OFF"
    if modeString == "HIGH":
        return "HI"
    if modeString == "LOW":
        return "LO"
    return modeString

for nSpaNum in range(len(lSpas)):
    facade = GeckoLocator.find_spa(CLIENT_ID, lSpas[nSpaNum]).get_facade(False)
    print(f"Connecting to {facade.name} ", end="", flush=True)
    while not facade.is_connected:
        # Could also be `await asyncio.sleep(1)`
        facade.wait(1)
        print(".", end="", flush=True)
    print(" connected")

    # Do some things with the facade
    print(f"water heater: {facade.water_heater}")

    #
    sJson2Send = ""
    
    # Temperaturen
    print(f'sending temp and heater ops')
    # temp value must be within min/max temp +/-10 degrees
    if float(facade.water_heater.current_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.current_temperature) < (float(facade.water_heater.max_temp) + 10):
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.AktuelleTemperatur={}".format(nSpaNum, round(facade.water_heater.current_temperature, 2)) + "&ack=true& "
    if float(facade.water_heater.target_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.target_temperature) < (float(facade.water_heater.max_temp) + 10):
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.ZielTemperatur={}".format(nSpaNum, round(facade.water_heater.target_temperature, 2)) + "&ack=true& "
    if float(facade.water_heater.real_target_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.real_target_temperature) < (float(facade.water_heater.max_temp) + 10):
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.EchteZielTemperatur={}".format(nSpaNum, round(facade.water_heater.real_target_temperature, 2)) + "&ack=true& "
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Heizer={}".format(nSpaNum, facade.water_heater.current_operation) + "&ack=true& "
    
    # Wasserprflege
    print('sending water care')
    watercaremodes = list()
    try:
        for index, item in enumerate(facade.water_care.modes):
            facade.water_care.modes[index] = dictEn2De[item]
    except:
        print(".")
    if facade.water_care.mode != None:
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Wasserpflege={}".format(nSpaNum, facade.water_care.modes[facade.water_care.mode]) + "&ack=true& "
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.WasserpflegeModi={}".format(nSpaNum, facade.water_care.modes) + "&ack=true& "
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.WasserpflegeIndex={}".format(nSpaNum, facade.water_care.mode) + "&ack=true& "
    
    # Pumpen
    print('sending pumps')
    for pump in facade.pumps:
        print(f"{pump.name}: {pump.mode}, {pump.modes}")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Pumpen.{}.Modus={}".format(nSpaNum, pump.key, pump.mode) + "&ack=true& "
        # new pump state name
        SET_PUMP_STATE_NAME = cutModeName(pump.mode)
        # new pump state id
        for x in range(len(pump.modes)):
            if SET_PUMP_STATE_NAME == pump.modes[x]:
                SET_PUMP_STATE = x
                break
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Pumpen.{}.Switch={}".format(nSpaNum, pump.key, SET_PUMP_STATE) + "&ack=true& "
    
    # Lichter
    print('sending lights')
    for light in facade.lights:
        print(f"{light.name}")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Lichter.{}.Is_On={}".format(nSpaNum, light.key, str(light.is_on).lower()) + "&ack=true& "
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Lichter.{}.Switch={}".format(nSpaNum, light.key, str(light.is_on).lower()) + "&ack=true& "
    
    # Sensoren
    print('sending sensors')
    for binary_sensor in facade.binary_sensors:
        print(f"{binary_sensor.name}")
        sKey = binary_sensor.key
        sKey = sKey.replace(" ", "_")
        sKey = sKey.replace(":", "_")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Sensoren.{}.State={}".format(nSpaNum, sKey, urllib.parse.quote((str(binary_sensor.state)).lower())) + "&ack=true& "
    

    sJson2Send = sJson2Send[:len(sJson2Send)-2] + ""
    print(sJson2Send)
    try:
        oResponse = requests.post(IOBROKER_BASE_URL, data = sJson2Send)
    except Exception as e:
        print(e)
        print("an error occured on sending an http request to ioBroker Rest API, no data was sent, check url")
    else:
        print(f"http response code: {oResponse.status_code}")
        if oResponse.status_code != 200:
            print("respose text:")
            print(oResponse.text)
