#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Define function for bringing down services
cleanup() {
  eval "$(docker-services-cli down --env)"
}

# Check for arguments
# Note: "-k" would clash with "pytest"
keep_services=0
pytest_args=()
for arg in $@; do
	# from the CLI args, filter out some known values and forward the rest to "pytest"
	# note: we don't use "getopts" here b/c of some limitations (e.g. long options),
	#       which means that we can't combine short options (e.g. "./run-tests -Kk pattern")
	case ${arg} in
		-K|--keep-services)
			keep_services=1
			;;
        -V)
            echo "Setting verbose option in the shell. To use the -V flag for pytest, use --version instead."
            set -o verbose
            ;;
		*)
			pytest_args+=( "${arg}" )
			;;
	esac
done

if [[ ${keep_services} -eq 0 ]]; then
	trap cleanup EXIT
fi

export LC_TIME=en_US.UTF-8
eval "$(docker-services-cli up --db "${DB:-postgresql}" --search "${SEARCH:-opensearch}" --mq "${MQ:-rabbitmq}" --cache "${CACHE:-redis}" --env)"

# Note: expansion of pytest_args looks like below to not cause an unbound
# variable error when 1) "nounset" and 2) the array is empty.
pytest ${pytest_args[@]+"${pytest_args[@]}"}
coverage xml
tests_exit_code=$?
exit "$tests_exit_code"
