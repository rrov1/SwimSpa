import sys
import asyncio
import requests
import urllib.parse
import logging
import signal

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

VERSION = "0.2.1"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 5:
    print("*** Wrong number of script arguments.\n")
    print(f"*** call example: {sys.argv[0]} clientId ioBrSimpleRestApiUrl spaIds dpBasePath")
    quit(-1)

print("total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connect using client id: {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
spaIds = sys.argv[3]
if (spaIds.find(",") >= 0):
    SPA_ID = spaIds.split(",")
    print(f"Connecting to spa ids {spaIds}")
else:
    SPA_ID = [spaIds]
    print(f"Connecting to spa id {spaIds}")
IOB_DP_BASE_PATH = sys.argv[4]
print(f"Base path to datapoints: {IOB_DP_BASE_PATH}")

dictEn2De = {'Away From Home': 'Abwesend',
          'Standard': 'Standard', 
          'Energy Saving': 'Energiesparen',
          'Super Energy Saving': 'Energiesparen Plus',
          'Weekender': 'Wochenende'
}

def set_run_timeout(timeout):
    """Set maximum execution time of the current Python process"""
    def alarm(*_):
        raise SystemExit("Timed out!")
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(timeout)

def cutModeName(modeString):
    # correct mode string in case geckolib returns longer strings than in modes collection
    if modeString == "OFF":
        return "OFF"
    if modeString == "HIGH":
        return "HI"
    if modeString == "LOW":
        return "LO"
    return modeString

class SampleSpaMan(GeckoAsyncSpaMan):
    """Sample spa man implementation"""

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        #print(f"{event}: {kwargs}")
        pass

async def main() -> None:
    sJson2Send = ""
    set_run_timeout(90)

    for nSpaNum in range(len(SPA_ID)):
        spa = SPA_ID[nSpaNum]
        async with SampleSpaMan(CLIENT_ID, spa_identifier=spa) as spaman:
            print(f"*** {nSpaNum}: connecting to {spa}")
            # Wait for descriptors to be available
            await spaman.wait_for_descriptors()

            if len(spaman.spa_descriptors) == 0:
                print("*** there were no spas found on your network.")
                quit(-1)

            await spaman.async_connect(spa_identifier=spa)

            # Wait for the facade to be ready
            await spaman.wait_for_facade()
            print("*** connected")

            facade = spaman.facade
            
            # Temperaturen
            print(f'sending temp and heater ops')
            print(f'Heizung vorhanden {facade.water_heater.is_present}')
            # temp value must be within min/max temp +/-10 degrees
            if float(facade.water_heater.current_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.current_temperature) < (float(facade.water_heater.max_temp) + 10):
                sJson2Send = sJson2Send + "{}.{}.AktuelleTemperatur={}".format(IOB_DP_BASE_PATH, nSpaNum, round(facade.water_heater.current_temperature, 2)) + "&ack=true& "
            if float(facade.water_heater.target_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.target_temperature) < (float(facade.water_heater.max_temp) + 10):
                sJson2Send = sJson2Send + "{}.{}.ZielTemperatur={}".format(IOB_DP_BASE_PATH, nSpaNum, round(facade.water_heater.target_temperature, 2)) + "&ack=true& "
            if float(facade.water_heater.real_target_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.real_target_temperature) < (float(facade.water_heater.max_temp) + 10):
                sJson2Send = sJson2Send + "{}.{}.EchteZielTemperatur={}".format(IOB_DP_BASE_PATH, nSpaNum, round(facade.water_heater.real_target_temperature, 2)) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Heizer={}".format(IOB_DP_BASE_PATH, nSpaNum, facade.water_heater.current_operation) + "&ack=true& "

            # Wasserprflege
            print('sending water care')
            try:
                for index, item in enumerate(facade.water_care.modes):
                    facade.water_care.modes[index] = dictEn2De[item]
            except:
                print(".")
            if facade.water_care.mode != None:
                sJson2Send = sJson2Send + "{}.{}.Wasserpflege={}".format(IOB_DP_BASE_PATH, nSpaNum, facade.water_care.modes[facade.water_care.mode]) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.{}.WasserpflegeIndex={}".format(IOB_DP_BASE_PATH, nSpaNum, facade.water_care.mode) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.{}.WasserpflegeSwitch={}".format(IOB_DP_BASE_PATH, nSpaNum, facade.water_care.mode) + "&ack=true& "
            
            # Pumpen
            print('sending pumps')
            for pump in facade.pumps:
                print(f"{pump.name}: {pump.mode}, {pump.modes}")
                sJson2Send = sJson2Send + "{}.{}.Pumpen.{}.Modus={}".format(IOB_DP_BASE_PATH, nSpaNum, pump.key, pump.mode) + "&ack=true& "
                # new pump state name
                SET_PUMP_STATE_NAME = cutModeName(pump.mode)
                # new pump state id
                for x in range(len(pump.modes)):
                    if SET_PUMP_STATE_NAME == pump.modes[x]:
                        SET_PUMP_STATE = x
                        break
                sJson2Send = sJson2Send + "{}.{}.Pumpen.{}.Switch={}".format(IOB_DP_BASE_PATH, nSpaNum, pump.key, SET_PUMP_STATE) + "&ack=true& "
            
            # Lichter
            print('sending lights')
            for light in facade.lights:
                print(f"{light.name}")
                sJson2Send = sJson2Send + "{}.{}.Lichter.{}.Is_On={}".format(IOB_DP_BASE_PATH, nSpaNum, light.key, str(light.is_on).lower()) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.{}.Lichter.{}.Switch={}".format(IOB_DP_BASE_PATH, nSpaNum, light.key, str(light.is_on).lower()) + "&ack=true& "
            
            # Sensoren
            print('sending sensors')
            for binary_sensor in facade.binary_sensors:
                print(f"{binary_sensor.name}")
                sKey = binary_sensor.key
                sKey = sKey.replace(" ", "_")
                sKey = sKey.replace(":", "_")
                sJson2Send = sJson2Send + "{}.{}.Sensoren.{}.State={}".format(IOB_DP_BASE_PATH, nSpaNum, sKey, urllib.parse.quote((str(binary_sensor.state)).lower())) + "&ack=true& "

    sJson2Send = sJson2Send[:len(sJson2Send)-2] + ""
    print(sJson2Send)
    try:
        oResponse = requests.post("{}/setBulk".format(IOBRURL), data = sJson2Send)
    except Exception as e:
        print(e)
        print("an error occured on sending an http request to ioBroker Rest API, no data was sent, check url")
    else:
        print(f"http response code: {oResponse.status_code}")
        if oResponse.status_code != 200:
            print("respose text:")
            print(oResponse.text)

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
