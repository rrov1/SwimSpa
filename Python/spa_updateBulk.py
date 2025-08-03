import sys
import asyncio
import requests
import urllib.parse
import logging
import signal
import json

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent  # type: ignore

VERSION = "0.3.0"
print(f"{sys.argv[0]} Version: {VERSION}")

# Anzahl Argumente prüfen
if len(sys.argv) != 6:
    print("*** Wrong number of script arguments.", file=sys.stderr)
    print(f"*** call example: {sys.argv[0]} clientId ioBrSimpleRestApiUrl spaIds spaIPs dpBasePath", file=sys.stderr)
    quit(-1)

print("total arguments passed:", len(sys.argv))
CLIENT_ID = sys.argv[1]
print(f"Connect using client id: {CLIENT_ID}")
IOBRURL = sys.argv[2]
print(f"ioBroker Simple Rest API URL: {IOBRURL}")
spaIds = sys.argv[3]
if (spaIds.find(",") >= 0):
    SPA_ID = spaIds.split(",")
    print(f"Connecting to spa ids {spaIds}")
else:
    SPA_ID = [spaIds]
    print(f"Connecting to spa id {spaIds}")
spaIPs = sys.argv[4]
if (spaIPs.find(",") >= 0):
    SPA_IP = spaIPs.split(",")
    print(f"Connecting to spa ips {spaIPs}")
else:
    SPA_IP = [spaIPs]
    print(f"Connecting to spa ip {spaIPs}")
IOB_DP_BASE_PATH = sys.argv[5]
print(f"Base path to datapoints: {IOB_DP_BASE_PATH}")

dictEn2De = {'Away From Home': 'Abwesend',
          'Standard': 'Standard', 
          'Energy Saving': 'Energiesparen',
          'Super Energy Saving': 'Energiesparen Plus',
          'Weekender': 'Wochenende'
}

def set_run_timeout(timeout):
    """Set maximum execution time of the current Python process"""
    def alarm(*_):
        raise SystemExit("Timed out: Maximum script runtime reached.")
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(timeout)

def cutModeName(modeString):
    # correct mode string in case geckolib returns longer strings than in modes collection
    if modeString == "OFF":
        return "OFF"
    if modeString == "HIGH":
        return "HI"
    if modeString == "LOW":
        return "LO"
    return modeString

class SampleSpaMan(GeckoAsyncSpaMan):
    """Sample spa man implementation"""

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        # Uncomment this line to see events generated
        #print(f"{event}: {kwargs}")
        pass

def buildBulkGetforSpa(basePath, spaNum, facade):
    # read current values for datapoints from ioBroker
    ids2Get = ""
    ids2Get = ids2Get + "{}.{}.Heizer".format(basePath, spaNum) + ","
    ids2Get = ids2Get + "{}.{}.AktuelleTemperatur".format(basePath, spaNum) + ","
    ids2Get = ids2Get + "{}.{}.ZielTemperatur".format(basePath, spaNum) + ","
    ids2Get = ids2Get + "{}.{}.EchteZielTemperatur".format(basePath, spaNum) + ","
    ids2Get = ids2Get + "{}.{}.WasserpflegeSwitch".format(basePath, spaNum) + ","
    # Pumpen
    for pump in facade.pumps:
        ids2Get = ids2Get + "{}.{}.Pumpen.{}.Modus".format(basePath, spaNum, pump.key) + ","
        ids2Get = ids2Get + "{}.{}.Pumpen.{}.Switch".format(basePath, spaNum, pump.key) + ","
    # Lichter
    for light in facade.lights:
        ids2Get = ids2Get + "{}.{}.Lichter.{}.Is_On".format(basePath, spaNum, light.key) + ","
        ids2Get = ids2Get + "{}.{}.Lichter.{}.Switch".format(basePath, spaNum, light.key) + ","
    # Sensoren
    for binary_sensor in facade.binary_sensors:
        sKey = binary_sensor.key
        sKey = sKey.replace(" ", "_")
        sKey = sKey.replace(":", "_")
        ids2Get = ids2Get + "{}.{}.Sensoren.{}.State".format(basePath, spaNum, sKey) + ","
    # some sensors
    ids2Get = ids2Get + "{}.{}.Sensoren.RF_Signal.State".format(basePath, spaNum) + ","
    ids2Get = ids2Get + "{}.{}.Sensoren.RF_Channel.State".format(basePath, spaNum) + ","
    ids2Get = ids2Get + "{}.{}.Sensoren.Last_Ping.State".format(basePath, spaNum) + ","
    ids2Get = ids2Get + "{}.{}.Sensoren.Status.State".format(basePath, spaNum)

    return ids2Get

def search(keyName, keyValue, listOfDict):
    return [element for element in listOfDict if element[keyName] == keyValue]

def searchForValue(keyName, keyValue, valName, listOfDict):
    # search a list of dicts, find a keyName with keyValue and return value of item valName in this dict
    res = [element for element in listOfDict if element[keyName] == keyValue]
    if len(res) > 0:
        return res[0][valName]
    return None
 
