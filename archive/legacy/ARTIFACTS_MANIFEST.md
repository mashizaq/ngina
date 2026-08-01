# Archive Manifest: Demo Artifacts

This manifest records demo/prototype artifacts identified for archival from the repository root. These files were flagged for archival as part of the transition from demo placeholders (Base44, Anthropic Claude, etc.) to the Core Machine Intelligence Stack.

Identified artifacts (present on the main branch):

- NGINA.zip — https://github.com/mashizaq/ngina/blob/main/NGINA.zip
- ngina 2.zip — https://github.com/mashizaq/ngina/blob/main/ngina%202.zip

Action taken in this branch:
- Added this manifest and a helper script (move_to_archive.sh) that performs the git moves locally.

Recommended next steps (automated by maintainer or CI):
1) Run the helper script locally on a checked-out copy of the chore/archive-demo-artifacts branch to move the artifacts into archive/legacy/ and commit the changes.
2) Run tests and CI, then open a PR from chore/archive-demo-artifacts → main.

If you want me to perform the actual git moves inside this branch (create the relocated files and remove originals), I can attempt to create new files at archive/legacy/ with the binary contents encoded (base64) — please confirm if you'd like the binary content preserved in the repo as base64 files, or if text pointers are sufficient.
