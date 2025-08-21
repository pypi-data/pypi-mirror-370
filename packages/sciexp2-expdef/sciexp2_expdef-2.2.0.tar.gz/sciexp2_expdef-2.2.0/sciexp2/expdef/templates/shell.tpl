#!/bin/bash
# Launch script for local shell jobs


# Executes everything from the base directory (Launchgen.out, set as $BASE).
#
# When starting, $STDOUT, $STDERR, $DONE and $FAIL are removed, and the last two
# are re-created as empty files. If CMD executes successfully, $FAIL is removed.
#
# The script exits at the first failing command.
#
# The contents of CMD are run on a separate script, and signals SIGINT and
# SIGTERM are forwarded to it. Remember to forward these signals to the commands
# executed in the CMD script to avoid lingering child processes when such
# signals are raised (use bash commands "trap" or "exec" in CMD).


##################################################
# Environment preparation

# Early fail
set -e

# Absolute path to base directory
# (LAUNCHER cannot be outside BASE)
BASE=`readlink -f $0`
BASE=${BASE%{{LAUNCHER}}}
# Start at base directory
cd $BASE

# Create output directories
mkdir -p `dirname {{STDOUT}}`
mkdir -p `dirname {{STDERR}}`
mkdir -p `dirname {{DONE}}`
mkdir -p `dirname {{FAIL}}`

# Absolute paths to important directories / files
STDOUT=`readlink -f {{STDOUT}}`
STDERR=`readlink -f {{STDERR}}`
FAIL=`readlink -f {{FAIL}}`
DONE=`readlink -f {{DONE}}`

# Start with a clean slate
rm -Rf $STDOUT
rm -Rf $STDERR
rm -Rf $FAIL && touch $FAIL
rm -Rf $DONE && touch $DONE


##################################################
# Run user-specified commands

# Create a separate script with the user's commands; needed to run it with
# 'stdbuf', which unbuffers stdout/stderr to see CMD's output in its original
# order.
CMDFILE=`mktemp`
function cmdcleanup() {
    rm -f $CMDFILE
}
trap cmdcleanup EXIT

# Export relevant variables
export BASE STDOUT STDERR DONE FAIL

# Forward relevant signals to child
run_with_signals() {
    _int() {
        kill -INT "$child" 2>/dev/null
    }
    _term() {
        kill -TERM "$child" 2>/dev/null
    }
    trap _int SIGINT
    trap _term SIGTERM
    $@ &
    child=$!
    err=130
    set +e
    while [ $err -eq 130 -o $err -eq 143 ]; do
        wait $child
        err=$?
    done
    trap - SIGINT
    trap - SIGTERM
    set -e
    if [ $err -ne 0 ]; then
        exit $err
    fi
}

cat >$CMDFILE <<'__EOF_CMDFILE__'
stdbuf -o0 -e0 echo -n
# Early fail
set -e
# Early abort on first error (including inside a chain of pipes)
set -o pipefail;
{{CMD}}
__EOF_CMDFILE__
# Copy stdout/stderr to STDOUT/STDERR (but do not completely redirect them)
run_with_signals stdbuf -o0 -e0 bash $CMDFILE 1> >(tee -a $STDOUT) 2> >(tee -a $STDERR >&2)


##################################################
# Error checking

# Ensure the job will be detected as done, and not as failed
touch $DONE
rm -Rf $FAIL
