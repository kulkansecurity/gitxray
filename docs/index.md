# Welcome to Gitxray

Gitxray (short for Git X-Ray) is a multifaceted security tool designed for use on GitHub repositories. It serves various use cases, including OSINT, forensics, and security teams, as well as developers looking to secure their repositories, organizations, and related contributors. Gitxray leverages public GitHub REST APIs to gather information that would otherwise be very time-consuming to obtain manually. Additionally, it seeks out information in unconventional places.

## Use-cases when using Gitxray

* [OSINT and Pentesting](osint_pentest.md)
* [Forensics and Spotting Associations](forensics_spotting.md)
* [Securing your Team and Repositories](securing_repos.md)

## Rate Limits and the GitHub API

Gitxray can work out of the box without a GitHub API key, _but_ you'll likely hit RateLimits pretty fast. This is detailed by GitHub in their [documentation here](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-unauthenticated-users). A simple read-only token created for PUBLIC repositories will however help you increase those restrictions considerably. If you're not in a hurry or can leave Gitxray running you'll be able to use Gitxray in its full capacity, as it pauses execution while waiting for the limits to lift.

## Reasons to &hearts; Gitxray 

A few reasons why we think Gitxray is special include:

* It parses Signature BLOBs in order to capture Personal Information, Algorithm configurations, Creation Time subpackets, and more.
* It displays user-supplied data obtained from weird places, such as Key names and copy-paste mistakes appended before/after armored Keys.
* It cross-references data from different users, displaying what we call "*associations*", likely revealing _potential_ shared or fake accounts.
* It inspects Repository releases and identifies when assets were updated *after* being released; _potentially_ implying infected or tampered assets.
* And a lot more for you to discover.


## Ready to get started?

Jump to [Installing and running Gitxray](installing.md) in order to get started.
