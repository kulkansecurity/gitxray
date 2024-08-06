# Securing your Team and Repositories

If you have one or more repositories to safeguard, then you may be able to leverage `gitxray` to improve the security stance of your repository and/or your development team.

## Checking contributors for information disclosure

You may be concerned about what your team members are currently sharing in their profile to the world.

Filtering results across all Organization repositories focused on personal information and emails
``` bash
gitxray -o https://github.com/SampleOrg -f personal,emails
```

We've discovered A LOT of internal information being disclosed by accident through Key names. Try filtering for user_input to find those cases
``` bash
gitxray -o https://github.com/SampleOrg -f user_input
```

## Checking for contributors who have not signed their commits
Those who have not signed ANY of their commits may need your help in understanding how signing is done and the dangers of impersonation.

``` bash
gitxray -r https://github.com/SampleOrg/repo1 -f "not signed any"
```

## Checking for contributors who have a mix of signed and unsigned commits
These contributors likely need to be reminded of the importance of signing, AND their unsigned commits could require an audit.

``` bash
gitxray -r https://github.com/SampleOrg/repo1 -f "has a mix of"
```

## Checking for broken signatures
These are attempts at signing that have likely failed for multiple reasons. You'll likely want to check the reason behind these failures; as it sometimes is as simple as the contributor not having uploaded their public key to their profile.

``` bash
gitxray -r https://github.com/SampleOrg/repo1 -f signatures
```

More use-cases for gitxray can be found in the [Forensics and Spotting Associations](forensics_spotting.md) and [Securing your Team and Repositories](securing_repos.md) sections.

