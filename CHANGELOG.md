# Changelog

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
