from gitxray.include import gx_definitions

def run(gx_context, gx_output):
    print("Checking for potential associations across accounts by cross-referencing all gathered data...")

    collisions = gx_context.getCollisions()

    for colType, colValue in collisions:
        affected_accounts = collisions.get((colType, colValue))
        if not affected_accounts: continue
        msg = None

        if colType == "PGP_KEYID" and (colValue not in gx_definitions.GITHUB_WEB_EDITOR_SIGNING_KEYS):
                msg = f"WARNING: A Personal/Private PGP Key with ID {colValue} found shared by accounts: {affected_accounts}."
        elif colType == "PGP_SCT":
            msg = f"PGP Signature Creation Time ({colValue}) shared by accounts: {affected_accounts}."
        elif colType == "PGP_SUBKEY_CREATED_AT":
            msg = f"The following contributor accounts have PGP Subkeys that were created in the same day: {affected_accounts}."
        elif colType == "SSH_SIGNING_KEY_CREATED_AT":
            msg = f"The following contributor accounts have SSH signing keys that were created in the same day: {affected_accounts}."
        elif colType == "KEY_ARMORED_VERSION":
            msg = f"Exact same Version field extracted from a Key for accounts: {affected_accounts}: {colValue}."
        elif colType == "KEY_ARMORED_COMMENT":
            msg = f"Exact same Comment field extracted from a Key for accounts: {affected_accounts}: {colValue}."
        elif colType == "EMAIL":
            msg = f"Email {colValue} shared by accounts: {affected_accounts}."
        elif colType == "DAYS_SINCE_CREATION":
            msg = f"The following contributor accounts were created in the same day, precisely {colValue} days ago: {affected_accounts}."

        # Let's only add the result to the repository group
        if msg != None: gx_output.r_log(msg, rtype="association")
        msg = None

        # Let's keep a group of associations under verbose only
        if gx_output.verbose_enabled():
            if colType == "DAYS_SINCE_UPDATED" :
                msg = f"The following contributor accounts were last updated in the same day, precisely {colValue} days ago: {affected_accounts}."
            elif colType == "PGP_HA":
                msg = f"PGP Hash Algorithm ({colValue}) shared by accounts: {affected_accounts}."
            elif colType == "PGP_PKA":
                msg = f"PGP Public Key Algorithm ({colValue}) shared by accounts: {affected_accounts}."
            elif colType == "PGP_KEYID" and colValue in gx_definitions.GITHUB_WEB_EDITOR_SIGNING_KEYS:
                msg = f"GitHub's Web Editor (Key ID: {colValue}) was used by accounts: {affected_accounts}."
            elif colType == "PGP_SIG_TYPE":
                msg = f"PGP Signature Type ({colValue}) shared by accounts: {affected_accounts}."
            elif colType == "SSH_SA":
                msg = f"SSH Signature Algorithm ({colValue}) shared by accounts: {affected_accounts}."

        if msg != None: gx_output.r_log(msg, rtype="association")

    return True
