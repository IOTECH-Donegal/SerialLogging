""""
Main routine for Binary Mux
Forked from the Comm module of SD-Node, written c. 2017
Takes a serial input and logs, optionally, forward to a UDP address:port
Tested with Python >=3.6

By: JOR
    v0.1    26AUG21     Modified NMEAMux to log UBX
"""

from datetime import datetime
import serial
import ubx.ClassID as ubc
import ubx.MessageID as ubm
import ubx.Parser


print('***** BinaryMux1 *****')
print('Accepts all data from a serial port and:')
print('1. Saves with a date/time named logfile')
print('2. Outputs to a mixed IP address and port for other applications to use.')

# Create the log file
def nmealogfilename():
    now = datetime.now()
    return '%0.4d%0.2d%0.2d-%0.2d%0.2d%0.2d.nmea' % \
                (now.year, now.month, now.day,
                 now.hour, now.minute, now.second)

# For Windows
output_filename = nmealogfilename()
# For RPi
#output_filename = "/home/pi/Logfiles/" + logfilename()
nmea_output_file = open(output_filename, 'a', newline='')

# Configure the serial port, this should be ttyS0
Serial_Port1 = serial.Serial(
    # For Windows
    port='COM13',
    # For RPi
    #port='/dev/ttyS0',
    baudrate=115200,
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
        byte1 = Serial_Port1.read(1)
        if len(byte1) <1:
            break

        # Check for UBX
        if byte1 == b"\xb5":
            byte2 = Serial_Port1.read(1)
            if len(byte2) < 1:
                break
            if byte2 == b"\x62":
                # Get the UBX class
                byte3 = Serial_Port1.read(1)
                # Get the UBX message
                byte4 = Serial_Port1.read(1)
                # Get the UBX payload length
                byte5and6 = Serial_Port1.read(2)
                # Calculate the length of the payload
                length_of_payload = int.from_bytes(byte5and6, "little", signed=False)
                # Read the buffer for the payload length
                ubx_payload = Serial_Port1.read(length_of_payload)
                ubx_crc = Serial_Port1.read(2)
                # Last two bytes are 2*CRC
                ubx_crc_a_int = int.from_bytes(Serial_Port1.read(1), "little")
                ubx_crc_b_int = int.from_bytes(Serial_Port1.read(1), "little")
                # Calculate CRC using CLASS + MESSAGE + LENGTH + PAYLOAD
                payload_for_crc = byte3 + byte4 + byte5and6 + ubx_payload
                # Go get the two CRCs
                crc_a, crc_b = ubx.Parser.crc(payload_for_crc)
                # Now catch the error if there is one
                if ubx_crc_a_int != crc_a:
                    print(f'CRC_A Error, {ubx_crc_a_int} not equal to {crc_a}')
                    break
                if ubx_crc_b_int != crc_b:
                    print(f'CRC_B Error, {ubx_crc_b_int} not equal to {crc_b}')
                    break

                if byte3 in ubc.UBX_CLASS:
                    if ubc.UBX_CLASS[byte3] == 'NAV':
                        if byte4 in ubm.UBX_NAV:
                            print(f'UBX:{ubm.UBX_NAV[byte4]}')

        # Check for NMEA0183, leading with a $ symbol
        elif byte1 == b"\x24":
            nmea_full_bytes = Serial_Port1.readline()
            nmea_full_string = nmea_full_bytes.decode("utf-8")
            nmea_output_file.writelines(nmea_full_string)
            print(f'NMEA: {nmea_full_string[0:5]}')

        # Check for AIS, leading with a ! symbol
        elif byte1 == b"\x21":
            print(Serial_Port1.readline())

        # Check for RTCM corrections
        elif byte1 == b"\xd3":
            # Find the message length
            byte2and3 = Serial_Port1.read(2)
            # The first 6 bits are reserved, but always zero, so convert the first two bytes directly to int
            length_of_payload = int.from_bytes(byte2and3, "big", signed=False)
            # Read the payload from the buffer
            rtcm_payload = Serial_Port1.read(length_of_payload)
            # Locate the message ID and convert it to an INT, its 12 bits of 16 so divide by 16
            message_id_bytes = rtcm_payload[0:2]
            message_id_int = int.from_bytes(message_id_bytes, "big")/16
            print(f'RTCM3: {str(message_id_int)}')
            # Finally extract the RTCM CRC
            rtcm_crc = Serial_Port1.read(3)

        # Unhandled spurious byte
        else:
            print(f"What is {byte1}")


except KeyboardInterrupt:
    print("\n" + "Caught keyboard interrupt, exiting")
    nmea_output_file.close()
    exit(0)
finally:
    print("Exiting Main Thread")
    exit(0)
