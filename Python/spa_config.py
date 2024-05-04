import sys
import asyncio
import logging
import requests
import urllib
from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

VERSION = "0.2.4"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 4:
    print("*** Wrong number of script arguments.", file=sys.stderr)
    print(f"*** call example: {sys.argv[0]} clientId ioBrSimpleRestApiUrl dpBasePath ", file=sys.stderr)
    quit(-1)

print("total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connect using client id: {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
IOB_DP_BASE_PATH = sys.argv[3]
print(f"Base path to datapoints: {IOB_DP_BASE_PATH}")


class SampleSpaMan(GeckoAsyncSpaMan):
    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        #print(f"{event}: {kwargs}")
        pass


async def main() -> None:
    async with SampleSpaMan(CLIENT_ID) as spaman:
        print("*** looking for spas on your network ...")

        # Wait for descriptors to be available
        await spaman.wait_for_descriptors()

        if len(spaman.spa_descriptors) == 0:
            print("*** there were no spas found on your network.", file=sys.stderr)
            quit(-1)

        # get all spa names
        allNames = []
        for descriptor in spaman.spa_descriptors:
            allNames.append(descriptor.name)
        
        mySpaDescriptors = []
        # sort spa names and create a new spa descriptors array sorted by spa_name
        for myName in sorted(allNames):
            for descriptor in spaman.spa_descriptors:
                if descriptor.name == myName:
                    mySpaDescriptors.append(descriptor)

        for nSpaNum in range(len(mySpaDescriptors)):
            spa_descriptor = mySpaDescriptors[nSpaNum]
            print(f"connecting to {spa_descriptor.name} at {spa_descriptor.ipaddress} with {spa_descriptor.identifier_as_string}")

            await spaman.async_set_spa_info(
                spa_descriptor.ipaddress,
                spa_descriptor.identifier_as_string,
                spa_descriptor.name,
            )

            # Wait for the facade to be ready
            await spaman.wait_for_facade()

            #
            sJson2Send = ""

            print(f"spa_state {spaman.spa_state}")
            print(f"ip address: {spa_descriptor.ipaddress}")
            sJson2Send = sJson2Send + "{}.{}.IPAddresse={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spa_descriptor.ipaddress)) + "&ack=true& "

            # name and id
            print(f"identifier {spaman.facade.name}")
            sJson2Send = sJson2Send + "{}.{}.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.facade.name)) + "&ack=true& "
            print(f"identifier {spa_descriptor.identifier_as_string}")
            sJson2Send = sJson2Send + "{}.{}.ID={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spa_descriptor.identifier_as_string)) + "&ack=true& "
            print(f"uid: {spaman.facade.unique_id}")
            sJson2Send = sJson2Send + "{}.{}.U_ID={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.facade.unique_id)) + "&ack=true& "
            
            # some sensors
            print(f"radio_sensor: {spaman.radio_sensor}")
            sJson2Send = sJson2Send + "{}.{}.Sensoren.RF_Signal.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.radio_sensor.name)) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Sensoren.RF_Signal.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.radio_sensor.state))) + "&ack=true& "
            print(f"channel_sensor: {spaman.channel_sensor}")
            sJson2Send = sJson2Send + "{}.{}.Sensoren.RF_Channel.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.channel_sensor.name)) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Sensoren.RF_Channel.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.channel_sensor.state))) + "&ack=true& "
            print(f"ping_sensor: {spaman.ping_sensor}")
            sJson2Send = sJson2Send + "{}.{}.Sensoren.Last_Ping.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.ping_sensor.name)) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Sensoren.Last_Ping.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.ping_sensor.state))) + "&ack=true& "
            print(f"status_sensor: {spaman.status_sensor}")
            sJson2Send = sJson2Send + "{}.{}.Sensoren.Status.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.status_sensor.name)) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Sensoren.Status.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.status_sensor.state)) + "&ack=true& "
            
            #
            print(f'Heizung vorhanden {spaman.facade.water_heater.is_present}')
            print(f'Temperatureinheit {spaman.facade.water_heater.temperature_unit}')
            sJson2Send = sJson2Send + "{}.{}.Temperatureinheit={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.facade.water_heater.temperature_unit)) + "&ack=true& "
            #
            print(f"Wasserpflegemodi {spaman.facade.water_care.modes}")
            sJson2Send = sJson2Send + "{}.{}.WasserpflegeModi={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.facade.water_care.modes))) + "&ack=true& "

            #
            print(f"anzahl pumpen: {len(spaman.facade.pumps)}")
            for pump in spaman.facade.pumps:
                print(f"pump key {pump.key}, name {pump.name}, modes {str(pump.modes)}")
                sJson2Send = sJson2Send + "{}.{}.Pumpen.{}.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, pump.key, urllib.parse.quote(pump.name)) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.{}.Pumpen.{}.Modi={}".format(IOB_DP_BASE_PATH, nSpaNum, pump.key, urllib.parse.quote(str(pump.modes))) + "&ack=true& "
            #
            print(f"anzahl blowers: {len(spaman.facade.blowers)}")
            #
            print(f"anzahl lichter: {len(spaman.facade.lights)}")
            for light in spaman.facade.lights:
                print(f"light key {light.key}, name {light.name}")
                sJson2Send = sJson2Send + "{}.{}.Lichter.{}.Name'={}".format(IOB_DP_BASE_PATH, nSpaNum, light.key, urllib.parse.quote(light.name)) + "&ack=true& "
            #
            print(f"***anzahl Sensoren: {len(spaman.facade.sensors)}")
            for sensor in spaman.facade.sensors:
                print(f"sensor key {sensor.key}, name {sensor.name}, state {sensor.state}, unit_of_measurement {sensor.unit_of_measurement}")
                sKey = sensor.key
                sKey = sKey.replace(" ", "_")
                sKey = sKey.replace(":", "_")
                sJson2Send = sJson2Send + "{}.{}.Sensoren.{}.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, sKey, urllib.parse.quote(sensor.name)) + "&ack=true& "
            
            print(f"***anzahl bin. Sensoren: {len(spaman.facade.binary_sensors)}")
            for binary_sensor in spaman.facade.binary_sensors:
                print(f"sensor key {binary_sensor.key}, name {binary_sensor.name}, is_on {binary_sensor.is_on}")
                sKey = binary_sensor.key
                sKey = sKey.replace(" ", "_")
                sKey = sKey.replace(":", "_")
                sJson2Send = sJson2Send + "{}.{}.Sensoren.{}.Name={}".format(IOB_DP_BASE_PATH, nSpaNum, sKey, urllib.parse.quote(binary_sensor.name)) + "&ack=true& "
            
            rm = spaman.facade.reminders_manager
            print(f"anzahl reminders: {len(rm.reminders)}")
            # fixe Wartezeit, ansonsten sind keine Werte verfügbar
            await asyncio.sleep(4)
            print(f"anzahl reminders: {len(rm.reminders)}")
            for reminder in rm.reminders:
                #print(f"reminder: {reminder.description} - {str(reminder.days)}")
                sJson2Send = sJson2Send + "{}.{}.Erinnerungen.{}={}".format(IOB_DP_BASE_PATH, nSpaNum, reminder.description, urllib.parse.quote(str(reminder.days))) + "&ack=true& "

            print(f"error sensor state {spaman.facade.error_sensor.state}")

            sJson2Send = sJson2Send[:len(sJson2Send)-2] + ""
            print(sJson2Send)
            try:
                oResponse = requests.post("{}/setBulk".format(IOBRURL), data = sJson2Send)
            except Exception as e:
                print(e)
                print("an error occured on sending an http request to ioBroker Rest API, no data was sent, check url", file=sys.stderr)
            else:
                print(f"http response code: {oResponse.status_code}")
                if oResponse.status_code != 200:
                    print("respose text:")
                    print(oResponse.text)
            
            await asyncio.sleep(1)

        # ende
        print("*** end")
        return

if __name__ == "__main__":
    # Install logging
    stream_logger = logging.StreamHandler()
    stream_logger.setLevel(logging.DEBUG)
    stream_logger.setFormatter(
        logging.Formatter("%(asctime)s> %(levelname)s %(message)s")
    )
    logging.getLogger().addHandler(stream_logger)
    logging.getLogger().setLevel(logging.INFO)

    asyncio.run(main())
