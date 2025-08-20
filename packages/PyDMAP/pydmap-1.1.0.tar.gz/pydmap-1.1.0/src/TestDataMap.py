"""
    This script purpose is to test the Reading/Writing capabilities of the module
    PyDMAP.py. The script has several examples for reading and writing DataMap files,
    some of them are commented out. Please see
    :ref:`PyDMAP`
    for more details.


Author: Giuseppe Romeo
JHU/APL
12/03/2024
"""

import math
import struct
import sys
import zlib
from functools import partial
from tabnanny import verbose

import numpy as np

import argparse
import os


_rpath_ = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.insert(1, os.path.join(_rpath_, "lib"))

import PyDMAP as dmap

if __name__ == "__main__":
    """useful for testing DMAP.py module. This script
    returns no input, just reads to validate
    """

    parser = argparse.ArgumentParser(
        prog="Teste for DataMap Reader/Writer",
        description="""
       Script that reads/writes compressed, or not, binary dmap input files
       """,
    )

    parser.add_argument(
        "-F",
        "--infile",
        help="""Select input dmap file""",
        default=os.path.join(_rpath_, "tests","sample_data", "1985.smdl.60s.rev-0006.dmap"),
        # default=os.path.join(_rpath_,'sample_data','20170715.rbspa.efw.l3.dmap'),
        # default=os.path.join(_rpath_,'sample_data','test.dmap'),
        type=str,
    )

    parser.add_argument(
        "-O",
        "--output",
        help="""Specify output dmap file""",
        # default=os.path.join(_rpath_,'sample_data','1985.smdl.60s.rev-0006.dmap'),
        default=None,
        # default=os.path.join(_rpath_,'sample_data','test.dmap'),
        # default=os.path.join(_rpath_,'sample_data','test_py.dmap'),
        type=str,
    )

    parser.add_argument(
        "-V",
        "--verbose",
        help="""Verbosity level, default is 0""",
        required=False,
        default=0,
        type=int,
    )

    parser.add_argument(
        "-N",
        "--num_threads",
        help="""Number of Threads, default is 0""",
        required=False,
        default=0,
        type=int,
    )

    parser.add_argument(
        "-R",
        "--readonly",
        help="""Verbosity level, default is 0""",
        required=False,
        default=True,
        action="store_false",
    )

    parser.add_argument(
        "-W",
        "--writeall",
        help="""Specify whether to write all dictionary using function call or object call""",
        required=False,
        default=False,
        action="store_true",
    )

    args = parser.parse_args()

    filename = args.infile
    verbose = args.verbose
    readonly = args.readonly
    outfile = args.output
    writeall = args.writeall
    num_threads = args.num_threads

    if not os.path.exists(filename):
        print(f"ERROR - Input dmap file {filename} does NOT exist")
        sys.exit(1)

    if verbose > 0:
        print(f"Reading file {filename}")


    my_dmap, errormsg = dmap.read_datamap(filename, num_threads, verbose)

    # Reader = dmap.DataMapReader(filename, verbose)
    # # Reads the whole file at once
    # my_dmap = Reader.read_file(byblock=True)

    # Using a passed file Handle to read thew file
    # fp = open(filename, "rb")
    # Reader = dmap.DataMapReader(None, verbose)
    # Reader.set_filehandle4reading(fp)
    # # my_dmap = Reader.read_file_fromhandle()
    # my_dmap = []
    # data = 1
    # while data is not None:
    #     data = Reader.read_block_fromhandle()
    #     if isinstance(data, dict):
    #         my_dmap.append(data)

    # Reads file one block per iteration. This is slower, but perhaps more efficient
    # my_dmap = 1
    # while my_dmap is not None:
    #     my_dmap = Reader.read_block()

    # Reader.close()

    if not readonly:
        if outfile is None:
            fname = os.path.basename(filename)
            dname = os.path.dirname(filename)
            fname2 = fname.split(".dmap")[0]

            outfile = os.path.join(dname, fname2 + "_py.dmap")

        if os.path.exists(outfile):
            os.remove(outfile)
            if verbose:
                print(f"INFO - Deleted file {outfile} before writing a new version")

        if writeall or isinstance(my_dmap, list):
            writer = dmap.DataMapWriter(outfile, compress=True, verb=verbose)
            if isinstance(my_dmap, list):
                for data in my_dmap:
                    if isinstance(data, dict):
                        status = writer.write2file(data, False)
                        if status != 0:
                            break
            else:
                status = writer.write2file(my_dmap)

            writer.close_file()
        else:
            ermsg, status = dmap.write_datamap(outfile, my_dmap, verbose)

    pass

# -V 0 -F /Users/romeog1/MOUNTS/HORAE/project/ampere/data/next/mv3/l0/2024/20240101/ampere.20240101.sv181.mv3.rev000.l0.dmap -R
# -V 0 -F /Users/romeog1/MOUNTS/HORAE/project/ampere/data/next/mv3/l0/2024/20240101/ampere.20240101.sv181.mv3.rev000.l0.dmap -O /Users/romeog1/DataMap/datamap_python/sample_data/ampere.20240101.sv181.mv3.rev000.l0_py.dmap
# -V 0 -F /Users/romeog1/MOUNTS/HORAE/project/ampere/data/next/mv3/l0/2024/20240301/ampere.20240301.sv132.mv3.rev000.l0.dmap -O /Users/romeog1/DataMap/datamap_python/sample_data/ampere.20240301.sv132.mv3.rev000.l0_py.dmap
