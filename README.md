# Welcome to Gitxray

<div style="float: left; margin-right: 10px;">
	<img src="https://kulkansecurity.github.io/gitxray/images/logo_gitxray.png" alt="gitxray logo" width="300"/>
</div>
<p>Gitxray (short for Git X-Ray) is a multifaceted security tool designed for use on GitHub repositories. It can serve many purposes, including OSINT and Forensics. `gitxray` leverages public GitHub REST APIs to gather information that would otherwise be very time-consuming to obtain manually. Additionally, it seeks out information in unconventional places. </p>
<p>&nbsp;</p>

[![Build Workflows](https://github.com/kulkansecurity/gitxray/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kulkansecurity/gitxray)
[![Latest Version in PIP](https://img.shields.io/pypi/v/gitxray.svg)](https://pypi.org/project/gitxray)
[![Python Versions](https://img.shields.io/pypi/pyversions/gitxray.svg)](https://pypi.org/project/gitxray)
[![License](https://img.shields.io/pypi/l/gitxray.svg)](https://github.com/kulkansecurity/gitxray/blob/main/LICENSE)

<br/>
# Use-cases and documentation
- [https://kulkansecurity.github.io/gitxray/](https://kulkansecurity.github.io/gitxray/)
- [https://www.gitxray.com/](https://www.gitxray.com/)

<p align="center">
  <img src="https://kulkansecurity.github.io/gitxray/images/console_gitxray.png" alt="gitxray console" width="700" />
</p>

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
