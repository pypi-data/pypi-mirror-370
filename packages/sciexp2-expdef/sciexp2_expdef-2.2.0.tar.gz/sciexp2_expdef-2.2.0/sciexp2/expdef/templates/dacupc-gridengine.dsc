# -*- mode: python -*-

description = """
Base template for clusters in DAC/UPC:
  https://gw.ac.upc.edu/go/lcac/wiki/Clusters/Users.
Variable CSCRATCH points to the central shared scratch zone (/scratch/nas/2/`whoami`).
Variable LSCRATCH points to a job-specific directory in the node-local scratch zone (removed after execution).
"""

parent = "gridengine"

overrides = dict(
    SYNCIN="""
CSCRATCH=/scratch/nas/2/`whoami`
LSCRATCH=/scratch/1/`whoami`/${JOB_ID}
SYNC="rsync"
mkdir -p ${LSCRATCH}/

trap "rm -Rf ${LSCRATCH}/" ERR

{{SYNCIN}}
""",

    CMD="""
CSCRATCH=/scratch/nas/2/`whoami`
LSCRATCH=/scratch/1/`whoami`/${JOB_ID}
SYNC="rsync"

trap "rm -Rf ${LSCRATCH}/" ERR

{{CMD}}
""",

    SYNCOUT="""
CSCRATCH=/scratch/nas/2/`whoami`
LSCRATCH=/scratch/1/`whoami`/${JOB_ID}
SYNC="rsync"

trap "rm -Rf ${LSCRATCH}/" EXIT

{{SYNCOUT}}
""",
)
