# Werkstueck_A_IPC


SS2022 Projektarbeit Interprozesskommunikation


Arne Chris Müller
Falko-Hennig Roderich Claus Köning
Franz Blaschke
Jasdip Erhart


Abstract
Interprozesskommunikation erlaubt laufenden Prozessen auf einem Betriebssystem eine sichere Art der Kommunikation. Wie die Synapsen eines Gehirns, bieten sie die Infrastruktur für den Austauschen von Nachrichten. In der folgenden Dokumentation wird dieser Mechanismus anhand von vier Varianten der Prozesskommunikation veranschaulicht.

Problemstellung
Die Herausforderung bei der Implementierung von Interprozesskommunikation ist es, diese mit Python auf Windows bzw. Unix Betriebssystemen zu verwirklichen. Anders als mit den für Betriebssystemen üblichen Programmiersprachen, beispielweise C, gibt es hier keine Dokumentationen oder Lösungsansätze, die studiert werden könnten. Eine Lösung musste somit, mit einfachen Beispielen und der Python Docs Dokumentation, eigenständig entworfen werden. Zudem galt es die Simultanverarbeitung von Multicore-Prozessoren oder symmetrische Mehrfachprozessorarchitektur (SMP) zu unterstützen. 



Shared Memory

Um Prozessen auf einem Rechner mit Multicore-Prozessor und Windows Betriebssystem eine Prozesskommunikation zu ermöglichen, gibt es einige Ansätze, die in den folgenden Abschnitten dargestellt werden. Diese Ansätze finden sich unter anderem in dem Python multiprocessing Modul¹, welches seit Python 2.6 eine Lösung für Mehrrechnerverarbeitung von Prozessen bietet⁷.
Die Shared Memory Map⁷ (Value⁸ und Array⁹)
Diese Methode gibt durch den Aufruf multiprocessing.Value (typecode_or_type, args) ein ctype-Objekt zurück, welches aus einem gemeinsamen Speichersegment zugewiesen wird. Wobei der Rückgabewert der Methode in einen Wrapper verpackt ist. Es gilt, diese Methode bei der Verwendung von shared state-Variablen zu vermeiden, besonders beim Einsatz von vielen parallellaufenden Prozessen. Objekte dieser Art sind sowohl vor Prozessen geschützt als auch Thread-sicher.
SharedMemory Klasse²
Mit dieser Klasse können Prozesse ein neues gemeinsames Speichersegment erzeugen oder sich mit einem bereits existierendes Speichersegment verbinden. Die close()⁵ Methode ermöglicht Prozessen sich von dem Speichersegment zu lösen, ohne dieses dabei zu löschen. Ruft ein Prozess die unlink()⁶ Methode auf, wird das Segment gelöscht und der Speicher ordnungsgemäß bereinigt. 
SharedMemoryManager³ Klasse und ShareableList⁴
Das Multiprocessing-Modul stellt noch den SharedMemoryManager als auch die ShareableList zur Verfügung. Wobei der Manager über viele Prozesse hinweg die Verwaltung von gemeinsamen Speichersegmenten ermöglicht. Die ShareableList kreiert und gibt ein Objekt zurück, welches aus einem gemeinsamen Speichersegment zugewiesen wird und einer Python List nicht unähnlich ist. Dazu sei gesagt, dass die SharableList nicht ihre Länge verändern kann und kein slicing erlaubt⁴.
Für die Prozesskommunikation eines A-/D Converters mit einer Funktion zur Dokumentation und einer statistischen Auswertung werden lediglich natürliche Zahlenwerte übermittelt. Nach der statistischen Auswertung wird wiederrum ein ganzer Zahlenwert und zwei natürlich Zahlenwerte an eine Report-Funktion übermittelt.  Da es sich hier um eine einfache und wenig dynamische Anforderung handelt, wird in dem folgenden Projekt das gemeinsame Speichersegment mit der Value Methode erstellt.
Die Main Methode 
Das Programm versorgt den Benutzer zunächst mit generellen Informationen zum Ablauf und erstellt eine Textdatei die später für die Berechnung der Summe mit einer ‘0‘ beschrieben wird. Anschließend wird der Signal-Handler und der Converter-Prozess gestartet.
Der Conv. Prozess
Zur Überwachung der Durchläufe bzw. späteren Berechnung des Mittelwerts initialisieren wir einen Durchlaufzähler lap_counter = 0. 
Die while True Endlosschleife stellt sicher, dass Conv. regelmäßig an die empfangenden Prozesse sendet und zählt mit lap_counter += 1 die Durchläufe. Anschließend wird eine zufällige Zahl zwischen 0 und 100 erstellt und in einer Variabel, namens random_integer, gespeichert. Sleep(0.8) gibt der Schleife einen 0.8 Sekunden Takt vor. 
In jedem Durchlauf wird eine Variable, mit der zufälligen Zahl, in einem Wrapper verpackt und in einem gemeinsamen Speichersegment erzeugt. Dazu wird der Datentyp der Variable, in diesem Fall ‘i‘ für Integer, angegeben und unter dem Namen shm_numbers gespeichert. 

