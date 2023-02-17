import sys
import asyncio
import logging
import requests

IOBROKER_BASE_URL = "http://<<iobroker_ip_address>>:8087/setBulk"

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
print(f"Got channel for update: {IOBR_PUMP_CHANNEL}")

class SampleSpaMan(GeckoAsyncSpaMan):
    """Sample spa man implementation"""

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        # print(f"{event}: {kwargs}")
        pass
    
    def cutModeName(self, modeString):
        # correct mode string in case geckolib returns longer strings than in modes collection
        if modeString == "OFF":
            return "OFF"
        if modeString == "HIGH":
            return "HI"
        if modeString == "LOW":
            return "LO"
        return modeString

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

        print(f"*** pump name: {spaman.facade.pumps[PUMP_ID].name}")
        print(f"*** pump modes: {spaman.facade.pumps[PUMP_ID].modes}")
        print(f"*** current pump mode: {spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)}")
        NEW_PUMP_STATE_NAME = spaman.facade.pumps[PUMP_ID].modes[NEW_PUMP_STATE]
        print(f"*** new pump state name: {NEW_PUMP_STATE_NAME}")

        if len(spaman.facade.pumps) > 0:
            print(f"*** found: {len(spaman.facade.pumps)} pumps")
        else:
            print(f"error: no pumps returned from geckolib")
            quit(-1)

        #
        sJson2Send = ""

        if spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode) != NEW_PUMP_STATE_NAME:
            await spaman.facade.pumps[PUMP_ID].async_set_mode(NEW_PUMP_STATE_NAME)
            await asyncio.sleep(1)
            print(f"*** pump mode is now: {spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)}")
            # new pump state name
            SET_PUMP_STATE_NAME = spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)
            # new pump state id
            for x in range(len(spaman.facade.pumps[PUMP_ID].modes)):
                if SET_PUMP_STATE_NAME == spaman.facade.pumps[PUMP_ID].modes[x]:
                    SET_PUMP_STATE = x
                    break
            # sending state updates to ioBroker
            sJson2Send = sJson2Send + "{}.Switch={}".format(IOBR_PUMP_CHANNEL, SET_PUMP_STATE) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.Modus={}".format(IOBR_PUMP_CHANNEL, SET_PUMP_STATE_NAME) + "&ack=true& "
        else:
            print(f"*** nothing to do, pump mode is already: {spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)}")
            # sending state updates to ioBroker
            sJson2Send = sJson2Send + "{}.Switch={}".format(IOBR_PUMP_CHANNEL, NEW_PUMP_STATE) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.Modus={}".format(IOBR_PUMP_CHANNEL, NEW_PUMP_STATE_NAME) + "&ack=true& "
        
        sJson2Send = sJson2Send[:len(sJson2Send)-2] + ""
        #print(sJson2Send)
        try:
            oResponse = requests.post(IOBROKER_BASE_URL, data = sJson2Send)
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

