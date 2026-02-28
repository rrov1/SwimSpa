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
    NO_LIGHTS_AVAILABLE = 2
    LIGHT_NOT_FOUND = 3
    HTTP_ERROR = 4
    INVALID_HTTP_RESPONSE = 5
    IOBROKER_API_ERROR = 6
    SPA_CONNECTION_FAILED = 7


VERSION = "0.2.6"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 7:
    print("*** Wrong number of script arguments.", file=sys.stderr)
    print("*** call example: {sys.argv[0]} clientId restApiUrl spaId spaIP lightKey lightChannel", file=sys.stderr)
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
            if len(spaman.facade.lights) > 0:
                print(f"*** light count: {len(spaman.facade.lights)}")
            else:
                print("error: no lights returned from geckolib", file=sys.stderr)
                return ExitCode.NO_LIGHTS_AVAILABLE

            # search for light based on key
            keyNotFound = True
            for light in spaman.facade.lights:
                if LIGHT_KEY == light.key:
                    print(f"*** found light with key {LIGHT_KEY} and name: {light.name} with state {light.is_on}")
                    keyNotFound = False
                    if light.is_on:
                        print("*** switching light off")
                        await light.async_turn_off()
                    else:
                        print("*** switching light on")
                        await light.async_turn_on()
                    await asyncio.sleep(1)
                    newLightMode = light.is_on
                    break

            if keyNotFound:
                print(f"error: light with key: {LIGHT_KEY} not found", file=sys.stderr)
                return ExitCode.LIGHT_NOT_FOUND

            print(f"*** light mode is now: {newLightMode}")

            sJson2Send = sJson2Send + "{}.Switch={}".format(IOBR_LIGHT_CHANNEL, str(newLightMode).lower()) + "&ack=true& "
            sJson2Send = sJson2Send + "{}.Is_On={}".format(IOBR_LIGHT_CHANNEL, str(newLightMode).lower()) + "&ack=true& "

            await asyncio.sleep(1)
            await spaman.async_reset()
            print("connection closed/reset")
        else:
            print(f"*** cannot establish connection to spa controller, spa_state: {spaman.spa_state}", file=sys.stderr)
            return ExitCode.SPA_CONNECTION_FAILED

        if not sJson2Send:
            print("*** no ioBroker updates to send")
            print("*** end")
            return return_code

        sJson2Send = sJson2Send[: len(sJson2Send) - 2] + ""
        try:
            oResponse = requests.post("{}/setBulk".format(IOBRURL), data=sJson2Send)
        except Exception as e:
            print(e)
            print("an error occured on sending an http request to ioBroker Rest API, no data was sent, check url", file=sys.stderr)
            return_code = ExitCode.HTTP_ERROR
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
