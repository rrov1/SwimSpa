import requests
import urllib.parse

from geckolib import GeckoLocator

CLIENT_ID = "<<any_guid>>"
lSpas = ["SPA68:aa:bb:cc:dd:ee"]
IOBROKER_BASE_URL = "http://<iobroker_ip_address>>:8087/setBulk"

for nSpaNum in range(len(lSpas)):
    facade = GeckoLocator.find_spa(CLIENT_ID, lSpas[nSpaNum]).get_facade(False)
    print(f"Connecting to {facade.name} ", end="", flush=True)
    while not facade.is_connected:
        # Could also be `await asyncio.sleep(1)`
        facade.wait(1)
        print(".", end="", flush=True)
    print(" connected")

    #
    sJson2Send = ""

    # name and id
    print(f"identifier {facade.name}")
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Name={}".format(nSpaNum, urllib.parse.quote(facade.name)) + "&ack=true& "
    print(f"identifier {facade.identifier}")
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.ID={}".format(nSpaNum, urllib.parse.quote(facade.identifier)) + "&ack=true& "
    print(f"uid: {facade.unique_id}")
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.U_ID={}".format(nSpaNum, urllib.parse.quote(facade.unique_id)) + "&ack=true& "
    #
    print(f'Temperatureinheit {facade.water_heater.temperature_unit}')
    sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Temperatureinheit={}".format(nSpaNum, urllib.parse.quote(facade.water_heater.temperature_unit)) + "&ack=true& "
    #
    print(f"anzahl pumpen: {len(facade.pumps)}")
    for pump in facade.pumps:
        print(f"{pump.key}")
        print(f"{pump.name}")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Pumpen.{}.Name={}".format(nSpaNum, pump.key, urllib.parse.quote(pump.name)) + "&ack=true& "
        print(f"{str(pump.modes)}")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Pumpen.{}.Modi={}".format(nSpaNum, pump.key, urllib.parse.quote(str(pump.modes))) + "&ack=true& "
    #
    print(f"anzahl blowers: {len(facade.blowers)}")
    #
    print(f"anzahl lichter: {len(facade.lights)}")
    for light in facade.lights:
        print(f"{light.key}")
        print(f"{light.name}")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Lichter.{}.Name'={}".format(nSpaNum, light.key, urllib.parse.quote(light.name)) + "&ack=true& "
    #
    print(f"***anzahl Sensoren: {len(facade.sensors)}")
    for sensor in facade.sensors:
        print(f"{sensor.key}")
        print(f"{sensor.name}")
        print(f"{sensor.state}")
    
    print(f"***anzahl bin. Sensoren: {len(facade.binary_sensors)}")
    for binary_sensor in facade.binary_sensors:
        print(f"{binary_sensor.key}")
        print(f"{binary_sensor.name}")
        sKey = binary_sensor.key
        sKey = sKey.replace(" ", "_")
        sKey = sKey.replace(":", "_")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Sensoren.{}.Name={}".format(nSpaNum, sKey, urllib.parse.quote(binary_sensor.name)) + "&ack=true& "
    
    print(f"anzahl user devices: {len(facade.all_user_devices)}")
    # user_device brauchen wir nicht, Information doppelt
    #for user_device in facade.all_user_devices:
    #    print(f"user device: {user_device}")
    
    print(f"anzahl reminders: {len(facade.reminders)}")
    for reminder in facade.reminders:
        print(f"reminder: {reminder}")
        sJson2Send = sJson2Send + "javascript.0.Datenpunkte.SwimSpa.{}.Erinnerungen.{}={}".format(nSpaNum, reminder[0], urllib.parse.quote(str(reminder[1]))) + "&ack=true& "
    
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
