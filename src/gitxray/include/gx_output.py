import json, random, os, html, re, datetime, sys
from collections import defaultdict
from . import gx_definitions

class Output:
    ANSI_COLORS = { "RED": "\033[31m", "GREEN": "\033[32m", "YELLOW": "\033[33m", "BLUE": "\033[34m", "MAGENTA": "\033[35m", "CYAN": "\033[36m", "BRIGHT_RED": "\033[91m", "BRIGHT_GREEN": "\033[92m", "BRIGHT_YELLOW": "\033[93m", "BRIGHT_BLUE": "\033[94m", "BRIGHT_MAGENTA": "\033[95m", "BRIGHT_CYAN": "\033[96m", "BRIGHT_WHITE": "\033[97m", "RESET": "\033[0m" }


    def __init__(self, gx_context, outfile=None, outformat='text'):

        self._debug = gx_context.debugEnabled()

        self._outformat = gx_context.getOutputFormat()

        self._filters = gx_context.getOutputFilters()
        self._rtype_color_map = {}

        self._cscope = gx_context.getContributorScope() 

        self._gxcontext = gx_context

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
   
    # Direct output, not really waiting for results to print this out.
    def warn(self, message, shushable=True):
        colored_message = f"{self.ANSI_COLORS['YELLOW']}{message}{self.ANSI_COLORS['RESET']}"
        return self.stdout(colored_message, shushable)

    def notify(self, message, shushable=True):
        colored_message = f"{self.ANSI_COLORS['BRIGHT_BLUE']}{message}{self.ANSI_COLORS['RESET']}"
        return self.stdout(colored_message, shushable)

    # Stdout goes through here
    def stdout(self, message, shushable=True, end='\n', flush=True):
        if shushable and self._gxcontext.shushEnabled(): return
        return print(message, end=end, flush=flush)

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
                output += f"#" * gx_definitions.SCREEN_SEPARATOR_LENGTH + "\n"
                output += f"No results to show for {entity_string}.".replace("ENTITY_STR", entity)
                if self._filters: output += f" Try removing filters."
                output += "\n"

        if len(no_results) > 0:
            output += f"#" * gx_definitions.SCREEN_SEPARATOR_LENGTH + "\n"
            output += f"No results found for {entity_string}.\n".replace("ENTITY_STR", ",".join(no_results))
            
        return output


    def html_data_sanitize_and_process(self, text):
        # html.escape already escapes { and } to prevent expression injection
        sanitized_text = html.escape(text, quote=True)

        # New pattern to match URLs both inside and outside of brackets
        url_pattern = re.compile(r'\[(https?://[^\s\]]+)\]|\b(https?://[^\s]+)')
    
        # Function to handle matching groups
        def replace_url(match):
            url = match.group(1) or match.group(2)
            return f'<a href="{url}" target="_blank">{url}</a>'

        # Substitute using the custom function
        clickable_text = url_pattern.sub(replace_url, sanitized_text)
        return clickable_text

    def _create_html_output(self):
        TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "html_report")

        # Load all template files
        templates = {
            name: open(os.path.join(TEMPLATE_DIR, f"template_{name}.html"), "r", encoding="utf-8").read()
            for name in ["main", "repository", "contributor", "non_contributor", "table"]
        }

        category_sections = ""
        contributor_sections = ""
        more_sections = ""
        repository_sections = ""
        repository_sidebar_links = ""
        contributor_sidebar_links = ""
        category_sidebar_links = ""
        more_sidebar_links = ""

        for entity, data in self._repositories.items():
            sanitized_entity = self.html_data_sanitize_and_process(entity)
            r_template = templates['repository'].replace("{{repository_id}}", str(sanitized_entity))

            r_tables = []
            r_sidebar_links = []
            for rtype in data.keys():
                if not self.debug_enabled() and ("debug" in rtype.lower()): continue
                data_rows = []
                for line in data[rtype]:
                    if self._filters != None and (all(f.lower() not in f'{rtype.lower()} {line.lower()}' for f in self._filters)): continue
                    data_rows.append(f"<tr><td>{rtype}</td><td>{self.html_data_sanitize_and_process(line)}</td></tr>")

                if len(data_rows) > 0:
                    r_sidebar_links.append('<li class="nav-item"><a class="nav-link" href="#repository_'+str(sanitized_entity)+'_'+str(rtype)+'">'+str(rtype)+' '+gx_definitions.HTML_REPORT_EMOJIS.get(rtype,"")+'</a></li>')
                    r_tables.append(templates['table'].replace("{{table_rows}}", "".join(data_rows)).replace("{{table_title}}", f"{rtype} {gx_definitions.HTML_REPORT_EMOJIS.get(rtype,'')}").replace("{{table_id}}", "repository_"+str(sanitized_entity)+"_"+rtype))

            if len(r_tables) > 0:
                repository_sidebar_links += '<ul class="nav flex-column mb-0"><li class="nav-item"><a class="nav-link collapsed" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="nav_'+str(sanitized_entity)+'" href="#nav_'+str(sanitized_entity)+'">'+str(sanitized_entity)+' &#128193;</a><div class="collapse" id="nav_'+str(sanitized_entity)+'"><ul class="nav flex-column ms-3">'
                repository_sidebar_links += "".join(r_sidebar_links)
                repository_sidebar_links += '</ul></div></li></ul>'
                r_template = r_template.replace("{{repository_tables}}", "".join(r_tables))
                repository_sections += r_template
            else:
                repository_sections += "<h5>No Results</h5>"


        # We now merge all rtypes across all contributor results
        tables_by_rtype = {}
        for entity, data in self._contributors.items():
            # Skip non-contributors
            if not self._gxcontext.isContributor(entity): continue
            
            sanitized_entity = self.html_data_sanitize_and_process(entity)
            
            # Loop through all rtypes for the current contributor
            for rtype in data.keys():
                if not self.debug_enabled() and ("debug" in rtype.lower()): continue
                
                if rtype not in tables_by_rtype:
                    tables_by_rtype[rtype] = ""

                for line in data[rtype]:
                    tables_by_rtype[rtype] += f"<tr><td><a href='#contributor-section-{sanitized_entity}'>{sanitized_entity}</a></td><td>{self.html_data_sanitize_and_process(line)}</td></tr>"

        for rtype, table_rows in tables_by_rtype.items():
            if self._filters != None and (all(f.lower() not in f'{rtype.lower()} {table_rows.lower()}' for f in self._filters)): continue
            category_sidebar_links += '<ul class="nav flex-column mb-0"><li class="nav-item"><a href="#nav_category_'+str(rtype)+'">'+str(rtype)+' '+gx_definitions.HTML_REPORT_EMOJIS.get(rtype,"")+'</a></li></ul>'
            table_html = templates['table'].replace("{{table_rows}}", table_rows) \
                                       .replace("{{table_title}}", f"{rtype} {gx_definitions.HTML_REPORT_EMOJIS.get(rtype, '')}") \
                                       .replace("{{table_id}}", f"nav_category_{rtype}")
            category_sections += table_html


        for entity, data in self._contributors.items():
            # In the HTML report we skip any non-contributor results when showing contributor results
            if not self._gxcontext.isContributor(entity): 
                continue

            sanitized_entity = self.html_data_sanitize_and_process(entity)
            c_template = templates['contributor'].replace("{{contributor_id}}", str(sanitized_entity))
            c_template = c_template.replace("{{contributor_name}}", str(sanitized_entity) + "&#128193;")

            c_tables = []
            c_sidebar_links = []
            for rtype in data.keys():
                if not self.debug_enabled() and ("debug" in rtype.lower()): continue
                data_rows = []
                for line in data[rtype]:
                    if self._filters != None and (all(f.lower() not in f'{rtype.lower()} {line.lower()}' for f in self._filters)): continue
                    data_rows.append(f"<tr><td>{sanitized_entity}</td><td>{self.html_data_sanitize_and_process(line)}</td></tr>")

                if len(data_rows) > 0:
                    c_sidebar_links.append('<li class="nav-item"><a class="nav-link" href="#contributor_'+str(sanitized_entity)+'_'+str(rtype)+'">'+str(rtype)+' '+gx_definitions.HTML_REPORT_EMOJIS.get(rtype,"")+'</a></li>')
                    c_tables.append(templates['table'].replace("{{table_rows}}", "".join(data_rows)).replace("{{table_title}}", f"{rtype} {gx_definitions.HTML_REPORT_EMOJIS.get(rtype,'')}").replace("{{table_id}}", "contributor_"+str(sanitized_entity)+"_"+str(rtype)))

            if len(c_tables) > 0:
                contributor_sidebar_links += '<ul class="nav flex-column mb-0"><li class="nav-item"><a class="nav-link collapsed" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="nav_'+str(sanitized_entity)+'" href="#nav_'+str(sanitized_entity)+'">'+str(sanitized_entity)+' &#128193;</a><div class="collapse" id="nav_'+str(sanitized_entity)+'"><ul class="nav flex-column ms-3">'
                contributor_sidebar_links += "".join(c_sidebar_links)
                contributor_sidebar_links += '</ul></div></li></ul>'
                c_template = c_template.replace("{{contributor_tables}}", "".join(c_tables))
                contributor_sections += c_template

        if len(self._anonymous) > 0 and len(next(iter(self._anonymous.values()))) > 1:
            for entity, data in self._anonymous.items():
                sanitized_entity = "Anonymous"
                a_template = templates['non_contributor'].replace("{{non_contributor_id}}", str(sanitized_entity))
                a_template = a_template.replace("{{non_contributor_name}}", f'{sanitized_entity} &#128123;')
                more_sidebar_links += '<ul class="nav flex-column mb-0"><li class="nav-item"><a class="nav-link collapsed" data-bs-toggle="collapse" role="button" aria-expanded="false" aria-controls="nav_'+str(sanitized_entity)+'" href="#nav_'+str(sanitized_entity)+'">'+str(sanitized_entity)+' &#128123;</a><div class="collapse" id="nav_'+str(sanitized_entity)+'"><ul class="nav flex-column ms-3">'
                a_tables = ""
                for rtype in data.keys():
                    data_rows = []
                    for line in data[rtype]:
                        if self._filters != None and (all(f.lower() not in f'{rtype.lower()} {line.lower()}' for f in self._filters)): continue
                        data_rows.append(f"<tr><td>{rtype}</td><td>{self.html_data_sanitize_and_process(line)}</td></tr>")

                    if len(data_rows) > 0:
                        more_sidebar_links += '<li class="nav-item"><a class="nav-link" href="#contributor_'+str(sanitized_entity)+'_'+str(rtype)+'">'+str(rtype)+'</a></li>'

                    a_tables += templates['table'].replace("{{table_rows}}", "".join(data_rows)).replace("{{table_title}}", str(rtype)).replace("{{table_id}}", "contributor_"+str(sanitized_entity)+"_"+str(rtype))

                more_sidebar_links += '</ul></div></li></ul>'
                a_template = a_template.replace("{{non_contributor_tables}}", a_tables)
                more_sections += a_template
        else:
            more_sidebar_links = '<ul class="nav flex-column mb-0"><li class="nav-item"><ul class="nav flex-column ms-3"><li class="nav-item">No results</li></ul></li></ul>'
            more_sections = '<h5>No anonymous Contributors found</h5>'


        # We now merge all rtypes across all non-contributor results
        tables_by_rtype = {}
        for entity, data in self._contributors.items():
            # Skip contributors this time
            if self._gxcontext.isContributor(entity): continue

            sanitized_entity = self.html_data_sanitize_and_process(entity)
            for rtype in data.keys():
                if not self.debug_enabled() and ("debug" in rtype.lower()): continue

                if rtype not in tables_by_rtype:
                    tables_by_rtype[rtype] = ""

                for line in data[rtype]:
                    tables_by_rtype[rtype] += f"<tr><td>{sanitized_entity}</td><td>{self.html_data_sanitize_and_process(line)}</td></tr>"

        for rtype, table_rows in tables_by_rtype.items():
            if self._filters != None and (all(f.lower() not in f'{rtype.lower()} {table_rows.lower()}' for f in self._filters)): continue
            more_sidebar_links += '<ul class="nav flex-column mb-0"><li class="nav-item"><a href="#nav_more_'+str(rtype)+'">'+str(rtype)+' '+gx_definitions.HTML_REPORT_EMOJIS.get(rtype,"")+'</a></li></ul>'
            table_html = templates['table'].replace("{{table_rows}}", table_rows) \
                                       .replace("{{table_title}}", f"{rtype} {gx_definitions.HTML_REPORT_EMOJIS.get(rtype, '')}") \
                                       .replace("{{table_id}}", f"nav_more_{rtype}")
            more_sections += table_html



        output = templates['main'].replace("{{repository_sections}}", repository_sections)
        # repository sidebar links
        output = output.replace("{{repository_sidebar_links}}", repository_sidebar_links)
        # category sidebar links
        output = output.replace("{{category_sidebar_links}}", category_sidebar_links)
        # contributors sidebar links
        output = output.replace("{{contributor_sidebar_links}}", contributor_sidebar_links)
        # more sidebar links
        output = output.replace("{{more_sidebar_links}}", more_sidebar_links)

        output = output.replace("{{category_sections}}", category_sections)
        output = output.replace("{{contributor_sections}}", contributor_sections)
        output = output.replace("{{report_date}}", datetime.datetime.now().strftime("%B %d, %Y"))
        output = output.replace("{{more_sections}}", more_sections)


        if self._filters != None:
            output = output.replace("{{filters_html_text}}",f" with <strong>FILTERS ENABLED</strong>: <i>{self._filters}</i>. Disable Filters to get more results")
        else:
            output = output.replace("{{filters_html_text}}","")

        return output

    def _create_text_output(self, skip_ansi):
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
        if self._outformat == 'html':
            output = self._create_html_output()
        elif self._outformat == 'text':
            output = self._create_text_output(self._gxcontext.getOutputFile())
        elif self._outformat == 'json':
            output = self._create_json_output()
        else:
            raise ValueError("Unsupported format!")

        if self._gxcontext.getOutputFile(): 
            self._outfile = open(self._gxcontext.getOutputFile(), 'w+')
            self.warn(f"Writing output to [{self._outfile.name}] in format [{self._outformat}]", shushable=False)
            self._outfile.write(output)
            self._outfile.write("\n")
        else:
            print(output)

        # Now reset persisting data!
        self.reset()

    def testOutputFile(self):
        outfile = self._gxcontext.getOutputFile()
        if outfile:
            if os.path.isdir(outfile):
                print("[!] Can't specify a directory as the output file, exiting.")
                sys.exit()
            if os.path.isfile(outfile):
                target = outfile
            else:
                target = os.path.dirname(outfile)
                if target == '':
                    target = '.'

            if not os.access(target, os.W_OK):
                print("[!] Cannot write to output file, exiting")
                sys.exit()
