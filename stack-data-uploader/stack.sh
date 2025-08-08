#!/bin/bash

COMMAND=$1
shift

SCRIPTS_DIR="../common-scripts"
export SCRIPTS_DIR

"${SCRIPTS_DIR}/${COMMAND}.sh" "$@"