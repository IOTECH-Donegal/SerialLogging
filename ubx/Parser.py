'''
Parser for UBX sentences.
Only sentences used are coded for.
'''


def nav_relposned(ubx_payload):
    '''
    :param ubx_payload:
    :return: relPosHeading_in_deg
    '''

    debug = 0

    if debug == 1:
        # Version = 1
        version = ubx_payload[0]
        # Reserved = 0
        reserved = ubx_payload[1]
        # Station ID = 00 00
        refStationId = ubx_payload[2:3]
        # Format U4
        iTOW = ubx_payload[4:7]
        iTOW_in_ms = int.from_bytes(iTOW, "little", signed=False)
        # North, Format I4
        relPosN = ubx_payload[8:11]
        relPosN_in_cm = int.from_bytes(relPosN, "little", signed=True)
        # East, Format I4
        relPosE = ubx_payload[12:15]
        relPosE_in_cm = int.from_bytes(relPosE, "little", signed=True)
        # Down, Format I4
        relPosD = ubx_payload[16:19]
        relPosD_in_cm = int.from_bytes(relPosD, "little", signed=True)
        # Length, Format I4
        relPosLength = ubx_payload[20:23]
        relPosLength_in_cm = int.from_bytes(relPosLength, "little", signed=False)

        print(f'Version {version}')
        print(f'Reserved {reserved}')
        print(f'Referece Station {refStationId}')
        print(f'iTOW {iTOW_in_ms}')
        print(f'Relative North {relPosN_in_cm}')
        print(f'Relative East {relPosE_in_cm}')
        print(f'Relative Down {relPosD_in_cm}')
        print(f'Relative Length {relPosLength_in_cm}')

    # Heading, Format I4 scaled by 1e-5
    relPosHeading = ubx_payload[24:27]
    relPosHeading_in_deg = int.from_bytes(relPosHeading, "little", signed=False) / 100000

    return relPosHeading_in_deg

'''
8-bit Fletcher algorithm, which is used in the TCP standard RFC 1145
From UBlox Interface Descrip[tion manual
'''
def crc(ubx_payload):
    crc_a = 0
    crc_b = 0

    for byte in ubx_payload:
        crc_a += byte
        crc_a &= 0xFF
        crc_b += crc_a
        crc_b &= 0xFF
    return crc_a, crc_b