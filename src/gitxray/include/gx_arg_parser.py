# Our argparser is called by the Gitxray Context, we don't talk to it directly.
import os, sys, argparse, re

def parse_repositories_from_file(filepath):
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError(f"File not found: {filepath}")

    with open(filepath, 'r') as f:
        repositories = f.read().splitlines()

    for repo in repositories:
        validate_repository(repo)

    print("Loaded {} repositories.".format(len(repositories)))
    return repositories

def validate_repository_org_link(repo):
    if not repo.startswith("https://"):
        raise argparse.ArgumentTypeError(f"Invalid URL '{repo}'. It should start with 'https://'.")
    return repo

def validate_contributors(username_string):
    # Regex pattern to match valid GitHub usernames
    pattern = r"^[a-zA-Z0-9,-]+(-[a-zA-Z0-9]+)*$"
    if not re.match(pattern, username_string):
        raise argparse.ArgumentTypeError(f"Invalid GitHub usernames. Usernames must consist of alphanumeric characters or single hyphens, and cannot begin or end with a hyphen.")
    usernames = [username.strip() for username in username_string.split(',')]
    return usernames

def validate_filters(filter_string):
    filters = [filter_name.strip() for filter_name in filter_string.split(',')]
    return filters

def parse_arguments():
    parser = argparse.ArgumentParser(description="Gitxray")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-r', '--repository',
            type=validate_repository_org_link,
            action='store',
            help='The repository to check (an https:// URL)')

    group.add_argument('-rf', '--repositories-file',
            type=parse_repositories_from_file,
            action='store',
            help='A file containing repositories separated by newlines.')

    group.add_argument('-o', '--organization',
            type=validate_repository_org_link,
            action='store',
            help='An organization to check all of their repositories (an https:// URL)')

    group_two = parser.add_mutually_exclusive_group(required=False)

    group_two.add_argument('-c', '--contributor',
            type=validate_contributors,
            action='store',
            help="A comma-separated list of contributor usernames to focus on within the Repository or Organization that you Gitxray.")

    group_two.add_argument('-l', '--list',
            action='store_true',
            default=False,
            help="List contributors (if a repository was specified) or List repositories (if an Org was specified). Useful if you intend to then focus on a specific username or repository.")

    parser.add_argument('-f', '--filters',
            type=validate_filters,
            action='store',
            help="Comma separated keywords to filter results by (e.g. private,macbook).")

    parser.add_argument('-v', '--verbose',
            action='store_true', 
            default=False, 
            help='Verbose output. For example, print a detailed list of public events instead of a summary.')

    parser.add_argument('--debug', 
            action='store_true', 
            default=False, 
            help='Enable Debug mode - be prepared for an excessive amount of output.')

    parser.add_argument('-out', '--outfile', 
            type=str, 
            action='store',
            help='Set the location for the output log file.')

    parser.add_argument('-outformat', '--output-format', type=str, action='store',
            default='text',
            help='Format for log file (text,json) - default: text',
            choices = ['text', 'json'])

    args = parser.parse_args()

    if args.outfile:
        if os.path.isdir(args.outfile):
            print("[!] Can't specify a directory as the output file, exiting.")
            sys.exit()
        if os.path.isfile(args.outfile):
            target = args.outfile
        else:
            target = os.path.dirname(args.outfile)
            if target == '':
                target = '.'

        if not os.access(target, os.W_OK):
            print("[!] Cannot write to output file, exiting")
            sys.exit()

    return args
