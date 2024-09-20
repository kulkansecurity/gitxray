import os, requests, base64, re, time, urllib
from . import gx_definitions, gx_output

# GitHub API URL
GITHUB_API_BASE_URL = "https://api.github.com"
# Get an optional token to get better rate limits
GITHUB_TOKEN = os.environ.get("GH_ACCESS_TOKEN", None)

def make_request(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 401 or (response.status_code == 403 and "not accessible by" in response.text):
        print(response.text)
        raise Exception(f"\r\n\033[33mUnauthorized: Check your GitHub Access Token for permissions.\r\nIf testing against a private repository, you will need read-only: Contents, Custom Properties, Deployments, Actions, Issues and Pull Requests.\033[0m")

    data = response.json() if len(response.content) > 0 else []
    rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 1))
    rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', time.time() + 1))
    links = response.headers.get('Link', '')
    return data, links, rate_limit_remaining, rate_limit_reset

def get_total_pages_from_link_header(links):
    if not links:
        return None

    # Parse the Link header to find the "last" page
    for link in links.split(','):
        if 'rel="last"' in link:
            last_page_url = link.split(';')[0].strip('<> ')
            # Extract the page number from the URL
            if 'page=' in last_page_url:
                try:
                    return int(last_page_url.split('page=')[-1].split('&')[0])
                except ValueError:
                    pass
    return None

def get_last_two_path_segments(url):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path  
    parts = [part for part in path.split("/") if part]  
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    elif len(parts) == 1:
        return parts[-1]
    else:
        return "" 


def github_request_json(url, params=None, limit_results=None):
    # https://docs.github.com/en/rest/about-the-rest-api/api-versions?apiVersion=2022-11-28
    headers = {"X-GitHub-Api-Version":"2022-11-28"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    if params is None:
        params = {}
    params['per_page'] = 100

    all_results = None
    next_url = url
    remaining = -1
    pages_fetched = 0
    total_pages = None
    start_time = time.time()

    while next_url:

        try:

            try:
                data, links, remaining, reset = make_request(next_url, headers, params)
            except Exception as ex:
                print(ex)
                print(f"Failed to talk to the GitHub API when fetching URL: {next_url} - Quitting.")
                exit(-1)

            if remaining == 0:
                # Calculate how long to sleep, then sleep
                sleep_time = reset - time.time()
                if sleep_time > 0:
                    hours, remainder = divmod(int(sleep_time), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    message = f"GitHub Rate limit reached. Sleeping for {hours} hours, {minutes} minutes, and {seconds} seconds. You may go and make coffee.."
                    print(f"\r\n\033[33m{message}\033[0m", flush=True)
                    if GITHUB_TOKEN == None:
                        message = f"You should try using a Github Access Token, improves the experience significantly and it's easy!"
                        print(f"\033[33m{message}\033[0m", flush=True)
                        print("For information on how to create a GitHub API Access Token refer to: ")
                        print("https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens")
                        print("For information on GitHub Rate Limits refer to: ")
                        print("https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api")
    
                    time.sleep(sleep_time + 1)  # Sleep until the reset time, plus a little buffer
                    continue # and restart the loop

            if all_results is None:
               all_results = data
            # if we come from all_results being a list, then we're extending it.
            elif isinstance(all_results, list):
                all_results.extend(data)
            elif isinstance(all_results, dict) and data.get('total_count') != None:
                all_results[list(all_results.keys())[-1]].extend(list(data.values())[-1])
            else:
                all_results.update(data)

            pages_fetched += 1
            if total_pages is None:
                total_pages = get_total_pages_from_link_header(links)

            # Print progress if total pages is known
            if total_pages:
                progress = (pages_fetched / total_pages) * 100
                elapsed_time = time.time() - start_time
                avg_time_per_page = elapsed_time / pages_fetched
                remaining_pages = total_pages - pages_fetched
                estimated_time_left = remaining_pages * avg_time_per_page
                time_estimate = f": {estimated_time_left:.0f} seconds left."
                urlpath = get_last_two_path_segments(url)
                print(f"\rFetching {urlpath} [Hit CTRL^C to skip]: ({progress:.2f}%) {time_estimate}" + " " * 30, flush=True, end="")

            # Reset next_url
            next_url = None

            # Using "limit" we can cap the amount of results in order to prevent huge amounts of requests.
            if limit_results == None or \
                ((isinstance(all_results, list) and len(all_results) < limit_results) \
                or (isinstance(all_results, dict) and all_results.get('total_count') != None and len(list(all_results.values())[-1]) < limit_results)):
                if 'rel="next"' in links:
                    for link in links.split(','):
                        if 'rel="next"' in link:
                            next_url = link.split(';')[0].strip('<> ')
                            break

        except KeyboardInterrupt:
            print("\r\n\033[33mReceived CTRL+C - Skipping..\033[0m")
            next_url = None


    return all_results


def fetch_domains_from_code(repository):
    matches = github_request_json(f"{GITHUB_API_BASE_URL}/search/code?q=repo:{repository}%20in:file%20http")
    for m in matches['items']:
        code = base64.b64decode(github_request_json(m['url'])["content"]).decode()
        # This by no means is a complete regex - do not rely on this code picking up ALL possible domains
        url_pattern = r'https?://([\w.-]+)'
        # Find all matches in the code content
        matches = re.findall(url_pattern, code)
        return matches

def fetch_repository(github_url):
    # Extract owner and repository name from the GitHub URL
    parts = github_url.strip('/').split('/')
    owner = parts[-2]
    repo_name = parts[-1]
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo_name}")

def fetch_repositories_for_org(org_url):
    # Extract the Org from the URL
    org = org_url.strip('/').split('/')[-1]
    return github_request_json(f"{GITHUB_API_BASE_URL}/orgs/{org}/repos")

def fetch_repository_file_contents(repository, path):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repository.get('full_name')}/contents/{path}")

