import sys
import asyncio
import logging
import requests
import signal
from enum import IntEnum

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore


class ExitCode(IntEnum):
    OK = 0
    INVALID_ARGUMENTS = 1
    NO_PUMPS_AVAILABLE = 2
    PUMP_ID_OUT_OF_RANGE = 3
    PUMP_STATE_OUT_OF_RANGE = 4
    HTTP_ERROR = 5
    INVALID_HTTP_RESPONSE = 6
    IOBROKER_API_ERROR = 7
    SPA_CONNECTION_FAILED = 8
    IOBROKER_REQUEST_EXCEPTION = 9


VERSION = "0.2.7"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 8:
    print("*** Wrong number of script arguments.", file=sys.stderr)
    print("*** call example: {sys.argv[0]} clientId restApiUrl spaId spaIP pumpId newPumpState pumpChannel", file=sys.stderr)
    sys.exit(ExitCode.INVALID_ARGUMENTS)

print("Total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connecting using client id {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
SPA_ID = sys.argv[3]
print(f"Connecting to spa id {SPA_ID}")
SPA_IP = sys.argv[4]
print(f"Connecting to spa ip {SPA_IP}")
try:
    PUMP_ID = int(sys.argv[5])
except ValueError:
    print(f"error: pump id must be an integer, got {sys.argv[5]}", file=sys.stderr)
    sys.exit(ExitCode.INVALID_ARGUMENTS)
print(f"Switching pump id {PUMP_ID}")
try:
    NEW_PUMP_STATE = int(sys.argv[6])
except ValueError:
    print(f"error: new pump state must be an integer, got {sys.argv[6]}", file=sys.stderr)
    sys.exit(ExitCode.INVALID_ARGUMENTS)
print(f"Switching pump to state id {NEW_PUMP_STATE}")
IOBR_PUMP_CHANNEL = sys.argv[7]
print(f"Got channel for update: {IOBR_PUMP_CHANNEL}")


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

    def cutModeName(self, modeString):
        # correct mode string in case geckolib returns longer strings than in modes collection
        if modeString == "OFF":
            return "OFF"
        if modeString == "HIGH":
            return "HI"
        if modeString == "LOW":
            return "LO"
        return modeString


async def main() -> ExitCode:
    return_code = ExitCode.OK
    set_run_timeout(30)
    sJson2Send = ""

    async with SampleSpaMan(CLIENT_ID, spa_identifier=SPA_ID, spa_address=SPA_IP) as spaman:
        print(f"*** connecting to {SPA_ID} with ip {SPA_IP}")

        # connect
        await spaman.async_connect(spa_identifier=SPA_ID, spa_address=SPA_IP)

        # Wait for the facade to be ready
        result = await spaman.wait_for_facade()

        print(f"*** connect result-> {result}")
        if result is True:
            if len(spaman.facade.pumps) > 0:
                print(f"*** found: {len(spaman.facade.pumps)} pumps")
            else:
                print("error: no pumps returned from geckolib", file=sys.stderr)
                return ExitCode.NO_PUMPS_AVAILABLE

            if PUMP_ID < 0 or PUMP_ID >= len(spaman.facade.pumps):
                print(
                    f"error: pump id {PUMP_ID} out of range (available: 0-{len(spaman.facade.pumps)-1})",
                    file=sys.stderr,
                )
                return ExitCode.PUMP_ID_OUT_OF_RANGE

            print(f"*** pump name: {spaman.facade.pumps[PUMP_ID].name}")
            print(f"*** pump modes: {spaman.facade.pumps[PUMP_ID].modes}")
            print(f"*** current pump mode: {spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)}")

            if NEW_PUMP_STATE < 0 or NEW_PUMP_STATE >= len(spaman.facade.pumps[PUMP_ID].modes):
                print(f"error: new pump state {NEW_PUMP_STATE} out of range for pump {PUMP_ID}", file=sys.stderr)
                return ExitCode.PUMP_STATE_OUT_OF_RANGE

            new_pump_state_name = spaman.facade.pumps[PUMP_ID].modes[NEW_PUMP_STATE]
            print(f"*** new pump state name: {new_pump_state_name}")

            if spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode) != new_pump_state_name:
                await spaman.facade.pumps[PUMP_ID].async_set_mode(new_pump_state_name)
                await asyncio.sleep(1)
                print(f"*** pump mode is now: {spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)}")
                set_pump_state_name = spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)
                set_pump_state = NEW_PUMP_STATE
                for index, mode in enumerate(spaman.facade.pumps[PUMP_ID].modes):
                    if set_pump_state_name == mode:
                        set_pump_state = index
                        break
                sJson2Send = sJson2Send + "{}.Switch={}".format(IOBR_PUMP_CHANNEL, set_pump_state) + "&"
                sJson2Send = sJson2Send + "{}.Modus={}".format(IOBR_PUMP_CHANNEL, set_pump_state_name) + "&"
            else:
                print(f"*** nothing to do, pump mode is already: {spaman.cutModeName(spaman.facade.pumps[PUMP_ID].mode)}")
                sJson2Send = sJson2Send + "{}.Switch={}".format(IOBR_PUMP_CHANNEL, NEW_PUMP_STATE) + "&"
                sJson2Send = sJson2Send + "{}.Modus={}".format(IOBR_PUMP_CHANNEL, new_pump_state_name) + "&"

            await asyncio.sleep(5)
            await spaman.async_reset()
            print("connection closed/reset")
        else:
            print(f"*** cannot establish connection to spa controller, spa_state: {spaman.spa_state}", file=sys.stderr)
            return ExitCode.SPA_CONNECTION_FAILED

        if not sJson2Send:
            print("*** no ioBroker updates to send")
            print("*** end")
            return return_code

        if len(sJson2Send) > 0:
            sJson2Send = sJson2Send + "ack=true"
        
        try:
            oResponse = requests.post("{}/setBulk".format(IOBRURL), data=sJson2Send)
        except Exception as e:
            print(e)
            print("an error occured on sending an http request to ioBroker Rest API, no data was sent, check url", file=sys.stderr)
            return_code = ExitCode.IOBROKER_REQUEST_EXCEPTION
        else:
            if oResponse.status_code != 200:
                print(f"http response code: {oResponse.status_code}", file=sys.stderr)
                print("respose text:", file=sys.stderr)
                print(oResponse.text, file=sys.stderr)
                return_code = ExitCode.HTTP_ERROR
            else:
                print(f"http response code: {oResponse.status_code}")
                try:
                    oResponseJson = oResponse.json()
                except ValueError:
                    print("response is not valid JSON:", file=sys.stderr)
                    print(oResponse.text, file=sys.stderr)
                    return_code = ExitCode.INVALID_HTTP_RESPONSE
                else:
                    for entry in oResponseJson:
                        if isinstance(entry, dict) and "error" in entry:
                            print(entry["error"], file=sys.stderr)
                            return_code = ExitCode.IOBROKER_API_ERROR

        print("*** end")
        return return_code


if __name__ == "__main__":
    stream_logger = logging.StreamHandler()
    stream_logger.setLevel(logging.DEBUG)
    stream_logger.setFormatter(logging.Formatter("%(asctime)s> %(levelname)s %(message)s"))
    logging.getLogger().addHandler(stream_logger)
    logging.getLogger().setLevel(logging.INFO)

    sys.exit(asyncio.run(main()))
