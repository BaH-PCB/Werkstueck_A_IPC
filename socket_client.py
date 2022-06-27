# -------------------------------------------------------------------------------------------------------------------
# title:             Werkstueck_A_IPC_Sockets
# description:       This python program is enabling inter process communication via
#                    the socket method for Win OS using a client server architecture.
#                    This program file represents the client in that architecture.
#                    Four communicating processes are implemented:
#                    First, client: Conv will generate a random number to simulate A/D-Converter,
#                    Second, server: Log will save Converter number in text file,
#                    Third, server: Stat will calculate Converter numbers sum and average,
#                    Fourth, client: Report will print Stat results in the shell.
#                    The program will exit by SIGINT or Ctrl-C.
# author:            Arne Chris Mueller (1302448)
# team:              Arne, Jay, Falko, Franz
# url:               ----------------------
# date:              June 26th 2022
# version:           1.0
# notes:             This client program creates a socket and connects to
#                    the server program, so the server needs to be started first.
#                    The server program creates a socket as well to establish the connection.
#                    The client generates numbers and sends them to the server,
#                    the server writes those numbers in a log file, calculates sum and average,
#                    and sends the results back to the client, while the client prints the results.
# -------------------------------------------------------------------------------------------------------------------

import socket
import random
from time import sleep
from signal import signal, SIGINT
from sys import exit


# ------------------------------------------------------Processes----------------------------------------------------
def conv_send_process():
    # Conv process for generating random numbers and sending them to the server using socket connection
    random_number = random.randint(0, 100)                                  # Random number between 0 and 100
    client_socket.send(str(random_number).encode('utf8'))                   # Send utf8-encoded string number to server
    print('Conv   - Gesendeter Zahlenwert: ' + str(random_number) + '\n')   # Print notification


def report_recv_process():
    # Report process for getting sum and average from server using socket connection
    data = client_socket.recv(4096)                                         # Receiving encoded data from server
    (report_recv) = data.decode('utf8')                                     # Write utf8-decoded data in variable
    print(report_recv)                                                      # Print that data as string
    print('\n----------------------------------------\n')


def handler(signal_received, frame):
    # SIGINT or Ctrl-C will trigger a graceful exit and cleanup while connections are getting closed
    print("\nStrg-C oder SIGINT Befehl wurde empfangen, Programm wird beendet.\n")
    client_socket.close()
    exit(0)


# --------------------------------------------------------Main-------------------------------------------------------
if __name__ == '__main__':

    # Client socket gets created using internet protocol and tcp with loopback ip-address, to connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Open socket with internet protocol and tcp
    server_addr = ('127.0.0.1', 51337)                                  # Assign loopback ip-adress and port

    # Client trys to connect to server.py program with previously defined server adress
    client_socket.connect(server_addr)
    print('\n----Verbindung zu Server hergestellt----\n\n')             # Connection notification

    # Endless loop starts going into each process
    while True:
        signal(SIGINT, handler)                                         # SIGINT process
        conv_send_process()                                             # Conv process, sending random numbers
        report_recv_process()                                           # Report process, printing sum and average
        sleep(1)                                                        # Run through loop every second