def fetch_commits(repo, author=None):
    return github_request_json(repo.get('commits_url').replace("{/sha}", f'?author={author}' if author != None else ""))

def fetch_ssh_signing_keys(login):
    return github_request_json(f"{GITHUB_API_BASE_URL}/users/{login}/ssh_signing_keys")

def fetch_ssh_auth_keys(login):
    return github_request_json(f"{GITHUB_API_BASE_URL}/users/{login}/keys")

def fetch_gpg_keys(login):
    return github_request_json(f"{GITHUB_API_BASE_URL}/users/{login}/gpg_keys")

def fetch_repository_stargazers(repo, limit):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/stargazers", limit_results=limit)

def fetch_repository_custom_values(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/properties/values")

def fetch_repository_public_events(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/events")

def fetch_repository_commit_comments(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/comments")

def fetch_repository_issues_comments(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/issues/comments")

def fetch_repository_pulls_comments(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/pulls/comments")

def fetch_repository_actions_workflows(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/actions/workflows")

def fetch_repository_actions_artifacts(repo, limit=None):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/actions/artifacts", limit_results=limit)

def fetch_repository_actions_runs(repo, workflow_file=None, limit=None):
    if workflow_file != None:
        return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/actions/workflows/{workflow_file}/runs", limit_results=limit)
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/actions/runs", limit_results=limit)

def fetch_repository_releases(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/releases")

def fetch_repository_tags(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/tags")

def fetch_repository_labels(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/labels")

def fetch_repository_branches(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/branches")

def fetch_repository_contributors(repo):
    return github_request_json(repo.get('contributors_url'), {'anon':1})

def fetch_repository_deployments(repo):
    return github_request_json(repo.get('deployments_url'))

def fetch_repository_environments(repo):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/environments")

def fetch_environment_protection_rules(repo, environment):
    return github_request_json(f"{GITHUB_API_BASE_URL}/repos/{repo.get('full_name')}/environments/{environment}/deployment_protection_rules")

def fetch_repository_pull_requests(repo):
    return github_request_json(repo.get('pulls_url').replace("{/number}",""), {'state':'all'})

def fetch_repository_issues(repo):
    return github_request_json(repo.get('issues_url').replace("{/number}",""), {'state':'all'})

def fetch_contributor(contributor_obj):
    return github_request_json(contributor_obj['url'])

def fetch_contributor_contributions(repo, contributor_obj):
    return github_request_json(repo.get('commits_url').replace("{/sha}", ""), {'author':contributor_obj['login']})

def fetch_contributor_events(contributor_obj):
    return github_request_json(contributor_obj.get('events_url').replace("{/privacy}", ""))

def search_repositories_by_name(name, limit):
    return github_request_json(f"{GITHUB_API_BASE_URL}/search/repositories", {'q':name, 'type':'repositories','s':'stars','o':'desc'}, limit_results=limit)
