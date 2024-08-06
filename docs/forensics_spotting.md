# Forensics and Spotting Associations

Open source projects are under attack, with malicious actors hiding in plain sight. Attackers are normally well-funded and take precautions to avoid detection. Enter some of `gitxray`'s features: If you've woken up today wearing your Batman t-shirt and/or you're carefully looking at evidence while protecting a repository, try leveraging some of `gitxray`'s features.

## Important - Please read

Associations MUST NOT be directly and blindly used to report fake or shadow accounts. They are automatic observations from a piece of well-intended code. Do NOT treat association results as findings directly. 

Remember, there is more good than evil out there. We must protect open-source projects by first and foremost respecting open-source developers. Ensure that any actions taken are thoughtful and based on solid evidence, not just automated associations. Collaboration and trust are the foundations of the open-source community, and preserving these values is crucial for its continued success.
## Run a full verbose X-Ray on a repository
``` bash
gitxray -r https://github.com/SampleOrg/Repo1 -v
```

## Focus on associations
Associations are currently supported at a _Repository level only_. 

Spotted associations can include:

* Sharing of PGP Keys or Emails
* Accounts that were created and/or updated precisely in the same day
* Accounts which relied on GitHub's Web Editor to sign commits
* Accounts which used the same Algorithms for SSH/PGP signatures
* Armored Keys which displayed the same Comment or Version fields

``` bash
gitxray -r https://github.com/SampleOrg/repo1 -f association
```

## Spot users who are in the Top 3 of Rejected PRs
``` bash
gitxray -r https://github.com/SampleOrg/repo1 -f contributors
```

## Releases and Assets
When reviewing repository Releases and Assets, Gitxray will:

* Print out which users have historically created releases and/or uploaded assets, as well as the % vs. the total amount of releases or assets; so you can flag potential suspicious activity.

* Report on any Assets that were uploaded at least a day AFTER their initial release, which might lead to suggest they've been infected and/or tampered with.

``` bash
gitxray -r https://github.com/SampleOrg/repo1 -f user_input,pass,private
```

## Observing user Recent behaviour 
When Verbose mode is enabled, recent events from the past 90 days for each user account will be processed and printed by Gitxray, among which you may spot:
* Accounts which are automatically following other users. You'll likely notice a large amount of consecutive follow events.
* Accounts which are automatically starring repositories. You'll likely notice a large amount of consecutive watching activity.
* Accounts which are forking a large amount of repositories; potentially for the sake of tricking victims into using their tampered fork.

More use-cases for gitxray can be found in the [OSINT and Pentesting](osint_pentest.md) and [Securing your Team and Repositories](securing_repos.md) sections.
