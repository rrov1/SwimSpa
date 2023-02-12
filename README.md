# ioBroker Skript Integration von Gecko Alliance spa pack systems bzw. in.touch2 mit geckolib

## Funktionsumfang

* [X] Unterstützung mehrere Spa Controller
* [X] Bereitstellen von Datenpunkten mit der Konfiguration des Spa Controllers
* [X] Bereistellen von Datenpunkten mit aktuellen Laufzeitinformationen
* [X] Schalten der Pumpen
* [X] Schalten der Beleuchtung
* [X] Einstellen der Zieltemperatur
* [ ] Einstellen des Wasserpflegemodus

## Installation/Update

### gazoodle/geckolib (github)

Quelle: [https://github.com/gazoodle/geckolib](https://github.com/gazoodle/geckolib)

Voraussetzung zur Installation: Python3&Pip (am besten unter einem Linux)

Installation: pip install geckolib

Update: pip install geckolib --upgrade

### Python Skripte

Alle Python Skripte befinden aus dem Repository (Ordner: [Python](Python)) in einem Verzeichnis bereitstellen.

Momentan sind in den Scripten noch einige Parameter fest codiert, welche vor der Nutzung angepasst werden müssen (wird in zukünftigen Versionen entfallen). Beispiel spa_config.py:

```
CLIENT_ID = "any_guid"
lSpas = ["SPA68:aa:bb:cc:dd:ee"]
IOBROKER_BASE_URL = "http://<<iobroker_ip_address>:8087/set/"
```


| **Variable**      | **Verwendungszweck/Wert**                                                                                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLIENT_ID         | GUID die von der geckolib im weiteren verwendet wird, falls nicht vorhanden, dann wird die im ioBroker hinterlegte GUID verwendet                                                                                       |
| lSpas             | Spa-ID der geckolib, wen mehrere in.touch2 Systeme im Netz sind, ggf. auch mehrere (Komma separierte Liste).<br /><br/>Hinweis: Die Spa-ID steht nach dem ersten ausführen von spa_config.py in einem der Datenpunkte. |
| IOBROKER_BASE_URL | Hier muss die IP Adresse vom ioBroker eingetragen werden (für die Aktualisierung der Datenpunkte via Simple Rest API)                                                                                                  |

### Javascript Skripte für ioBroker

Voraussetzung:

* Javascript/Blockly & Simple Rest API Adapter
* Einstellung des Javascript Adapters:
  * Option: Enable Command "setObject" - ist aktiviert
  * Option: Enable Command "exec" - ist aktiviert

Schritt 1: Erstellen der Datenpunkte

* Skript SpaVariablen.js einspielen und Konfiguration anpassen


| **Variable** | **Verwendungszweck/Wert**                                                                                                |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| BASE_ADAPTER | Basispfad zum Adapter unter dem die Datenpunkte angelegt werden. Standard ist der erste Javascript Adapter: "javascript.0". |
| BASE_FOLDER  | Basispfad unter dem die Datenpunkte angelegt werden sollen, Standardwert ist: "Datenpunkte.SwimSpa"                         |

Um die notwendigen Datenpunkte zu erstellen müssen die Parameter der Funktion createDatapoints() noch angepasst werden:


| **Parameter** | **Wert**                                       |
| --------------- | ------------------------------------------------ |
| 1             | Anzahl Spa Controller im Netz, typ. Weise: 1   |
| 2             | Anzahl Pumpen pro Spa Controller, typ. Weise 3 |
| 3             | Datenpukte für Wasserfall mit anlegen         |

* Nach dem speichern, das Script 1x ausführen
* Prüfen ob die Datenpunkte vorhanden sind

Schritt 2: Weitere Skripte anlegen

Die weiteren Scripte im Ordner Javascript müssen ebenfalls erstellt werden. Wichtig, wenn im vorhergehenden Schritt bei BASE_ADAPTER bzw. BASE_FOLDER abweichende Pfade angegeben worden sind, müssen diese in den on()-Aufrufen ebenfalls angepasst werden.

Hinweis: Wenn die Python Scripte in einem speziellen Ordner liegen, dann muss der Pfad ggf. im Javascript-Skript im exec()-Aufruf angepasst werden.

## Nutzung

### spa_config.py Aufrufe

Das Skript liefert relativ statische Werte der Spa Konfiguration zurück. Es muss nach der Installation einmal aufgeufen werden (z.B. auch manuell), danach sollte es 1x am Tag bis max. 4x am Tag laufen (aller 6h). Dies kann z.B. mittels eines cron Aufrufs erfolgen:

crontab Eintrag:

```
0 5 * * * python3 ~/spa_config.py >/dev/null 2>&1
```

### spa_updateBulk.py Aufrufe

Das Skript liefert laufend den Status für die Datenpunkte. Es sollte minütlich aufgerufen werden (kürzere Taktung ergibt eines schnellere Reaktion auf manuelle Bedienungen - ggf. selbst testen).

crontab Eintrag:

```
* * * * * python3 ~/spa_updateBulk.py  >/dev/null 2>&1
```

### Sonstige Scripte:

Werden bei ändern eines Datenpunktes zum Schalten von Pumpe oder Licht per Javascript ausgelöst.


| **Zweck**                 | **Javascript**              | **Python Skript** |
| ------------------------- | --------------------------- | --------------------------- |
| Schalten der Pumpen       | PumpSwitches.js             | spa_switchPump.py |
| Schalten der Beleuchtung  | LightToggle.js              | spa_toggleLight.py |
| Setzen der Zieltemperatur | TargetTemp.js               | spa_setTargetTemp.py |

# Todo's

* Momentan ist der Pfad zu den Datenpunkten in den Python Scripten noch fest codiert - umstellen auf Parameter nötig
* Die URL vom ioBroker Rest API muss als Parameter mit übergeben werden
* Alle Python Skripte sollen ohne Konstanten aufrufbar sein
* Statt cron soll der regelmäßige Aufruf mit ioBroker Schedule möglich sein
* spa_config.py umstellen von set() auf setBulk() (Simpe Rest API Aufrufe)
* Status der Erreichbarkeit des Spa in Datenpunkt darstellen (Ebene Netzwerk, Online/Offline), sowie Fehler bei letzten Kommando
* Richtiges Discovery der Eigenschaften des Spa Controllers anstatt feste Anlage der Datenpunkte via Skript
* Das setzen der Zieltemperatur ist empfindlich ggü. mehreren schnell auseinanderfolgenden Wertänderungen. Momentan am besten einen Slider nutzen, der eine Funktion "Update value on release" untersützt, so dass der DP nur einmal geändert wird. Das Script braucht immer ein paar Sekunden bis der Wert im Hintergrund gesetzt wurde.
* ...