async def main() -> None:
    sData2Send = ""
    set_run_timeout(90)

    for nSpaNum in range(len(SPA_ID)):
        spa = SPA_ID[nSpaNum]
        ip = SPA_IP[nSpaNum]
        
        async with SampleSpaMan(CLIENT_ID, spa_identifier=spa, spa_address=ip) as spaman:
            print(f"*** {nSpaNum}: connecting to {spa}")
            
            # connect
            await spaman.async_connect(spa_identifier=spa, spa_address=ip)

            # Wait for the facade to be ready
            result = await spaman.wait_for_facade()
            
            print(f"*** connect result-> {result}")
            if result == True:
                facade = spaman.facade
                currentStates = ""
                # read current states (update only when state change is here detected)
                try:
                    oResponse = requests.get("{}/getBulk/{}".format(IOBRURL, buildBulkGetforSpa(IOB_DP_BASE_PATH, nSpaNum, facade)))
                except Exception as e:
                    print(e)
                    print("an error occured on sending an http request to ioBroker Rest API, no data was get, check url")
                else:
                    print(f"http response code: {oResponse.status_code}")
                    if oResponse.status_code == 200:
                        currentStates = json.loads(oResponse.text)
                
                print(f"type: {type(currentStates)}, len {len(currentStates)}")
                for stateRow in range(len(currentStates)):
                    if 'val' in currentStates[stateRow]:
                        print(f"{stateRow}: {currentStates[stateRow]['id']}, val: {currentStates[stateRow]['val']}, type: {type(currentStates[stateRow])}")

                print("sending heater ops")
                print(f'heater available-> {facade.water_heater.is_available}')
                print(f"current heater operation-> {facade.water_heater.current_operation}")
                ioBrDp = "{}.{}.Heizer".format(IOB_DP_BASE_PATH, nSpaNum)
                currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                if currentIoBrVal != facade.water_heater.current_operation:
                    print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {facade.water_heater.current_operation}")
                    sData2Send = sData2Send + "{}={}".format(ioBrDp, facade.water_heater.current_operation) + "&ack=true& "
                
                # Temperaturen
                print('sending temp')
                # temp value must be within min/max temp +/-10 degrees
                ioBrDp = "{}.{}.AktuelleTemperatur".format(IOB_DP_BASE_PATH, nSpaNum)
                currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                if currentIoBrVal != round(facade.water_heater.current_temperature, 2):
                    print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {round(facade.water_heater.current_temperature, 2)}")
                    if float(facade.water_heater.current_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.current_temperature) < (float(facade.water_heater.max_temp) + 10):
                        print(f"current temp-> {round(facade.water_heater.current_temperature, 2)}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, round(facade.water_heater.current_temperature, 2)) + "&ack=true& "
                ioBrDp = "{}.{}.ZielTemperatur".format(IOB_DP_BASE_PATH, nSpaNum)
                currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                if currentIoBrVal != round(facade.water_heater.target_temperature, 2):
                    print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {round(facade.water_heater.target_temperature, 2)}")
                    if float(facade.water_heater.target_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.target_temperature) < (float(facade.water_heater.max_temp) + 10):
                        print(f"target temp-> {round(facade.water_heater.target_temperature, 2)}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, round(facade.water_heater.target_temperature, 2)) + "&ack=true& "
                ioBrDp = "{}.{}.EchteZielTemperatur".format(IOB_DP_BASE_PATH, nSpaNum)
                currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                if currentIoBrVal != round(facade.water_heater.real_target_temperature, 2):
                    print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {round(facade.water_heater.real_target_temperature, 2)}")
                    if float(facade.water_heater.real_target_temperature) > (float(facade.water_heater.min_temp) - 10) and float(facade.water_heater.real_target_temperature) < (float(facade.water_heater.max_temp) + 10):
                        print(f"real target temp-> {round(facade.water_heater.real_target_temperature, 2)}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, round(facade.water_heater.real_target_temperature, 2)) + "&ack=true& "
                
                # Wasserprflege
                print('sending water care')
                myMode = await facade.spa.async_get_watercare_mode()
                print(f"current watercare mode: {myMode}")
                ioBrDp = "{}.{}.WasserpflegeSwitch".format(IOB_DP_BASE_PATH, nSpaNum)
                currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                if currentIoBrVal != myMode:
                    print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {myMode}")
                    sData2Send = sData2Send + "{}={}".format(ioBrDp, myMode) + "&ack=true& "
                
                # Pumpen
                print('sending pumps')
                for pump in facade.pumps:
                    print(f"{pump.name}-> {pump.mode}, {pump.modes}")
                    ioBrDp = "{}.{}.Pumpen.{}.Modus".format(IOB_DP_BASE_PATH, nSpaNum, pump.key)
                    currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                    if currentIoBrVal != pump.mode:
                        print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {pump.mode}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, pump.mode) + "&ack=true& "
                    # short pump state name
                    shortPumpStateNAme = cutModeName(pump.mode)
                    # calculate new pump state id
                    for x in range(len(pump.modes)):
                        if shortPumpStateNAme == pump.modes[x]:
                            pumpStateId = x
                            break
                    ioBrDp = "{}.{}.Pumpen.{}.Switch".format(IOB_DP_BASE_PATH, nSpaNum, pump.key)
                    currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                    if currentIoBrVal != pumpStateId:
                        print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {pumpStateId}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, pumpStateId) + "&ack=true& "
                
                # Lichter
                print('sending lights')
                for light in facade.lights:
                    print(f"{light.name}-> {str(light.is_on).lower()}")
                    ioBrDp = "{}.{}.Lichter.{}.Is_On".format(IOB_DP_BASE_PATH, nSpaNum, light.key)
                    currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                    if str(currentIoBrVal).lower() != str(light.is_on).lower():
                        print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {str(light.is_on).lower()}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, str(light.is_on).lower()) + "&ack=true& "
                    ioBrDp = "{}.{}.Lichter.{}.Switch".format(IOB_DP_BASE_PATH, nSpaNum, light.key)
                    currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                    if str(currentIoBrVal).lower() != str(light.is_on).lower():
                        print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {str(light.is_on).lower()}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, str(light.is_on).lower()) + "&ack=true& "
                
                # Sensoren
                print('sending sensors')
                for binary_sensor in facade.binary_sensors:
                    print(f"{binary_sensor.name}-> {binary_sensor.state}")
                    sKey = binary_sensor.key
                    sKey = sKey.replace(" ", "_")
                    sKey = sKey.replace(":", "_")
                    ioBrDp = "{}.{}.Sensoren.{}.State".format(IOB_DP_BASE_PATH, nSpaNum, sKey)
                    currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                    if str(currentIoBrVal).lower() != str(binary_sensor.state).lower():
                        print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {str(binary_sensor.state).lower()}")
                        sData2Send = sData2Send + "{}={}".format(ioBrDp, urllib.parse.quote((str(binary_sensor.state)).lower())) + "&ack=true& "
                
                # spaman sensoren
                print('sending other sensors')
                
                print(f"radio_sensor-> {spaman.radio_sensor.state}")
                ioBrDp = "{}.{}.Sensoren.RF_Signal.State".format(IOB_DP_BASE_PATH, nSpaNum)
                currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                if currentIoBrVal != spaman.radio_sensor.state:
                    print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {str(spaman.radio_sensor.state)}")
                    sData2Send = sData2Send + "{}={}".format(ioBrDp, urllib.parse.quote(str(spaman.radio_sensor.state))) + "&ack=true& "
                
                print(f"channel_sensor-> {spaman.channel_sensor.state}")
                ioBrDp = "{}.{}.Sensoren.RF_Channel.State".format(IOB_DP_BASE_PATH, nSpaNum)
                currentIoBrVal = searchForValue("id", ioBrDp, "val", currentStates)
                if currentIoBrVal != spaman.channel_sensor.state:
                    print(f"value of {ioBrDp} is different ioBr: {currentIoBrVal} != {str(spaman.channel_sensor.state)}")
                    sData2Send = sData2Send + "{}={}".format(ioBrDp, urllib.parse.quote(str(spaman.channel_sensor.state))) + "&ack=true& "
                
                print(f"ping_sensor-> {spaman.ping_sensor.state}")
                # send always
                sData2Send = sData2Send + "{}.{}.Sensoren.Last_Ping.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(str(spaman.ping_sensor.state))) + "&ack=true& "

                print(f"status_sensor-> {spaman.status_sensor.state}")
                # send always
                sData2Send = sData2Send + "{}.{}.Sensoren.Status.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote(spaman.status_sensor.state)) + "&ack=true& "
                print("finished reading all data")

                # kurz warten (löst das Problem mit den längeren Wartezeiten)
                await asyncio.sleep(1)

                # reset/close connection
                await spaman.async_reset()
                print("connection closed/reset")
            else:
                print(f"*** cannot establish connection to spa controller, spa_state: {spaman.spa_state}", file=sys.stderr)
                sData2Send = sData2Send + "{}.{}.Sensoren.Status.State={}".format(IOB_DP_BASE_PATH, nSpaNum, urllib.parse.quote("Connect failed")) + "&ack=true& "
    
    if len(sData2Send) > 0:
        sData2Send = sData2Send[:len(sData2Send)-2] + ""
    
    if len(sData2Send) > 0:
        print(f"***data2send: {sData2Send}")
        try:
            oResponse = requests.post("{}/setBulk".format(IOBRURL), data = sData2Send)
        except Exception as e:
            print(e)
            print("an error occured on sending an http request to ioBroker Rest API, no data was sent, check url", file=sys.stderr)
        else:
            print(f"http response code: {oResponse.status_code}")
            if oResponse.status_code != 200:
                print("respose text:")
                print(oResponse.text)
    else:
        print("nothing 2 send")
    
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