shm_numbers = multiprocessing.Value('i', random_integer)
log1 = multiprocessing.Process(target=log, args=(shm_numbers,))
log1.start()
log1.join()

Anschließend wird ein Prozess, log1, gestartet, welcher wiederrum die log Funktion aufruft und die Variable aus einem gemeinsamen Speichersegment übergibt. 
join() hat die Funktion den Elternprozess zu stoppen¹, bis der Kinderprozess fertig ausgeführt wurde. Dies sorgt in diesem Fall, dass keine Zahl von Conv. erstellt wird, die Log. und Stat. nicht bekommen.  

Der Log. Prozess
Die Aufgabe von Log. ist die prozessübergreifende Datensicherung aller zufälligen Zahlen des Converters. Dazu wird beim ersten Durchlauf eine Textdatei erstellt auf die in den folgenden Durchläufen zugegriffen werden kann. Bei jedem Durchlauf schreibt Log. die Zahl in die Textdatei und schließt diese anschließend.

Der Stat. Prozess
Stat. soll statistische Daten errechnen und diese an einen weiteren Prozess übergeben. Ziel ist, jede Zahl, die der Converter verschickt, aufzusummieren und anschließend den Mittelwert zu bestimmen. Auch hier wird zur prozessübergreifenden Datensicherung eine Textdatei verwendet, welche zu Beginn des Programms in der Main Methode mit einer ‘0‘ beschrieben wurde und nach jedem Durchlauf von Stat. wieder mit der neuen Summe beschrieben wird. 
Aus dieser Textdatei wird die letzte Summe gelesen und mit der zufälligen Conv. Zahl verrechnet. Der Durchlaufzähler ermöglicht anschließend eine Berechnung des Mittelwerts. Die Summe wird anschließend in dem Dokument gespeichert, welches zuvor mit der Berechtigung ‘w+‘ bereinigt wurde. 
Stat. öffnet im weiteren Verlauf ein gemeinsames Speichersegment und übergibt Report den Durchlaufzähler, Mittelwert und Summe. Auch hier wartet Stat. wieder durch den join() Befehl auf die Ausführung von Report.
Report Prozess
Hier werden mit einem Print-Statement die statistischen Daten in der Shell ausgegeben. Um die Lesbarkeit zu steigern, wird hier auch der Durchlaufzähler übermittelt. Somit bleibt der Rechenweg leicht nachzuvollziehen. 

Signalhandler Prozess
Zur ordentlichen Beendigung des Programmes wurde ein Signalhandler für das Abfangen des SIGINT Befehls implementiert. Zur Sicherheit, werden hier auch ein letztes Mal die verwendeten Textdateien geöffnet und ihr Inhalt gelöscht. Danach wird das Programm geschlossen.
Bewertung meiner Ergebnisse
In der Lösung übermitteln alle Prozesse ihre Daten zuverlässig und ausschließlich über gemeinsame Speichersegmente, jede Zahl die der Converter produziert wird auch von Stat., Log. und Report verarbeitet. Alle Prozesse werden mit den für Windows verfügbaren Befehlen in der Simultanverarbeitung ausgeführt, ähnlich wie mit Fork für Unix Betriebssysteme. Die Synchronisation wird durch den join() Befehl garantiert. Das Programm lässt sich wie gefordert in der Kommandozeile ausführen und kann mit Ctrl-C abgebrochen werden. 
Somit lässt sich, außer der für Windows nichtexistierenden Überwachung der Prozesse (top, ps und pstree) und das Freigeben von gemeinsamem Speicher, jede Anforderung erfüllen. 

Fazit
Es wird deutlich, dass Python noch nicht lange zu den für Betriebssystem genutzten Programmiersprachen zählt. Zudem stellt sich heraus, dass Windows nicht die einfachste Plattform für eine solche Aufgabe bietet. So findet man sich an vielen Stellen ohne jegliche Referenz wieder und muss eigene Ideen entwickeln um Problemstellungen zu lösen. Tatsächlich bin ich stolz auf meine Umsetzung obwohl es sicherlich professionellere und dynamische Ansätze gibt.
Würde ich die gleichen Anforderungen ein weiteres Mal umsetzen wollen, wäre ich geneigt dies mit C und Linux zu tun. Generell zeigt mir dieses Projekt auf, wie umständlich die Arbeit mit Windows seien kann, so ist ein probeweiser Betriebssystem-Wechsel eine Konsequenz die ich privat aus dieser Arbeit mitnehmen werde.

Quellen:
1.	https://docs.python.org/3/library/multiprocessing.html
2.	https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.shared_memory.SharedMemory
3.	https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.managers.SharedMemoryManager
4.	https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.managers.SharedMemoryManager.ShareableList
5.	https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.shared_memory.SharedMemory.close
6.	https://docs.python.org/3/library/multiprocessing.shared_memory.html#multiprocessing.shared_memory.SharedMemory.unlink
7.	https://docs.python.org/2.7/library/multiprocessing.html?highlight=shared%20memory
8.	https://docs.python.org/2.7/library/multiprocessing.html?highlight=shared%20memory#multiprocessing.Value
9.	https://docs.python.org/2.7/library/multiprocessing.html?highlight=shared%20memory#multiprocessing.Array



