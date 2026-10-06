#!/bin/bash

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

printf '\n### %s - Subagent started\n' "$TIMESTAMP" >> docs/changelog.md