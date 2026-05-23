# Inhalt
<!-- TOC -->

- [Inhalt](#inhalt)
- [Beispiel für eine Visualisierung](#beispiel-f%C3%BCr-eine-visualisierung)
- [Elemente zu Steuerung eines Spa Controllers](#elemente-zu-steuerung-eines-spa-controllers)
    - [1. Temperaturen und sonstige Werte](#1-temperaturen-und-sonstige-werte)
    - [2. Auswahl des Wasserpflegemodus](#2-auswahl-des-wasserpflegemodus)
    - [3. Zieltemperatur](#3-zieltemperatur)
    - [4. Schalten von Licht](#4-schalten-von-licht)
    - [5. Pumpen- oder Filterstatus](#5-pumpen--oder-filterstatus)

<!-- /TOC -->


# Beispiel für eine Visualisierung

![Visualisierung auf 10 Zoll Display](img/tablet_visualization.png)
Visualisierung für ein 10 Zoll Display horizontal. Parktisch kann jedes beliebige Widget verwendet werden. Es ist wichtig, dass die Datenpunkte selbst mit ack = false gesetzt werden (das ist eigentlich das Standardverhalten).

Der Chart ist mit eChart erstellt, die Datenpunkte können z.B. mit dem "SQL logging" Adapter in einer mariaDB aufgezeichnet werden (geht aber praktisch auch alles andere was ioBroker unterstürzt).


# Elemente zu Steuerung eines Spa Controllers
## Temperaturen und sonstige Werte
Basic Number Widget:<br>
![Basic Number Widget](img/basic-number.png)<br>

Konfiguration: <br>
![Basic Number Widget Attributes](img/basic-number_attributes.png)<br>

## Auswahl des Wasserpflegemodus
inventwo design: Universal (Schalter, Taster, Nav & mehr):<br>
![inventwo design Universal](img/Modus_Auswahl.png)<br>

Konfiguration: <br>
![inventwo design Universal Attribute](img/Modus_Auswahl_Attribute.png)<br>

## Zieltemperatur
inventwo design: Schieberegler: <br>
![inventwo_design_Schieberegler](img/inventwo_design_Schieberegler.png)<br>

Konfiguration: <br>
**Wichtig:** Der Slider darf den Wert erst am Ende setzen (Option: "Update value on release" unbedingt aktivieren!)
![inventwo_design_Schieberegler_Attribute](img/inventwo_design_Schieberegler_Attribute.png)

## Schalten von Licht
vis-inventwo - Universal Switch: <br>
![vis-inventwo - Universal Switch](img/vis-inventwo-Universal_Switch.png)<br>
Diese Button müsste sich auch für Pumpen eignen, die nur 2 Stufen (OFF & HIGH) haben, da man den Wert beinflussen kann.

Konfiguration: <br>
![vis-inventwo - Universal Switch Attributes Part1](img/vis-inventwo-Universal_Switch_attributes_part1.png)
![vis-inventwo - Universal Switch Attributes Part2](img/vis-inventwo-Universal_Switch_attributes_part2.png)

## Pumpen- oder Filterstatus
vis-Inventwo - Image: <br>
![vis-Inventwo - Image](img/vis-Inventwo-Image.png)<br>

Konfiguration: <br>
![vis-Inventwo - Image Attributes Part1](img/vis-Inventwo-Image_attributes_part1.png)
![vis-Inventwo - Image Attributes Part2](img/vis-Inventwo-Image_attributes_part2.png)