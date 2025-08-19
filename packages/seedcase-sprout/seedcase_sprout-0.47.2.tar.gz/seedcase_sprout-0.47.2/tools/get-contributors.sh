#!/usr/bin/env bash

# Get a list of contributors to the Seedcase Sprout repository
# and save it to contributors.txt.tmp file. It also:
#
# - Formats users into Markdown links to their GitHub profiles.
# - Removes any usernames with the word "bot" in them.
# - Removes the trailing comma from the list.
gh api \
  /repos/seedcase-project/seedcase-sprout/contributors \
  --template '{{range .}} [\@{{.login}}]({{.html_url}}){{"\n"}}{{end}}' | \
  grep -v "\[bot\]" | \
  tr '\n' ', ' | \
  sed -e 's/,$//' > contributors.txt.tmp
