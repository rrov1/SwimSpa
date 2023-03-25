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
    print("*** call example: {sys.argv[0]} clientId spaId restApiUrl lightKey lightChannel")
    quit(-1)

print("Total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connecting using client id {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
SPA_ID = sys.argv[3]
print(f"Connecting to spa id {SPA_ID}")
LIGHT_KEY = sys.argv[4]
print(f"Switching light: {LIGHT_KEY}")
IOBR_LIGHT_CHANNEL = sys.argv[5]
print(f"Got channel for update: {IOBR_LIGHT_CHANNEL}")

class SampleSpaMan(GeckoAsyncSpaMan):
    """Sample spa man implementation"""

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        # print(f"{event}: {kwargs}")
        pass

async def main() -> None:

    async with SampleSpaMan(CLIENT_ID, spa_identifier=SPA_ID) as spaman:
        print("Looking for spas on your network ...")

        # Wait for descriptors to be available
        await spaman.wait_for_descriptors()

        if len(spaman.spa_descriptors) == 0:
            print("*** there were no spas found on your network.")
            quit(-1)

        print("*** connecting to spa")
        await spaman.async_connect(spa_identifier=SPA_ID)

        # Wait for the facade to be ready
        await spaman.wait_for_facade()

        if len(spaman.facade.lights) > 0:
            print(f"*** light count: {len(spaman.facade.lights)}")
        else:
            print(f"*** current light mode: {spaman.facade.lights[0].is_on}")
            print(f"error: no pumps returned from geckolib")
            quit(-1)

        # search for light based on key
        keyNotFound = True
        for light in spaman.facade.lights:
            if LIGHT_KEY == light.key:
                print(f"*** found light with key {LIGHT_KEY} and name: {light.name} with state {light.is_on}")
                keyNotFound = False
                if light.is_on:
                    print(f"*** switching light off")
                    await spaman.facade.lights[0].async_turn_off()
                else:
                    print(f"*** switching light on")
                    await spaman.facade.lights[0].async_turn_on()
                await asyncio.sleep(1)
                newLightMode = light.is_on
                break
        
        if keyNotFound:
            print(f"error: light with key: {LIGHT_KEY} not found")
            quit(-1)
        
        print(f"*** light mode is now: {newLightMode}")

        #
        sJson2Send = ""

        # sending state updates to ioBroker
        sJson2Send = sJson2Send + "{}.Switch={}".format(IOBR_LIGHT_CHANNEL, str(newLightMode).lower()) + "&ack=true& "
        sJson2Send = sJson2Send + "{}.Is_On={}".format(IOBR_LIGHT_CHANNEL, str(newLightMode).lower()) + "&ack=true& "

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
