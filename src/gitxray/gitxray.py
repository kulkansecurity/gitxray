#!/usr/bin/env python3
import os, sys, datetime
from gitxray.include import gh_api as gh_api_class, gx_output as gx_output_class, gx_context as gx_context_class, gx_definitions
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
gitxray: X-Ray and analyze GitHub Repositories and their Contributors. Trust no one!
v1.0.17.1 - Developed by Kulkan Security [www.kulkan.com] - Penetration testing by creative minds.
"""+"#"*gx_definitions.SCREEN_SEPARATOR_LENGTH)

    # Let's initialize a Gitxray context, which parses arguments and more.
    gx_context = gx_context_class.Context()

    # Let's initialize our Output object that handles stdout and file writing in text or json
    gx_output = gx_output_class.Output(gx_context)

    # And GitHub's REST API, sharing a ref to the Output object
    gh_api = gh_api_class.GitHubRESTAPI(gx_output)

    # Let's warn the user that unauth RateLimits are pretty low
    if not gx_context.usingToken():
        gx_output.warn(f"{gx_definitions.ENV_GITHUB_TOKEN} environment variable not set, using GitHub RateLimits unauthenticated.")
        gx_output.warn("Unauthenticated requests to the GitHub API will enforce a very low and strict RateLimit.")
        gx_output.warn("Without setting a GitHub token you may only be able to scan small repositories uninterruptedly.")
    else:
        gx_output.notify(f"GitHub Token loaded from {gx_definitions.ENV_GITHUB_TOKEN} env variable.")

    gx_output.notify(f"Output format set to [{gx_context.getOutputFormat().upper()}] - You may change it with -outformat.")

    if gx_context.getOutputFile():
        gx_output.notify(f"Output file set to: {str(gx_context.getOutputFile())} - You may change it with -out.")
        if gx_context.getOrganizationTarget():
            # Let's warn the user that in Organization mode, the output file will contain a repository name preffix
            gx_output.warn("The Output file name when targetting an Organization will include an Organization and Repository prefix.")

    if gx_context.getOutputFilters():
        gx_output.notify(f"You have ENABLED filters - You will only see results containing the following keywords: {str(gx_context.getOutputFilters())}")

    if gx_context.getOrganizationTarget():
        org_repos = gh_api.fetch_repositories_for_org(gx_context.getOrganizationTarget())
        gx_output.stdout("#"*gx_definitions.SCREEN_SEPARATOR_LENGTH)
        if isinstance(org_repos, list) and len(org_repos) > 0: 
            gx_output.notify(f"YOU HAVE EXPANDED THE SCOPE TO AN ORGANIZATION: A list of {len(org_repos)} repositories have been discovered. Sit tight.")
            if gx_context.listAndQuit():
                gx_output.notify(f"LISTING REPOSITORIES FOR THE ORGANIZATION AND EXITING..", False)
                gx_output.stdout(", ".join([r.get('full_name') for r in org_repos]), False)
                sys.exit()
            gx_context.setRepositoryTargets([r.get('html_url') for r in org_repos])
        else: 
            gx_output.warn("Unable to pull repositories for the organization URL that was provided. Is it a valid Organization URL?")
            if gx_context.debugEnabled():
                gx_output.stdout(org_repos, shushable=False)
            sys.exit()

    try:
        for repo in gx_context.getRepositoryTargets():
            r_started_at = datetime.datetime.now()
            try:
                repository = gh_api.fetch_repository(repo)
                gx_output.r_log(f"X-Ray on repository started at: {r_started_at}", repository=repository.get('full_name'), rtype="metrics")
                gx_output.stdout("#"*gx_definitions.SCREEN_SEPARATOR_LENGTH)
                gx_output.stdout("Now verifying repository: {}".format(repository.get('full_name')))
            except Exception as ex:
                print("Unable to pull data for the repository that was provided. Is it a valid repo URL?")
                if gx_context.debugEnabled():
                    print(ex)
                sys.exit()
    
            # Let's keep track of the repository that we're X-Raying
            gx_context.setRepository(repository)

            # if an Organization is in target, add a repository prefix to the output filename
            if gx_context.getOrganizationTarget() and gx_context.getOutputFile(): gx_context.setOutputFilePrefix(repository.get("full_name"))

            # Now call our xray modules! Specifically by name, until we make this more plug and play
            # The standard is that a return value of False leads to skipping additional modules
    
            if not contributors_xray.run(gx_context, gx_output, gh_api): continue
            if not repository_xray.run(gx_context, gx_output, gh_api): continue
            if not workflows_xray.run(gx_context, gx_output, gh_api): continue

            # Now that we're done, let's cross reference everything in the repository.
            association_xray.run(gx_context, gx_output, gh_api)

            r_ended_at = datetime.datetime.now()
            gx_output.r_log(f"X-Ray on repository ended at: {r_ended_at} - {((r_ended_at-r_started_at).seconds/60):.2f} minutes elapsed", rtype="metrics")
            gx_output.doOutput()

            gx_output.stdout(f"\rRepository has been analyzed.." + " "*40)

            # We're resetting our context on every new repo; eventually we'll maintain a context per Org.
            gx_context.reset() 

    except KeyboardInterrupt:
        gx_output.warn("\r\nMain program flow interrupted - Printing all results obtained this far.")
        gx_output.doOutput()

if __name__ == "__main__":
    gitxray_cli()
