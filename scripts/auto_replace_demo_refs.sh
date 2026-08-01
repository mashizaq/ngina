#!/usr/bin/env bash
# scripts/auto_replace_demo_refs.sh
# Conservative automated replacer for demo artifacts.
# Run this locally from the repository root on the chore/archive-demo-artifacts branch.
# It will: preview matches, create a backup branch (auto-replace-preview), perform conservative replacements
# (Anthropic->"Generative AI", Claude->"Generative AI", Base44/Base-44 removal), skip binaries and archive/legacy.

set -euo pipefail

# Requirements: ripgrep (rg), perl, git
for cmd in rg perl git; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

echo "Creating a preview branch 'auto-replace-preview' from current branch..."
git checkout -b auto-replace-preview

# Prepare file list (skip archive/ and .git and known binary extensions)
echo "Searching for candidate files (skipping archive/, .git, and common binary extensions)..."
files=$(rg -l --hidden --no-ignore -S --glob '!archive/**' --glob '!.git/**' --glob '!**/*.zip' --glob '!**/*.pyc' --glob '!**/*.jar' --glob '!**/*.exe' --glob '!**/*.png' --glob '!**/*.jpg' --glob '!**/*.jpeg' --glob '!**/*.gif' --glob '!**/*.tar' --glob '!**/*.gz' "Anthropic|anthropic|Claude|claude|Base44|Base-44" || true)

if [ -z "$files" ]; then
  echo "No candidate files found for conservative replacements. Exiting preview branch (no changes)."
  git checkout -
  git branch -D auto-replace-preview || true
  exit 0
fi

echo "Found candidate files:" 
printf "%s\n" "$files"

# Show preview diffs for user to review
echo
echo "=== Preview diffs (no files modified yet) ==="
for f in $files; do
  echo
  echo "--- $f ---"
  git --no-pager diff --no-index --color=auto "$f" <(perl -pe 's/\bAnthropic\b/Generative AI/g; s/\bClaude\b/Generative AI/g; s/\bBase44\b//g; s/\bBase-44\b//g' "$f") || true
done

echo
read -p "Apply these conservative replacements to the found files and commit them on this preview branch? [y/N] " yn
yn=${yn:-N}
if [[ ! "$yn" =~ ^[Yy]$ ]]; then
  echo "No changes applied. You are on branch auto-replace-preview with no modifications. Review diffs and re-run to apply." 
  exit 0
fi

# Apply replacements
echo "Applying replacements..."
for f in $files; do
  perl -pi -e 's/\bAnthropic\b/Generative AI/g; s/\bClaude\b/Generative AI/g; s/\bBase44\b//g; s/\bBase-44\b//g' "$f"
done

# Stage and commit
git add $files
git commit -m "chore: conservative replacements — Anthropic/Claude -> Generative AI; remove Base44 placeholders"

echo "Replacements applied on branch auto-replace-preview. Run tests locally, review changes, then merge into chore/archive-demo-artifacts if satisfied."

echo "To move changes into the feature branch (chore/archive-demo-artifacts):"
echo "  git checkout chore/archive-demo-artifacts"
echo "  git merge --no-ff auto-replace-preview -m \"chore: merge conservative replacements into chore/archive-demo-artifacts\""
echo "  git push origin chore/archive-demo-artifacts"

echo "If you want me to prepare the PR update after you push, paste the PR URL here."
