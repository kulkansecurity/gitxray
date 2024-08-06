# Calling this Ugly because I can, but also because it assumes more than it should. 
# Made this with trial and error, and love.
# Oh, and why write our own? Rather reinvent the wheel in this case than rely on more ext dependencies.
import re, base64, datetime

def ugly_inhouse_ssh_signature_block(armored_ssh_signature):

    # Bring down the armor! Expose thy binary signature.
    base64_str = re.sub(r'-----BEGIN SSH SIGNATURE-----', '', armored_ssh_signature)
    base64_str = re.sub(r'-----END SSH SIGNATURE-----', '', base64_str)
    base64_str = re.sub(r'\s+', '', base64_str)

    decoded_blob = base64.b64decode(base64_str.encode('ascii', 'ignore'))
   
    # This appears to be standard
    if decoded_blob[:6] == b"SSHSIG":
        # Yet this offset here is likely too hardcoded
        algorithm_length = int(decoded_blob[17])
        # The length of the algorithm helps us get the entire string.
        algorithm = decoded_blob[18:18+algorithm_length]
        return {"ssh_signature_algorithm":algorithm}

    return None

def ugly_inhouse_ssh_key(ssh_key):
    # First keep the algorithm
    algorithm_match = re.match(r'^(\S+)', ssh_key)

    # Then just split with space and decode the second part
    # Stopped here; but eventually we could parse multiple formats to get key strength at least?
    # decoded_blob = base64.b64decode(ssh_key.split()[1].encode('ascii', 'ignore'))

    # fingerprint = sha256(decoded_blog)
    if algorithm_match: 
        return algorithm_match.group(1) 

    return None
