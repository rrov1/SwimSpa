import sys
import asyncio
import logging
import requests

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

VERSION = "0.2.0"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 6:
    print("*** Wrong number of script arguments.")
    print("*** call example: {sys.argv[0]} clientId restApiUrl spaId targetTemp targetTempDatapoint")
    quit(-1)

def is_float(element: any) -> bool:
    #If you expect None to be passed:
    if element is None: 
        return False
    try:
        float(element)
        return True
    except ValueError:
        return False

print("Total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connecting using client id {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
SPA_ID = sys.argv[3]
print(f"Connecting to spa id {SPA_ID}")
TARGET_TEMP = sys.argv[4]
if (not is_float(TARGET_TEMP)):
    print(f"error: argument {TARGET_TEMP} is not a float")
    quit(-1)
print(f"New target temp: {TARGET_TEMP}")
IOBR_TARGET_TEMP_DP = sys.argv[5]
print(f"Got datapoint to update: {IOBR_TARGET_TEMP_DP}")

class SampleSpaMan(GeckoAsyncSpaMan):
    """Sample spa man implementation"""

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        # print(f"{event}: {kwargs}")
        pass

async def main() -> None:

    async with SampleSpaMan(CLIENT_ID, spa_identifier=SPA_ID) as spaman:
        print(f"*** connecting to spa")
        # Wait for descriptors to be available
        await spaman.wait_for_descriptors()

        if len(spaman.spa_descriptors) == 0:
            print("*** there were no spas found on your network.")
            quit(-1)

        print("*** connecting to spa")
        await spaman.async_connect(spa_identifier=SPA_ID)

        # Wait for the facade to be ready
        await spaman.wait_for_facade()

        if spaman.facade.water_heater.is_present:
            print(f"*** water heater present")
        else:
            print(f"error: no water heater present returned from geckolib")
            quit(-1)
        
        print(f"*** current target temp: {spaman.facade.water_heater.target_temperature}")

        # check that new target temp is in temp range
        if float(TARGET_TEMP) < float(spaman.facade.water_heater.min_temp):
            print(f"error: new target temp ({TARGET_TEMP}) below minimum value ({spaman.facade.water_heater.min_temp})")
            quit(-1)
        if float(TARGET_TEMP) > float(spaman.facade.water_heater.max_temp):
            print(f"error: new target temp ({TARGET_TEMP}) above maximum value ({spaman.facade.water_heater.max_temp})")
            quit(-1)

        if float(spaman.facade.water_heater.target_temperature) != float(TARGET_TEMP):
            await spaman.facade.water_heater.async_set_target_temperature(TARGET_TEMP)
            await asyncio.sleep(1)
            print(f"*** target temp is now: {spaman.facade.water_heater.target_temperature}")
        else:
            print(f"*** new target temp is identical to current, nothing to do")
        
        #
        sJson2Send = ""

        # sending state updates to ioBroker
        sJson2Send = sJson2Send + "{}={}".format(IOBR_TARGET_TEMP_DP, str(spaman.facade.water_heater.target_temperature)) + "&ack=true& "

        sJson2Send = sJson2Send[:len(sJson2Send)-2] + ""
        #print(sJson2Send)
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

