# Calling this Ugly because I can, but also because it assumes more than it should. 
# Made this with trial and error, and love.
# https://www.rfc-editor.org/rfc/rfc4880 - for specs on OpenPGP parsing
# https://cirw.in/gpg-decoder/  - for OpenPGP debugging, cheers to Conrad Irwin
# Oh, and why write our own? Rather reinvent the wheel in this case than rely on more ext dependencies.
import re, base64, datetime
from .gx_definitions import OPENPGP_SIG_TYPES, OPENPGP_PK_ALGOS, OPENPGP_HASH_ALGOS 


# data must point to the first field containing the length of (un)hashed subpackets
def ugly_inhouse_subpacket_parser(data, output_attributes):
    subpackets_length = int.from_bytes(data[:2], byteorder='big')
    subpacket_data_start = 2
    subpacket_data_end = subpacket_data_start + subpackets_length
    subpacket_data = data[subpacket_data_start:subpacket_data_end]
    current_pos = 0
    while current_pos < len(subpacket_data):
        subpacket_length = subpacket_data[current_pos]
        subpacket_type = subpacket_data[current_pos + 1]
        #print(f'{hex(subpacket_type)} subpacket_type found, len is {subpacket_length}')
        if subpacket_type == 16:  # Issuer Key ID subpacket
            key_id_bytes = subpacket_data[current_pos + 2:current_pos + 2 + subpacket_length - 1]
            key_id = key_id_bytes.hex().upper()
            output_attributes.update({"pgp_keyid":key_id})
        if subpacket_type == 2:  # Signature Creation Time subpacket
            # Ensure the subpacket length is enough for 4-byte timestamp
            if subpacket_length >= 5:
                creation_time_data = subpacket_data[current_pos + 2:current_pos + 6]
                creation_time = int.from_bytes(creation_time_data, byteorder='big')
                output_attributes.update({"pgp_signature_creation_time":datetime.datetime.utcfromtimestamp(creation_time)})

        current_pos += subpacket_length + 1

    return subpacket_data_end

def parse_openpgp_fields(decoded_data):
    attributes = {}
    total_bytes = len(decoded_data)

    unhashed_subpackets = False
    if decoded_data[0] & 0x80:  
        if decoded_data[0] & 0x40:  # We assume no unhashed subpackets
            packet_type = decoded_data[0] & 0x3F
        else:  # Supposedly an Old format; it contains unhashed subpackets
            packet_type = (decoded_data[0] & 0x3C) >> 2
            unhashed_subpackets = True

        offset = 3

        version = decoded_data[offset]
        if packet_type == 2:  # Signature packet
            attributes['pgp_signature_version'] = version

            if version == 4:
                offset += 1 
                attributes['pgp_sig_type'] = OPENPGP_SIG_TYPES.get(decoded_data[offset], "Unknown")
                offset += 1 
                attributes['pgp_publicKeyAlgorithm'] = OPENPGP_PK_ALGOS.get(decoded_data[offset], "Unknown")
                offset += 1 
                attributes['pgp_hashAlgorithm'] = OPENPGP_HASH_ALGOS.get(decoded_data[offset], "Unknown")
                offset += 1 

                subpacket_data_end = ugly_inhouse_subpacket_parser(decoded_data[offset:], attributes)
                if unhashed_subpackets: 
                    ugly_inhouse_subpacket_parser(decoded_data[subpacket_data_end+offset:], attributes)

        elif packet_type == 6: # Public key packet
            attributes['key_version'] = version
            offset += 1
            attributes['creation_time'] = int.from_bytes(decoded_data[offset:offset+4], byteorder='big')
            offset += 4 
            if version == 4:
                attributes['pgp_publicKeyAlgorithm'] = OPENPGP_PK_ALGOS.get(decoded_data[offset], "Unknown")
                offset += 1
                # we're going to skip analysis on N for now and go straight to trivial data
                n_length = int.from_bytes(decoded_data[offset:offset+2], byteorder='big') // 8
                offset += 2
                # here comes N but we're going to get past it
                offset += n_length
                # and same for E; all of those RSA CTF challenges giving us 'the look' right now.
                e_length = int.from_bytes(decoded_data[offset:offset+2], byteorder='big') // 8
                offset += 2 
                # here comes E
                offset += e_length

                if offset < total_bytes and decoded_data[offset] == 0x01 and decoded_data[offset+1] == 0xb4:
                    offset += 2
                    userid_length = decoded_data[offset]
                    offset += 1 
                    attributes['userId'] = decoded_data[offset:offset+userid_length].decode('utf-8')
                    

        else:
            print(f'OMG packet_type was: {packet_type} - This was unexpected!!')

    return attributes



# More information on how I'm parsing signature and key blobs in RFC4880 (https://www.rfc-editor.org/rfc/rfc4880)
def ugly_inhouse_openpgp_block(pgp_armored_input):

    # We've found data before in weird places, likely tasty user input.. hidden messages, ..we want to capture them <3
    malformed_beginning = re.search(r'(.+)\r?\n?-----BEGIN', pgp_armored_input.replace('\r','').replace('\n',''), re.MULTILINE)
    malformed_ending = re.search(r'END PGP PUBLIC KEY BLOCK-----\r?\n?(.+)$', pgp_armored_input.replace('\r','').replace('\n',''), re.MULTILINE)
    if malformed_beginning != None or malformed_ending != None: 
        return {
            "malformed_beginning": malformed_beginning.group(1) if malformed_beginning else None,
            "malformed_ending": malformed_ending.group(1) if malformed_ending else None
        }

    # If we get here, there was nothing malformed prior or after the Key. Signatures are created by GitHub so.. unlikely they are broken.
    # And the magic awful parsing begins..

    # format the data a bit by removing unwanted strings and chars, also consider a potential Version
    base64_str = re.sub(r'-----BEGIN PGP SIGNATURE-----|-----BEGIN PGP PUBLIC KEY BLOCK-----', '', pgp_armored_input)
    base64_str = re.sub(r'Charset: (.+)\r?\n?', '', base64_str)
    base64_str = re.sub(r'Version: (.+)\r?\n?', '', base64_str)
    base64_str = re.sub(r'Comment: (.+)\r?\n?', '', base64_str)
    base64_str = re.sub(r'-----END PGP SIGNATURE-----|-----END PGP PUBLIC KEY BLOCK-----', '', base64_str)
    base64_str = re.sub(r'\s+', '', base64_str)

    decoded_blob = base64.b64decode(base64_str.encode('ascii', 'ignore'))

    openpgp_findings = parse_openpgp_fields(decoded_blob)

    # Add any comment and version values from the armored ascii to our findings.
    version_match = re.search(r'Version: (.+)\r?\n?', pgp_armored_input)
    comment_match = re.search(r'Comment: (.+)\r?\n?', pgp_armored_input)
    if version_match: openpgp_findings["armored_version"] = version_match.group(1).replace('\r','').replace('\n','')
    if comment_match: openpgp_findings["armored_comment"] = comment_match.group(1).replace('\r','').replace('\n','')

    return openpgp_findings

