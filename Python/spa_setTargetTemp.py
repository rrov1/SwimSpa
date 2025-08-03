import sys
import asyncio
import logging
import requests
import signal

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

VERSION = "0.3.0"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 7:
    print("*** Wrong number of script arguments.", file=sys.stderr)
    print("*** call example: {sys.argv[0]} clientId restApiUrl spaId spaIP targetTemp targetTempDatapoint", file=sys.stderr)
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
SPA_IP = sys.argv[4]
print(f"Connecting to spa ip {SPA_IP}")
TARGET_TEMP = sys.argv[5]
if (not is_float(TARGET_TEMP)):
    print(f"error: argument {TARGET_TEMP} is not a float")
    quit(-1)
print(f"New target temp: {TARGET_TEMP}")
IOBR_TARGET_TEMP_DP = sys.argv[6]
print(f"Got datapoint to update: {IOBR_TARGET_TEMP_DP}")

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
        sJson2Send = ""
        if result == True:
            if spaman.facade.water_heater.is_available:
                print(f"*** water heater available")
            else:
                print(f"error: no water heater available returned from geckolib", file=sys.stderr)
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
            
            # sending state updates to ioBroker
            sJson2Send = sJson2Send + "{}={}".format(IOBR_TARGET_TEMP_DP, str(spaman.facade.water_heater.target_temperature)) + "&ack=true& "
            
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

