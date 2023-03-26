# ioBroker Skript Integration von Gecko Alliance spa pack systems bzw. in.touch2 mit geckolib

## Funktionsumfang

* [X] Unterstützung mehrere Spa Controller
* [X] Bereitstellen von Datenpunkten mit der Konfiguration des Spa Controllers
* [X] Bereistellen von Datenpunkten mit aktuellen Laufzeitinformationen
* [X] Schalten der Pumpen
* [X] Schalten der Beleuchtung
* [X] Einstellen der Zieltemperatur
* [X] Einstellen des Wasserpflegemodus
* [ ] ToDos unten umsetzen

## Installation/Update

### gazoodle/geckolib (github)

Quelle: [https://github.com/gazoodle/geckolib](https://github.com/gazoodle/geckolib)

Voraussetzung zur Installation: Python3&Pip (am besten unter einem Linux)

Installation: sudo pip install geckolib

Update: sudo pip install geckolib --upgrade

### Python Skripte

Alle Python Skripte  aus dem Repository (Ordner: [Python](Python)) in einem Verzeichnis bereitstellen. Die Python-Skripte werden von den Javascript-Skripten aus aufgerufen mit den nötigen Parametern.


### Javascript Skripte für ioBroker

#### Voraussetzungen

* Javascript/Blockly & Simple Rest API Adapter
* Einstellung des Javascript Adapters:
  * Option: Enable Command "setObject" - ist aktiviert
  * Option: Enable Command "exec" - ist aktiviert

#### Schritt 1: Skript SpaGlobal.js bereitstellen

* "Expert Mode" im Adapter aktivieren, damit der Ordner "global" angezeigt wird
* im Ordner "global" ein neues Skript "SpaGlobal" anlegen und den Inhalt hineinkopieren und evtl. Konfiguration anpassen:

| **Variable** | **Verwendungszweck/Wert** |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| BASE_ADAPTER | Basispfad zum Adapter unter dem die Datenpunkte angelegt werden. Standard ist der erste Javascript Adapter: "javascript.0". |
| BASE_FOLDER  | Basispfad unter dem die Datenpunkte angelegt werden sollen, Standardwert ist: "Datenpunkte.SwimSpa" |
| SPA_EXECUTEABLE | Auszuführendes Programm, Standard ist "python3" |

#### Schritt 2: Erstellen bzw. Aktualisieren der Datenpunkte

* Skript SpaVariablen.js einspielen
* den Aufruf der Funktion createDatapoints() anpassen:

| **Parameter** | **Wert**                                       |
| ------------- | ---------------------------------------------- |
| 1             | Anzahl Spa Controller im Netz, typ. Weise: 1   |
| 2             | Anzahl Pumpen pro Spa Controller, typ. Weise 3 |
| 3             | Datenpukte für Wasserfall mit anlegen          |

* Nach dem speichern, das Script 1x ausführen
* Prüfen ob die Datenpunkte vorhanden sind

#### Schritt 3: Skripte für Spa Controller Konfiguration und Update der Zustände

* Neuen Ordner "Spa" im JavaScript-Adapter anlegen (um die Skripte etwas zu sortieren)
* Skript: SpaUpdateConfig.js erstellen (das zugehörige Pytho-Skript ist: spa_config.py clientId restApiUrl dpBasePath)
* Die Javascript Funktion: updateSpaConfig() wird beim speichern 1x ausgeführt, danach aller 6h.
* Prüfen ob die Datenpunkte die eher statische Konfigurationswerte darstellen, wie (z.B.: Temepratureinheit, ID, U_ID) aktualisiert worden sind
* Skcript: SpaUpdateValues.js erstellen (das zugehörige Python-Skript ist: spa_updateBulk.py clientId restApiUrl spaIdList dpBasePath)
* Das Skript wird minütlich aufgerufen und aktualisiert alle anderen Werte wie z.B. die Wassertemperaturen, Pumpenstatus, Licht usw.

**Hinweis:** Wenn die Python Scripte in einem speziellen Ordner liegen, dann muss der Pfad ggf. im Javascript-Skript im exec()-Aufruf angepasst werden.

#### Schritt 4: Weitere Skripte nach Bedarf

* Falls nicht vorhanden einen neuen Ordner "Spa" im JavaScript-Adapter anlegen (um die Skripte etwas zu sortieren)
* Skripte bereitstellen

| **Zweck**                    | **Javascript**              | **Python Skript**           |
| ---------------------------- | --------------------------- | --------------------------- |
| Schalten der Pumpen          | PumpSwitches.js             | spa_switchPump.py ClientGUID SpaId PumpId PumpstateId PumpChannelPath |
| Schalten der Beleuchtung     | LightToggle.js              | spa_toggleLight.py ClientGUID SpaId LightKey LightChannelPath |
| Setzen der Zieltemperatur    | TargetTemp.js               | spa_setTargetTemp.py ClientGUID SpaId TargetTemp TargetTempDatapointPath |
| Setzen des Wasserpflegemodus | WatercareMode.js            | spa_setWatercareMode.py ClientGUID SpaId waterCareModeIdx DevicePath |


**Hinweis:** Wenn im vorhergehenden Schritt bei BASE_ADAPTER bzw. BASE_FOLDER abweichende Pfade angegeben worden sind, müssen diese in den on()-Aufrufen ebenfalls angepasst werden.

# Todo's

* [X] Momentan ist der Pfad zu den Datenpunkten in den Python Scripten noch fest codiert - umstellen auf Parameter nötig
* [X] Die URL vom ioBroker Rest API muss als Parameter mit übergeben werden
* [X] Alle Python Skripte sollen ohne Konstanten aufrufbar sein
* [X] Statt cron soll der regelmäßige Aufruf mit ioBroker Schedule möglich sein
* [ ] Status der Erreichbarkeit des Spa in Datenpunkt darstellen (Ebene Netzwerk, Online/Offline), sowie Fehler bei letzten Kommando
* [ ] Richtiges Discovery der Eigenschaften des Spa Controllers anstatt feste Anlage der Datenpunkte via Skript
* [ ] Das setzen der Zieltemperatur ist empfindlich ggü. mehreren schnell auseinanderfolgenden Wertänderungen. Momentan am besten einen Slider nutzen, der eine Funktion "Update value on release" untersützt, so dass der DP nur einmal geändert wird. Das Script braucht immer ein paar Sekunden bis der Wert im Hintergrund gesetzt wurde.
* [ ] ...
