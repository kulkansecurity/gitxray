# Welcome to Gitxray

Gitxray (short for Git X-Ray) is a multifaceted security tool designed for use on GitHub repositories. It serves various use cases, including OSINT, forensics, and security teams, as well as developers looking to secure their repositories, organizations, and related contributors. Gitxray leverages public GitHub REST APIs to gather information that would otherwise be very time-consuming to obtain manually. Additionally, it seeks out information in unconventional places.

<p align="center">
  <img src="https://github.com/user-attachments/assets/0572b2eb-42a2-40a8-93cd-b4521c047133" alt="gitxray"/>
</p>

# Use-cases and documentation

Available at: https://www.gitxray.com/

# Installing and running Gitxray

gitxray was written with no use of external package dependencies other than the `requests` library.

## PyPI (PIP) Way

`gitxray` is on PyPI and can be installed with:

```bash
pip install gitxray
```

Once installed, simply run gitxray from your command line by typing:
```bash
gitxray -h
```

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

* `-r, --repository [URL]` - Specify a single repository URL to check. The URL must begin with `https://`. **Example**: `--repository https://github.com/example/repo`

* `-rf, --repositories-file [FILEPATH]` - Provide a file path containing a list of repositories, each on a new line. The file must exist. **Example**: `--repositories-file ./list_of_repos.txt`

* `-o, --organization [URL]` - Specify an organization URL to check all repositories under that organization. The URL must begin with `https://`. **Example**: `--organization https://github.com/exampleOrg`

### Optional Arguments

You'll find these optional but very handy in common gitxray usage.

- `-l, --list` - List contributors if a repository is specified or list repositories if an organization is specified. Useful for further focusing on specific entities. **Example**: `--list`

- `-c, --contributor [USERNAMES]` - A comma-separated list of GitHub usernames to focus on within the specified repository or organization. **Example**: `--contributor user1,user2`

- `-f, --filters [KEYWORDS]` - Comma-separated keywords to filter the results by, such as 'user_input', 'association', or 'mac'. **Example**: `--filters user_input,association,mac`

#### Verbose and Debug
- `-v, --verbose` - Enable verbose output which, for example, provides a detailed list of public events instead of a summary. **Example**: `--verbose`

- `--debug` - Enable Debug mode for a detailed and extensive output. **Example**: `--debug`

#### Output and Formats

- `-out, --outfile [FILEPATH]` - Specify the file path for the output log. Cannot be a directory. **Example**: `--outfile ./output.log`

- `-outformat, --output-format [FORMAT]` - Set the format for the log file. Supported formats are `text` and `json`. Default is `text`. **Example**: `--output-format json`
