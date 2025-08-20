# Installing and Updating Gitxray

gitxray was written with no use of external package dependencies other than the `requests` library.

## PyPI (PIP) Way

`gitxray` is on PyPI and can be installed and updated with:

```bash
pip install gitxray --upgrade
```

Once installed, simply run gitxray from your command line by typing:
```bash
gitxray -o https://github.com/SampleOrg
```
or
```bash
gitxray -r https://github.com/SampleOrg/SampleRepo
```

Including https://github.com/ in the Repository or Organization is optional.

## Installing from source

You may also run `gitxray` directly by cloning or downloading its GitHub [repository](https://github.com/kulkansecurity/gitxray/) and running:

```bash
python3 -m pip install -r requirements.txt
cd src/
python3 -m gitxray.gitxray
```

## Creating an Access Token to increase Rate Limits

Gitxray gracefully handles Rate Limits and can work out of the box without a GitHub API token, but you'll likely hit RateLimits pretty fast (A small to medium-size repository with 10+ Contributors could take hours to complete while it waits for RateLimits to reset) This is detailed by GitHub in their [documentation here](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-unauthenticated-users). 

[Creating a simple read-only token scoped to PUBLIC repositories](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) will however help you increase those restrictions considerably. If you're not in a hurry or can leave gitxray running you'll be able to use its full capacity, as it pauses execution while waiting for the limits to lift.

You may then load the token safely by using (prevents the token from being displayed on screen or getting logged in your shell history):

```bash
read -rs GH_ACCESS_TOKEN
export
```

## Integration with VirusTotal

Gitxray can optionally use the VirusTotal API to check any hosts identified with GitHub's Code search API, but it requires a VirusTotal API Key to work. Instructions on how to get your VirusTotal API Key are available at: https://docs.virustotal.com/docs/please-give-me-an-api-key

Unfortunately, personal API Keys are (as of today) limited by VirusTotal to 500 lookups a day.

Once you have the API key, you may safely load it in your environment with:

```bash
read -rs VT_API_KEY
export
```

## Command Line Arguments

### Required Arguments

One of the following must be specified:

* `-r, --repository [URL]` - Specify a single repository URL to check. The URL must begin with `https://`. **Example**: `--repository https://github.com/example/repo`

* `-rf, --repositories-file [FILEPATH]` - Provide a file path containing a list of repositories, each on a new line. The file must exist. **Example**: `--repositories-file ./list_of_repos.txt`

* `-o, --organization [URL]` - Specify an organization URL to check all repositories under that organization. The URL must begin with `https://`. **Example**: `--organization https://github.com/exampleOrg`

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

