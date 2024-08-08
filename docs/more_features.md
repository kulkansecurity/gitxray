# More Features &#129470

There's awesome and then there's _good_ features. 

## Lots of e-mail addresses &#128231; and Profiling data &#128100;

`gitxray` will report for each Contributor, an `emails` category listing all unique e-mail address collected from parsing:

* The User's profile
* Each commit made by the User
* PGP Primary Keys and PGP SubKeys

Additionally, Personal Information (e.g. social networks) voluntarily made Public by the User is extracted from multiple sources including PGP Key BLOBs and reported under a `personal` category.

Finally, the `profiling` category tends to display information related to the account itself (e.g. creation date, last updated, and more.)

You may focus specifically on `emails`, `personal`, and `profiling` fields with (Verbose is optional):
```py
gitxray -o https://github.com/SampleOrg -v -f emails,personal,profiling
```
or, for a specific repository, with: 
``` py
gitxray -r https://github.com/SampleOrg/SampleRepo -v -f emails,personal,profiling
```

## Looking out for malicious Releases and Assets &#128065; 

It is possible for Threat Actors to compromise credentials of a Repository Maintainer in order to deploy malware by silently updating released Assets (the typical package you would download when a Release includes downloadable Assets); which is why `gitxray` looks at all Repository Releases and informs of:

* Assets that were **updated** at least a day **AFTER** their release, which might lead to suggest they've been infected and/or tampered with. Or it could just be a maintainer fixing an asset without wanting to create a new release.

* Users who have historically created releases and/or uploaded assets, as well as the % vs. the total amount of releases or assets uploaded in the repository; which may allow you to flag potential suspicious activity. For example, you might notice an account which never created Releases before now uploading assets.


All of this information is included by `gitxray` in a `releases` category, which means you can focus on those results (if any exist) with:

``` bash
gitxray -o https://github.com/SampleOrg -f releases
```

## Anonymous contributors &#128065; 

As stated in [GitHub documentation](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-contributors), only the first 500 author email addresses in a Repository will link to actual GitHub users or accounts. The rest will appear as "anonymous" contributors without associated GitHub information.

Additionally, when an author's email address in a commit is not associated with a GitHub account, the User will also be considered Anonymous.

Lucky for us, `gitxray` also includes within its output the entire list of Anonymous contributors received from GitHub. The list is first processed to combine all variations of Names used by the author for a same e-mail, which means the list can also be pretty useful when, for example, executing OSINT.

To filter for anonymous contributors, you may use:
``` bash
gitxray -o https://github.com/SampleOrg -f anonymous
```

## And so much more.

We've covered a large amount of use-cases for `gitxray`, yet we're nowhere finished. Start X-Raying today your favorite Organizations and Repositories and discover more ways of connecting dots. We've outlined a series of Ideas we are working on under the [Pending Work](pending_work.md) section.
