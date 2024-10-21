# Welcome to Gitxray 
Gitxray (short for Git X-Ray) is a multifaceted security tool designed for use on GitHub repositories. It can serve many purposes, including OSINT and Forensics. `gitxray` leverages public GitHub REST APIs to gather information that would otherwise be very time-consuming to obtain manually. Additionally, it seeks out information in unconventional places.

[![Build Workflows](https://github.com/kulkansecurity/gitxray/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kulkansecurity/gitxray) [![Latest Version in PIP](https://img.shields.io/pypi/v/gitxray.svg)](https://pypi.org/project/gitxray) [![Python Versions](https://img.shields.io/pypi/pyversions/gitxray.svg)](https://pypi.org/project/gitxray) [![License](https://img.shields.io/pypi/l/gitxray.svg)](https://github.com/kulkansecurity/gitxray/blob/main/LICENSE) 
--- 
![Gitxray HTML Report](https://kulkansecurity.github.io/gitxray/images/html_report_gitxray.png "Gitxray HTML Report")
<div style="clear: both;"></div>

# Use cases
Gitxray can be used to, for example:

- Find sensitive information in contributor profiles disclosed by accident within, for example, Armored PGP Keys, or Key Names.

- Identify threat actors in a Repository. You may spot co-owned or shared accounts, as well as inspect public events to spot fake Stargazers.

- Identify fake or infected Repositories. It can detect tampered commit dates as well as, for example, Release assets updated post-release.

- Forensics use-cases, such as filtering results by date in order to check what else happened on the day of an incident.

- And a lot more! Run a full X-Ray in to collect a ton of data.

` gitxray -r https://github.com/some-org/some-repository`

- If you rather use text output, you may want to filter output with filters:

` gitxray -r https://github.com/some-org/some-repository -f user_input -outformat text`

` gitxray -r https://github.com/some-org/some-repository -f keys,association,starred -outformat text`

` gitxray -r https://github.com/some-org/some-repository -f warning -outformat text`

` gitxray -r https://github.com/some-org/some-repository -f 2024-09-01 -outformat text`

Please refer to the Documentation for additional use-cases and introductory information.

# Documentation
- [https://kulkansecurity.github.io/gitxray/](https://kulkansecurity.github.io/gitxray/)
- [https://www.gitxray.com/](https://www.gitxray.com/)

# Rate Limits and the GitHub API

Gitxray gracefully handles Rate Limits and can work out of the box without a GitHub API key, but you'll likely hit RateLimits pretty fast (A small to medium-size repository with 10+ Contributors could take hours to complete while it waits for RateLimits to reset) This is detailed by GitHub in their [documentation here](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-unauthenticated-users). 

[Creating a simple read-only token scoped to PUBLIC repositories](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) will however help you increase those restrictions considerably. If you're not in a hurry or can leave gitxray running you'll be able to use its full capacity, as it pauses execution while waiting for the limits to lift.

You may then load the token safely by using (prevents the token from being displayed on screen or getting logged in your shell history):

```bash
read -rs GH_ACCESS_TOKEN
export
```

# Installing, Updating, and running Gitxray

gitxray was written with no use of external package dependencies other than the `requests` library.

## PyPI (PIP) Way

`gitxray` is on PyPI and can be installed and updated with:

```bash
pip install gitxray --upgrade
```

Once installed, simply run gitxray from your command line by typing:
```bash
gitxray -h
```

## Run your first full X-Ray
```bash
gitxray -o https://github.com/kulkansecurity
```

![Gitxray Console](https://kulkansecurity.github.io/gitxray/images/console_gitxray.png "Gitxray Console") 
<div style="clear: both;"></div>

## Installing from source

You may also run `gitxray` directly by cloning or downloading its GitHub repository and running.

```bash
python3 -m pip install -r requirements.txt
cd src/
python3 -m gitxray.gitxray
```

## Command Line Arguments

### Required Arguments

One of the following must be specified:

* `-r, --repository [URL]` - Specify a single repository to check. The URL may optionally begin with `https://github.com/`. **Example**: `--repository https://github.com/example/repo`

* `-rf, --repositories-file [FILEPATH]` - Provide a file path containing a list of repositories, each on a new line. The file must exist. **Example**: `--repositories-file ./list_of_repos.txt`

* `-o, --organization [URL]` - Specify an organization to check all repositories under that organization. The URL may optionally begin with `https://github.com/`. **Example**: `--organization https://github.com/exampleOrg`

### Optional Arguments

You'll find these optional but very handy in common gitxray usage.

- `-l, --list` - List contributors if a repository is specified or list repositories if an organization is specified. Useful for further focusing on specific entities. **Example**: `--list`

- `-c, --contributor [USERNAMES]` - A comma-separated list of GitHub usernames to focus on within the specified repository or organization. **Example**: `--contributor user1,user2`

- `-f, --filters [KEYWORDS]` - Comma-separated keywords to filter the results by, such as 'user_input', 'association', or 'mac'. **Example**: `--filters user_input,association,mac`

#### Output and Formats

- `-out, --outfile [FILEPATH]` - Specify the file path for the output log. Cannot be a directory. **Example**: `--outfile ./output.log`

- `-outformat, --output-format [FORMAT]` - Set the format for the log file. Supported formats are `html`, `text` and `json`. Default is `html`. **Example**: `--output-format json`

#### Debug

- `--debug` - Enable Debug mode for a detailed and extensive output. **Example**: `--debug`

# Terms of Use

The user is solely responsible for ensuring that this tool is used in compliance with applicable laws and regulations, including obtaining proper authorization for repository scanning and the distribution of any results generated. Unauthorized use or sharing of results may violate local, national, or international laws.

