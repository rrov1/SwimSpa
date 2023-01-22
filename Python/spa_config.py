import requests
import urllib.parse

from geckolib import GeckoLocator

CLIENT_ID = "<<any_guid>>"
lSpas = ["SPA68:aa:bb:cc:dd:ee"]
IOBROKER_BASE_URL = "http://<iobroker_ip_address>>:8087/set/"

for nSpaNum in range(len(lSpas)):
    facade = GeckoLocator.find_spa(CLIENT_ID, lSpas[nSpaNum]).get_facade(False)
    print(f"Connecting to {facade.name} ", end="", flush=True)
    while not facade.is_connected:
        # Could also be `await asyncio.sleep(1)`
        facade.wait(1)
        print(".", end="", flush=True)
    print(" connected")

    # Do some things with the facade
    # name and id
    print(f"identifier {facade.name}")
    requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.Name?value={urllib.parse.quote(facade.name)}")
    print(f"identifier {facade.identifier}")
    requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.ID?value={urllib.parse.quote(facade.identifier)}")
    print(f"uid: {facade.unique_id}")
    requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.U_ID?value={urllib.parse.quote(facade.unique_id)}")
    #
    print(f'Temperatureinheit {facade.water_heater.temperature_unit}')
    requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.Temperatureinheit?value={urllib.parse.quote(facade.water_heater.temperature_unit)}")
    #
    print(f"anzahl pumpen: {len(facade.pumps)}")
    for pump in facade.pumps:
        print(f"{pump.key}")
        print(f"{pump.name}")
        requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.Pumpen.{pump.key}.Name?value={urllib.parse.quote(pump.name)}")
        print(f"{pump.modes}")
        requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.Pumpen.{pump.key}.Modi?value={pump.modes}")
    #
    print(f"anzahl blowers: {len(facade.blowers)}")
    #
    print(f"anzahl lichter: {len(facade.lights)}")
    for light in facade.lights:
        print(f"{light.key}")
        print(f"{light.name}")
        requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.Lichter.{light.key}.Name?value={urllib.parse.quote(light.name)}")
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
        requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.Sensoren.{sKey}.Name?value={urllib.parse.quote(binary_sensor.name)}")
    
    print(f"anzahl user devices: {len(facade.all_user_devices)}")
    # user_device brauchen wir nicht
    #for user_device in facade.all_user_devices:
    #    print(f"user device: {user_device}")
    print(f"anzahl reminders: {len(facade.reminders)}")
    for reminder in facade.reminders:
        print(f"reminder: {reminder}")
        requests.get(f"{IOBROKER_BASE_URL}javascript.0.Datenpunkte.SwimSpa.{nSpaNum}.Erinnerungen.{reminder[0]}?value={urllib.parse.quote(str(reminder[1]))}")
    