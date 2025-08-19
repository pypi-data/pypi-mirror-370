#!/usr/bin/env bash

set -euo pipefail

# Use tr to trim whitespace: https://stackoverflow.com/a/3232433
MEGALINTER_IMAGE="$(grep 'image: oxsecurity/megalinter-python' "$PWD"/.gitlab-ci.yml | sed 's/image://g' | tr -d '[:space:]')"

docker run --rm \
	-v "$PWD":/tmp/lint \
	-w /tmp/lint \
	-e "VALIDATE_ALL_CODEBASE=true" \
	-e "APPLY_FIXES=all" \
	--init \
	"$MEGALINTER_IMAGE"
