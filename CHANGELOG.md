# Changelog

## Release v1.0.17 (January 26th, 2025)
* Added a new "--shush" parameter which turns "shushable" mode on, discarding any progress output from stdout.
* Added a new finding under the "personal" category which tells if the contributor has enabled "Available for hire" in their profile (docs describe it here: https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-user-account-settings/about-available-for-hire)
* Added a "WARNING" label/prefix on a couple of Workflow findings which deserve an extra highlight.
* Turned gh_api into a class named GitHubRESTAPI which stores a reference to gx_output.
* Added a new stdout method in gx_output to act as a proxy for print() calls, discarding "shushable" output.

## Release v1.0.16.5 (January 18th, 2025)
* Fixed an error case (an unhandled exception) that showed up when scanning repositories with a very large list of contributors (e.g. torvalds/linux, or MicrosoftDocs/azure-docs), which leads to GitHub REST APIs responding in an undocumented manner, stating that: "The history or contributor list is too large to list contributors for this repository via the API".

## Release v1.0.16.4 (October 30th, 2024)
* Fixed an error case that should be fixed in gh_api.py eventually: GitHub returning unexpected error responses when querying for certain releases while being unauthenticated. Thank you once again @fearcito for your input and testing.

## Release v1.0.16.3 (October 28th, 2024)
* Only showing "updated at" for comments if the created_at and updated_at field values differ. This helps place focus on updated comments which could potentially reveal a contributor trying to hide a past comment. GitHub is kind to show an Edit history for said comments as a menu option next to the comment itself.

## Release v1.0.16.2 (October 25th, 2024)
* Added validation against Null values for fields "author" and "uploader" in Releases and Assets. Special thanks to @fearcito for reporting the issue.

## Release v1.0.16.1 (October 22nd, 2024)
* Fixed a typo in a call to r_log() which led to an uhandled exception when scanning repositories with self-hosted runners. Special thanks to @farnaboldi for reporting the issue.

## Release v1.0.16 (October 18th, 2024)
* Added a brand new HTML output format/report by default, making results a lot easier to navigate! Custom search bar instead of relying on DataTables which can be super slow for large HTML files. We're now also groupping results by Category across all contributors and highlighting results which contain a WARNING keyword.
* Added certain association results to Contributor results, not all to prevent extra noise.
* Added the ability to specify a directory for output instead of a file, gitxray creating the filename for you.
* Removed the concept of 'Verbose' results, merging them with the non-verbose categories.
* Removed the need for repositories and organizations to start with https://github.com (Thanks to @mattaereal for pointing that out!)

## Release v1.0.15 (September 20th, 2024)

* Added searching for similar repository names in GitHub, Warning if another repository with the same name and better reputation is found.
* Added commit time analysis, grouping commit hours per contributor and calculating the percentage of commits at each hour. This feature provides insights into contributors' activity patterns and helps identify potential anomalies.
* Added new Workflows X-Ray module which contains all Workflow-related logic. Moved in some of the logic that was under the Repository x-Ray.
* Added counts of Workflow Runs to identify when Workflow Runs were DELETED, which may have been the result of an attacker erasing their tracks, or legitimate cleanup.
* Added a series of basic Workflow security checks which might be an indicator of a vulnerable Workflow.
* Added to the Workflows X-Ray the ability to print, for each workflow, how many times it was executed by non-contributors as well as contributors.
* Added to the Workflows X-Ray the ability to parse and print any secret names used in a Workflow.
* Added a display of Progress % for time consuming queries and a time estimate in seconds-left prior to resuming execution.
* Added ability to SKIP heavy querying live by handling CTRL+C, which means we've also removed any caps or limits recently introduced.
* Fixed parsing of dict-formatted results coming from the REST API so that we keep the last key and not the second one.
* Fixed a few exceptions which arise by hitting CTRL+C and skipping or breaking API calls

