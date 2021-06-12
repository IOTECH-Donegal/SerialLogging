""""
Single serial port logger, forked from the Comm module of SD-Node
Takes a serial input and logs NMEA data, drops all binary data.
Tested with Python >=3.9
By: JOR
    v0.1    26APR20     First go!
    v0.2    24MAY20     Removed all complexity, threading, etc.
    v0.3    06JUN20	    Modified as a single serial logger
    v0.4    12JUN21     Refactored
"""

import sys
import serial

# Create the log file and open it
output_filename = "survey.nmea"
output_file = open(output_filename, 'a', newline='')


# Configure the first serial port, this should be the master GPS
# U-Blox connected directly should be ttyACM0 on a RPi
Serial_Port1 = serial.Serial(
    port='COM4',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    rtscts=True,
    dsrdtr=True,
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
                # Check to see if its a NMEA sentence
                if read_buffer1[0] == '$':
                    current_line = str(read_buffer1)
                    # Log the data
                    output_file.writelines(current_line)
                    # Turn on flush and print for short test runs
                    # output_file.flush()
                    # print('GPS:' + current_line.strip())
                # It could be RTCM3 or UXB, or a malformed message, just continue and ignore
                else:
                    continue
            except Exception as error:
                print("Main loop error: ", sys.exc_info()[0])
            finally:
                read_buffer1 = Serial_Port1.readline().decode('ascii', errors='replace')

except KeyboardInterrupt:
    print("\n" + "Caught keyboard interrupt, exiting")
    output_file.close()
    exit(0)
finally:
    print("Exiting Main Thread")
    exit(0)
