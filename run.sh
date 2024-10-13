#!/bin/sh
#
# runs program locally

set -e # Exit early if any commands fail
exec pipenv run python3 -m app.main "$@"
