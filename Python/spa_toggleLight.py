import sys
import asyncio
import logging
import requests
import signal

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

VERSION = "0.2.4"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 7:
    print("*** Wrong number of script arguments.", file=sys.stderr)
    print("*** call example: {sys.argv[0]} clientId restApiUrl spaId spaIP lightKey lightChannel", file=sys.stderr)
    quit(-1)

print("Total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connecting using client id {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
SPA_ID = sys.argv[3]
print(f"Connecting to spa id {SPA_ID}")
SPA_IP = sys.argv[4]
print(f"Connecting to spa ip {SPA_IP}")
LIGHT_KEY = sys.argv[5]
print(f"Switching light: {LIGHT_KEY}")
IOBR_LIGHT_CHANNEL = sys.argv[6]
print(f"Got channel for update: {IOBR_LIGHT_CHANNEL}")

def set_run_timeout(timeout):
    """Set maximum execution time of the current Python process"""
    def alarm(*_):
        raise SystemExit("Timed out: Maximum script runtime reached.")
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(timeout)

class SampleSpaMan(GeckoAsyncSpaMan):
    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        # print(f"{event}: {kwargs}")
        pass

async def main() -> None:
    set_run_timeout(30)

    async with SampleSpaMan(CLIENT_ID, spa_identifier=SPA_ID, spa_address=SPA_IP) as spaman:
        print(f"*** connecting to {SPA_ID} with ip {SPA_IP}")

        #connect
        await spaman.async_connect(spa_identifier=SPA_ID, spa_address=SPA_IP)

        # Wait for the facade to be ready
        result = await spaman.wait_for_facade()

        print(f"*** connect result-> {result}")
        if result == True:
            if len(spaman.facade.lights) > 0:
                print(f"*** light count: {len(spaman.facade.lights)}")
            else:
                print(f"*** current light mode: {spaman.facade.lights[0].is_on}")
                print(f"error: no lights returned from geckolib", file=sys.stderr)
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
                print(f"error: light with key: {LIGHT_KEY} not found", file=sys.stderr)
                quit(-1)
            
            print(f"*** light mode is now: {newLightMode}")

            #
            sJson2Send = ""

            # sending state updates to ioBroker
            sJson2Send = sJson2Send + "{}.Switch={}".format(IOBR_LIGHT_CHANNEL, str(newLightMode).lower()) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.Is_On={}".format(IOBR_LIGHT_CHANNEL, str(newLightMode).lower()) + "&ack=true& "

            # kurz warten (löst das Problem mit den längeren Wartezeiten)
            await asyncio.sleep(1)
            
            # reset/close connection
            await spaman.async_reset()
            print("connection closed/reset")
        else:
            print(f"*** cannot establish connection to spa controller, spa_state: {spaman.spa_state}", file=sys.stderr)
        
        sJson2Send = sJson2Send[:len(sJson2Send)-2] + ""
        #print(sJson2Send)
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
