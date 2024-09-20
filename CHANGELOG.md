# Changelog

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
