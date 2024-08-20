# Welcome to Gitxray 
Gitxray (short for Git X-Ray) is a multifaceted security tool designed for use on GitHub repositories. It can serve many purposes, including OSINT and Forensics. `gitxray` leverages public GitHub REST APIs to gather information that would otherwise be very time-consuming to obtain manually. Additionally, it seeks out information in unconventional places.

The Octocat getting X-Rayed  | [![Build Workflows](https://github.com/kulkansecurity/gitxray/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kulkansecurity/gitxray) [![Latest Version in PIP](https://img.shields.io/pypi/v/gitxray.svg)](https://pypi.org/project/gitxray) [![Python Versions](https://img.shields.io/pypi/pyversions/gitxray.svg)](https://pypi.org/project/gitxray) [![License](https://img.shields.io/pypi/l/gitxray.svg)](https://github.com/kulkansecurity/gitxray/blob/main/LICENSE)
--- | ---
![Gitxray Logo](https://kulkansecurity.github.io/gitxray/images/logo_gitxray.png "Gitxray Logo") | ![Gitxray Console](https://kulkansecurity.github.io/gitxray/images/console_gitxray.png "Gitxray Console")
<div style="clear: both;"></div>

# What is it for?
* [Finding sensitive information in contributor profiles](/awesome_features/#unintended-disclosures-in-contributor-profiles) disclosed by accident within, for example, Armored PGP Keys, or Key Names.
* Identifying threat actors in a Repository. [You may spot co-owned or shared accounts](/awesome_features/#spotting-shared-co-owned-or-fake-contributors), as well as inspect public events to [spot fake Stargazers](/awesome_features/#fake-stars-private-repos-gone-public-and-more).
* Collecting [email addresses and analyzing contributor accounts](/more_features/#lots-of-e-mail-addresses-and-profiling-data) belonging to GitHub organizations and repositories.
* Identifying fake or infected Repositories. It can [detect tampered commit dates](/awesome_features/#untrustworthy-repositories-and-activity) as well as, for example, [Release assets updated post-release](/more_features/#looking-out-for-malicious-releases-and-assets).
* And so. much. more.

# Getting started
* [Installing Gitxray](installing.md)
* [Awesome Features](awesome_features.md) &#128171;
* [More Features](more_features.md) &#129470;

## Rate Limits and the GitHub API

Gitxray gracefully handles Rate Limits and can work out of the box without a GitHub API key, _but_ you'll likely hit RateLimits pretty fast. This is detailed by GitHub in their [documentation here](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-unauthenticated-users). A simple read-only token created for PUBLIC repositories will however help you increase those restrictions considerably. If you're not in a hurry or can leave `gitxray` running you'll be able to use its full capacity, as it pauses execution while waiting for the limits to lift.

## License

`gitxray` is provided under the terms and conditions of the [GNU Affero GPL v3 License](https://www.gnu.org/licenses/agpl-3.0.txt).
