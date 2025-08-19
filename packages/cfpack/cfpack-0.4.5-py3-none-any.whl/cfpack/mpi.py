#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath, 2025

try:
    from mpi4py import MPI
    have_mpi = True
except ImportError:
    MPI = None
    have_mpi = False

# set basic MPI data
if have_mpi:
    comm = MPI.COMM_WORLD  # MPI communicator
    nPE  = comm.Get_size() # get number of MPI ranks
    myPE = comm.Get_rank() # get this MPI rank's number
else:
    comm = None
    nPE  = 1
    myPE = 0

# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":

    from cfpack.defaults import *
    import cfpack as cfp
    import argparse
    import numpy as np

    # parse script arguments
    parser = argparse.ArgumentParser(description='MPI (mpi4py) demo.')
    args = parser.parse_args()

    # start a new timer
    timer = cfp.timer('mpi4py test')

    # print MPI info
    print("Total number of MPI ranks = "+str(nPE))
    comm.Barrier()

    # define n and local, global arrays
    n = int(1e7)
    sum_local = np.array(0.0)
    sum_global = np.array(0.0)

    # === domain decomposition ===
    mod = n % nPE
    div = n // nPE
    if mod != 0: # Why do this? ...
        div += 1
    print("domain decomposition mod, div = "+str(mod)+", "+str(div))
    my_start =  myPE    * div     # loop start index
    my_end   = (myPE+1) * div - 1 # loop end index
    # last PE gets the rest
    if (myPE == nPE-1): my_end = n
    print("my_start = "+str(my_start)+", my_end = "+str(my_end), mpi=True)

    # loop over local chunk of loop
    for i in range(my_start, my_end+1):
        sum_local += i

    print("sum_local = "+str(sum_local), mpi=True)
    comm.Barrier()

    # MPI collective communication (all reduce)
    comm.Allreduce(sum_local, sum_global, op=MPI.SUM)
    print("sum_global = "+str(sum_global))

    # let the timer report
    timer.report()
