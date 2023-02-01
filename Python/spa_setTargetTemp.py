import sys
import asyncio
import logging
import requests

IOBROKER_BASE_URL = "http://<<iobroker_ip_address>>:8087/set/"
from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

# Anzahl Argumente prüfen
if len(sys.argv) != 5:
    print("*** Wrong number of script arguments.")
    print("*** call example: {sys.argv[0]} clientId spaId targetTemp targetTempDatapoint")
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
SPA_ID = sys.argv[2]
print(f"Connecting to spa id {SPA_ID}")
TARGET_TEMP = sys.argv[3]
if (not is_float(TARGET_TEMP)):
    print(f"error: argument {TARGET_TEMP} is not a float")
    quit(-1)
print(f"New target temp: {TARGET_TEMP}")
IOBR_TARGET_TEMP_DP = sys.argv[4]
print(f"Got datapoint to update: {IOBR_TARGET_TEMP_DP}")

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

        if spaman.facade.water_heater.is_present:
            print(f"*** water heater present")
        else:
            print(f"error: no water heater present returned from geckolib")
            quit(-1)
        
        print(f"*** current target temp: {spaman.facade.water_heater.target_temperature}")

        if float(spaman.facade.water_heater.target_temperature) != float(TARGET_TEMP):
            await spaman.facade.water_heater.async_set_target_temperature(TARGET_TEMP)
            await asyncio.sleep(1)
            print(f"*** target temp is now: {spaman.facade.water_heater.target_temperature}")
        else:
            print(f"*** new target temp is identical to current, nothing to do")
        
        # sending state updates to ioBroker
        requests.get(f"{IOBROKER_BASE_URL}{IOBR_TARGET_TEMP_DP}?value={str(spaman.facade.water_heater.target_temperature)}&ack=true")
        #print(f"{IOBROKER_BASE_URL}{IOBR_TARGET_TEMP_DP}?value={str(spaman.facade.water_heater.target_temperature)}&ack=true")
        requests.get(f"{IOBROKER_BASE_URL}{IOBR_TARGET_TEMP_DP}?value={str(spaman.facade.water_heater.target_temperature)}&ack=true")
        #print(f"{IOBROKER_BASE_URL}{IOBR_TARGET_TEMP_DP}?value={str(spaman.facade.water_heater.target_temperature)}&ack=true")

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

