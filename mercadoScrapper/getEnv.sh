#!/bin/bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]] then
   echo "Do not run this script directly; source it to properly activate the virtualenv."
   exit 1
fi

[ ! -d .venv ] && python3 -m venv .venv

# use this venv from now on
source .venv/bin/activate
