import sys
import asyncio
import logging
import requests
import signal

dictEn2De = {'Away From Home': 'Abwesend',
          'Standard': 'Standard', 
          'Energy Saving': 'Energiesparen',
          'Super Energy Saving': 'Energiesparen Plus',
          'Weekender': 'Wochenende'
}

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

VERSION = "0.2.2"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 6:
    print("*** Wrong number of script arguments.")
    print("*** call example: {sys.argv[0]} clientId restApiUrl spaId waterCareModeIdx devicePath")
    quit(-1)

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

print("Total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connecting using client id {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
SPA_ID = sys.argv[3]
print(f"Connecting to spa id {SPA_ID}")
NEW_WATERCAREMODE_IDX = sys.argv[4]
if (not is_integer(NEW_WATERCAREMODE_IDX)):
    print(f"error: value {NEW_WATERCAREMODE_IDX} of argument 3 is not an int")
    quit(-1)
NEW_WATERCAREMODE_IDX = int(NEW_WATERCAREMODE_IDX)
if (NEW_WATERCAREMODE_IDX < 0 and NEW_WATERCAREMODE_IDX > 4):
    print(f"error: value {NEW_WATERCAREMODE_IDX} is out of allowed range")
    quit(-1)
print(f"New watercare mode index: {NEW_WATERCAREMODE_IDX}")
IOBR_DEVICE_PATH = sys.argv[5]
print(f"Got device path to update: {IOBR_DEVICE_PATH}")

def set_run_timeout(timeout):
    """Set maximum execution time of the current Python process"""
    def alarm(*_):
        raise SystemExit("Timed out: Maximum script runtime reached.")
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(timeout)

class SampleSpaMan(GeckoAsyncSpaMan):
    """Sample spa man implementation"""

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        # print(f"{event}: {kwargs}")
        pass

async def main() -> None:
    set_run_timeout(30)

    async with SampleSpaMan(CLIENT_ID, spa_identifier=SPA_ID) as spaman:
        print(f"*** connecting to {SPA_ID}")

        #connect
        await spaman.async_connect(spa_identifier=SPA_ID)

        # Wait for the facade to be ready
        result = await spaman.wait_for_facade()

        # get current watercare mode
        # currentWatercareMode = spaman.facade.water_care.active_mode
        currentWatercareMode = await spaman.facade.spa.async_get_watercare()
        print(f"current watercare mode: {currentWatercareMode}")
        
        print(f"*** connect result-> {result}")
        sJson2Send = ""
        if result == True:
            if currentWatercareMode == NEW_WATERCAREMODE_IDX:
                print(f"*** nothing to do, old and new watercare mode are equal")
                # sending state updates to ioBroker
                sJson2Send = sJson2Send + "{}.WasserpflegeSwitch={}".format(IOBR_DEVICE_PATH, currentWatercareMode) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.WasserpflegeIndex={}".format(IOBR_DEVICE_PATH, currentWatercareMode) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.Wasserpflege={}".format(IOBR_DEVICE_PATH, dictEn2De[spaman.facade.water_care.modes[currentWatercareMode]]) + "&ack=true& "
            else:
                print(f"*** changing watercare mode from \"{spaman.facade.water_care.modes[currentWatercareMode]}\" to: \"{spaman.facade.water_care.modes[NEW_WATERCAREMODE_IDX]}\"")

                # set water care mode
                await spaman.facade.water_care.async_set_mode(spaman.facade.water_care.modes[NEW_WATERCAREMODE_IDX])
            
                # sending state updates to ioBroker
                sJson2Send = sJson2Send + "{}.WasserpflegeSwitch={}".format(IOBR_DEVICE_PATH, NEW_WATERCAREMODE_IDX) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.WasserpflegeIndex={}".format(IOBR_DEVICE_PATH, NEW_WATERCAREMODE_IDX) + "&ack=true& "
                sJson2Send = sJson2Send + "{}.Wasserpflege={}".format(IOBR_DEVICE_PATH, dictEn2De[spaman.facade.water_care.modes[NEW_WATERCAREMODE_IDX]]) + "&ack=true& "
            
            # kurz warten (löst das Problem mit den längeren Wartezeiten)
            await asyncio.sleep(1)
            
            # reset/close connection
            await spaman.async_reset()
            print("connection closed/reset")
        else:
            print(f"*** cannot establish connection to spa controller, spa_state: {spaman.spa_state}")
            print(f"status_sensor: {spaman.status_sensor.state}")
            print(f"radio_sensor: {spaman.radio_sensor.state}")
            print(f"channel_sensor: {spaman.channel_sensor.state}")
            print(f"ping_sensor: {spaman.ping_sensor.state}")
            # some sensors
            sJson2Send = sJson2Send + "{}.{}.Sensoren.RF_Signal.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.radio_sensor.state))) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Sensoren.RF_Channel.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.channel_sensor.state))) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Sensoren.Last_Ping.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.ping_sensor.state))) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.{}.Sensoren.Status.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.status_sensor.state)) + "&ack=true& "
        
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
