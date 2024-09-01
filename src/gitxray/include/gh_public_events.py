from collections import defaultdict
from gitxray.include import gh_time
import datetime

def log_events(events, gx_output, for_repository=False):
    if events == None or len(events) == 0: return

    logging_func = gx_output.c_log if not for_repository else gx_output.r_log

    event_summary = defaultdict(int)

    for event in events:
        etype = event.get('type')
        ts = event.get('created_at')
        payload = event.get('payload', {})
        actor = event.get('actor', {}).get('login', '')+' ' if for_repository else ""
        repo_name = event.get('repo', {}).get('name', 'unknown')

        # We're going to summarize recent events by YYYY-MM in order not to flood our console 
        try: 
            event_date = gh_time.parse_date(ts)
            month_key = event_date.strftime('%Y-%m')
        except Exception:
            gx_output.debug(f"Invalid date format for event: {ts}")
            continue

        action = payload.get('action', 'performed')
        repo_name = event.get('repo', {}).get('name', 'unknown')

        # Add one more event type to the summary
        summary_key = (month_key, etype, action)
        event_summary[summary_key] += 1

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#commitcommentevent
        if etype == "CommitCommentEvent":
                logging_func(f"{ts}: {actor}created a comment in a commit: [{payload.get('comment').get('html_url')}]", rtype="v_90d_events")
                pass

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#createeventA
        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#deleteevent
        elif etype == "CreateEvent" or etype == "DeleteEvent":
            action = "created" if etype == "CreateEvent" else "deleted"
            if payload.get('ref_type') == "repository":
                logging_func(f"{ts}: {actor}{action} a repository: [{event.get('repo').get('name')}]", rtype="v_90d_events")
            else:
                logging_func(f"{ts}: {actor}{action} a {payload.get('ref_type')}: [{payload.get('ref')}] in repo [{event.get('repo').get('name')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#forkevent
        elif etype == "ForkEvent":
            logging_func(f"{ts}: {actor}forked a repository: {event.get('repo').get('name')} into {payload.get('forkee').get('full_name')}", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#gollumevent
        elif etype == "GollumEvent":
            for page in payload.get('pages'):
                logging_func(f"{ts}: {actor}{page.get('action')} Wiki page at [{page.get('html_url')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#issuecommentevent
        elif etype == "IssueCommentEvent":
            logging_func(f"{ts}: {actor}{action} a comment in an Issue [{payload.get('issue').get('html_url')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#issuesevent
        elif etype == "IssuesEvent":
                logging_func(f"{ts}: {actor}{action} an Issue: [{payload.get('issue').get('html_url')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#memberevent
        elif etype == "MemberEvent":
            added_who = payload.get('member').get('login')
            to_repo = event.get('repo').get('name')
            logging_func(f"{ts}: {actor}{action} a user [{added_who}] as a collaborator to repo: [{to_repo}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#publicevent
        elif etype == "PublicEvent":
            logging_func(f"{ts}: {actor}switched a repository from PRIVATE to PUBLIC, repo: [{event.get('repo').get('name')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#pullrequestevent
        elif etype == "PullRequestEvent":
            logging_func(f"{ts}: {actor}{action} a PR: [{payload.get('pull_request').get('html_url')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#pullrequestreviewevent
        elif etype == "PullRequestReviewEvent":
            logging_func(f"{ts}: {actor}{action} a PR Review: [{payload.get('pull_request').get('html_url')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#pullrequestreviewcommentevent
        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#pullrequestreviewthreadevent
        elif etype == "PullRequestReviewCommentEvent" or etype == "PullRequestReviewThreadEvent":
            logging_func(f"{ts}: {actor}{action} a comment in PR: [{payload.get('pull_request').get('html_url')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#pushevent
        elif etype == "PushEvent":
            logging_func(f"{ts}: {actor}pushed a total of {len(payload.get('commits'))} commits from: [{payload.get('ref')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#releaseevent
        elif etype == "ReleaseEvent":
            logging_func(f"{ts}: {actor}published a Release at [{payload.get('release').get('html_url')}]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#sponsorshipevent
        elif etype == "SponsorshipEvent":
            logging_func(f"{ts}: {actor}{action} a Sponsorship Event]", rtype="v_90d_events")

        # https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#watchevent
        elif etype == "WatchEvent":
            logging_func(f"{ts}: {actor}starred a repository: [{event.get('repo').get('name')}]", rtype="v_90d_events")
        else:
            logging_func(f"Missing parser in recent events for: {etype} with {payload}", rtype="debug")


    # If verbose is enabled, we skip the summary as it becomes redundant.
    if gx_output.verbose_enabled(): return 

    # Now let's create the non-debug summarized version of messages.
    for (month, etype, action), count in event_summary.items():
        summary_message = f"In {month}, "
        if etype == "WatchEvent":
            if for_repository:
                summary_message += f"{count} users starred the repository."
            else:
                summary_message += f"the user starred {count} repositories."
        elif etype == "ForkEvent":
            if for_repository:
                summary_message += f"the repository was forked {count} times."
            else:
                summary_message += f"the user forked {count} repositories"
        elif etype == "SponsorshipEvent":
            if for_repository:
                summary_message += f"the repository had a sponsorship event."
            else:
                summary_message += f"the user created a sponsorship event."
        elif etype == "ReleaseEvent":
            if for_repository:
                summary_message += f"the repository had published {count} releases."
            else:
                summary_message += f"the user published {count} releases."
        elif etype == "PushEvent":
            if for_repository:
                summary_message += f"users pushed commits to the repository {count} times."
            else:
                summary_message += f"the user pushed commits {count} times."
        elif etype == "PullRequestReviewCommentEvent" or etype =="PullRequestReviewThreadEvent":
            if for_repository:
                summary_message += f"users {action} comments in PRs {count} times."
            else:
                summary_message += f"the user {action} comments in PRs {count} times."
        elif etype == "PullRequestEvent":
            if for_repository:
                summary_message += f"users {action} PRs {count} times."
            else:
                summary_message += f"the user {action} PRs {count} times."
        elif etype == "PullRequestReviewEvent":
            if for_repository:
                summary_message += f"users {action} PR Reviews {count} times."
            else:
                summary_message += f"the user {action} PR Reviews {count} times."
        elif etype == "PublicEvent":
            if for_repository:
                summary_message += f"the repository's visibility switched from private to PUBLIC!"
            else:
                summary_message += f"the user switched a repository from private to PUBLIC!"
        elif etype == "GollumEvent":
            if for_repository:
                summary_message += f"users {action} the repository Wiki page {count} times."
            else:
                summary_message += f"the user {action} repository Wikis {count} times."
        elif etype == "IssueCommentEvent":
            if for_repository:
                summary_message += f"users {action} comments in repository Issues {count} times."
            else:
                summary_message += f"the user {action} comments in repository Issues {count} times."
        elif etype == "IssuesEvent":
            if for_repository:
                summary_message += f"users {action} Issues {count} times."
            else:
                summary_message += f"the user {action} Issues on a repository {count} times."
        elif etype == "IssuesEvent":
            if for_repository:
                summary_message += f"users were {action} as collaborators of the repository {count} times."
            else:
                summary_message += f"the user {action} other users as collaborators to repositories {count} times."
        elif etype == "CommitCommentEvent":
            if for_repository:
                summary_message += f"users created comments in commits {count} times."
            else:
                summary_message += f"the user created comments in commits {count} times."
        elif etype == "CreateEvent" or etype == "DeleteEvent":
            action = "created" if etype == "CreateEvent" else "deleted"
            if for_repository:
                summary_message += f"users {action} a branch or tag {count} times."
            else:
                summary_message += f"the user {action} a repository, branch or tag {count} times."
        elif etype == "MemberEvent":
            if for_repository:
                summary_message += f"users were {action} as collaborators {count} times."
            else:
                summary_message += f"the user {action} a user as a collaborator to a repo {count} times."
        else:
            summary_message += f"{etype}"


        logging_func(summary_message, rtype="90d_events")
    logging_func("For a detailed individual list of recent public events, use --verbose", rtype="90d_events")
    return
