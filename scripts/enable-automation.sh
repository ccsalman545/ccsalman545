#!/usr/bin/env bash
#
# Install the profile automation workflows.
#
# GitHub does not allow apps or bots to create files under .github/workflows/,
# so the workflows ship as templates in docs/workflow-templates/ and this
# script copies them into place. Run it locally with your own credentials:
#
#   bash scripts/enable-automation.sh
#   git add .github/workflows
#   git commit -m "ci: enable profile automation"
#   git push
#
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
src="$repo_root/docs/workflow-templates"
dest="$repo_root/.github/workflows"

if [ ! -d "$src" ]; then
  echo "error: expected workflow templates in $src" >&2
  exit 1
fi

mkdir -p "$dest"

installed=0
for template in "$src"/*.yml; do
  name="$(basename "$template")"
  if [ -f "$dest/$name" ] && cmp -s "$template" "$dest/$name"; then
    echo "= $name (already installed, unchanged)"
    continue
  fi
  cp "$template" "$dest/$name"
  echo "+ $name"
  installed=$((installed + 1))
done

echo
if [ "$installed" -eq 0 ]; then
  echo "All workflows are already up to date."
else
  echo "Installed $installed workflow(s). Review, commit, and push:"
  echo
  echo "  git add .github/workflows && git commit -m 'ci: enable profile automation' && git push"
  echo
  echo "Then open Settings -> Actions -> General -> Workflow permissions"
  echo "and select 'Read and write permissions'."
fi
