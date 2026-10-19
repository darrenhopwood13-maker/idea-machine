#!/bin/bash
# Daily refresh: pull live Google Trends into index.html, commit + push to GitHub Pages
set -e
cd /opt/data/deploy/idea-machine

# Refresh trends
/opt/data/outreach/instructlead/.venv/bin/python3 /opt/data/deploy/idea-machine/refresh_trends.py

# Commit + push if anything changed
if ! git diff --quiet; then
  git add -A
  git -c user.name="darrenhopwood13-maker" -c user.email="darrenhopwood13@gmail.com" \
      commit -m "Daily trends refresh $(date +%Y-%m-%d)"
  git push origin main
  echo "Pushed trend refresh $(date +%H:%M)"
else
  echo "No trend changes today"
fi