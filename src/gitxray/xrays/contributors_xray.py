from gitxray.include import gh_api, gh_time, gh_public_events, gx_definitions
from gitxray.include import gx_ugly_openpgp_parser, gx_ugly_ssh_parser 
from datetime import datetime, timezone
from collections import defaultdict
import sys, re, base64

def run(gx_context, gx_output):

    repository = gx_context.getRepository()
    contributor_scope = gx_context.getContributorScope()

    if contributor_scope != None:
        gx_output.notify(f"YOU HAVE SCOPED THIS GITXRAY TO CONTRIBUTORS: {contributor_scope} - OTHER USERS WON'T BE ANALYZED.")

    print(f"Querying GitHub for repository contributors.. Please wait.", end='', flush=True)

    # Let's store the whole set of contributors in the context
    gx_context.setContributors(gh_api.fetch_repository_contributors(repository))

    c_users = []
    c_anon = []

    c_len = len(gx_context.getContributors())
    print(f"\rIdentified {c_len} contributors.." + ' '*70, flush=True)

    # If focused on a contributor, let's first make sure the contributor exists in the repository
    if contributor_scope != None:
        if not gx_context.areContributors(contributor_scope): 
            gx_output.warn(f"One of the collaborators you specified {contributor_scope} were not found as a contributor in the repo.")
            gx_output.warn(f"If you intend to filter results for a non-contributor, using the filter function instead (eg. -f johnDoe03). Quitting..")
            return False

    # Were were invoked to just list contributors and quit?
    if gx_context.listAndQuit():
        gx_output.notify(f"LISTING CONTRIBUTORS (INCLUDING THOSE WITHOUT A GITHUB USER ACCOUNT) AND EXITING..")
        print(", ".join([c.get('login', c.get('email')) for c in gx_context.getContributors()]))
        return False

    if c_len > 500:
        print(f"IMPORTANT: The repository has 500+ contributors. GitHub states > 500 contributors will appear as Anonymous")
        print(f"More information at: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-contributors")

    for i, c in enumerate(gx_context.getContributors()):
        if contributor_scope != None and c.get('login') not in contributor_scope: continue
        print('\rFetching repository contributor details [{}/{}]'.format(i+1, c_len), end='', flush=True)
        ctype = c.get('type')
        if ctype in ["User", "Bot"]:
            c_users.append(gh_api.fetch_contributor(c))
        elif ctype == "Anonymous":
            c_anon.append(c)
        else:
            print(c)
            raise Exception("Contributor of Type !== User/Anonymous found. Failing almost gracefully")

    if contributor_scope == None:
        print(f"\r\nDiscovered {len(c_users)} contributors with Github User accounts, and {len(c_anon)} Anonymous contributors", end='', flush=True)
        gx_output.r_log(f"Repository has {len(c_anon)} Anonymous contributors.", rtype="contributors")
        gx_output.r_log(f"Repository has {len(c_users)} contributors with Github User accounts.", rtype="contributors")

    print(f"\r\nPlease wait, beginning to collect keys and commits for User contributors..", end='', flush=True)

    c_users_index = 1
    for contributor in c_users:
        if contributor is None: continue
        unique_pgp_keyids = []
        contributor_emails = []
        contributor_login = contributor.get('login')
        c_started_at = datetime.now()
        gx_output.c_log(f"X-Ray on contributor started at {c_started_at}", contributor=contributor_login, rtype="metrics")

        print(f"\r[{c_users_index}/{len(c_users)}] Analyzing Profile data for {contributor.get('login')}"+' '*40, end = '', flush=True)
        gx_output.c_log(f"Contributor URL: {contributor.get('html_url')}", rtype="urls")
        gx_output.c_log(f"Owned repositories: https://github.com/{contributor_login}?tab=repositories", rtype="urls")

        if contributor.get('name') != None:
            gx_output.c_log(f"[Name: {contributor.get('name')}] obtained from the user's profile.", rtype="personal")

        if contributor.get('twitter_username') != None:
            gx_output.c_log(f"[X/Twitter account: {contributor.get('twitter_username')}] obtained from the user's profile.", rtype="personal")
        if contributor.get('bio') != None:
            bio = contributor.get('bio').replace("\r\n"," | ")
            gx_output.c_log(f"[Bio: {bio}] obtained from the profile.", rtype="personal")
        if contributor.get('company') != None:
            gx_output.c_log(f"[Company: {contributor.get('company')}] obtained from the user's profile.", rtype="personal")
        if contributor.get('blog') != None and len(contributor.get('blog')) > 0:
            gx_output.c_log(f"[Blog: {contributor.get('blog')}] obtained from the user's profile.", rtype="personal")
        if contributor.get('location') != None:
            gx_output.c_log(f"[Location: {contributor.get('location')}] obtained from the user's profile.", rtype="personal")

        if contributor.get('email') != None:
            gx_output.c_log(f"[{contributor.get('email')}] obtained from the user's profile.", rtype="emails")
            gx_context.linkIdentifier("EMAIL", [contributor.get('email')], contributor_login)

        contributor_created_at_time = gh_time.parse_date(contributor.get('created_at'))
        days_since_account_creation = (datetime.now(timezone.utc) - contributor_created_at_time).days 

        # Let's keep track of when the accounts were created.
        gx_context.linkIdentifier("DAYS_SINCE_CREATION", [days_since_account_creation], contributor_login)

        message = f"{days_since_account_creation} days old"
        if days_since_account_creation > 365:
            years = "{:.2f}".format(days_since_account_creation / 365)
            message = f"{years} years old"

        gx_output.c_log(f"Contributor account created: {contributor.get('created_at')}, is {message}.", rtype="profiling")

        if contributor.get('updated_at') != None:
            days_since_updated = (datetime.now(timezone.utc) - gh_time.parse_date(contributor.get('updated_at'))).days 
            gx_output.c_log(f"The account was last updated at {contributor.get('updated_at')}, {days_since_updated} days ago.", rtype="profiling")
            # Let's keep track of when the accounts were last updated.
            gx_context.linkIdentifier("DAYS_SINCE_UPDATED", [days_since_updated], contributor_login)

        if contributor.get('site_admin') != False:
            gx_output.c_log(f"The account may be an administrator. It has 'site_admin' set to True", rtype="profiling")

        commits = gh_api.fetch_commits(repository, author=contributor.get('login'))
        if commits != None and len(commits) > 0:
            commits_message = f", at {commits[0]['commit']['author']['date']}."
            oldest_commit = commits[-1]['commit']['author']['date']
            if len(commits) > 1:
                commits_message = f", first one at {oldest_commit} and last one at {commits[0]['commit']['author']['date']}."
            gx_output.c_log(f'Made (to this repo) {len(commits)} commits{commits_message}', rtype="commits")

        signed_commits = []
        failed_verifications = []
        signature_attributes = []
        dates_mismatch_commits = []
        commit_times = defaultdict(int)
        print(f"\r[{c_users_index}/{len(c_users)}] Analyzing {len(commits)} commits and any signing keys for {contributor.get('login')}"+' '*40, end = '', flush=True)
        for commit in commits:
            c = commit["commit"]

            v_reason = c["verification"]["reason"]
            if c["verification"]["verified"] == True:
                try:
                    if "BEGIN SSH SIGNATURE" in c["verification"]["signature"]:
                        signature_attributes.append(gx_ugly_ssh_parser.ugly_inhouse_ssh_signature_block(c["verification"]["signature"]))
                    else:
                        signature_attributes.append(gx_ugly_openpgp_parser.ugly_inhouse_openpgp_block(c["verification"]["signature"]))
                except Exception as ex:
                    gx_output.c_log(f"Failed at parsing a signature, not strange due to our ugly parsing code. Here's some more data. {c['verification']['signature']} - {ex}", rtype="debug")

                if v_reason != "valid":
                    gx_output.c_log(f"Unexpected condition - verified commit set to True and reason != 'valid'. Reason is: {v_reason} - Report to dev!", rtype="debug")
                else:
                    signed_commits.append(c)
            elif v_reason != "unsigned":
                if v_reason == "bad_email": 
                    gx_output.c_log(f"The email in the signature doesn't match the 'committer' email: {commit['html_url']}", rtype="signatures")
                elif v_reason == "unverified_email": 
                    gx_output.c_log(f"The committer email in the signature was not Verified in the account: {commit['html_url']}", rtype="signatures")
                elif v_reason == "expired_key": 
                    gx_output.c_log(f"The key that made the signature expired: {commit['html_url']}", rtype="signatures")
                elif v_reason == "not_signing_key": 
                    gx_output.c_log(f"The PGP key used in the signature did not include the 'signing' flag: {commit['html_url']}", rtype="signatures")
                elif v_reason == "gpgverify_error" or v_reason == "gpgverify_unavailable": 
                    gx_output.c_log(f"There was an error communicating with the signature verification service: {commit['html_url']}", rtype="signatures")
                elif v_reason == "unknown_signature_type": 
                    gx_output.c_log(f"A non-PGP signature was found in the commit: {commit['html_url']}", rtype="signatures")
                elif v_reason == "no_user": 
                    gx_output.c_log(f"The email address in 'committer' does not belong to a User: {commit['html_url']}", rtype="signatures")
                elif v_reason == "unknown_key": 
                    gx_output.c_log(f"The key used to sign the commit is not in their profile and can't be verified: {commit['html_url']}", rtype="signatures")
                elif v_reason == "malformed_signature" or v_reason == "invalid": 
                    gx_output.c_log(f"The signature was malformed and a parsing error took place: {commit['html_url']}", rtype="signatures")
                failed_verifications.append(c)

            if c["author"]["email"] not in contributor_emails: 
                gx_output.c_log(f"[{c['author']['email']}] obtained by parsing commits.", rtype="emails")
                contributor_emails.append(c["author"]["email"]) 
                gx_context.linkIdentifier("EMAIL", [c["author"]["email"]], contributor_login)

            commit_date = gh_time.parse_date(c['author']['date'])
            if commit_date < contributor_created_at_time:
                dates_mismatch_commits.append(c)

            # Let's group by commit hour, we may have an insight here.
            commit_times[commit_date.hour] += 1

        if len(dates_mismatch_commits) > 0:
            gx_output.c_log(f"WARNING: UNRELIABLE DATES (Older than Account) in {len(dates_mismatch_commits)} commits by [{contributor_login}]. Potential tampering, account re-use, or Rebase. List at: {repository.get('html_url')}/commits/?author={contributor_login}&until={contributor.get('created_at')}", rtype="commits")
            gx_output.c_log(f"View commits with unreliable DATES here: {repository.get('html_url')}/commits/?author={contributor_login}&until={contributor.get('created_at')}", rtype="commits")
            gx_context.linkIdentifier("DATE_MISMATCH_COMMITS", [len(dates_mismatch_commits)], contributor_login)

        if len(commit_times) > 0:
            # Let's link these commit hours to this contributor, and we'll do extra analysis in the associations X-Ray
            gx_context.linkIdentifier("COMMIT_HOURS", commit_times, contributor_login)

            total_commits = len(commits)
            formatted_output = f"Commit Hours for [{total_commits}] commits:"
            sorted_commit_times = sorted(commit_times.items(), key=lambda item: item[1], reverse=True)
            
            for commit_hour, count in sorted_commit_times:
                percentage = (count / total_commits) * 100
                range_label = gx_definitions.COMMIT_HOURS[commit_hour]
                formatted_output += f" [{range_label}: {count} ({percentage:.2f}%)]"

            gx_output.c_log(formatted_output, rtype="commits")

        # PGP Signature attributes: We have precise Key IDs used in signatures + details on signature creation time and algorithm
        unique_pgp_pka = set(attribute.get('pgp_publicKeyAlgorithm') for attribute in signature_attributes if attribute.get('pgp_pulicKeyAlgorithm') is not None)
        unique_pgp_st = set(attribute.get('pgp_sig_type') for attribute in signature_attributes if attribute.get('pgp_sig_type') is not None)
        unique_pgp_ha = set(attribute.get('pgp_hashAlgorithm') for attribute in signature_attributes if attribute.get('pgp_hashAlgorithm') is not None)
        unique_pgp_sct = set(attribute.get('pgp_signature_creation_time') for attribute in signature_attributes if attribute.get('pgp_signature_creation_time') is not None)
        unique_pgp_keyids = set(attribute.get('pgp_keyid') for attribute in signature_attributes if attribute.get('pgp_keyid') is not None)

        # We don't link SSH Key IDs because SSH keys are unique across Github; PGP keys can be added to more than 1 account.
        gx_context.linkIdentifier("PGP_KEYID", unique_pgp_keyids, contributor_login)
        gx_context.linkIdentifier("PGP_PKA", unique_pgp_pka, contributor_login)
        gx_context.linkIdentifier("PGP_HA", unique_pgp_ha, contributor_login)
        gx_context.linkIdentifier("PGP_SCT", unique_pgp_sct, contributor_login)

        # SSH Signature attributes: We don't have a Key ID so far, but we do have the signature algorithms - hey, it's something! right? right??
        unique_ssh_sa = set(attribute.get('ssh_signature_algorithm') for attribute in signature_attributes if attribute.get('ssh_signature_algorithm') is not None)
        if len(unique_ssh_sa) > 0: gx_output.c_log(f"SSH signatures used Algorithms: [{unique_ssh_sa}] obtained from parsing signature blobs", rtype="keys")
        gx_context.linkIdentifier("SSH_SA", unique_ssh_sa, contributor_login)

        # Let's add signature attributes output.
        if len(unique_pgp_pka) > 0: gx_output.c_log(f"PGP signatures used publicKeyAlgorithms: [{unique_pgp_pka}] obtained from parsing signature blobs", rtype="keys")
        # Based on our testing, Signature Type appears to be always 0 in GitHub: Signature of a binary document - Let's only log if it differs.
        if len(unique_pgp_st) > 0:
            for sigtype in unique_pgp_st:
                if sigtype != "Signature of a binary document": 
                    gx_output.c_log(f"PGP signatures used an atypical signature Type: [{sigtype}] obtained from parsing signature blobs", rtype="keys")
                    # Let's also link the atypical sigtype to the user just in case we spot more accounts using it.
                    gx_context.linkIdentifier("PGP_SIG_TYPE", [sigtype], contributor_login)
        if len(unique_pgp_ha) > 0: gx_output.c_log(f"PGP signatures used hash Algorithms: [{unique_pgp_ha}] obtained from parsing signature blobs", rtype="keys")


        # https://docs.github.com/en/rest/users/gpg-keys?apiVersion=2022-11-28#list-gpg-keys-for-a-user
        # Github calls them GPG keys, but we're going to refer to them as PGP for the OpenPGP standard
        pgp_keys = gh_api.fetch_gpg_keys(contributor_login)
        if pgp_keys != None and len(pgp_keys) > 0:
            primary_key_ids = [key.get('key_id') for key in pgp_keys]
            gx_output.c_log(f"{len(pgp_keys)} Primary PGP Keys in this contributor's profile: {str(primary_key_ids)}", rtype="keys")
            gx_output.c_log(f"PGP Keys: https://api.github.com/users/{contributor_login}/gpg_keys", rtype="keys")

        for primary_key in pgp_keys:
            # Let's parse and drain info from raw_key fields in primary keys
            if primary_key.get('raw_key') != None:
                key_attributes = gx_ugly_openpgp_parser.ugly_inhouse_openpgp_block(primary_key.get('raw_key'))
                if key_attributes.get('malformed_beginning') != None:
                    malformed_beginning = key_attributes.get('malformed_beginning').replace('\r\n',' | ')
                    gx_output.c_log(f"Bogus data found at the beginning of a PGP Key containing: {malformed_beginning}", rtype="user_input")
                if key_attributes.get('malformed_ending') != None:
                    malformed_ending = key_attributes.get('malformed_ending').replace('\r\n',' | ')
                    gx_output.c_log(f"Bogus data found at the end of a PGP Key containing: {malformed_ending}", rtype="user_input")
                if key_attributes.get('userId') != None:
                    gx_output.c_log(f"[{key_attributes.get('userId')}] obtained from parsing PGP Key ID {primary_key.get('key_id')}", rtype="personal")
                if key_attributes.get('armored_version') != None:
                    armored_version = key_attributes.get('armored_version').replace('\r\n',' | ')
                    gx_output.c_log(f"[Version: {armored_version}] obtained from parsing PGP Key ID {primary_key.get('key_id')}", rtype="keys")
                    gx_context.linkIdentifier("KEY_ARMORED_VERSION", [armored_version], contributor_login)
                if key_attributes.get('armored_comment') != None:
                    armored_comment = key_attributes.get('armored_comment').replace('\r\n',' | ')
                    gx_output.c_log(f"[Comment: {armored_comment}] obtained from parsing PGP Key ID {primary_key.get('key_id')}", rtype="keys")
                    gx_context.linkIdentifier("KEY_ARMORED_COMMENT", [armored_comment], contributor_login)

            # Let's add to the colab+key relationship all primary and subkeys from the user profile
            primary_key_id = primary_key.get('key_id')

            # Link this Primary Key ID to the contributor
            if primary_key_id: gx_context.linkIdentifier("PGP_KEYID", [primary_key_id], contributor_login)

            if primary_key.get('name') != None:
                gx_output.c_log(f"Primary key name typed by user for key {primary_key_id}: [{primary_key.get('name')}]", rtype="user_input")

            for email in primary_key.get('emails'):
                if email not in contributor_emails: 
                    message = "(shows as Verified)" if email.get('verified') == True else "(shows as Not Verified)"
                    gx_output.c_log(f"[{email.get('email')}] {message} obtained from primary Key with ID {primary_key_id}", rtype="emails")
                    contributor_emails.append(email)
                    # There's a Verified: False or True field, we link it disregarding if its verified.
                    gx_context.linkIdentifier("EMAIL", [email['email']], contributor_login)
 
            for sub_key in primary_key["subkeys"]:
                sub_key_id = sub_key.get('key_id')
                if sub_key_id: gx_context.linkIdentifier("PGP_KEYID", [sub_key_id], contributor_login)

                if sub_key.get('name') != None:
                    gx_output.c_log(f"Subkey name typed by user for key {sub_key_id}: {sub_key.get('name')}", rtype="user_input")

                for email in sub_key.get('emails'):
                    if email not in contributor_emails: 
                        gx_output.c_log(f"[{email}] obtained from subKey with ID {sub_key_id}", rtype="emails")
                        contributor_emails.append(email)
                        gx_context.linkIdentifier("EMAIL", [email], contributor_login)
 
                if sub_key.get('expires_at') != None:
                    kexpiration = gh_time.parse_date(sub_key.get('expires_at'))
                    if kexpiration < datetime.now(timezone.utc):
                        message = '(EXPIRED)'
                    else:
                        message = f'(EXPIRES in {(kexpiration-datetime.now(timezone.utc)).days} days)'
                else:
                    message = '(DOES NOT EXPIRE)'

                gx_output.c_log(f"PGP Subkey {sub_key.get('key_id')} in profile. Created at: {sub_key.get('created_at')} - Expires: {sub_key.get('expires_at')} {message}", rtype="keys")
                days_since_creation = (datetime.now(timezone.utc) - gh_time.parse_date(sub_key.get('created_at'))).days 
                gx_context.linkIdentifier("PGP_SUBKEY_CREATED_AT", [days_since_creation], contributor_login)

            gx_output.c_log(f'Primary Key details: {primary_key}', rtype="debug")


        # SSH Signing keys 
        # https://docs.github.com/en/rest/users/ssh-signing-keys?apiVersion=2022-11-28#list-ssh-signing-keys-for-a-user
        ssh_signing_keys = gh_api.fetch_ssh_signing_keys(contributor_login)
        if ssh_signing_keys != None and len(ssh_signing_keys) > 0:
            gx_output.c_log(f"{len(ssh_signing_keys)} SSH Keys used for Signatures in this contributor's profile", rtype="keys")
            gx_output.c_log(f"SSH Signing Keys: https://api.github.com/users/{contributor_login}/ssh_signing_keys", rtype="keys")

        for ssh_signing_key in ssh_signing_keys:
            algorithm = gx_ugly_ssh_parser.ugly_inhouse_ssh_key(ssh_signing_key.get('key'))
            gx_output.c_log(f"SSH Signing Key title typed by user for Key ID [{ssh_signing_key.get('id')}]: [{ssh_signing_key.get('title')}]", rtype="user_input")
            algorithm = f"of type [{algorithm}] " if algorithm != None else ""
            gx_output.c_log(f"SSH Signing Key ID [{ssh_signing_key.get('id')}] {algorithm}in profile, created at {ssh_signing_key.get('created_at')}.", rtype="keys")
            days_since_creation = (datetime.now(timezone.utc) - gh_time.parse_date(ssh_signing_key.get('created_at'))).days 
            gx_context.linkIdentifier("SSH_SIGNING_KEY_CREATED_AT", [days_since_creation], contributor_login)

        # SSH Authentication keys
        ssh_auth_keys = gh_api.fetch_ssh_auth_keys(contributor_login)
        if len(ssh_auth_keys) > 0:
            gx_output.c_log(f"{len(ssh_auth_keys)} SSH Authentication Keys in this contributor's profile", rtype="keys")
            gx_output.c_log(f"SSH Authentication Keys: https://api.github.com/users/{contributor_login}/keys", rtype="keys")

        # We don't keep track of duplicate/cloned keys for authentication SSH keys because GitHub won't allow them
        # https://docs.github.com/en/authentication/troubleshooting-ssh/error-key-already-in-use
        for ssh_auth_key in ssh_auth_keys:
            algorithm = gx_ugly_ssh_parser.ugly_inhouse_ssh_key(ssh_auth_key.get('key'))
            algorithm = f"of type [{algorithm}] " if algorithm != None else ""
            gx_output.c_log(f"SSH Authentication Key ID [{ssh_auth_key.get('id')}] {algorithm}in profile.", rtype="keys")

        gx_output.c_log(f"All commits (for this Repo): {repository.get('html_url')}/commits/?author={contributor_login}", rtype="commits")
        # Unique key ids for now only holds keys we've extracted from commit signatures
        if len(unique_pgp_keyids) > 0:
            # https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#constructing-a-search-query
            # Unfortunately Github requires (for other users than our own) to provide (non-regex) input keywords in order to
            # return results in the commits API which accept filtering such as is:signed - and input keywords restrict our results.
            gx_output.c_log(f"{len(unique_pgp_keyids)} Keys ({unique_pgp_keyids}) were used by this contributor when signing commits.", rtype="keys")
            github_keys_used = [keyid for keyid in unique_pgp_keyids if keyid in gx_definitions.GITHUB_WEB_EDITOR_SIGNING_KEYS]
            if len(github_keys_used) > 0:
                gx_output.c_log(f"{len(github_keys_used)} of the keys used to sign commits belong to Github's Web editor {github_keys_used}", rtype="keys")

        if len(commits) == len(signed_commits):
            gx_output.c_log(f"Contributor has signed all of their {len(signed_commits)} total commits (to this repo).", rtype="signatures")

        if len(failed_verifications) > 0:
            gx_output.c_log(f"Contributor has failed signature verifications in {len(failed_verifications)} of their total {len(signed_commits)} signed commits.", rtype="signatures")

        if len(signed_commits) == 0 and len(failed_verifications) == 0:
            gx_output.c_log(f"Contributor has not signed any of their {len(commits)} commits (in this repo).", rtype="signatures")

        if len(signed_commits) == 0 and len(failed_verifications) > 0:
            gx_output.c_log(f"Contributor has {len(failed_verifications)} failed attempts at signing commits and 0 succesful commits signed out of their {len(commits)} total commits.", rtype="signatures")

        if len(signed_commits) > 0 and len(signed_commits) < len(commits):
            gx_output.c_log(f"Contributor has a mix of {len(signed_commits)} signed vs. {len(commits)-len(signed_commits)} unsigned commits (in this repo).", rtype="commits")

        for scommit in signed_commits: 
            if scommit['verification']['reason'] != 'valid': print(scommit) # This shouldn't happen

        public_repos = int(contributor.get('public_repos'))
        if public_repos > 0:
            gx_output.c_log(f"Contributor has {public_repos} total public repos.", rtype="profiling")

        gx_output.c_log(f"Contributor has {contributor.get('followers')} followers.", rtype="profiling")


        matching_anonymous = [user for user in c_anon if user['email'] in contributor_emails]
        if len(matching_anonymous) > 0:
            gx_output.c_log(f"One of {contributor_login} emails matched the following anonymous users: {matching_anonymous}", rtype="profiling")


        print(f"\r[{c_users_index}/{len(c_users)}] Collecting recent (90d) public events for {contributor.get('login')}"+' '*40, end = '', flush=True)

        # Get Public Events generated by this account, if any. GitHub offers up to 90 days of data, which might still be useful.
        public_events = gh_api.fetch_contributor_events(contributor)
        if len(public_events) > 0:
            gh_public_events.log_events(public_events, gx_output, for_repository=False)

        c_users_index += 1 
        c_ended_at = datetime.now()
        gx_output.c_log(f"X-Ray on contributor ended at {c_ended_at} - {(c_ended_at-c_started_at).seconds} seconds elapsed", rtype="metrics")

    # Let's first create a dictionary merging by email - this is because duplicate anonymous are "normal" or regularly seen
    # Github checks if any of (email OR name) differ and if so treats the anonymous user as different
    # Add all of these under Anonymous contributor output
    unique_anonymous = {}
    for ac in c_anon:
        email = ac.get('email','ERROR_PULLING_ANON_EMAIL')
        if email not in unique_anonymous:
            unique_anonymous[email] = []
        unique_anonymous[email].append(ac.get('name','ERROR_PULLING_ANON_NAME'))

    commits_url = f"Find commits with: https://api.github.com/search/commits?q=repo:{repository.get('full_name')}+author-email:PLACE_EMAIL_HERE"
    gx_output.a_log(commits_url, anonymous="#", rtype="urls")
    for k,v in unique_anonymous.items():
        gx_output.a_log(f'{k} - {v}', anonymous="#", rtype="anonymous")

    print('\rContributors have been analyzed..'+' '*60, flush=True)

    return True
