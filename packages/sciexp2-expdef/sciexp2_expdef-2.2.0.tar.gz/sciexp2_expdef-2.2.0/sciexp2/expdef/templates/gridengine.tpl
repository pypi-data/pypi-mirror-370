#!/bin/bash
# Launch script for clusters using gridengine
#
# Job name
#$ -N {{JOB_NAME}}
# Specify a shell
#$ -S /bin/bash
# When to send me a mail
#$ -m {{QSUB_MAIL}}
#$ -M {{EMAIL}}
# Job standard output
#$ -o {{JOB_STDOUT}}
# Job standard error
#$ -e {{JOB_STDERR}}
# Job standard input
#$ -i {{JOB_STDIN}}
# User-defined options to 'qsub'
{{QSUB_OPTS}}


# Executes everything from the base directory (Launchgen.out, set as $BASE),
# which must be available from all execution nodes.
#
# Files for the execution and results should be copied to/from local filesystems
# in SYNCIN/SYNCOUT in order to minimize network usage (e.g., if the cluster has
# a networked filesystem and a local scratch zone).
#
# When starting, $DONE is removed and $FAIL is set to an empty file. If CMD
# executes successfully, $FAIL is removed.
#
# The script exits at the first failing command.
#
# The contents of CMD are run on a separate script, and signals SIGINT and
# SIGTERM are forwarded to it. Remember to forward these signals to the commands
# executed in the CMD script to avoid lingering child processes when such
# signals are raised (use bash commands "trap" or "exec" in CMD).
#
# If you kill a job and re-launch it, the old job might still generate some
# files even after the new job has started execution. In order to avoid file
# clobbering from the old job into the files of the new job, you can uniquify
# temporal directory and file names with gridengine's $JOB_ID variable or the
# mktemp command.


##################################################
# Environment preparation

# Early fail
set -e

# Absolute paths to important directories / files
# (created by gridengine before manually cd'ing into $BASE)
JOB_STDOUT=`readlink -f {{JOB_STDOUT}}`
JOB_STDERR=`readlink -f {{JOB_STDERR}}`

# Absolute path to base directory
BASE=${LAUNCHER_BASE}
if [ -z "$BASE" ]; then
    # Not executing with launcher; detect base directory
    # (LAUNCHER cannot be outside BASE)
    BASE=`readlink -f $0`
    BASE=${BASE%{{LAUNCHER}}}
fi
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
# (do not remove if already exists as JOB_STDOUT/JOB_STDERR)
[ "$DONE" = "$JOB_STDOUT" -o "$DONE" = "$JOB_STDERR" ] || rm -Rf $DONE && touch $DONE
[ "$FAIL" = "$JOB_STDOUT" -o "$FAIL" = "$JOB_STDERR" ] || rm -Rf $FAIL && touch $FAIL

_redirect()
{
    if [ "$1" = "$JOB_STDOUT" -o "$1" = "$JOB_STDERR" ]; then
        tee /dev/null
    else
        tee -a "$1"
    fi
}


# We will create separate scripts with the user's commands; needed to run it
# with 'stdbuf', which unbuffers stdout/stderr to see the commands's output in
# their original order.
CMDFILE=`mktemp`
function cmdcleanup() {
    rm -f $CMDFILE
}
trap cmdcleanup EXIT

# Export relevant variables
export BASE STDOUT STDERR DONE FAIL
export JOB_STDOUT JOB_STDERR

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


##################################################
# Synchronize files to be used
cat >$CMDFILE <<'__EOF_CMDFILE__'
stdbuf -o0 -e0 echo -n
# Early fail
set -e
# Early abort on first error (including inside a chain of pipes)
set -o pipefail;
{{SYNCIN}}
__EOF_CMDFILE__
# Copy stdout/stderr to STDOUT/STDERR (but do not completely redirect them)
run_with_signals stdbuf -o0 -e0 bash $CMDFILE 1> >(_redirect $STDOUT) 2> >(_redirect $STDERR >&2)


##################################################
# User-specified commands
cat >$CMDFILE <<'__EOF_CMDFILE__'
stdbuf -o0 -e0 echo -n
# Early fail
set -e
# Early abort on first error (including inside a chain of pipes)
set -o pipefail;
{{CMD}}
__EOF_CMDFILE__
# Copy stdout/stderr to STDOUT/STDERR (but do not completely redirect them)
run_with_signals stdbuf -o0 -e0 bash $CMDFILE 1> >(_redirect $STDOUT) 2> >(_redirect $STDERR >&2)


##################################################
# Copy results back
cat >$CMDFILE <<'__EOF_CMDFILE__'
stdbuf -o0 -e0 echo -n
# Early fail
set -e
# Early abort on first error (including inside a chain of pipes)
set -o pipefail;
{{SYNCOUT}}
__EOF_CMDFILE__
# Copy stdout/stderr to STDOUT/STDERR (but do not completely redirect them)
run_with_signals stdbuf -o0 -e0 bash $CMDFILE 1> >(_redirect $STDOUT) 2> >(_redirect $STDERR >&2)


##################################################
# Error checking

# Ensure the job will be detected as done, and not as failed
touch $DONE
rm -Rf $FAIL
