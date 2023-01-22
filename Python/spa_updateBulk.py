import requests
import urllib.parse

from geckolib import GeckoLocator

CLIENT_ID = "<<any_guid>>"
lSpas = ["SPA68:aa:bb:cc:dd:ee"]
IOBROKER_BASE_URL = "http://<iobroker_ip_address>>:8087/setBulk"

dictEn2De = {'Away From Home': 'Abwesend',
          'Standard': 'Standard', 
          'Energy Saving': 'Energiesparen',
          'Super Energy Saving': 'Energiesparen Plus',
          'Weekender': 'Wochenende'
}

for nSpaNum in range(len(lSpas)):
    facade = GeckoLocator.find_spa(CLIENT_ID, lSpas[nSpaNum]).get_facade(False)
    print(f"Connecting to {facade.name} ", end="", flush=True)
    while not facade.is_connected:
        # Could also be `await asyncio.sleep(1)`
        facade.wait(1)
        print(".", end="", flush=True)
    print(" connected")

    # Do some things with the facade
    print(f"Water heater : {facade.water_heater}")

    #
    sJson2Send = ""
    #sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}={}".format(, ) + "& "
    
    # Temperaturen
    print(f'sending temp and heater ops')
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Temperatureinheit={}".format(nSpaNum, urllib.parse.quote(facade.water_heater.temperature_unit)) + "& "
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.AktuelleTemperatur={}".format(nSpaNum, round(facade.water_heater.current_temperature, 2)) + "& "
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.ZielTemperatur={}".format(nSpaNum, round(facade.water_heater.target_temperature, 2)) + "& "
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.EchteZielTemperatur={}".format(nSpaNum, round(facade.water_heater.real_target_temperature, 2)) + "& "
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Heizer={}".format(nSpaNum, facade.water_heater.current_operation) + "& "
    
    # Wasserprflege
    print('sending water care')
    watercaremodes = list()
    try:
        for index, item in enumerate(facade.water_care.modes):
            facade.water_care.modes[index] = dictEn2De[item]
    except:
        print(".")
    if facade.water_care.mode != None:
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Wasserpflege={}".format(nSpaNum, facade.water_care.modes[facade.water_care.mode]) + "& "
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.WasserpflegeModi={}".format(nSpaNum, facade.water_care.modes) + "& "
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.WasserpflegeIndex={}".format(nSpaNum, facade.water_care.mode) + "& "
    
    # Pumpen
    print('sending pumps')
    for pump in facade.pumps:
        print(f"{pump.name}")
        if (pump.name != "Waterfall"):
            sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Pumpen.{}.Modus={}".format(nSpaNum, pump.key, pump.mode) + "& "
    
    # Lichter
    print('sending lights')
    for light in facade.lights:
        print(f"{light.name}")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Lichter.{}.Is_On={}".format(nSpaNum, light.key, str(light.is_on).lower()) + "& "
    
    # Sensoren
    print('sending sensors')
    for binary_sensor in facade.binary_sensors:
        print(f"{binary_sensor.name}")
        sKey = binary_sensor.key
        sKey = sKey.replace(" ", "_")
        sKey = sKey.replace(":", "_")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Sensoren.{}.State={}".format(nSpaNum, sKey, urllib.parse.quote((str(binary_sensor.state)).lower())) + "& "
    

    sJson2Send = sJson2Send[:len(sJson2Send)-2] + ""
    print(sJson2Send)
    oResponse = requests.post(IOBROKER_BASE_URL, data = sJson2Send)
    print(oResponse.status_code)
    #print(oResponse.text)
