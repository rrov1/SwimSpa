import sys
import asyncio
import logging
import requests

IOBROKER_BASE_URL = "http://<iobroker_ip_address>>:8087/set/"

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

# Anzahl Argumente prüfen
if len(sys.argv) != 6:
    print("*** Wrong number of script arguments.\n")
    print("*** call example: {sys.argv[0]} clientId spaId pumpId newPumpState pumpChannel")
    quit(-1)

print("Total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connecting using client id {CLIENT_ID}")
SPA_ID = sys.argv[2]
print(f"Connecting to spa id {SPA_ID}")
PUMP_ID = int(sys.argv[3])
print(f"Switching pump id {PUMP_ID}")
NEW_PUMP_STATE = int(sys.argv[4])
print(f"Switching pump to state id {NEW_PUMP_STATE}")
IOBR_PUMP_CHANNEL = sys.argv[5]
print(f"Got channel for update {IOBR_PUMP_CHANNEL}")

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
            print("**** There were no spas found on your network.")
            return

        print("*** connecting to spa")
        await spaman.async_connect(spa_identifier=SPA_ID)

        # Wait for the facade to be ready
        await spaman.wait_for_facade()

        #print(f"*** {spaman.facade.pumps}")
        print(f"*** current pump mode: {spaman.facade.pumps[PUMP_ID].mode}")
        NEW_PUMP_STATE_NAME = spaman.facade.pumps[PUMP_ID].modes[NEW_PUMP_STATE]
        print(f"*** new pump state name: {NEW_PUMP_STATE_NAME}")
        
        if spaman.facade.pumps[PUMP_ID].mode != NEW_PUMP_STATE_NAME:
            await spaman.facade.pumps[PUMP_ID].async_set_mode(NEW_PUMP_STATE_NAME)
            await asyncio.sleep(1)
            print(f"*** pump mode is now: {spaman.facade.pumps[PUMP_ID].mode}")
            # sending state updates to ioBroker
            requests.get(f"{IOBROKER_BASE_URL}{IOBR_PUMP_CHANNEL}.Switch?value={NEW_PUMP_STATE}&ack=true")
            #print(f"{IOBROKER_BASE_URL}{IOBR_PUMP_CHANNEL}.Switch?value={NEW_PUMP_STATE}&ack=true")
            requests.get(f"{IOBROKER_BASE_URL}{IOBR_PUMP_CHANNEL}.Modus?value={NEW_PUMP_STATE_NAME}&ack=true")
            #print(f"{IOBROKER_BASE_URL}{IOBR_PUMP_CHANNEL}.Modus?value={NEW_PUMP_STATE_NAME}&ack=true")
        else:
            print(f"*** nothing to do, pump mode is already: {spaman.facade.pumps[PUMP_ID].mode}")
        
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

