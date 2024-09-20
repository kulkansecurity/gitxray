from datetime import datetime, timezone
from collections import defaultdict
import math
from gitxray.include import gh_api, gh_time, gh_public_events, gh_reactions

def run(gx_context, gx_output):
    print("Running verifications on the repository..")

    repository = gx_context.getRepository()
    contributors = gx_context.getContributors()

    print(f"Checking for similar repository names in GitHub.."+" "*40, end="")
    # This gets all repository names matching our repository name, sorted first by highest rating
    similar_names = gh_api.search_repositories_by_name(repository.get('name'), limit=10)
    if similar_names != None and similar_names.get('total_count') != None and similar_names.get('total_count') > 0:
        most_rated = similar_names.get('items')[0]
        search_url = f"https://github.com/search?q={repository.get('name')}%20in:name&type=repositories&s=stars&o=desc"
        if most_rated.get('full_name') == repository.get('full_name'):
            gx_output.r_log(f"This is the highest rating repository with name [{repository.get('name')}]", rtype="profiling")
        else:
            gx_output.r_log(f"WARNING: This is NOT the highest rating repository with name [{repository.get('name')}]", rtype="profiling")

        if similar_names.get('total_count') > 1:
            gx_output.r_log(f'{similar_names.get("total_count")} repositories with a similar name were discovered - See them here: {search_url}', 'profiling')

    stargazers_message = f"Stars count: [{repository.get('stargazers_count')}]"
    if repository.get('stargazers_count') > 0:
        stargazers_message += f" List at: {repository.get('stargazers_url')}"
    gx_output.r_log(stargazers_message, rtype="profiling")

    if repository.get('owner'):
        gx_output.r_log(f"Repository owner account is [{repository.get('owner').get('login')}]: {repository.get('owner').get('html_url')}", rtype="profiling")

    if repository.get('html_url'):
        gx_output.r_log(f"Repository Url: [{repository.get('html_url')}]", rtype="urls")

    if repository.get('homepage'):
        gx_output.r_log(f"Homepage: [{repository.get('homepage')}]", rtype="urls")

    # These go in the repository xray and not contributors because the REST API returns all per repository
    # https://api.github.com/repos/infobyte/faraday/issues/comments - and won't allow filtering in a helpful (to us) way
    print(f"\rGetting all repository comments on commits.."+" "*40, end="")
    commit_comments = gh_api.fetch_repository_commit_comments(repository)
    if len(commit_comments) > 0: 
        total_comments = defaultdict(int)
        positive_reactions = defaultdict(int)
        negative_reactions = defaultdict(int)
        neutral_reactions = defaultdict(int)
        for cc in commit_comments:
            gh_reactions.categorize_reactions(cc, positive_reactions, negative_reactions, neutral_reactions)
            login = cc.get('user').get('login')
            message = f"User {login} added a comment to a Commit on [{cc.get('created_at')}], updated [{cc.get('updated_at')}]: {cc.get('html_url')}"
            total_comments[login] += 1
            gx_output.c_log(message, rtype="v_comments", contributor=login)

            created_at_ts = gh_time.parse_date(cc.get('created_at'))
            updated_at_ts = gh_time.parse_date(cc.get('updated_at'))
            # Comments updated after a day of being posted are of interest; they are not typo edits made right away.
            if (updated_at_ts-created_at_ts).days > 0:
                gx_output.c_log(f"A comment by [{login}] on a Commit was updated {(updated_at_ts-created_at_ts).days} days after being created: {cc.get('html_url')}", rtype="comments", contributor=login)

        for login,ccount in total_comments.items():        
            if not gx_context.isContributor(login):
                login_tmp = f"{login} [NOT a contributor]"
            else:
                login_tmp = login
            gx_output.c_log(f"User {login_tmp} added {ccount} Comments to Commits. {gx_context.verboseLegend()}", rtype="comments", contributor=login)
            #gx_output.c_log(f"{ccount} Comments added to Commits by [{login}] available at: {repository.get('url')}/comments", rtype="comments")

        # Not adding much value 
        gx_output.r_log(f"{len(commit_comments)} Comments in commits available at: {repository.get('url')}/comments", rtype="comments")

        # Comment with the most reactions
        if len(positive_reactions) > 0:
            url, count = gh_reactions.sort_reactions(positive_reactions)[0]
            if count > 0: gx_output.r_log(f"The Commits comment with the most POSITIVE reactions ({count}) is available at: {url}", rtype="comments")
        if len(negative_reactions) > 0:
            url, count = gh_reactions.sort_reactions(negative_reactions)[0]
            if count > 0: gx_output.r_log(f"The Commits comment with the most NEGATIVE reactions ({count}) is available at: {url}", rtype="comments")
        if len(neutral_reactions) > 0:
            url, count = gh_reactions.sort_reactions(neutral_reactions)[0]
            if count > 0: gx_output.r_log(f"The Commits comment with the most NEUTRAL reactions ({count}) is available at: {url}", rtype="comments")

    
    print(f"\rGetting all repository comments on issues.."+" "*30, end="")
    issues_comments = gh_api.fetch_repository_issues_comments(repository)
    if issues_comments != None and len(issues_comments) > 0: 
        total_comments = defaultdict(int)
        positive_reactions = defaultdict(int)
        negative_reactions = defaultdict(int)
        neutral_reactions = defaultdict(int)
        for cc in issues_comments:
            gh_reactions.categorize_reactions(cc, positive_reactions, negative_reactions, neutral_reactions)
            login = cc.get('user').get('login')
            message = f"User [{login}] added a comment to an Issue on [{cc.get('created_at')}], updated [{cc.get('updated_at')}]: {cc.get('html_url')}"
            total_comments[login] += 1
            gx_output.c_log(message, rtype="v_comments", contributor=login)

            created_at_ts = gh_time.parse_date(cc.get('created_at'))
            updated_at_ts = gh_time.parse_date(cc.get('updated_at'))
            # Comments updated after a day of being posted are of interest; they are not typo edits made right away.
            if (updated_at_ts-created_at_ts).days > 0:
                gx_output.c_log(f"A comment by [{login}] on an Issue was updated {(updated_at_ts-created_at_ts).days} days after being created: {cc.get('html_url')}", rtype="comments", contributor=login)

        for login,ccount in total_comments.items():
            if not gx_context.isContributor(login):
                login_tmp = f"{login} [NOT a contributor]"
            else:
                login_tmp = login
            gx_output.c_log(f"User {login_tmp} added {ccount} Comments to Issues. {gx_context.verboseLegend()}", rtype="comments", contributor=login)
            #gx_output.c_log(f"{ccount} Comments added to Issues by [{login}] available at: {repository.get('url')}/issues/comments", rtype="comments")

        gx_output.r_log(f"{len(issues_comments)} Comments in issues available at: {repository.get('url')}/issues/comments", rtype="comments")

        # Comment with the most reactions
        if len(positive_reactions) > 0:
            url, count = gh_reactions.sort_reactions(positive_reactions)[0]
            if count > 0: gx_output.r_log(f"The Issues comment with the most POSITIVE reactions ({count}) is available at: {url}", rtype="comments")
        if len(negative_reactions) > 0:
            url, count = gh_reactions.sort_reactions(negative_reactions)[0]
            if count > 0: gx_output.r_log(f"The Issues comment with the most NEGATIVE reactions ({count}) is available at: {url}", rtype="comments")
        if len(neutral_reactions) > 0:
            url, count = gh_reactions.sort_reactions(neutral_reactions)[0]
            if count > 0: gx_output.r_log(f"The Issues comment with the most NEUTRAL reactions ({count}) is available at: {url}", rtype="comments")

    print(f"\rGetting all repository comments on pull requests.."+" "*30, end="")
    pulls_comments = gh_api.fetch_repository_pulls_comments(repository)
    if pulls_comments != None and len(pulls_comments) > 0: 
        total_comments = defaultdict(int)
        positive_reactions = defaultdict(int)
        negative_reactions = defaultdict(int)
        neutral_reactions = defaultdict(int)
        for cc in pulls_comments:
            gh_reactions.categorize_reactions(cc, positive_reactions, negative_reactions, neutral_reactions)
            login = cc.get('user').get('login')
            message = f"User {login} added a comment to a PR on [{cc.get('created_at')}], updated [{cc.get('updated_at')}]: {cc.get('html_url')}"
            total_comments[login] += 1
            gx_output.c_log(message, rtype="v_comments", contributor=login)

            created_at_ts = gh_time.parse_date(cc.get('created_at'))
            updated_at_ts = gh_time.parse_date(cc.get('updated_at'))
            # Comments updated after a day of being posted are of interest; they are not typo edits made right away.
            if (updated_at_ts-created_at_ts).days > 0:
                gx_output.c_log(f"A comment by [{login}] on a PR was updated {(updated_at_ts-created_at_ts).days} days after being created: {cc.get('html_url')}", rtype="comments", contributor=login)

        for login,ccount in total_comments.items():        
            if not gx_context.isContributor(login):
                login_tmp = f"{login} [NOT a contributor]"
            else:
                login_tmp = login
            gx_output.c_log(f"User {login_tmp} added {ccount} Comments to PRs. {gx_context.verboseLegend()}", rtype="comments", contributor=login)
            #gx_output.c_log(f"{ccount} Comments added to PRs by [{login}] available at: {repository.get('url')}/pulls/comments", rtype="comments")

        gx_output.r_log(f"{len(pulls_comments)} Comments in pulls available at: {repository.get('url')}/pulls/comments", rtype="comments")

        # Comment with the most reactions
        if len(positive_reactions) > 0:
            url, count = gh_reactions.sort_reactions(positive_reactions)[0]
            if count > 0: gx_output.r_log(f"The PRs comment with the most POSITIVE reactions ({count}) is available at: {url}", rtype="comments")
        if len(negative_reactions) > 0:
            url, count = gh_reactions.sort_reactions(negative_reactions)[0]
            if count > 0: gx_output.r_log(f"The PRs comment with the most NEGATIVE reactions ({count}) is available at: {url}", rtype="comments")
        if len(neutral_reactions) > 0:
            url, count = gh_reactions.sort_reactions(neutral_reactions)[0]
            if count > 0: gx_output.r_log(f"The PRs comment with the most NEUTRAL reactions ({count}) is available at: {url}", rtype="comments")


    print(f"\rChecking for repository deployments.."+" "*30, end="")
    if repository.get('deployments_url'):
         deployments = gh_api.fetch_repository_deployments(repository)
         if len(deployments) > 0: gx_output.r_log(f"{len(deployments)} Deployments available at: [{repository.get('html_url')}/deployments]", rtype="deployments")

    print(f"\rChecking for repository environments.."+" "*30, end="")
    environments = gh_api.fetch_repository_environments(repository)
    if environments != None and environments.get('total_count') != None and environments.get('total_count') > 0:
        gx_output.r_log(f"{environments.get('total_count')} Environments available at: [{repository.get('url')}/environments]", rtype="environments")
        for environment in environments.get('environments'):
            gx_output.r_log(f"Environment [{environment.get('name')}] created [{environment.get('created_at')}], updated [{environment.get('updated_at')}]: {environment.get('html_url')}", rtype="environments")
            #print(gh_api.fetch_environment_protection_rules(repository, environment.get('name')))

    print(f"\rChecking for repository forks.."+" "*30, end="")
    if repository.get('forks_count') > 0:
        gx_output.r_log(f"Repository has {repository.get('forks_count')} forks: {repository.get('forks_url')}", rtype="profiling")

    print(f"\rInspecting repository branches.."+" "*40, end="")
    branches = gh_api.fetch_repository_branches(repository)
    if branches != None and len(branches) > 0: 
        gx_output.r_log(f"{len(branches)} Branches available at: [{repository.get('html_url')}/branches]", rtype="branches")
        unprotected_branches = []
        protected_branches = []
        for branch in branches:
            if branch.get('protected') == False:
                unprotected_branches.append(branch.get('name'))
            else:
                protected_branches.append(branch.get('name'))

        if len(unprotected_branches) > 0: gx_output.r_log(f"{len(unprotected_branches)} Unprotected Branches: {unprotected_branches}", rtype="branches")
        if len(protected_branches) > 0: gx_output.r_log(f"{len(protected_branches)} Protected Branches: {protected_branches}", rtype="branches")

    print(f"\rInspecting repository labels.."+" "*40, end="")
    labels = gh_api.fetch_repository_labels(repository)
    if labels != None and len(labels) > 0: 
        gx_output.r_log(f"{len(labels)} Labels available at: [{repository.get('html_url')}/labels]", rtype="labels")
        non_default_labels = [label.get('name') for label in labels if label.get('default') == False]
        if len(non_default_labels) > 0:
            gx_output.r_log(f"{len(non_default_labels)} Non-default Labels: {non_default_labels} available at: [{repository.get('html_url')}/labels]", rtype="labels")

    print(f"\rInspecting repository tags.."+" "*40, end="")
    tags = gh_api.fetch_repository_tags(repository)
    if tags != None and len(tags) > 0: gx_output.r_log(f"{len(tags)} Tags available at: [{repository.get('html_url')}/tags]", rtype="tags")
    tag_taggers = defaultdict(int)

    """ A bit shameful here because we can't really get too much data out of tags because of the way the GH API is implemented.
    It only returns stripped tags when getting all tags, we can't even get who the tagger was. """
    for tag in tags:
        tagger = tag.get('tagger')
        if tagger == None:
            # Lightweight tags - for some reason GitHub's API is returning stripped down version of tags even if they are not lightweight
            gx_output.r_log(f"Tag [{tag.get('name')}] is available at: [{repository.get('html_url')}/tags]", rtype="v_tags")
        else: 
            tagger = tagger.get('email')
            tag_taggers[tagger] += 1
            gx_output.r_log(f"A tag was created by {tagger} at {tag.get('tagger').get('date')}: {tag.get('url')}", rtype="v_tags")

    total_tags = sum(tag_taggers.values())
    for tagger, tags in tag_taggers.items():
        percentage_tags = (tags / total_tags) * 100
        message = f"{tagger} created historically {tags} tags [{percentage_tags:.2f}%]"
        gx_output.r_log(message, rtype="tags")


    print(f"\rInspecting repository releases.."+" "*40, end="")
    releases = gh_api.fetch_repository_releases(repository)
    if len(releases) > 0: gx_output.r_log(f"{len(releases)} Releases available at: [{repository.get('html_url')}/releases]", rtype="releases")

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
                message = f"An asset was uploaded by {uploaded_by} at {created_at}: {asset.get('url')}"
                gx_output.r_log(message, rtype="v_releases")
                gx_output.c_log(message, rtype="v_releases", contributor=uploaded_by)
                created_at_ts = gh_time.parse_date(created_at)
                updated_at = asset.get('updated_at')
                updated_at_ts = gh_time.parse_date(updated_at)
                if (updated_at_ts-created_at_ts).days > 0:
                    gx_output.r_log(f"WARNING: An asset in Release [{release.get('name')}] by [{uploaded_by}] was updated {(updated_at_ts-created_at_ts).days} days after its release: {asset.get('url')}", rtype="releases")

    total_releases = sum(release_authors.values())
    total_assets = sum(asset_uploaders.values())
    asset_uploaders_set = set(asset_uploaders.keys())
    for author, releases in release_authors.items():
        percentage_releases = (releases / total_releases) * 100
        if gx_context.isContributor(author):
            message = f"User {author} created historically {releases} releases [{percentage_releases:.2f}%]"
        else:
            message = f"WARNING: {author} is NOT a contributor to this repository and yet created historically {releases} releases [{percentage_releases:.2f}%]"

        # Check if the author has also uploaded assets
        if author in asset_uploaders:
            assets = asset_uploaders[author]
            percentage_assets = (assets / total_assets) * 100
            message += f" and uploaded a total of {assets} assets [{percentage_assets:.2f}%]"
            asset_uploaders_set.remove(author)  # Remove from set as it's been handled
        else:
            message += " and never uploaded assets."

        if gx_context.verboseEnabled() == False: message += " Turn on Verbose mode for more information."

        gx_output.r_log(message, rtype="releases")
        gx_output.c_log(message, rtype="releases", contributor=author)

    # Handle asset uploaders who did not create any releases
    for uploader in asset_uploaders_set:
        assets = asset_uploaders[uploader]
        percentage_assets = (assets / total_assets) * 100
        message = f"WARNING: User {uploader} has uploaded {assets} assets [{percentage_assets:.2f}%] and never created a release."
        if gx_context.verboseEnabled() == False: message += " Turn on Verbose mode for more information."
        gx_output.r_log(message, rtype="releases")
        gx_output.c_log(message, rtype="releases", contributor=uploader)

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

    watchers_message = f"Watchers count: [{repository.get('subscribers_count')}]"
    if repository.get('subscribers_count') > 0:
        watchers_message += f" List at: {repository.get('subscribers_url')}"
    gx_output.r_log(watchers_message, rtype="profiling")

    if repository.get('open_issues_count') > 0:
        gx_output.r_log(f"Repository has {repository.get('open_issues_count')} Open Issues: {repository.get('html_url')}/issues", rtype="profiling")

    if repository.get('description'):
        gx_output.r_log(f"Repository description: [{repository.get('description')}]", rtype="profiling")

    if repository.get('topics'):
        gx_output.r_log(f"Topics: {str(repository.get('topics'))}", rtype="profiling")

    if repository.get('fork') != False:
        parent = repository.get('parent').get('full_name')
        source = repository.get('source').get('full_name')
        print(f"\rRepository is a FORK of a parent named: {repository.get('parent').get('full_name')}: {repository.get('parent')['html_url']}")
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
                    gx_output.c_log(f"{details['submitted']} Pull Requests by [{user}] at: {repository.get('html_url')}/pulls?q=author%3a{user}", rtype="prs", contributor=user)
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

    # Check if there were any users with mismatches in commits dates in the repository.
    for user, dates_mismatch_commits in gx_context.getIdentifierValues("DATE_MISMATCH_COMMITS").items():
            gx_output.r_log(f"WARNING: UNRELIABLE DATES (Older than Account) in {dates_mismatch_commits} commits by [{user}]. Potential tampering, account re-use, or Rebase.", rtype="commits")
       

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
