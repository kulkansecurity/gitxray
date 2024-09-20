from . import gx_arg_parser, gx_definitions
from collections import defaultdict
import os

class Context:
    def __init__(self):
        self._cmd_args = gx_arg_parser.parse_arguments()
        self._USING_TOKEN = os.environ.get(gx_definitions.ENV_GITHUB_TOKEN, None)
        self.reset()

    def reset(self):
        self._identifier_user_relationship = defaultdict(list)

    def usingToken(self):
        return self._USING_TOKEN != None

    def debugEnabled(self):
        return self._cmd_args.debug

    def verboseEnabled(self):
        return self._cmd_args.verbose

    def verboseLegend(self):
        return "" if self.verboseEnabled() else "Set verbose mode for more data. "

    def listAndQuit(self):
        return self._cmd_args.list

    def getOutputFile(self):
        return self._cmd_args.outfile

    def getOutputFormat(self):
        return self._cmd_args.output_format if self._cmd_args.output_format is not None else "text"

    def getOutputFilters(self):
        return self._cmd_args.filters

    def getContributorScope(self):
        return self._cmd_args.contributor

    def getRepositoryTargets(self):
        return self._cmd_args.repositories_file if self._cmd_args.repositories_file is not None else [self._cmd_args.repository]

    def setRepositoryTargets(self, targets_list):
        self._cmd_args.repositories_file = targets_list
        return

    def getOrganizationTarget(self):
        return self._cmd_args.organization

    def setRepository(self, repository):
        self._repository = repository
        return

    def setContributor(self, contributor):
        self._contributor = contributor
        return

    def setContributors(self, contributors):
        self._contributors = contributors
        return

    def getRepository(self):
        return self._repository

    def getContributor(self):
        return self._contributor

    def getContributors(self):
        return self._contributors

    def isContributor(self, contributor_login):
        return any(contributor.get('login') == contributor_login for contributor in self.getContributors())

    def areContributors(self, contributors_logins):
        return any(contributor.get('login') in contributors_logins for contributor in self.getContributors())

    # We also use our gitxray context to cross-reference identifiers.
    def linkIdentifier(self, identifierType, identifierValues, contributorLogin):
        for identifierValue in identifierValues:
            if contributorLogin not in self._identifier_user_relationship[(identifierType, identifierValue)]:
                self._identifier_user_relationship[(identifierType, identifierValue)].append(contributorLogin)
        return

    def getCollisions(self):
        collisions = defaultdict(list)
        for (identifierType, identifierValue), contributors in self._identifier_user_relationship.items():
            if len(contributors) > 1:
                collisions[(identifierType, identifierValue)].extend(contributors)

        return dict(collisions)

    def getIdentifierValues(self, identifierType):
        results = defaultdict(list)
        for (currentIdentifierType, identifierValue), contributors in self._identifier_user_relationship.items():
            if currentIdentifierType == identifierType:
                for contributor in contributors:
                    if identifierValue not in results[contributor]:
                        results[contributor].append(identifierValue)
        return dict(results)

