# Code structure

A few pointers on how the Gitxray codebase is structured:

* `gitxray.py` - The main script, creates a gx_context, gx_output and calls X-Ray modules.

The include directory has files split in two naming conventions:

* Suffix: `gh_` - Files that handle GitHub API responses or talk to the GitHub API
* Suffix: `gx_` - Files with more Gitxray-specific logic

Some of the supporting files in the include directory:

* `gx_context.py` - Holds a context of data that is shared across different X-Ray modules and through out execution.
* `gx_output.py` - Takes care of any console printing, as well as text and json output.

For parsing SSH and PGP signatures, we wrote our own code and placed it in:

* `gx_ugly_openpgp_parser.py` - Parses Armors and BLOBs based on RFC4880
* `gx_ugly_ssh_parser.py` - Parses (if you can call that Parsing) SSH Armors and BLOBs

Finally, last but not least important, the X-Rays under the xrays directory:

* `contributors_xray.py` - Handles all Contributor-related data and decides what to log.
* `repository_xray.py` - Handles all Repository-related data and decides what to log.
* `workflows_xray.py` - Handles all Workflow-related analysis and decides what to log.
* `associations_xray.py` - Analyzes and reports all associations carried from prior X-Ray modules.
