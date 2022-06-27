import multiprocessing
from signal import signal, SIGINT
from random import randint
from time import sleep
from sys import exit

# ----------------------------------------------------------------------------------
# title:             Werkstueck_A_IPC_SharedMemory
# description:       This python program is enabling inter process communication
#                    via the shared memory method for Windows operating systems
#                    Four communicating processes are implemented
#                    First, Conv will generate a random number to simulate A/D-Converter
#                    Second, Log will save Converter number in text file
#                    Third, Stat will calculate Converter numbers sum and average
#                    Fourth, Report will print Stat results in the shell
#                    Program will exit by SIGINT or Ctrl-C
# author:            Franz Blaschke (1398669)
# team:              Arne Müller, Jay, Falko, Franz Blaschke
# date:              June 9th 2022
# ----------------------------------------------------------------------------------


def conv():
    #   Converter generates a random number and sends it to log and stat
    lap_counter = 0
    while True:
        lap_counter += 1
        random_integer = randint(0, 100)  # Generates random number
        sleep(0.8)  # Numbers are generated every 0.8 seconds

    #   Random number shared memory variable is created
        shm_numbers = multiprocessing.Value('i', random_integer)
    #   Connects to log and provides the random number via shared memory
        log1 = multiprocessing.Process(target=log, args=(shm_numbers,))
        log1.start()
    #   Stops current process and waits until new one, log, is finished
        log1.join()

    #   Same procedure for the stat process, provides random number plus a lap counter
        shm_lapcounter = multiprocessing.Value('i', lap_counter)
        stat1 = multiprocessing.Process(target=stat, args=(shm_numbers, shm_lapcounter))
        stat1.start()
        stat1.join()


# ----------------------------------------------------------------------------------


def log(shm_numbers):
    #   Log will protocol all converter numbers in a textfile
    print("\n\nConverter Zahl von Log:    ", str(shm_numbers.value))  # print a proof
    #   Saves converter number in logData.txt
    with open("logData.txt", "a") as log_file:
        log_file.write(str(shm_numbers.value) + "\n")
        log_file.close()


# ----------------------------------------------------------------------------------


def stat(shm_numbers, shm_lapcounter):
    #   Stat recieves converter numbers and calculates sum and average
    #   Stat passes that data on to report via shared memory
    with open("statData.txt", "r") as stat_file:  # statData.txt will hold last sum
        total = shm_numbers.value + int(stat_file.read())  # Calculate sum
        average = total / shm_lapcounter.value  # Calculate average

    #   Deletes old sum and write in new one
    with open("statData.txt", "w+") as stat_file:
        stat_file.write(str(total))

    #   Connect to report and pass on sum, average and lap counter
    shm_total = multiprocessing.Value('i', total)
    shm_average = multiprocessing.Value('d', average)
    report1 = multiprocessing.Process(target=report, args=(shm_total, shm_average, shm_lapcounter))
    report1.start()
    report1.join()


# ----------------------------------------------------------------------------------


def report(shm_total, shm_average, mul_pro_lapcounter):
    #   Report will output statistical data to the shell
    print("Report Nummer:             ", str(mul_pro_lapcounter.value),
          "\nSumme:                     ", str(shm_total.value),
          "\nMittelwert:                ", str(round(shm_average.value)))


# ----------------------------------------------------------------------------------


def handler(signal_received, frame):
    #   Ctrl-C will trigger a graceful exit and cleanup
    print("\n\nStrg-C Befehl wurde empfangen, Programm wird beendet.\n")
    log_file = open("logData.txt", "w+")
    log_file.close()
    stat_file = open("statData.txt", "w+")
    stat_file.close()
    exit(0)


# ----------------------------------------------------------------------------------


if __name__ == '__main__':
   print("\nPortfoliopruefung - Werkstueck A - Alternative 1\n"
         "Programm startet\n"
         "Strg-C fuehrt zum Programmabbruch")
   stat_file = open("statData.txt", "w+")
   stat_file.write("0")  # Provide an initial value for stats sum calculation
   stat_file.close()
   signal(SIGINT, handler)
   conv()


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------