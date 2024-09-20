from gitxray.include import gx_definitions, gh_api, gh_time
from collections import defaultdict
import base64, re


def run(gx_context, gx_output):
    print("\rRunning verifications on existing Workflows..."+" "*50)
    repository = gx_context.getRepository()
    contributors = gx_context.getContributors()

    print(f"\rQuerying for repository action workflows.."+" "*50, end="")
    workflows = gh_api.fetch_repository_actions_workflows(repository)
    if workflows != None and workflows.get('total_count') > 0:
        gx_output.r_log(f"{workflows.get('total_count')} Workflows available at: [{repository.get('url')}/actions/workflows]", rtype="workflows")
        for workflow in workflows.get('workflows'):
            workflow_file = workflow.get('path').split('/')[-1]
            gx_output.r_log(f"Workflow [{workflow.get('name')}] created [{workflow.get('created_at')}], updated [{workflow.get('updated_at')}]: [{workflow.get('html_url')}]", rtype="workflows")

            runs = gh_api.fetch_repository_actions_runs(repository, workflow_file=workflow_file)
            if runs != None and runs.get('total_count', 0) > 0: 
                run_contributors = defaultdict(int)
                run_non_contributors = defaultdict(int)
                run_actors = defaultdict(int)
                run_numbers = []
                for run in runs.get('workflow_runs'):
                    run_numbers.append(run.get('run_number', -1))
                    run_actors[run.get('actor').get('login')] += 1

                if len(run_numbers) > 0:
                    min_run = min(run_numbers)
                    max_run = max(run_numbers)
                    missing_numbers = sorted(set(range(min_run, max_run+1)) - set(run_numbers))
                    if len(missing_numbers) > 0: 
                        gx_output.r_log(f"Workflow [{workflow.get('name')}] has [{len(missing_numbers)}] missing or deleted runs. This could have been an attacker erasing their tracks, or legitimate cleanup. {gx_context.verboseLegend()}", rtype="workflows")
                        if gx_context.verboseEnabled():
                            gx_output.r_log(f"Missing run numbers for Workflow [{workflow.get('name')}]: {missing_numbers}", rtype="v_workflows")

                total_runs = int(runs.get('total_count'))
                for actor, actor_runs in run_actors.items():
                    percentage_runs = (actor_runs / total_runs) * 100
                    if gx_context.isContributor(actor):
                        run_contributors[actor] += 1
                        message = f"Contributor [{actor}] ran {actor_runs} [{percentage_runs:.2f}%] times workflow [{workflow.get('name')}] - See them at: [{repository.get('html_url')}/actions?query=actor%3A{actor}]"
                    else:
                        run_non_contributors[actor] += 1
                        message = f"{actor} is NOT a contributor and ran {actor_runs} [{percentage_runs:.2f}%] times workflow [{workflow.get('name')}] - See them at: [{repository.get('html_url')}/actions?query=actor%3A{actor}]"

                    gx_output.c_log(message, rtype="v_workflows", contributor=actor)
                    gx_output.r_log(message, rtype="v_workflows")
          
                if len(run_non_contributors) > 0 or len(run_contributors) > 0: 
                    all_non_c_runners = len(run_non_contributors.keys())
                    all_non_c_runs = sum(run_non_contributors.values())
                    all_c_runners = len(run_contributors.keys())
                    all_c_runs = sum(run_contributors.values())
                    gx_output.r_log(f"Workflow [{workflow.get('name')}] was run by [{all_non_c_runners}] NON-contributors [{all_non_c_runs}] times and by [{all_c_runners}] contributors [{all_c_runs}] times. {gx_context.verboseLegend()}[{repository.get('html_url')}/actions/workflows/{workflow_file}]", rtype="workflows")

            contents = gh_api.fetch_repository_file_contents(repository, workflow.get('path'))
            if contents.get('content') != None:

                # We have the contents of a workflow, let's analyze it.
                encoded_content = contents.get('content')
                decoded_content = base64.b64decode(encoded_content).decode('utf-8').lower()

                # https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners
                if "self-hosted" in decoded_content: gx_output.rlog(f"Workflow [{workflow.get('name')}] appears to be executing in a self-hosted runner: [{workflow.get('html_url')}]", rtype="workflows")

                # https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/
                if any(a in decoded_content for a in ["pull_request_target","workflow_run","issue_comment","issue:"]):
                    gx_output.r_log(f"Workflow [{workflow.get('name')}] may be triggered by an event that might be misused by attackers. See more at https://gitxray.com/vulnerable_workflows", rtype="workflows")

                #https://github.com/actions/toolkit/issues/641
                if "ACTIONS_ALLOW_UNSECURE_COMMANDS: true" in decoded_content: gx_output.r_log(f"Workflow [{workflow.get('name')}] sets ACTIONS_ALLOW_UNSECURE_COMMANDS.", rtype="workflows")

                if "secrets." in decoded_content: 
                    secrets = re.findall(r"secrets\.[A-Za-z-_0-9]*", decoded_content) 
                    gx_output.r_log(f"Workflow [{workflow.get('name')}] makes use of Secrets: {secrets}: [{workflow.get('html_url')}]", rtype="workflows")

                # https://securitylab.github.com/resources/github-actions-untrusted-input/
                user_inputs = []
                for input_label, pattern in gx_definitions.WORKFLOWS_USER_INPUT.items():
                    if re.search(pattern, decoded_content):
                        user_inputs.append(input_label)
 
                if len(user_inputs) > 0: gx_output.r_log(f"Workflow [{workflow.get('name')}] handles user input via: {user_inputs}", rtype="workflows")


    print(f"\rQuerying for repository workflow artifacts.."+" "*30, end="")
    artifacts = gh_api.fetch_repository_actions_artifacts(repository)
    if artifacts != None and artifacts.get('total_count') > 0:
        gx_output.r_log(f"{artifacts.get('total_count')} Artifacts available at: [{repository.get('url')}/actions/artifacts]", rtype="artifacts")
        for artifact in artifacts.get('artifacts'):
            # There are normally multiple artifacts hence we keep them under verbose.
            gx_output.r_log(f"Artifact [{artifact.get('name')}] created [{artifact.get('created_at')}], updated [{artifact.get('updated_at')}]: {artifact.get('url')}", rtype="v_artifacts")
            created_at = artifact.get('created_at')
            created_at_ts = gh_time.parse_date(created_at)
            updated_at = artifact.get('updated_at')
            updated_at_ts = gh_time.parse_date(updated_at)
            # This shouldn't happen but we still run a check; artifacts can't be updated but instead completely overwritten
            # More data here: https://github.com/actions/upload-artifact#overwriting-an-artifact
            if (updated_at_ts-created_at_ts).days > 0:
                gx_output.r_log(f"WARNING: An artifact [{artifact.get('name')}] was updated {(updated_at_ts-created_at_ts).days} days after being created: {artifact.get('url')}", rtype="artifacts")


    print()
    return True
