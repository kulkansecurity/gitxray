#!/usr/bin/env python3
import os, sys, datetime
from gitxray.include import gh_api, gx_output as gx_output_class, gx_context as gx_context_class, gx_definitions
from gitxray.xrays import repository_xray
from gitxray.xrays import contributors_xray
from gitxray.xrays import association_xray
from gitxray.xrays import workflows_xray

def gitxray_cli():
    print("""
           ███   █████                                              
          ░░░   ░░███                                               
  ███████ ████  ███████   █████ █████ ████████   ██████   █████ ████
 ███░░███░░███ ░░░███░   ░░███ ░░███ ░░███░░███ ░░░░░███ ░░███ ░███ 
░███ ░███ ░███   ░███     ░░░█████░   ░███ ░░░   ███████  ░███ ░███ 
░███ ░███ ░███   ░███ ███  ███░░░███  ░███      ███░░███  ░███ ░███ 
░░███████ █████  ░░█████  █████ █████ █████    ░░████████ ░░███████ 
 ░░░░░███░░░░░    ░░░░░  ░░░░░ ░░░░░ ░░░░░      ░░░░░░░░   ░░░░░███ 
 ███ ░███                                                  ███ ░███ 
░░██████                                                  ░░██████  
 ░░░░░░                                                    ░░░░░░   
gitxray: X-Ray and analyze Github Repositories and their Contributors. Trust no one!
v1.0.15 - Developed by Kulkan Security [www.kulkan.com] - Penetration testing by creative minds.
"""+"#"*gx_definitions.SCREEN_SEPARATOR_LENGTH)

    # Let's initialize a Gitxray context, which parses arguments and more.
    gx_context = gx_context_class.Context()

    # Let's initialize our Output object that handles stdout and file writing in text or json
    gx_output = gx_output_class.Output(gx_context)

    # Let's warn the user that unauth RateLimits are pretty low
    if not gx_context.usingToken():
        gx_output.warn(f"{gx_definitions.ENV_GITHUB_TOKEN} environment variable not set, using GitHub RateLimits unauthenticated.")
        gx_output.warn("Unauthenticated requests to the Github API will enforce a very low and strict RateLimit.")
        gx_output.warn("Without setting a GitHub token you may only be able to scan small repositories uninterruptedly.")
    else:
        gx_output.notify(f"GitHub Token loaded from {gx_definitions.ENV_GITHUB_TOKEN} env variable.")

    if not gx_context.verboseEnabled():
        gx_output.notify(f"Verbose mode is DISABLED. You might want to use -v if you're hungry for information.")

    if gx_context.getOutputFilters():
        gx_output.notify(f"You have ENABLED filters - You will only see results containing the following keywords: {str(gx_context.getOutputFilters())}")

    if gx_context.getOrganizationTarget():
        org_repos = gh_api.fetch_repositories_for_org(gx_context.getOrganizationTarget())
        print("#"*gx_definitions.SCREEN_SEPARATOR_LENGTH)
        if isinstance(org_repos, list) and len(org_repos) > 0: 
            gx_output.notify(f"YOU HAVE EXPANDED THE SCOPE TO AN ORGANIZATION: A list of {len(org_repos)} repositories have been discovered. Sit tight.")
            if gx_context.listAndQuit():
                gx_output.notify(f"LISTING REPOSITORIES FOR THE ORGANIZATION AND EXITING..")
                print(", ".join([r.get('full_name') for r in org_repos]))
                sys.exit()
            gx_context.setRepositoryTargets([r.get('html_url') for r in org_repos])
        else: 
            gx_output.warn("Unable to pull repositories for the organization URL that was provided. Is it a valid Organization URL?")
            if gx_context.debugEnabled():
                print(org_repos)
            sys.exit()

    try:
        for repo in gx_context.getRepositoryTargets():
            r_started_at = datetime.datetime.now()
            try:
                repository = gh_api.fetch_repository(repo)
                gx_output.r_log(f"X-Ray on repository started at: {r_started_at}", repository=repository.get('full_name'), rtype="metrics")
                print("#"*gx_definitions.SCREEN_SEPARATOR_LENGTH)
                print("Now verifying repository: {}".format(repository.get('full_name')))
            except Exception as ex:
                print("Unable to pull data for the repository that was provided. Is it a valid repo URL?")
                if gx_context.debugEnabled():
                    print(ex)
                sys.exit()
    
            # Let's keep track of the repository that we're X-Raying
            gx_context.setRepository(repository)

            # Now call our xray modules! Specifically by name, until we make this more plug and play
            # The standard is that a return value of False leads to skipping additional modules
    
            if not contributors_xray.run(gx_context, gx_output): continue
            if not repository_xray.run(gx_context, gx_output): continue
            if not workflows_xray.run(gx_context, gx_output): continue

            # Now that we're done, let's cross reference everything in the repository.
            association_xray.run(gx_context, gx_output)

            r_ended_at = datetime.datetime.now()
            gx_output.r_log(f"X-Ray on repository ended at: {r_ended_at} - {((r_ended_at-r_started_at).seconds/60):.2f} minutes elapsed", rtype="metrics")
            gx_output.doOutput()

            print(f"\rRepository has been analyzed.." + " "*40)

            # We're resetting our context on every new repo; eventually we'll maintain a context per Org.
            gx_context.reset() 

    except KeyboardInterrupt:
        gx_output.warn("\r\nMain program flow interrupted - Printing all results obtained this far.")
        gx_output.doOutput()

if __name__ == "__main__":
    gitxray_cli()
