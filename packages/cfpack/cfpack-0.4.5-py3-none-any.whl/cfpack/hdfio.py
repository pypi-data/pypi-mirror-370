#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath, 2019-2025

import os, sys
from shutil import move
import numpy as np
import h5py
from cfpack import run_shell_command, print, stop
import argparse
import humanize

# ============= get_shape =============
def get_shape(filename, datasetname):
    # open HDF5 file
    f = h5py.File(filename, "r")
    # get shape
    dset = f[datasetname]
    shape = dset.shape
    f.close()
    return shape
# ============= end: get_shape =============

# ============= read =============
# ind should be of type slice or np.s_ to index into the dataset, in order to select hyperslabs;
# return_attributes=True will return the dataset's attributes as a dictionary
def read(filename, datasetname, ind=(), return_attributes=False):
    # open HDF5 file
    f = h5py.File(filename, "r")
    # grab the dataset as a numpy array (with requested index ind, if provided, else all)
    dset = f[datasetname]
    if return_attributes: # return attributes of this dataset as a dict
        ret = {}
        attr_keys = dset.attrs.keys()
        for key in attr_keys:
            val = dset.attrs.get(key)
            ret[key] = val # add key and value
    else: # return dataset content
        ret = np.array(dset[ind])
    f.close()
    return ret
# ============= end: read =============

# ============= write =============
def write(data, filename, datasetname, overwrite_file=False, overwrite_dataset=False):
    # first test if file exists
    openflag = "w"
    if os.path.isfile(filename):
        if not overwrite_file: openflag = "a" # append/modify
    # open HDF5 file
    f = h5py.File(filename, openflag)
    # check if dataset name exists in hdf5 file
    if datasetname in f.keys():
        if overwrite_dataset:
            del f[datasetname] # if we overwrite, then delete first
        else:
            print("dataset '"+datasetname+"' already in file '"+filename+"'. Use option 'overwrite_dataset=True' to overwrite.", error=True)
    # create and write data
    dset = f.create_dataset(datasetname, data=data)
    f.close()
    print("'"+datasetname+"' written in file '"+filename+"'", highlight=3)
    return data
# ============= end: write =============

# ============= delete =============
def delete(filename, datasetname, quiet=False):
    # open HDF5 file
    f = h5py.File(filename, "a")
    # check if dataset name exists in hdf5 file
    if datasetname in f.keys():
        if not quiet: print("deleting dataset '"+datasetname+"' in file '"+filename+"'.", warn=True)
        del f[datasetname]
    else:
        if not quiet: print("dataset '"+datasetname+"' does not exist in file '"+filename+"'.", warn=True)
    f.close()
# ============= end: delete =============

# ============= get_dataset_names =============
def get_dataset_names(filename):
    # open HDF5 file
    f = h5py.File(filename, "r")
    dsets = list(f.keys())
    f.close()
    return dsets
# ============= end: get_dataset_names =============


# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Manipulate HDF files.')
    subparsers = parser.add_subparsers(title='sub-commands', dest='subcommand', help='see additional help with -h')

    # subcommand 'compare'
    parser_compare = subparsers.add_parser('compare', help="Compare dataset(s) in two HDF5 files.")
    parser_compare.add_argument("file1", help="HDF5 input file 1")
    parser_compare.add_argument("file2", help="HDF5 input file 2")
    parser_compare.add_argument("-d", "--d", dest='datasetnames', nargs='+', help="HDF5 dataset name(s) to compare", default=None)
    parser_compare.add_argument("-relative_diff", "--relative_diff", dest='relative_diff', type=float, help="tolerance for relative difference (default: %(default)s)")
    parser_compare.add_argument("-print_diff", "--print_diff", action='store_true', help="Switch to print differences", default=False)
    parser_compare.add_argument("-options", "--options", dest='options', help="Additional options to pass on to h5diff", default="")

    # subcommand 'delete'
    parser_compare = subparsers.add_parser('delete', help="Delete dataset(s) in HDF5 file(s).")
    parser_compare.add_argument("-i", "--i", dest='files', required=True, nargs='+', help="HDF5 input file(s)")
    parser_compare.add_argument("-d", "--d", dest='datasetnames', required=True, nargs='+', help="HDF5 dataset name(s) to delete")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_usage()
        exit()

    # subcommand 'compare': compare dataset(s) in two HDF5 files
    if args.subcommand == 'compare':
        dset_strings = []
        if args.datasetnames is None:
            # compare all datasets
            dset_strings.append("")
        else:
            # compare only list of specified datasets
            for dsetn in args.datasetnames:
                dset_strings.append(" /"+dsetn)
        # whether to print the differences to stdout
        print_diff_str = ""
        if args.print_diff: print_diff_str = " -r"
        # call h5diff to compare
        rel_diff_str = ""
        if args.relative_diff:
            print("h5diff relative difference (-p option) does not seem to work reliably -- use with caution!", warn=True)
            rel_diff_str = " -p "+str(args.relative_diff)
        for dset_str in dset_strings:
            cmd = "h5diff "+args.options+print_diff_str+rel_diff_str+" "+args.file1+" "+args.file2+dset_str
            run_shell_command(cmd)

    # subcommand 'delete': delete dataset(s) in HDF5 file(s)
    if args.subcommand == 'delete':
        # loop over input files
        for fname in args.files:
            # first test if file exists
            if not os.path.isfile(fname):
                print("File '"+fname+"' does not exist - skipping it...", warn=True)
                continue
            # calling delete function
            for dsetn in args.datasetnames:
                delete(fname, dsetn)
            # call h5repack to actually reduce the filesize (create a temporary hdf5 file that is repacked)
            h5repack_completed = False
            fname_tmp = fname+"_repack"
            try:
                cmd = "h5repack "+fname+" "+fname_tmp+" --enable-error-stack --verbose"
                run_shell_command(cmd)
                h5repack_completed = True
            except:
                print("Problem in call to h5repack - skipping...", warn=True)
                continue
            if h5repack_completed:
                # print out file size comparison
                fsize_original = humanize.naturalsize(os.path.getsize(fname))
                fsize_repacked = humanize.naturalsize(os.path.getsize(fname_tmp))
                print(f"File size before and after repack: "+fsize_original+" -> "+fsize_repacked, color="green")
                # if all went well up to here, we replace the original with the tmp file
                print("Now replacing '"+fname_tmp+"' with original '"+fname+"'...", color="magenta")
                move(fname_tmp, fname)
                print('...done.', color="magenta")


# ======================= MAIN End ===========================
