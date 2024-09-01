import json, random
from . import gx_definitions

class Output:
    ANSI_COLORS = { "RED": "\033[31m", "GREEN": "\033[32m", "YELLOW": "\033[33m", "BLUE": "\033[34m", "MAGENTA": "\033[35m", "CYAN": "\033[36m", "BRIGHT_RED": "\033[91m", "BRIGHT_GREEN": "\033[92m", "BRIGHT_YELLOW": "\033[93m", "BRIGHT_BLUE": "\033[94m", "BRIGHT_MAGENTA": "\033[95m", "BRIGHT_CYAN": "\033[96m", "BRIGHT_WHITE": "\033[97m", "RESET": "\033[0m" }


    def __init__(self, gx_context, outfile=None, outformat='text'):

        self._debug = gx_context.debugEnabled()
        self._verbose = gx_context.verboseEnabled() or self._debug 

        self._outfile = None
        # We're appenders, we're not destroyers.
        if gx_context.getOutputFile(): self._outfile = open(gx_context.getOutputFile(), 'a+')
        self._outformat = gx_context.getOutputFormat()

        self._filters = gx_context.getOutputFilters()
        self._rtype_color_map = {}

        self._cscope = gx_context.getContributorScope() 

        self.reset()

    def reset(self):
        self._repositories = {}
        self._contributors = {}
        self._anonymous = {}
        self._keys = {}
        self._index = None
        self._repository = None
        self._contributor = None
 

    def _log(self, log_type, data="Default log data", rtype="info", identifier=None):
        if not identifier:
            raise Exception("You need to specify an identifier.")

        storage = getattr(self, f"_{log_type}")

        if identifier not in storage:
            storage[identifier] = {}

        if rtype not in storage[identifier]:
            storage[identifier][rtype] = []

        storage[identifier][rtype].append(data)

    def r_log(self, data="You called r_log without specifying data", rtype="info", repository=None):
        if repository: self._repository = repository
        self._log('repositories', data, rtype, self._repository)

    def c_log(self, data="You called c_log without specifying data", rtype="info", contributor=None):
        if contributor: self._contributor = contributor

        if self._cscope and (self._contributor not in self._cscope): return
        self._log('contributors', data, rtype, self._contributor)

    def a_log(self, data="You called a_log without specifying data", rtype="info", anonymous=None):
        self._log('anonymous', data, rtype, anonymous)


    # Direct output, not really waiting for results to print this out.
    def debug(self, message):
        if self._debug:
            colored_message = f"{self.ANSI_COLORS['YELLOW']}[D]{self.ANSI_COLORS['RESET']} {message}"
            return print(colored_message)

    def debug_enabled(self):
        return self._debug
   
    def verbose_enabled(self):
        return self._verbose

    # Direct output, not really waiting for results to print this out.
    def warn(self, message):
        colored_message = f"{self.ANSI_COLORS['YELLOW']}{message}{self.ANSI_COLORS['RESET']}"
        return print(colored_message)

    def notify(self, message):
        colored_message = f"{self.ANSI_COLORS['BRIGHT_BLUE']}{message}{self.ANSI_COLORS['RESET']}"
        return print(colored_message)

    def get_rtype_color(self, rtype):
        if rtype not in self._rtype_color_map:
            self._rtype_color_map[rtype] = random.choice(list(self.ANSI_COLORS.values())[:-1])
        return self._rtype_color_map[rtype]

    def _print_output(self, data_source, entity_string, skip_ansi=False):
        output = ""

        if skip_ansi: temp_colors = {} # empty colors
        else: temp_colors = self.ANSI_COLORS

        reset_color = temp_colors.get('RESET','')

        # Gather all unique rtypes from both repositories and contributors
        all_rtypes = {rtype for data in self._repositories.values() for rtype in data.keys()}
        all_rtypes.update(rtype for data in self._contributors.values() for rtype in data.keys())

        # Find the longest rtype for formatting purposes
        max_rtype_length = max(len(rtype) for rtype in all_rtypes) if len(all_rtypes) > 0 else 0

        no_results = []
        for entity, data in data_source.items():

            result_lines = []
            for rtype in data.keys():
                if not self.debug_enabled() and ("debug" in rtype.lower()):
                    continue
                if not self.verbose_enabled() and ("v_" in rtype.lower()):
                    continue

                random_color = "" if skip_ansi else (self.get_rtype_color(rtype) if data_source != self._anonymous else temp_colors.get('BLUE',''))
                formatted_rtype = f"[{rtype}]:".ljust(max_rtype_length + 1)

                for line in data[rtype]:
                    outline = f"{random_color}{formatted_rtype}{reset_color} {line}\n" 
                    if self._filters != None and (all(f.lower() not in outline.lower() for f in self._filters)):
                        continue
                    result_lines.append(outline)


            if len(result_lines) > 0: 
                output += f"#" * gx_definitions.SCREEN_SEPARATOR_LENGTH + "\n"
                output += f"{temp_colors.get('GREEN','')}Found results{temp_colors.get('RESET','')} for {entity_string}.".replace("ENTITY_STR", entity)
                if self._filters != None:
                    color = temp_colors.get('BRIGHT_BLUE','')
                    output += f" {color}Filters applied: {str(self._filters)}{reset_color}\n"
                else: output += "\r\n"
                output += "".join(result_lines)

            else:
                if self.verbose_enabled():
                    output += f"#" * gx_definitions.SCREEN_SEPARATOR_LENGTH + "\n"
                    output += f"No results to show for {entity_string}.".replace("ENTITY_STR", entity)
                    if self._filters: output += f" Try removing filters."
                    output += "\n"
                else:
                    no_results.append(entity)

        if len(no_results) > 0:
            output += f"#" * gx_definitions.SCREEN_SEPARATOR_LENGTH + "\n"
            output += f"No results found for {entity_string}.\n".replace("ENTITY_STR", ",".join(no_results))
            
        return output

    def _create_text_output(self, outfile):
        skip_ansi = outfile != None
        output = self._print_output(self._repositories, f"Repository https://github.com/ENTITY_STR", skip_ansi)
        output += self._print_output(self._contributors, f"account ENTITY_STR", skip_ansi)

        if len(self._anonymous) > 0 and len(next(iter(self._anonymous.values()))) > 1: # Did this so that I don't hardcode "#" as an index
            output += self._print_output(self._anonymous, "Anonymous Contributors (those with no GitHub account)", skip_ansi)
        else:
            output += f"#" * gx_definitions.SCREEN_SEPARATOR_LENGTH + "\n"
        return output

    def _create_json_output(self):
        data = { "repositories": [] }

        for repo_name, repo_info in self._repositories.items():
            repo_data = { "name": repo_name, "contributors": [], "anonymous_contributors": [], "results": {} }

            for rtype, rtype_values in repo_info.items():
                repo_data["results"][rtype] = rtype_values

        for contributor_name, contrib_details in self._contributors.items():
            contrib_data = { "name": contributor_name, "results": {} }

            for rtype, rtype_values in contrib_details.items():
                contrib_data["results"][rtype] = rtype_values

            repo_data["contributors"].append(contrib_data)

        for contributor_email, contrib_details in self._anonymous.items():
            contrib_data = { }

            for rtype, rtype_values in contrib_details.items():
                contrib_data[rtype] = rtype_values

            repo_data["anonymous_contributors"].append(contrib_data)


        data["repositories"].append(repo_data)

        json_output = json.dumps(data, indent=4)  # 'indent' for pretty printing
        return json_output

    def doOutput(self):
        if self._outformat == 'text':
            output = self._create_text_output(self._outfile)
        elif self._outformat == 'json':
            output = self._create_json_output()
        else:
            raise ValueError("Unsupported format!")

        if self._outfile:
            print(f"Writing (Appending) output to {self._outfile.name} in format {self._outformat}")
            self._outfile.write(output)
            self._outfile.write("\n")
        else:
            print(output)

        # Now reset persisting data!
        self.reset()

