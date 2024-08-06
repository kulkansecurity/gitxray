from datetime import datetime, timezone
from collections import defaultdict
import math
from gitxray.include import gh_api, gh_time, gh_public_events

def run(gx_context, gx_output):
    print("Running verifications on the repository..")

    repository = gx_context.getRepository()
    contributors = gx_context.getContributors()

    if repository.get('owner'):
        gx_output.r_log(f"Repository owner account is [{repository.get('owner').get('login')}]: {repository.get('owner').get('html_url')}", rtype="profiling")

    if repository.get('html_url'):
        gx_output.r_log(f"Repository Url: [{repository.get('html_url')}]", rtype="urls")

    if repository.get('homepage'):
        gx_output.r_log(f"Homepage: [{repository.get('homepage')}]", rtype="urls")

    print(f"Checking for repository deployments..")
    if repository.get('deployments_url'):
         deployments = gh_api.fetch_repository_deployments(repository)
         if len(deployments) > 0: gx_output.r_log(f"Deployments available at: [{repository.get('html_url')}/deployments]", rtype="urls")

    if repository.get('forks_count') > 0:
        gx_output.r_log(f"Repository has {repository.get('forks_count')} forks: {repository.get('forks_url')}", rtype="profiling")

    print(f"Querying about repository action workflows..")
    workflows = gh_api.fetch_repository_actions_workflows(repository)
    if workflows != None and workflows.get('total_count') > 0:
        for workflow in workflows.get('workflows'):
            gx_output.r_log(f"Repository has a GitHub Action workflow at {workflow.get('html_url')}", rtype="workflows")


    print(f"Inspecting repository releases..")
    releases = gh_api.fetch_repository_releases(repository)
    if len(releases) > 0: gx_output.r_log(f"Releases available at: [{repository.get('html_url')}/releases]", rtype="urls")

    release_authors = defaultdict(int)
    asset_uploaders = defaultdict(int)

    for release in releases:
        release_authors[release.get('author').get('login')] += 1
        gx_output.r_log(f"A release was created by {release.get('author').get('login')} at {release.get('created_at')}: {release.get('html_url')}", rtype="v_releases")
        if len(release.get('assets')) > 0:
            # This release has assets other than frozen code. Let's check if updated_at differs from created_at
            # Which may be an indicator of a compromised release by a malicious actor updating binaries.
            for asset in release.get('assets'):
                uploaded_by = asset.get('uploader').get('login')
                asset_uploaders[uploaded_by] += 1
                created_at = asset.get('created_at')
                gx_output.r_log(f"An asset was uploaded by {uploaded_by} at {created_at}: {asset.get('url')}", rtype="v_releases")
                created_at_ts = gh_time.parse_date(created_at)
                updated_at = asset.get('updated_at')
                updated_at_ts = gh_time.parse_date(updated_at)
                if (updated_at_ts-created_at_ts).days > 0:
                    gx_output.r_log(f"An asset in Release [{release.get('name')}] by [{uploaded_by}] was updated {(updated_at_ts-created_at_ts).days} days after its release: {asset.get('url')}", rtype="releases")

    total_releases = sum(release_authors.values())
    total_assets = sum(asset_uploaders.values())
    asset_uploaders_set = set(asset_uploaders.keys())
    for author, releases in release_authors.items():
        percentage_releases = (releases / total_releases) * 100
        message = f"User {author} created historically {releases} releases [{percentage_releases:.2f}%]"

        # Check if the author has also uploaded assets
        if author in asset_uploaders:
            assets = asset_uploaders[author]
            percentage_assets = (assets / total_assets) * 100
            message += f" and uploaded a total of {assets} assets [{percentage_assets:.2f}%]"
            asset_uploaders_set.remove(author)  # Remove from set as it's been handled
        else:
            message += " and never uploaded assets."

        gx_output.r_log(message, rtype="releases")

    # Handle asset uploaders who did not create any releases
    for uploader in asset_uploaders_set:
        assets = asset_uploaders[uploader]
        percentage_assets = (assets / total_assets) * 100
        gx_output.r_log(f"User {uploader} has uploaded {assets} assets [{percentage_assets:.2f}%] and never created a release, Warning.", rtype="releases")

        """ Work in Progress: This sounded fun but ended up being a dead end.
        # Let's run an additional check on stargazers if, and only if, the repository has up to 5000 gazers.
        # This is because we can only pull groups of 100, in which case we would send an extra 50 requests to get all of them.
        # More than that sounds too much overhead for a remains-to-be-seen-how-helpful-this-is feature which lacks AI & blockchain superpowers.

        # We're relying here on a trick to make it work. Unfortunately the gazers API does NOT return creation time for accounts,
        # BUT it does return the account ID which is a sequential value. And by paying attention we've been able to tell about ~50-100k accounts
        # get created daily. Anyhow, if we group the accounts by close IDs; we may end up being able to identify accounts that were created close to eachother
        # and we set a threshold (eg 50%) and inform our user the % of accounts that appear to be fake and gazing the repo that way.

     
        if repository.get('stargazers_count') <= 5000: 
            print(f"Buscando {repository.get('stargazers_count')} stargazers.")
            stargazers = gh_api.fetch_repository_stargazers(repository, limit=5000)
            if len(stargazers) > 0:
                starusers = [(star.get('id'), star.get('login')) for star in stargazers]  # Collect both id and login
                sorted_ids = sorted(starusers, key=lambda x: x[0])  # Sort by user ID
                groups = {}

                group_width = 1000000

                for id, login in sorted_ids:
                    group_key = id // group_width  # Determine the group key based on id_width
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append((id, login))

      
                total_users = int(repository.get('stargazers_count')) 
                threshold = total_users * 0.05

                # Output the groups
                for grou_key, group in groups.items():
                    if group:  # Ensure the group is not empty
                        range_start = min(group, key=lambda x: x[0])[0]
                        range_end = max(group, key=lambda x: x[0])[0]
                        if len(group) > threshold:
                            logins = ', '.join([user[1] for user in group])  # Collect all logins in the group
                            print(f"Group length: {len(group)} - Group ID: {group_key}: Range {range_start} to {range_end}, Members: {len(group)}, Logins: {logins}")
        """

    if repository.get('watchers_count') > 0:
        gx_output.r_log(f"Repository is being Watched by {repository.get('subscribers_count')} Subscribers: {repository.get('subscribers_url')}", rtype="profiling")

    if repository.get('open_issues_count') > 0:
        gx_output.r_log(f"Repository has {repository.get('open_issues_count')} Open Issues: {repository.get('html_url')}/issues", rtype="profiling")

    if repository.get('description'):
        gx_output.r_log(f"Repository description: [{repository.get('description')}]", rtype="profiling")

    if repository.get('topics'):
        gx_output.r_log(f"Topics: {str(repository.get('topics'))}", rtype="profiling")

    if repository.get('fork') != False:
        parent = repository.get('parent').get('full_name')
        source = repository.get('source').get('full_name')
        print(f"Repository is a FORK of a parent named: {repository.get('parent').get('full_name')}: {repository.get('parent')['html_url']}")
        gx_output.r_log(f"Repository is a FORK of repo: {repository.get('parent')['html_url']}", rtype="fork")
        print(f"This also means that GitHub will return ALL contributors (might be a LOT) up to the source repository")
        if parent != source:
            print(f"Please know the parent of this repository is not the original source, which is: {source}") 
            gx_output.r_log(f"The parent of this fork comes from SOURCE repo: {repository.get('source')['html_url']}", rtype="fork")


    days = (datetime.now(timezone.utc) - gh_time.parse_date(repository.get('created_at'))).days 
    message = f"{days} days old"
    if days > 365:
        years = "{:.2f}".format(days / 365)
        message = f"{years} years old"
    gx_output.r_log(f"Repository created: {repository.get('created_at')}, is {message}.", rtype="profiling")

    days = (datetime.now(timezone.utc) - gh_time.parse_date(repository.get('updated_at'))).days 
    message = f"{days} days ago"
    if days > 365:
        years = "{:.2f}".format(days / 365)
        message = f"{years} years ago"
    gx_output.r_log(f"Repository last updated: {repository.get('updated_at')}, {message}.", rtype="profiling")

    if repository.get('archived') == True:
        gx_output.r_log(f"Repository is archived and therefore likely no longer maintained.", rtype="profiling")

    if repository.get('disabled') == True:
        gx_output.r_log(f"Repository is disabled and therefore likely no longer maintained.", rtype="profiling")

    if repository.get('private') == True:
        gx_output.r_log(f"Repository's visibility is set to [private]", rtype="profiling")

    public_events = gh_api.fetch_repository_public_events(repository)
    if len(public_events) > 0:
        gh_public_events.log_events(public_events, gx_output, for_repository=True)

    if repository.get('organization'):
        org_url = repository.get('organization').get('url')
        gx_output.r_log(f"Repository is owned by an Organization {org_url} - (Note that Creating an Org is free in github.com.)", rtype="profiling")
        # Only supported in organizations
        custom_values = gh_api.fetch_repository_custom_values(repository)
        if len(custom_values) > 0:
            gx_output.r_log(f"Repository Custom Property Values: {str(custom_values)}", rtype="user_input")

    # Now look into PRs and let's try and identify anything interesting.
    prs = gh_api.fetch_repository_pull_requests(repository)
    submitter_contrib_counts = defaultdict(lambda: {'submitted': 0, 'accepted':0, 'open': 0, 'rejected': 0})
    submitter_notcontrib_counts = defaultdict(lambda: {'submitted': 0, 'accepted':0, 'open': 0, 'rejected': 0})
    clogins = [c.get('login') for c in contributors]
    for pr in prs:
        submitter = pr['user']['login']
        is_merged = pr['merged_at'] is not None
        if submitter not in clogins: 
            submitter_counts = submitter_notcontrib_counts
        else:
            submitter_counts = submitter_contrib_counts

        submitter_counts[submitter]['submitted'] += 1

        if is_merged:
            submitter_counts[submitter]['accepted'] += 1
        elif pr['state'] == 'closed':
            submitter_counts[submitter]['rejected'] += 1
        else:
            submitter_counts[submitter]['open'] += 1

    for submitter_counts in [submitter_contrib_counts, submitter_notcontrib_counts]:
        for user, details in submitter_counts.items():
            if details['submitted'] > 0:
                # Only add a link to the URL of PRs if it belongs to a user account
                if user in clogins:
                    gx_output.c_log(f"Pull Requests by {user} at: {repository.get('html_url')}/pulls?q=author%3a{user}", rtype="urls", contributor=user)
                details['rejected_percent'] = (details['rejected'] / details['submitted']) * 100
            else:
                details['rejected_percent'] = 0

            # Used GPT for this, we're automathgically weighting amount AND percentage, and it appears to be working.
            details['rejected_score'] = details['rejected_percent'] * math.log1p(details['rejected'])

    sorted_submitters_contrib_rejected = sorted(submitter_contrib_counts.items(), key=lambda x: (-x[1]['rejected_score'], -x[1]['submitted']))
    sorted_submitters_notcontrib_rejected = sorted(submitter_notcontrib_counts.items(), key=lambda x: (-x[1]['rejected_score'], -x[1]['submitted']))

    # First loop on top 3 to log in Repository output
    message = []
    for user, details in sorted_submitters_contrib_rejected[:3]:
        if details['rejected'] > 0:
            message.append(f"[{user} {details['rejected']} rejected out of {details['submitted']}]")
    if len(message) > 0:
        gx_output.r_log(f"Top repository contributors with rejected PRs: " + " | ".join(message), rtype="contributors")

    # Now for NON contributors
    message = []
    for user, details in sorted_submitters_notcontrib_rejected[:3]:
        if details['rejected'] > 0:
            message.append(f"[{user} {details['rejected']} rejected out of {details['submitted']}]")
    if len(message) > 0:
        gx_output.r_log(f"Top non-contributor GitHub users with rejected PRs: " + " | ".join(message), rtype="contributors")

    # And now loop on all to log under each user account.
    for user, details in submitter_contrib_counts.items():
        if details['rejected'] > 0:
            gx_output.c_log(f"The user submitted {details['submitted']} Pull Requests out of which {details['rejected']} were rejected.", rtype="profiling", contributor=user)
        if details['accepted'] > 0:
            gx_output.c_log(f"The user submitted {details['submitted']} Pull Requests out of which {details['accepted']} were merged.", rtype="profiling", contributor=user)
        if details['open'] > 0:
            gx_output.c_log(f"The user submitted {details['submitted']} Pull Requests out of which {details['open']} remain open.", rtype="profiling", contributor=user)

    """ This here next is Work in Progress - trying to figure out what to pay attention to here that makes sense.
    # Get all Issues. Note from GitHub that Issues returns both Issues + PRs:
    # https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28
    # The reason we request these again instead of just calling issues and using it above for PRs
    # is that the Issues endpoint does not include merged_at information. 
    issues = gh_api.fetch_repository_issues(repository)
    print(f"Analyzing a total of {len(issues)-len(prs)} issues and {len(prs)} PRs")
    not_created_by_contributors = 0
    i_pr_len = len(issues)
    c_logins = [item['login'] for item in contributors if item['type'] in ["User","Bot"]]
    for i in issues_prs:
        if i.get('user', {}).get('login') not in c_logins:
            not_created_by_contributors += 1

    gx_output.r_log(f"All {i_pr_len} existing issues and PRs were created by contributors.", rtype="profiling")
    gx_output.r_log(f"The repository has no record of Issues or Pull Requests.", rtype="profiling")
    """

    return True
