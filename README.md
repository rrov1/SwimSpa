<!-- TOC -->

- [ioBroker Skript Integration von Gecko Alliance spa pack systems bzw. in.touch2 mit geckolib](#iobroker-skript-integration-von-gecko-alliance-spa-pack-systems-bzw-intouch2-mit-geckolib)
    - [Funktionsumfang](#funktionsumfang)
    - [Installation/Update](#installationupdate)
        - [gazoodle/geckolib github](#gazoodlegeckolib-github)
        - [Python Skripte](#python-skripte)
        - [Javascript Skripte für ioBroker](#javascript-skripte-f%C3%BCr-iobroker)
            - [Voraussetzungen](#voraussetzungen)
            - [Schritt 1: Skript SpaGlobal.js bereitstellen](#schritt-1-skript-spaglobaljs-bereitstellen)
            - [Schritt 2: Erstellen bzw. Aktualisieren der Datenpunkte](#schritt-2-erstellen-bzw-aktualisieren-der-datenpunkte)
            - [Schritt 3: Skripte für Spa Controller Konfiguration und Update der Zustände](#schritt-3-skripte-f%C3%BCr-spa-controller-konfiguration-und-update-der-zust%C3%A4nde)
            - [Schritt 4: Weitere Skripte nach Bedarf](#schritt-4-weitere-skripte-nach-bedarf)
    - [Fehler und Sonderfälle](#fehler-und-sonderf%C3%A4lle)
        - [SpaUpdateValues.js/spa_updateBulk.py](#spaupdatevaluesjsspa_updatebulkpy)
        - [Kein SpaController gefunden, wenn ioBroker im Docker Container läuft](#kein-spacontroller-gefunden-wenn-iobroker-im-docker-container-l%C3%A4uft)
    - [Visualisierung](#visualisierung)
- [Todo's](#todos)

<!-- /TOC -->

# ioBroker Skript Integration von Gecko Alliance spa pack systems bzw. in.touch2 mit geckolib

## Funktionsumfang

* [X] Unterstützung mehrere Spa Controller
* [X] Bereitstellen von Datenpunkten mit der Konfiguration des Spa Controllers
* [X] Bereistellen von Datenpunkten mit aktuellen Laufzeitinformationen (z.B. Temperatur usw.)
* [X] Schalten der Pumpen
* [X] Schalten der Beleuchtung
* [X] Einstellen der Zieltemperatur
* [X] Einstellen des Wasserpflegemodus
* [X] Erinnerungen
* [ ] ToDos unten umsetzen

## Installation/Update

Hier auf Github werden 2 Arten von Skripten bereitgestellt:

1. Python-Skripte im Ordner: [Pyhton](Python), über die das geckolib API angesprochen wird
2. Javascript-Skripte im Ordner: [Javascript](JavaScript), welche im Javascript Adapter angelegt werden müssen

### gazoodle/geckolib (github)

Quelle: [https://github.com/gazoodle/geckolib](https://github.com/gazoodle/geckolib)

Voraussetzung zur Installation: **Python3 mind. v3.8** & **Pip** (am besten unter einem Linux, nur Versionen die unter [Support](https://devguide.python.org/versions/) sind)

Installation: `sudo pip install geckolib`<br>
Update: `sudo pip install geckolib --upgrade`<br>

Auch die geckolib muss ab und an mal aktualisiert werden.

### Python Skripte

Für die Python-Skripte sind noch folgende Bibliotheken bereitzustellen:

* requests: `sudo pip3 install requests`

Alle Python Skripte aus dem Repository (Ordner: [Python](Python)) müssen in einem Verzeichnis bereitgestellt werden. Im Beispiel nutzen wir jetzt direkt einen Order unterhalb `/`, clonen das Github Repo und kompieren die Dateien aus dem Ordner Python ans eigentliche Ziel. Danach wird noch der owner angepasst.

```
~$ sudo mkdir /SpaController
~$ git clone https://github.com/rrov1/SwimSpa.git
Cloning into 'SwimSpa'...
remote: Enumerating objects: 268, done.
remote: Counting objects: 100% (268/268), done.
remote: Compressing objects: 100% (199/199), done.
remote: Total 268 (delta 124), reused 202 (delta 64), pack-reused 0
Receiving objects: 100% (268/268), 774.44 KiB | 5.16 MiB/s, done.
Resolving deltas: 100% (124/124), done.
~$ sudo cp SwimSpa/Python/*.py /SpaController/
~$ sudo chown -R iobroker:iobroker /SpaController 
~$ ls -la /SpaController 
total 56
drwxr-xr-x  2 iobroker iobroker 4096 Apr  2 11:51 .
drwxr-xr-x 23 root     root     4096 Apr  2 11:37 ..
-rw-r--r--  1 iobroker iobroker 9147 Apr  2 11:51 spa_config.py
-rw-r--r--  1 iobroker iobroker 4353 Apr  2 11:51 spa_setTargetTemp.py
-rw-r--r--  1 iobroker iobroker 4844 Apr  2 11:51 spa_setWatercareMode.py
-rw-r--r--  1 iobroker iobroker 5022 Apr  2 11:51 spa_switchPump.py
-rw-r--r--  1 iobroker iobroker 4064 Apr  2 11:51 spa_toggleLight.py
-rw-r--r--  1 iobroker iobroker 7566 Apr  2 11:51 spa_updateBulk.py
```

Die Python-Skripte werden von den Javascript-Skripten aus aufgerufen mit den nötigen Parametern.<br>

**Wichtig:** ioBroker benötigt Zugriff auf die Python-Skripte, der Ablageort kann z.B. auch `/opt/iobroker/node_modules/iobroker.javascript` sein, das könnte allerdings mal Probleme mit Adapter oder ioBroker Updates geben.

### Javascript Skripte für ioBroker

#### Voraussetzungen

* Adapter: "Simple RESTful API" installiert und eine konfigurierte Instanz am laufen (bitte prüfen, dass die IP in der Instanzkonfiguration passend eingestellt ist, getestet sind die Skripte mit IPv4, egal ob 0.0.0.0 oder die IP des Netzwerkadapters)
* Adapter: Javascript/Blockly installiert und eine Instanz am laufen
* Konfiguration des Javascript Adapters anpassen:
  * Option: Enable Command "setObject" - ist aktiviert
  * Option: Enable Command "exec" - ist aktiviert

#### Schritt 1: Skript SpaGlobal.js bereitstellen

* "Expert Mode" im Adapter aktivieren, damit der Ordner `global` angezeigt wird
* im Ordner `global` ein neues Skript `SpaGlobal` anlegen und den Inhalt der Datei [SpaGlobal.js](JavaScript/global/SpaGlobal.js) hineinkopieren und evtl. Konfiguration anpassen:


| **Variable**        | **Verwendungszweck/Wert**                                                                                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `BASE_ADAPTER`      | Basispfad zum Adapter unter dem die Datenpunkte angelegt werden. Standard ist der erste Javascript Adapter: "javascript.0".  |
| `BASE_FOLDER`       | Basispfad unter dem die Datenpunkte angelegt werden sollen, Standardwert ist: "Datenpunkte.SwimSpa"                          |
| `SPA_EXECUTEABLE`   | Auszuführendes Programm, Standard ist "python3"                                                                             |
| `PY_SCRIPTS_FOLDER` | Verzeichnis in dem sich die Python-Skripte befinden. Standard ist`/SpaController` damit das mit der Anleitung zusammenpasst. |

#### Schritt 2: Erstellen bzw. Aktualisieren der Datenpunkte

* Neuen Ordner `Spa` im Javascript Adapter anlegen um alle folgenden Skripte an einen Ort zu abzulegen
* Neues Skript `SpaVariablen` in diesem Ordner anlegen und den Inahlt von [SpaVariablen.js](JavaScript/SpaVariablen.js) einspielen
* den Aufruf der Funktion createDatapoints() anpassen:


| **Parameter** | **Wert**                                       |
| --------------- | ------------------------------------------------ |
| 1             | Anzahl Spa Controller im Netz, typ. Weise: 1   |
| 2             | Anzahl Pumpen pro Spa Controller, typ. Weise 3 |
| 3             | Datenpukte für Wasserfall mit anlegen         |

* Nach dem Speichern, das Script 1x ausführen
* Prüfen ob die Datenpunkte vorhanden sind, der Objektbau sollte so aussehen:
  ![Datenpunkte im Objektbaum](doc/img/Datenpunkte_im_Objektbaum.png)

#### Schritt 3: Skripte für Spa Controller Konfiguration und Update der Zustände

Konfigurationswerte, die sich seltener ändern werden alle 6h von `SpaUpdateConfig` aktualisiert:

* Neues Skript: `SpaUpdateConfig` im Ordner `Spa` erstellen und den Inhalt von [SpaUpdateConfig.js](JavaScript/SpaUpdateConfig.js) einfügen
* Die Javascript Funktion: `updateSpaConfig()` wird beim speichern 1x ausgeführt, danach aller 6h.
* Jetzt prüfen ob die Datenpunkte die eher statische Konfigurationswerte darstellen, wie (z.B.: Temepratureinheit, ID, U_ID) aktualisiert worden sind

<br> 
Werte die sich häufig ändern werden minütlich von `SpaUpdateValues` aktualisiert:

* Neues Skcript: `SpaUpdateValues` im Ordner `Spa` erstellen und den Inhalt von [SpaUpdateValues.js](JavaScript/SpaUpdateValues.js) einfügen
* Das Skript wird minütlich aufgerufen und aktualisiert alle anderen Werte wie z.B. die Wassertemperaturen, Pumpenstatus, Licht usw.
* Jetzt überprüfen, on die Wassertemperatur aktualisiert wurde

#### Schritt 4: Weitere Skripte nach Bedarf

* Falls nicht vorhanden einen neuen Ordner `Spa` im JavaScript-Adapter anlegen (um die Skripte etwas zu sortieren)
* Skripte bereitstellen:


| **Zweck**                                   | **Javascript**                                                                       | **Python Skript**                                                               |
| --------------------------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Schalten der Pumpen                         | `PumpSwitches` (Datei: [PumpSwitches.js](JavaScript/PumpSwitches.js))                | `spa_switchPump.py clientId restApiUrl spaId spaIP pumpId newPumpState pumpChannel`   |
| Schalten der Beleuchtung                    | `LightToggle` (Datei: [LightToggle.js](JavaScript/LightToggle.js))                   | `spa_toggleLight.py clientId restApiUrl spaId spaIP lightKey lightChannel`            |
| Setzen der Zieltemperatur                   | `TargetTemp` (Datei: [TargetTemp.js](JavaScript/TargetTemp.js))                      | `spa_setTargetTemp.py clientId restApiUrl spaId spaIP targetTemp targetTempDatapoint` |
| Setzen des Wasserpflegemodus                | `WatercareMode` (Datei: [WatercareMode.js](JavaScript/WatercareMode.js))             | `spa_setWatercareMode.py clientId restApiUrl spaId spaIP waterCareModeIdx devicePath`          |
| Automaische Nachführung der Zieltemperatur | `SpaMoveTargetTemp` (Datei: [SpaMoveTargetTemp.js](JavaScript/SpaMoveTargetTemp.js)) | nicht benötigt                                                                 |

**Hinweis:** Wenn im vorhergehenden Schritt bei BASE_ADAPTER bzw. BASE_FOLDER abweichende Pfade angegeben worden sind, müssen diese in den on()-Aufrufen ebenfalls angepasst werden.

## Fehler und Sonderfälle

### SpaUpdateValues.js/spa_updateBulk.py

Diese Skripte werden jede Minute gestartet (Zeile 4 in `SpaUpdateValues.js`) um Änderungen von Werten wie z.B. der Wassertemperatur, Pumpenstatus usw. vom SpaController auszulesen. Von den 1.440 Aufrufen pro Tag schlagen bei mir lt. Protokoll: ~50 Aufrufe fehl. Eine Quote so in der Höhe, vielleicht bis zu 200 je Tag, kann als normal betrachtet werden. Das hängt u.a. damit zusammen wie die geckolib mit dem SpaController kommuniziert, dann natürlich das minütliche pollen, vielleicht noch die App die parallel was tut, leider jenseits von perfekt von der Implementierung her :-(.

### Kein SpaController gefunden, wenn ioBroker im Docker Container läuft

Wenn ioBroker in einem Docker Container betrieben wird funktioniert ie automatische Erkennung der SpaController nicht, da dies auf einem Broadcast beruht und der Container in einem separaten Netzsegment läuft. Für diese Fälle gibt es den Datenpunkt: `javascript.0.Datenpunkte.SwimSpa.discoverIP` in dem in diesem Fall die IP-Adresse bzw. eine Komma separierte Liste von IP-Adressen der SpaController hinterlegt werden kann.
Dieser Datenpunkt kann auch verwendet werden, wenn sich die SpaController in einem nicht per Broadcast erreichbaren Netzwerksegment befinden. 

## Visualisierung

[Hier](doc/visualization.md) mal ein Beispiel für eine Visualisierung mit vis im ioBroker.

# Todo's

* [X] Momentan ist der Pfad zu den Datenpunkten in den Python Scripten noch fest codiert - umstellen auf Parameter nötig
* [X] Die URL vom ioBroker Rest API muss als Parameter mit übergeben werden
* [X] Alle Python Skripte sollen ohne Konstanten aufrufbar sein
* [X] Statt cron soll der regelmäßige Aufruf mit ioBroker Schedule möglich sein
* [X] Status der Erreichbarkeit des Spa in Datenpunkt darstellen (Ebene Netzwerk, Online/Offline), sowie Fehler bei letzten Kommando
* [ ] Richtiges Discovery der Eigenschaften des Spa Controllers anstatt feste Anlage der Datenpunkte via Skript
* [X] Das setzen der Zieltemperatur ist empfindlich ggü. mehreren schnell auseinanderfolgenden Wertänderungen. Momentan am besten einen Slider nutzen, der eine Funktion "Update value on release" untersützt, so dass der DP nur einmal geändert wird. Das Script braucht immer ein paar Sekunden bis der Wert im Hintergrund gesetzt wurde.
* [X] Aktuell funktionieren die Erinnerungen nicht, da die geckolib keine Werte zurückgibt
* [X] Das Auslösen einer Aktion (Licht an/aus, Pumpe an/aus) braucht ca. 15 Sekunden bis es umgesetzt ist (liegt am Verbindungsaufbau der recht lange dauert bei der geckolib)
* [X] Pfad zu den Python Skripten global konfigurierbar machen und die Anleitung dahingehend anpassen (auch Skriptbereitstellung)
* [ ] Struktur der Datenpunkte noch mal etwas straffen:
  * [X] `javascript.0.Datenpunkte.SwimSpa.x.WasserpflegeIndex` -> entfällt zugunsten `WasserpflegeSwitch`
  * [ ] ...
* [ ] Python Scripte melden keine Statustexte mehr in Datenpunkte:
  * [X] `javascript.0.Datenpunkte.SwimSpa.x.Wasserpflege` -> entfällt zugunsten`WasserpflegeSwitch`, den zugehörigen z.B. deutschen Statustext kann ein Widget selbst darstellen (z.B. vis basic - ValueList Text oder eine Combobox)
  * [ ] ...
* [ ] Statussensor (`javascript.0.Datenpunkte.SwimSpa.x.Sensoren.Status.State`) Funktion herstellen (funktioniert momentant überhaupt nicht bzw. zeigt immer: Connected)
* [X] Nutzbarkeit im Docker Container herstellen (durch die besonderen Netzwerksituation geht Discovery nicht und auch die Steuerung)
