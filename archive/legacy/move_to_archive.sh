#!/bin/bash
# Helper: move_to_archive.sh
# Run this locally on a checked-out copy of the chore/archive-demo-artifacts branch.

set -euo pipefail

echo "Creating archive/legacy directory if it doesn't exist..."
mkdir -p archive/legacy

echo "Moving demo archives into archive/legacy/..."
git mv -f "NGINA.zip" "archive/legacy/NGINA.zip" || true
git mv -f "ngina 2.zip" "archive/legacy/ngina-2.zip" || true

echo "Demo archives moved. Please review 'git status' locally, run tests, then 'git commit' and 'git push' to update the remote branch."
