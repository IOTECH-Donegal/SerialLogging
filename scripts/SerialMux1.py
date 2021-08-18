""""
Main routine for Serial Mux
Forked from the Comm module of SD-Node, written c. 2017
Takes a serial input and logs, optionally, forward to a UDP address:port
Tested with Python >=3.6

By: JOR
    v0.1    26APR20     First in this iteration.
    v0.2    24MAY20     Removed all complexity, threading, etc.
    v0.3    06JUN20     Modified as a single serial logger
    v0.4    20FEB21     Modified and updated, changed logging style
    v0.5    30JUL21     Updated for AndiamoPort
"""

from datetime import datetime
import sys
import socket
import serial

print('***** SerialMux1 *****')
print('Accepts data from a serial port and:')
print('1. Saves with a date/time named logfile')
print('2. Outputs to a mixed IP address and port for other applications to use.')

# Create the log file and open it
def logfilename():
    now = datetime.now()
    return 'SerialLogger-%0.4d%0.2d%0.2d-%0.2d%0.2d%0.2d.nmea' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)


# For Windows
output_filename = logfilename()
# For RPi
#output_filename = "/home/pi/Logfiles/" + logfilename()

output_file = open(output_filename, 'a', newline='')

# Open a UDP server, even through we will not receive
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Hard code the destination port, expect KPlex, but can be anything
# Note that KPlex will not work with high precision GPS
kplex_IPv4 = "127.0.0.1"
kplex_Port = 2001
print("Expecting to find UDP receiver at " + kplex_IPv4 + ":" + str(kplex_Port))

# Configure the serial port, this should be ttyS0
Serial_Port1 = serial.Serial(
    # For Windows
    port='COM10',
    # For RPi
    #port='/dev/ttyS0',
    baudrate=38400,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
Serial_Port1.flushInput()

# Main Loop
try:
    print("press [ctrl][c] at any time to exit...")
    while True:
        # Receive data from serial link 1
        read_buffer1 = Serial_Port1.readline().decode('ascii', errors='replace')
        while len(read_buffer1) != 0:
            try:
                current_line = str(read_buffer1)
                if current_line[0] == '$':
                    # Send to UDP server
                    sock.sendto(bytes(current_line, "utf-8"), (kplex_IPv4, kplex_Port))
                    # Log the data
                    output_file.writelines(current_line)
                    print(current_line.strip())
                else:
                    print('Non NMEA line deteted')
            except Exception as error:
                print("Main loop error: ", sys.exc_info()[0])
            finally:
                read_buffer1 = Serial_Port1.readline().decode('ascii', errors='replace')

except KeyboardInterrupt:
    print("\n" + "Caught keyboard interrupt, exiting")
    exit(0)
finally:
    print("Exiting Main Thread")
    exit(0)
