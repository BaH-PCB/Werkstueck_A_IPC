from multiprocessing.dummy import Process
from multiprocessing import Queue
from time import sleep
from random import randint
from signal import SIGINT, signal
from sys import exit


# ----------------------------------------------------------------------------------
# title:             Werkstueck_A_IPC_SharedMemory
# description:       This python program is enabling inter process communication
#                    via Message Queues for Windows operating systems
#                    Four communicating processes are implemented
#                    First, Conv will generate a random number to simulate A/D-Converter
#                    Second, Log will save Converter number in text file
#                    Third, Stat will calculate Converter numbers sum and average
#                    Fourth, Report will print Stat results in the shell
# author:            Falko-Hennig Roderich Claus Koening (1404113)
# team:              Arne, Jay, Falko, Franz
# url:               ----------------------
# date:              June 26th 2022
# version:           1.0
# gcc_version:       ----------------------
# compile_with:      ----------------------
# ----------------------------------------------------------------------------------

# Conv generates a random number and sends it to log and stat via Messages Queue(q)
def conv(q):
    while True:  # loop
        abc = randint(1, 100)  # generating random number between 1 and 100
        q.put(abc)  # adds the random number to the Queue
        sleep(0.8)  # Numbers are generated every 0.8 seconds


# Log will save the random generated number from Conv and saves it in a textfile
def log(q):
    while True:  # loop
        abc = str(q.get())  # receiving the random number through the Message Queue(q)
        with open('log.txt', 'a') as numbers:  # open/creates a text file in append mode
            numbers.write(abc + "\n")  # writes the random number into the textfile and saves it that way
            numbers.close()
            sleep(0.8)  # Random Number is saved every 0.8 seconds


# Stat frequently calculates the Sum and Average of Random Numbers generated in Conv
# Stat will pass the Sum and Average on to Report via Message Queue(q2, q3)
def stat(q, q2, q3):
    stats = []  # creates array
    while True:
        value = q.get()  # receiving the random number through the Message Queue(q)
        stats.append(value)  # adds the random number to the array stats
        stats_sum = sum(stats)  # calculates the sum
        stats_average = stats_sum / len(stats)  # calculates the average
        q2.put(stats_sum)  # adding the sum to the Message Queue(q2)
        q3.put(round(stats_average))  # adding the average to the Message Queue(q3)
        sleep(0.8)

    # Report receives the Sum and Average Values calculated in Stat via Message Queue(q2, q3) and prints it


def report(q2, q3):
    while True:  # loop
        print("Summe: ", q2.get(), "\nDurchschnitt: ", q3.get(), "\n")  # printing


# Didnt work, i believe because i use windows and SIGINT is for linux
# def handler(signal_received, frame):
# pconv.terminate()
# plog.terminate()
# pstat.terminate()
# prep.terminate()
# exit(0)


if __name__ == '__main__':
    # Created Message Queues
    q = Queue()
    q2 = Queue()
    q3 = Queue()

    # Declares Functions as Processes
    pconv = Process(target=conv, args=(q,))
    plog = Process(target=log, args=(q,))
    pstat = Process(target=stat, args=(q, q2, q3))
    prep = Process(target=report, args=(q2, q3))

    # signal(SIGINT, handler) doesnt work
    print('Press Ctrl+C to stop the Programm')  # pressing ctrl + c wont stop the programm

    # .start() starts the Processes
    pconv.start()
    plog.start()
    pstat.start()
    prep.start()

    # .join() coordinates the synchronization between the processes
    # conv has to generate a random number before log and stat can work with it
    # stat has to calculate sum and average before report can print it
    pconv.join()
    plog.join()
    pstat.join()
    prep.join()