## Release v1.0.14 (September 1st, 2024)

* Added a new check on workflow runs for accounts which are NOT contributors, presenting a WARNING on screen. This could help identify hack attempts via Workflow runs.
* Added a new check on releases to identify accounts which create releases/upload assets and are NOT contributors, also WARNING on screen.
* Added pulling and analysis of Comments for Commits, Issues and Pull Requests.
* Added messages to point out when comments get updated (Edited) after a day of being created.
* Added parsing of reactions for comments in Commits, Issues and Pulls. We're printing the comment that had the most Positive, Neutral and Negative reactions in Commits, Issues and PRs.
* Added support capped to 5000 Workflow runs for analyzing past workflow runs in a repository. Runs can go very high in the, for example, 50k, which is why we cap.
* Added a limit of 5000 Artifacts inspection to prevent the analysis from being too expensive in really big repositories.
* Added support to get repository labels, pointing out specifically those which are custom.
* Added to the repository summary the printing of stargazers and watchers count even if 0, as it talks about reputation.
* Added code to fetch environment protection rules; but it is commented out because it is seldom used.
* Added to contributors_xray.py, a message to the user on how to use the filtering function in order to filter results for non-contributors.
* Added to gx_context.py, two (2) helper methods, isContributor and areContributors which iterate and check logins against the list of cached repo contributors.
* Added to the UNRELIABLE ACTIVITY message a clarification that the mismatch may be due to a rebased repository.
* Added count of Pull Requests to the output line showing the PR link for a contributor.
* Changed the way we refer to account results in gx_output.py - Instead of stating Contributors we're going to say accounts, as we may have non-contributor results.
* Moved multiple results that were under the "urls" category to the corresponding category instead (eg. commit urls to a commit category). Makes it easier to navigate visually.
* Fixed a visual typo (extra space) when printing 'starred' public events in verbose mode.
* Fixed querying of environments for exceptional repository-cases where the API returns a 404 not found in json format instead of an empty list of results.
* Fixed gh_api code for limiting results count in pagination when the API returns a dict with total_results followed by a list.
* Fixed identifying unreliable dates in commits mismatching account creation dates. Now only checking against 'author', and not checking against 'committer'.

## Release v1.0.13 (August 19th, 2024)

* Added the ability to identify unreliable commits containing unreliable dates in a repository. This could be the case when, for example, a contributor's account creation date is newer than a contributor's commit date in the repository. In certain cases, those can be attempts at faking historic activity by malicious actors, or it could also mean that an account was deleted and the same handle re-registered by someone else (https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-your-personal-account/deleting-your-personal-account), among other possibilities. These warnings will show under the "commits" category. Gitxray will present a Warning stating that Unreliable historic activity was detected. 
* Moved the summary of signed vs. unsigned commits to a new "commits" category.
* Added support for Tags and Artifacts; a full list can be printed by turning on Verbose mode (-v). Tags are only returned stripped/lightweight by the GitHub API (at least when listing them all), sad - Nonetheless we've included code to support collecting data on taggers; should at some point GH begin returning full tag data.
* Added Stargazers count to the profiling output of a repository.
* Added "WARNING" labels to results which may require special attention (eg for fake profiles, updated release assets, ...) Makes it easy to use "-f warning" when running gitxra if you only want to focus on warnings.
* Added listing branches under repository results, specifically pointing out which ones are unprotected vs. protected branches.
* Replicating in Contributor-specific results a series of Releases-related messages that were only displayed under Repository results.
* Added collecting and printing available Environments (https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment).
* Reduced temporary output lines when executing checks against a Repository.
* Added CHANGELOG.md file to track changes.

## Release v1.0.12 (August 7th, 2024)

* Fixed parsing of PGP armored keys by adding support for a "Charset" field.

## Release v1.0.11 (August 6th, 2024)

* First public release of Gitxray
* More information available at: https://kulkansecurity.github.io/gitxray/
