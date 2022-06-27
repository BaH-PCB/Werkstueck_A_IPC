import sys, signal, setproctitle
from subprocess import Popen, PIPE
from random import randint
from time import sleep


# erstellen und benennen des Prozesses conv(),
# welcher random zahlen in abstand von 1s generieren soll
def conv():
    setproctitle.setproctitle('Conv')  # Prozessnamen mithilfe von setproctitle auf conv() gesetzt
    while True:
        sys.stdout.write(str(randint(0, 100)))  # schreiben von random nummern in einen String
        sys.stdout.write('\n')
        sleep(1)  # 1 sekunde warten bis die nächste Zahl generiert wird


# erstellen und bennen des Prozesses log() welches ein string erstellen sell und in diesen schreiben soll.
# Dafür wird eine variable Output erstellt welche als Speichermedium dienen soll.
def log():
    setproctitle.setproctitle('Log')

    with open('pipe.log', 'w') as f:  # datei öffnen/erstellen im modus w in Stirng f
        f.truncate(0)  # inhalt von String löschen

    while True:
        with open("pipe.log", "a") as log:  # schleife öffen mit append in log()
            output = str(
                sys.stdin.readline())  # output gleichsetzen als string der eine eingabeauffordung durch stdin erhält
            log.write(output)  # Prozess log wird mithilfe von Outpot beschrieben


# erstellen und bennen des Prozesses stat(), welcher die Aufgabe hat den Mittelwert und die summe des Random Zahlen zu generieren.
def stat():
    setproctitle.setproctitle('Stat')
    values = list()  # erstellen einer Liste
    while True:
        output = int(sys.stdin.readline())  # output eingabe aufforderung als int gesetzt zum rechnen
        values.append(output)  # nach jedem schleifendurchgang wird die liste values jeweils mit output erweitert
        values_sum = sum(values)  # Summe berechnen
        values_average = values_sum / len(values)
        sys.stdout.write(f"Average: {values_average:.2f}, Sum: {values_sum}\n")


def report():
    setproctitle.setproctitle('Report')
    while True:
        output = str(sys.stdin.readline())  # werde wieder in eine String einlesen
        sys.stdout.write(output)  # output ausgeben über systemauferoderung stdout


if __name__ == "__main__":  # wenn dieses Programm als Hauptprozess aufgerufen wird soll nachfolgender codeblock ausgeführt werden
    if len(sys.argv) > 1:  # überprüfen ob argv ein elemen enthält
        if sys.argv[1] == "-conv":  # wenn argument vorhanden und gleich conv ist, wird prozessausgeführt.
            conv()
        elif sys.argv[1] == "-log":
            log()
        elif sys.argv[1] == "-stat":
            stat()
        elif sys.argv[1] == "-report":
            report()

    conv_process = Popen(['python3', '-u', 'Pipe.py', '-conv'], stdout=PIPE,
                         text=True)  # pipe wird durch popen geöffnet und definiert. Öffnet eine pipe zum ausgeben von daten. -u direkt ausgeben was erbekommt
    log_process = Popen(['python3', 'Pipe.py', '-log'], stdin=PIPE, text=True,
                        bufsize=1)  # öffnet eine pipe zum lesen von daten. bufsize=0 soll direkt werte ausgeben.
    stat_process = Popen(['python3', '-u', 'Pipe.py', '-stat'], stdin=PIPE, stdout=PIPE, text=True,
                         bufsize=1)  # soll eine pipe zum einlesen besitzen und eine zum ausgeben für report.
    report_process = Popen(['python3', 'Pipe.py', '-report'], stdin=stat_process.stdout, stdout=sys.stdout,
                           text=True)  # repor liest die definierten werte ein und gibt sie aus.

    while True:
        try:
            conv_output = str(
                conv_process.stdout.readline())  # liest die werte in nen string und gibt sie aus. Werte werden übergeben
            stat_process.stdin.write(conv_output)  # eingabeauffprderung wird auf conv_output gesetzt
            log_process.stdin.write(conv_output)  # eingabeaufforderung wird auf conv_output gesetzt
        except KeyboardInterrupt:
            report_process.send_signal(
                signal.SIGINT)  # beendet alle unterprogramme nachdem in der konsole das Hauptprogramm beendet wurde.
            stat_process.send_signal(signal.SIGINT)
            log_process.send_signal(signal.SIGINT)
            conv_process.send_signal(signal.SIGINT)
            exit(1)

