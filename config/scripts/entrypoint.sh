#!/usr/bin/env bash
set -e

# Run the Python repo-grabbing script
/projects/scripts/grab_repos.py

# After it's done, drop into an interactive shell
exec bash

