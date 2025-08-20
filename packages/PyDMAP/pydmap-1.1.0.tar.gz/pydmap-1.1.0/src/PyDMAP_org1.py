"""
This module reads/writes DataMap files, independently if they compressed or not

Author: Sandy Antunes/Giuseppe Romeo
JHU/APL
12/03/2024
"""

import math
import struct
import sys
import zlib

import numpy as np

import os
import re

import multiprocessing
import io


# taken from dmap/include/dmap.h
dtypes = {
    "char": 1,
    "int16": 2,
    "int32": 3,
    "int64": 4,
    "float": 4,
    "double": 8,
    "string": 9,
    "long": 10,
    "uchar": 16,
    "uint16": 17,
    "uint32": 18,
    "uint64": 19,
}

# derived from sample code
dsizes = {1: 1, 2: 2, 3: 4, 4: 4, 8: 8, 9: -1, 10: 8, 16: 1, 17: 2, 18: 4, 19: 8}
dformats = {
    1: "c",
    2: "h",
    3: "i",
    4: "f",
    8: "d",
    9: "s",
    10: "q",
    16: "B",
    17: "H",
    18: "I",
    19: "Q",
}

ndtypes = {
    "s1": "char",
    "i2": "int16",
    "i4": "int32",
    "i8": "int64",
    "f4": "float",
    "f8": "double",
    "string": "string",
    "i8": "long",
    "u1": "uchar",
    "u2": "uint16",
    "u4": "uint32",
    "u8": "uint64",
}


class DataMapReader:
    """
    This class is used to read and parse a DataMap binary input file.
    It can read a file using a file name or a file handle.

    """

    def __init__(self, infile=None, verb=0, **kwargs):
        self.infile = infile
        self.verbose = verb
        self.filehand = None
        self.errormsg = ""

        self.endian = None
        self.endiansymbol = None
        self.compressed = None
        self.blocknumber = 0
        self.totptr = 0

        if infile is not None:
            self.set_filehand()

    def set_filehand(self):
        """
        This function does the following actions:
            1. Check is the object file handler is set, and if so, close it
            2. Check if the input file does exist, and if not print an error and return
            3. Create a new file handler

        :param infile:
        :return:
        """
        if self.filehand is not None:
            self.filehand.close()

        if self.infile is None:
            print(f"ERROR - Input file for reading is not specified")
            return

        if not os.path.exists(self.infile):
            print(f"ERROR - Specified input DataMap file {self.infile} does not exists")
            return

        try:
            if self.verbose:
                print(f"INFO - Opening file {self.infile} for reading")
            self.filehand = open(self.infile, "rb")
        except:
            print(f"ERROR - Unable to open file {self.infile} for reading")

    def set_infile(self, infile):
        """
        Function setter for input file, which also used to set the
        object file handler.

        :param outfile:         <output file>
        :return:
        """
        self.infile = infile
        self.set_filehand()

    def set_filehandle4reading(self, obj):
        """
        This function used the passed
        :param filehanlde:
        :return:
        """
        if isinstance(obj, io.IOBase):
            self.infile = "Unspecified"
            if self.filehand is not None:
                self.close()

            self.filehand = obj

    def close(self):
        """
        This function closes the file handler if it is still open

        :return:
        """
        if self.filehand is not None:
            self.filehand.close()
            self.filehand = None
            self.blocknumber = 0
            self.totptr = 0

    def read_file(self):
        """
        This function reads in the entire binary content
        :return:
        """

        if self.filehand is None:
            self.set_filehand()

        file_size = os.path.getsize(self.infile)
        totptr = 0

        my_dmap = {}

        blocknumber = 0
        while totptr <= file_size:

            datacode = self.filehand.read(4)
            totptr += 4
            if datacode == b"\x00\x01\x00\x01":
                self.endian, self.endiansymbol, self.compressed = "big", ">", False
            elif datacode == b"\x10\x01\x00\x01":
                self.endian, self.endiansymbol, self.compressed = "big", ">", True
            elif datacode == b"\x01\x00\x01\x00":
                self.endian, self.endiansymbol, self.compressed = "little", "<", False
            elif datacode == b"\x01\x00\x01\x10":
                self.endian, self.endiansymbol, self.compressed = "little", "<", True
            else:
                print(
                    f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting"
                )
                self.errormsg += f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting\n"
                self.filehand.close()
                self.filehand = None
                return None

            if self.verbose > 1:
                print(
                    f"DEBUG - Block: {blocknumber} raw datacode: {datacode}, Endianess: {self.endian}, compressed: {self.compressed}"
                )

            sizeinfo = int.from_bytes(self.filehand.read(4), self.endian) - 8
            totptr += 4

            if self.verbose > 1:
                print(f"DEBUG - sizeinfo: {sizeinfo}")

            # second 4 bytes is size in bytes of total storage of data block
            # l = long, default 4 bytes, but python says it needs 8? Trying i = int
            block = None
            if self.compressed:
                # next 4 bytes are, if compressed, original data size
                osizeinfo = int.from_bytes(self.filehand.read(4), self.endian)
                totptr += 4

                comp_factor = 1.0 * osizeinfo / sizeinfo
                if self.verbose > 1:
                    print(
                        f"DEBUG - Uncompressed size will be {osizeinfo} (Compression factor: {comp_factor}"
                    )

                block = zlib.decompress(self.filehand.read(sizeinfo - 4))
                totptr += sizeinfo - 4
            else:
                block = self.filehand.read(sizeinfo)
                totptr += sizeinfo

            blocknumber += 1
            if self.verbose:
                print(f"INFO - Processing block {blocknumber}")

            self._decode(block, my_dmap)

            totptr += 1

        if totptr >= file_size:
            if self.verbose:
                print(f"Success - File {self.infile} read complete.")
        else:
            print("ERROR - There are still unread data")
            self.errormsg += "ERROR - There are still unread data\n"

        for name in my_dmap:
            if isinstance(my_dmap[name], list):
                my_dmap[name] = np.asarray(my_dmap[name])

        return my_dmap

    def read_file_fromhandle(self):
        """
        This function reads in the entire binary content using the file handle
        :return:
        """

        if self.filehand is None:
            self.errormsg += f"ERROR - File handle not yet set"
            return None

        my_dmap = {}

        blocknumber = 0
        while 1:

            try:
                datacode = self.filehand.read(4)
            except:
                if self.verbose:
                    print(f"INFO - Reached end of stream. or unable to read further")
                break

            if not datacode:
                if self.verbose:
                    print(f"INFO - Reached end of stream.")
                break

            if datacode == b"\x00\x01\x00\x01":
                self.endian, self.endiansymbol, self.compressed = "big", ">", False
            elif datacode == b"\x10\x01\x00\x01":
                self.endian, self.endiansymbol, self.compressed = "big", ">", True
            elif datacode == b"\x01\x00\x01\x00":
                self.endian, self.endiansymbol, self.compressed = "little", "<", False
            elif datacode == b"\x01\x00\x01\x10":
                self.endian, self.endiansymbol, self.compressed = "little", "<", True
            else:
                print(
                    f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting"
                )
                self.errormsg += f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting\n"
                self.filehand.close()
                self.filehand = None
                return None

            if self.verbose > 1:
                print(
                    f"DEBUG - Block: {blocknumber} raw datacode: {datacode}, Endianess: {self.endian}, compressed: {self.compressed}"
                )

            item = None
            try:
                item = self.filehand.read(4)
            except:
                if self.verbose:
                    print(f"INFO - Reached end of stream. or unable to read further")
                break

            sizeinfo = int.from_bytes(item, self.endian) - 8

            if self.verbose > 1:
                print(f"DEBUG - sizeinfo: {sizeinfo}")

            # second 4 bytes is size in bytes of total storage of data block
            # l = long, default 4 bytes, but python says it needs 8? Trying i = int
            block = None
            if self.compressed:
                item = None
                try:
                    item = self.filehand.read(4)
                except:
                    if self.verbose:
                        print(
                            f"INFO - Reached end of stream. or unable to read further"
                        )
                    break

                # next 4 bytes are, if compressed, original data size
                osizeinfo = int.from_bytes(item, self.endian)

                comp_factor = 1.0 * osizeinfo / sizeinfo
                if self.verbose > 1:
                    print(
                        f"DEBUG - Uncompressed size will be {osizeinfo} (Compression factor: {comp_factor}"
                    )

                cblock = None
                try:
                    cblock = self.filehand.read(sizeinfo - 4)
                except:
                    if self.verbose:
                        print(
                            f"INFO - Reached end of stream. or unable to read further"
                        )
                    break

                block = zlib.decompress(cblock)
            else:
                block = None
                try:
                    block = self.filehand.read(sizeinfo)
                except:
                    if self.verbose:
                        print(
                            f"INFO - Reached end of stream. or unable to read further"
                        )
                    break

            blocknumber += 1
            if self.verbose:
                print(f"INFO - Processing block {blocknumber}")

            self._decode(block, my_dmap)

        for name in my_dmap:
            if isinstance(my_dmap[name], list):
                my_dmap[name] = np.asarray(my_dmap[name])

        return my_dmap

    def read_block(self):
        """
        This function reads one single block of the DataMap binary content
        :return:
        """

        if self.filehand is None:
            self.errormsg += (
                f"ERROR - File handle is not set. Starting reading from the beginning"
            )
            self.set_filehand()

        file_size = os.path.getsize(self.infile)

        if self.totptr >= file_size:
            print(f"INFO - Reached end of file")
            return None

        my_dmap = {}
        datacode = self.filehand.read(4)
        self.totptr += 4

        if datacode == b"\x00\x01\x00\x01":
            self.endian, self.endiansymbol, self.compressed = "big", ">", False
        elif datacode == b"\x10\x01\x00\x01":
            self.endian, self.endiansymbol, self.compressed = "big", ">", True
        elif datacode == b"\x01\x00\x01\x00":
            self.endian, self.endiansymbol, self.compressed = "little", "<", False
        elif datacode == b"\x01\x00\x01\x10":
            self.endian, self.endiansymbol, self.compressed = "little", "<", True
        else:
            print(
                f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting"
            )
            self.errormsg += f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting\n"
            self.filehand.close()
            self.filehand = None
            return None

        sizeinfo = int.from_bytes(self.filehand.read(4), self.endian) - 8
        self.totptr += 4

        if self.verbose > 1:
            print(f"DEBUG - sizeinfo: {sizeinfo}")

        # second 4 bytes is size in bytes of total storage of data block
        # l = long, default 4 bytes, but python says it needs 8? Trying i = int
        block = None
        if self.compressed:
            # next 4 bytes are, if compressed, original data size
            osizeinfo = int.from_bytes(self.filehand.read(4), self.endian)
            self.totptr += 4

            comp_factor = 1.0 * osizeinfo / sizeinfo
            if self.verbose > 1:
                print(
                    f"DEBUG - Uncompressed size will be {osizeinfo} (Compression factor: {comp_factor}"
                )

            block = zlib.decompress(self.filehand.read(sizeinfo - 4))
            self.totptr += sizeinfo - 4
        else:
            block = self.filehand.read(sizeinfo)
            self.totptr += sizeinfo

        self.blocknumber += 1
        if self.verbose:
            print(f"INFO - Processing block {self.blocknumber}")

        self._decode(block, my_dmap)

        for name in my_dmap:
            if isinstance(my_dmap[name], list):
                my_dmap[name] = np.asarray(my_dmap[name])

        return my_dmap

    def read_block_fromhandle(self):
        """
        This function reads one single of the DataMap binary content
        :return:
        """

        if self.filehand is None:
            self.errormsg += (
                f"ERROR - File handle is not set. Starting reading from the beginning"
            )
            return None

        my_dmap = {}
        datacode = self.filehand.read(4)

        if not datacode:
            if self.verbose:
                print(f"INFO - Reached end of stream.")
            return None

        if datacode == b"\x00\x01\x00\x01":
            self.endian, self.endiansymbol, self.compressed = "big", ">", False
        elif datacode == b"\x10\x01\x00\x01":
            self.endian, self.endiansymbol, self.compressed = "big", ">", True
        elif datacode == b"\x01\x00\x01\x00":
            self.endian, self.endiansymbol, self.compressed = "little", "<", False
        elif datacode == b"\x01\x00\x01\x10":
            self.endian, self.endiansymbol, self.compressed = "little", "<", True
        else:
            print(
                f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting"
            )
            self.errormsg += f"ERROR - File {self.infile} appears to be corrupted. Cannot determine magic code, exiting\n"
            self.filehand.close()
            self.filehand = None
            return None

        sizeinfo = int.from_bytes(self.filehand.read(4), self.endian) - 8

        if self.verbose > 1:
            print(f"DEBUG - sizeinfo: {sizeinfo}")

        # second 4 bytes is size in bytes of total storage of data block
        # l = long, default 4 bytes, but python says it needs 8? Trying i = int
        block = None
        if self.compressed:
            # next 4 bytes are, if compressed, original data size
            osizeinfo = int.from_bytes(self.filehand.read(4), self.endian)
            self.totptr += 4

            comp_factor = 1.0 * osizeinfo / sizeinfo
            if self.verbose > 1:
                print(
                    f"DEBUG - Uncompressed size will be {osizeinfo} (Compression factor: {comp_factor}"
                )

            block = zlib.decompress(self.filehand.read(sizeinfo - 4))
            self.totptr += sizeinfo - 4
        else:
            block = self.filehand.read(sizeinfo)
            self.totptr += sizeinfo

        self.blocknumber += 1
        if self.verbose:
            print(f"INFO - Processing block {self.blocknumber}")

        self._decode(block, my_dmap)

        for name in my_dmap:
            if isinstance(my_dmap[name], list):
                my_dmap[name] = np.asarray(my_dmap[name])

        return my_dmap

    def _decode(self, block, my_dmap):
        """
        This is the function that does the actual processing of parsing all data into
        the passed dictionary

        :param block:       <Actual binary data to be parsed?
        :param my_dmap:     <Dictionary that will contain all parsed data>
        :return:
        """

        ptr = 0
        bnum_scalars = block[ptr : ptr + 4]
        num_scalars = struct.unpack(self.endiansymbol + "i", bnum_scalars)[0]
        ptr += 4

        if self.verbose > 1:
            print(f"num_scalars: {num_scalars}")
        bnum_arrays = block[ptr : ptr + 4]
        ptr += 4

        num_arrays = struct.unpack(self.endiansymbol + "i", bnum_arrays)[0]
        if self.verbose > 1:
            print(f"num arrays: {num_arrays}")

        # following are datablocks, either scaler or array
        # byte 0-3 is number of scalars, then 4-7 number of arrays

        # each set of 'sizeinfo' bytes are the datablock scalars
        for n in range(num_scalars):
            if self.verbose > 1:
                print(f"Grabbing scalar item {n}")
            name, ptr = grab_name(block, ptr)
            if name is None:
                print(f"ERROR - Unable to parse variable name")

            if self.verbose > 1:
                print(f"\tname: {name}")

            # each set of 'sizeinfo' bytes are the datablock scalars
            blocktype = block[ptr]
            if isinstance(blocktype, bytes):
                blocktype = int.from_bytes(block[ptr], self.endian)
            ptr += 1
            if self.verbose > 1:
                print(f"\tblocktype is {blocktype}")

            blocksize = dsizes[blocktype]
            blockformat = dformats[blocktype]
            if blockformat == "s":
                # null-terminated string
                data, ptr = grab_name(block, ptr)
            else:
                data = block[ptr : ptr + blocksize]
                ptr += blocksize
                data = struct.unpack(self.endiansymbol + blockformat, data)[0]
                if blockformat == "c":
                    data = data.decode()
            if self.verbose > 2:
                print(
                    f"\tdata specs: {blocktype},{blocksize},{blockformat},{self.endiansymbol} = {data}"
                )

            if self.verbose:
                print(f"\t{name}: {data}")
            elif self.verbose > 1:
                print(
                    f"Item {n+1}, Blocksize: {blocksize}, Name: {name}, Value: {data}"
                )

            if name in my_dmap:
                my_dmap[name].append(data)
            else:
                my_dmap[name] = [data]

        for n in range(num_arrays):
            if self.verbose > 1:
                print(f"Grabbing array item {n}")
            name, ptr = grab_name(block, ptr)
            if name is None:
                print(f"ERROR - Unable to parse variable name")
            if self.verbose > 1:
                print("\tname: {name}")

            blocktype = block[ptr]
            if isinstance(blocktype, bytes):
                blocktype = int.from_bytes(block[ptr], self.endian)
            ptr += 1

            blockformat = dformats[blocktype]
            blocksize = dsizes[blocktype]
            if self.verbose > 1:
                print(
                    f"\tblocktype {blocktype}, blockformat {blockformat}, blocksize {blocksize}"
                )

            bndim = block[ptr : ptr + 4]
            ptr += 4
            ndim = struct.unpack(self.endiansymbol + "i", bndim)[0]
            if self.verbose > 1:
                print(f"\tndim is {ndim}")

            axes = []
            for i in range(ndim):
                bval = block[ptr : ptr + 4]
                ptr += 4
                val = struct.unpack(self.endiansymbol + "i", bval)[0]
                axes.append(val)
            nelements = math.prod(axes)
            if self.verbose > 1:
                print(f"\tAxes are {axes}, nelements is {nelements}")

            if blockformat == "s":
                # null-terminated strings
                data = []
                for j in range(nelements):
                    val, ptr = grab_name(block, ptr)
                    data.append(val)
                myarr = np.array(data, dtype=object)
            else:
                data = block[ptr : ptr + blocksize * nelements]
                ptr += blocksize * nelements
                dt = np.dtype(self.endiansymbol + blockformat)
                if dt == "S1" or dt == "U1":
                    dt = np.uint8
                myarr = np.frombuffer(data, dtype=dt)

            myarr = myarr.reshape(tuple(reversed(axes)))

            if self.verbose:
                print(
                    f"Item {n + 1}, Blocksize: {blocksize}, Name: {name}, ndim: {ndim}"
                )
                print(f"\tAxes: {axes}, nelements: {nelements}, Shape: {myarr.shape}")
                print(f"\tfirst 2 ele: {myarr[0:2]}\n")

            if name in my_dmap:
                if ndim == 1:
                    try:
                        my_dmap[name] = np.vstack((my_dmap[name], myarr))
                    except:
                        print(f"ERROR - Unable to append data for {name}")
                        self.errormsg(f"ERROR - Unable to append data for {name}\n")
                else:
                    ashape = list(myarr.shape)
                    dshape = list(my_dmap[name].shape)
                    dndim = len(dshape)
                    newshape = [1] + ashape
                    if ndim == dndim:
                        my_dmap[name] = np.vstack(
                            (my_dmap[name].reshape(newshape), myarr.reshape(newshape))
                        )
                    else:
                        my_dmap[name] = np.vstack(
                            (my_dmap[name], myarr.reshape(newshape))
                        )

            else:
                my_dmap[name] = myarr


class DataMapWriter:
    """
    This class is to be used to handle Data Map writing to an output file.
    The object is initialized with an output file name, compression flag used to
    decide whether to compress the binary data (default is True), and a verbosity
    level with a default set to 0.
    """

    def __init__(self, outfile=None, compress=True, verb=0, **kwargs):
        # This is the Data Aggregator logfile handle
        self.outfile = outfile
        self.compress = compress
        self.verbose = verb
        self.filehand = None

        self.set_filehand()

        self.datacode = None
        self.endian = sys.byteorder
        self.endiansymb = ">"
        if self.endian == "little":
            self.endiansymb = "<"
            if self.compress:
                self.datacode = b"\x01\x00\x01\x10"
            else:
                self.datacode = b"\x01\x00\x01\x00"
        elif self.endian == "big":
            if self.compress:
                self.datacode = b"\x10\x01\x00\x01"
            else:
                self.datacode = b"\x00\x01\x00\x01"
        else:
            print("ERROR - Unable to determine machine endianess")

    def set_outfile(self, outfile):
        """
        Function setter for output file, which also used to set the
        object file handler.

        :param outfile:         <output file>
        :return:
        """
        self.outfile = outfile
        self.set_filehand()

    def set_compress(self, compress):
        """
        Function setter for the compression flag.
        :param compress:
        :return:
        """
        self.compress = compress

    def set_filehand(self):
        """
        This function does the following actions:
            1. Check is the object file handler is set, and if so, close it
            2. Check if the output file does exist, and if so, remove it
            3. Create a new file handler

        :param outfile:
        :return:
        """
        if self.filehand is not None:
            self.filehand.close()

        if self.outfile is not None:
            if os.path.exists(self.outfile):
                os.remove(self.outfile)
            try:
                if self.verbose:
                    print(f"INFO - Opening file {self.outfile} for writing")
                self.filehand = open(self.outfile, "wb")
            except:
                print(f"ERROR - Unable to open file {self.outfile} for writing")
        else:
            print(f"ERROR - Output file for writing is not specified")

    def write2file(self, indict):
        """
        This function takes a dictionary as input, which contains array and scalar,
        where for scalar it is meant also array containing only a single element, converts
        all data to binary. If the compression flag is set, then the converted data are
        compressed using zlib. Finally, the block so obtained is written to the indicated
        output file.

        :param indict:
        :return:
        """

        dict_info = self.analyze_dictionary(indict)
        if dict_info is None:
            print("ERROR - Unable to parse data dictionary\n")
            return -1

        scalars = dict_info["scalars"]
        arrays = dict_info["arrays"]
        datatypes = dict_info["datatypes"]

        binblock = b""

        # Doing scalar
        nscalars = 0
        for dim in scalars:
            for var in scalars[dim]:
                value = indict[var]
                if isinstance(value, np.ndarray):
                    value = value[0]
                dtype = datatypes[var]
                try:
                    binblock += encodeData(
                        var, value, self.endiansymb, dtype, dim, self.verbose
                    )
                except:
                    print(f"ERROR - Unable to convert to binary scalar {var}")
                    return -1

                nscalars += 1

        # Doing arrays
        narrays = 0
        for dim in arrays:
            for var in arrays[dim]:
                dtype = datatypes[var]
                if dtype == "object":
                    dtype = "string"
                values = indict[var]
                try:
                    binblock += encodeArrayData(
                        var, values, self.endiansymb, dtype, self.verbose
                    )
                except:
                    print(f"ERROR - Unable to convert to binary array {var}")
                    return -1

                narrays += 1

        block = struct.pack(self.endiansymb + "i", nscalars)
        block += struct.pack(self.endiansymb + "i", narrays)
        block += binblock

        sizeblock = len(block)
        compsize = -1
        if self.compress:
            zblock = None
            try:
                zblock = zlib.compress(block)
            except:
                print(f"ERROR - Unable to compress data")
                return -1

            compsize = len(zblock) + 8
            block = (
                self.datacode
                + struct.pack(self.endiansymb + "i", compsize + 4)
                + struct.pack(self.endiansymb + "i", sizeblock)
                + zblock
            )
        else:
            block = (
                self.datacode + struct.pack(self.endiansymb + "i", sizeblock) + block
            )

        self.filehand.write(block)

        return 0

    def close_file(self):
        if self.verbose:
            print(f"INFO - Closing file {self.outfile}")

        self.filehand.close()

    def analyze_dictionary(self, indict):
        """
        This function will attempt to identify scalars, which are 1D arrays, and arrays intended
        as multidimensional arrays whose first dimension will be used for creating DataMap blocks.

        :param indict:       <Input dictionary with all data>
        :param verb:         <Verbosity level>
        :return:
            A dictionary with the keynames used to identify each variable type
        """

        scalars = {}
        arrays = {}
        datatypes = {}

        varnames = indict.keys()

        # dtypes = {"char": 1, "int16": 2, "int32": 3, "int64": 4,
        #           "float": 4, "double": 8, "string": 9, "long": 10,
        #           "uchar": 16, "uint16": 17, "uint32": 18, "uint64": 19}

        # ndtypes = {'s1':'char', 'i2':'int16', 'i4':'int32', 'i8':'int64',
        #            'f4':'float', 'f8':'double', 'string':'string', 'i8':'long',
        #            'u1':'uchar', 'u2':'uint16', 'u4':'uint32', 'u8':'uint64',}

        for name in varnames:
            values = indict[name]
            vdatatype = values.dtype.str[1:].lower()
            if vdatatype in ndtypes:
                datatypes[name] = ndtypes[vdatatype]
            else:
                if re.match(r"s\d+", vdatatype) or re.match(r"u\d+", vdatatype):
                    datatypes[name] = "string"
                elif vdatatype == "o":
                    datatypes[name] = "object"
                else:
                    pass

            if not isinstance(values, np.ndarray):
                values = np.asarray(indict[name])

            shape = None
            try:
                shape = list(values.shape)
            except:
                print(f"ERROR - Unable to get dimensions for variable {name}")
                return None

            dim0 = 0
            ndims = len(shape)
            if ndims == 0:
                if dim0 in scalars:
                    scalars[dim0].append(name)
                else:
                    scalars[dim0] = [name]
            elif ndims == 1:
                dim0 = shape[0]
                if dim0 == 1:
                    if dim0 in scalars:
                        scalars[dim0].append(name)
                    else:
                        scalars[dim0] = [name]
                else:
                    if dim0 in arrays:
                        arrays[dim0].append(name)
                    else:
                        arrays[dim0] = [name]

            else:
                dim0 = shape[0]
                if dim0 in arrays:
                    arrays[dim0].append(name)
                else:
                    arrays[dim0] = [name]

        return {"scalars": scalars, "arrays": arrays, "datatypes": datatypes}


def grab_name(fp, ptr):
    """
    Function used to parse a string, which can be a variable name, or a value in the form of a string.
    The function will keep looping through each byte from the indicated starting point (ptr) until it
    encounters a null character, which will denote the end of teh parsed string. The end point where
    the null character is found is returned as well as the parsed string

    :param fp:      <DataMap file content, or block>
    :param ptr:     <starting point form which to begin looking for a null character>
    :return:
    """
    name = b""
    icount = 0
    byte = b"\1"
    while byte != b"\0":
        byte = fp[ptr : ptr + 1]

        if byte != b"\0":
            name += byte
            icount += 1
        ptr += 1

    try:
        rname = name.decode()
    except:
        print(f"ERROR - Unable to decode {name}")
        rname = None
    return rname, ptr


def decode(block, my_dmap, byteinfo, iblk, verb):
    """
    This function does the actual parsing of teh scalars and arrays contained within the passed block.
    The function is either called when run in single mode, in which case my_dmap accumulates all parsed
    data, or in multi-processing mode, in which case each thread will initialize the dictionary that will
    contain the patrsed data for teh single block, populate it with data, and return it.

    :param block:       <input binary block to be parsed>
    :param my_dmap:     <This is either None, in which case it is initialized to a dictionary and returned, or
                         it is a dictionary which will contain all parsed data>
    :param byteinfo:    <dictionary that contains all binary info, including endianess and compression flag>
    :param iblk:        <Block number>
    :param verb:        <verbosity level>
    :return:
        Depending on the input my_dmap, this function either does not return anything, or my_dmap.
    """
    endian = byteinfo["endian"]
    endiansymbol = byteinfo["endiansymbol"]
    compressed = byteinfo["compressed"]

    if verb:
        print(f"INFO - Processing block {iblk+1}")

    if len(block) <= 0:
        return None

    ptr = 0
    sizeinfo = int.from_bytes(block[ptr : ptr + 4], endian) - 8
    ptr += 4

    flgret = 0
    if my_dmap is None:
        my_dmap = {}
        flgret = 1

    if verb > 2:
        print(f"sizeinfo: {sizeinfo}")

    if compressed:
        # next 4 bytes are, if compressed, original data size
        osizeinfo = int.from_bytes(block[ptr : ptr + 4], endian)
        ptr += 4

        comp_factor = 1.0 * osizeinfo / sizeinfo
        if verb > 2:
            print(
                f"Uncompressed size will be {osizeinfo} (Compression factor: {comp_factor}"
            )

        block = zlib.decompress(block[ptr:])
    else:
        block = block[ptr:]

    ptr = 0
    bnum_scalars = block[ptr : ptr + 4]
    num_scalars = struct.unpack(endiansymbol + "i", bnum_scalars)[0]
    ptr += 4

    # bignum_scalars = int.from_bytes(bnum_scalers,"big")
    # littlenum_scalars = int.from_bytes(bnum_scalers,"little")
    # num_scalars = int.from_bytes(bnum_scalers,endian)
    if verb > 1:
        print(f"num_scalars: {num_scalars}")
    bnum_arrays = block[ptr : ptr + 4]
    ptr += 4

    num_arrays = struct.unpack(endiansymbol + "i", bnum_arrays)[0]
    # num_arrays = int.from_bytes(fp.read(4),endian)
    if verb > 1:
        print(f"num arrays: {num_arrays}")

    # following are datablocks, either scaler or array
    # byte 0-3 is number of scalars, then 4-7 number of arrays

    # each set of 'sizeinfo' bytes are the datablock scalars
    for n in range(num_scalars):
        name, ptr = grab_name(block, ptr)

        # each set of 'sizeinfo' bytes are the datablock scalars
        # blocktype = int.from_bytes(fp.read(1),endian)
        blocktype = block[ptr]
        if isinstance(blocktype, bytes):
            blocktype = int.from_bytes(block[ptr], endian)
        ptr += 1

        blocksize = dsizes[blocktype]
        blockformat = dformats[blocktype]
        if blockformat == "s":
            # null-terminated string
            data, ptr = grab_name(block, ptr)
        else:
            data = block[ptr : ptr + blocksize]
            ptr += blocksize
            data = struct.unpack(endiansymbol + blockformat, data)[0]
            if blockformat == "c":
                data = data.decode()

        if verb:
            print(f"\t{name}: {data}")
        elif verb > 1:
            print(f"Item {n+1}, Blocksize: {blocksize}, Name: {name}, Value: {data}")

        if name in my_dmap:
            my_dmap[name].append(data)
        else:
            my_dmap[name] = [data]

    for n in range(num_arrays):
        name, ptr = grab_name(block, ptr)

        # blocktype = int.from_bytes(fp.read(1),endian)
        blocktype = block[ptr]
        if isinstance(blocktype, bytes):
            blocktype = int.from_bytes(block[ptr], endian)
        ptr += 1

        blockformat = dformats[blocktype]
        blocksize = dsizes[blocktype]
        # if debug: print(f"\tblocktype {blocktype}, blockformat {blockformat}, blocksize {blocksize}")

        bndim = block[ptr : ptr + 4]
        ptr += 4
        ndim = struct.unpack(endiansymbol + "i", bndim)[0]

        axes = []
        for i in range(ndim):
            bval = block[ptr : ptr + 4]
            ptr += 4
            val = struct.unpack(endiansymbol + "i", bval)[0]
            axes.append(val)
        nelements = math.prod(axes)

        # if compressed:
        #     compressed_size = int.from_bytes(fp.read(4), endian)
        #     if debug: print(f"\tCompressed size is: {compressed_size}")

        if blockformat == "s":
            # null-terminated strings
            data = []
            # if compressed:
            #     print("Support for compressed strings not yet implemented")
            #     errormsg += "Support for compressed strings not yet implemented\n"
            for j in range(nelements):
                val, ptr = grab_name(block, ptr)
                data.append(val)
            myarr = np.array(data, dtype=object)
        else:
            data = block[ptr : ptr + blocksize * nelements]
            ptr += blocksize * nelements
            dt = np.dtype(endiansymbol + blockformat)
            if dt == "S1" or dt == "U1":
                dt = np.uint8
            myarr = np.frombuffer(data, dtype=dt)

        myarr = myarr.reshape(tuple(reversed(axes)))

        if verb:
            print(f"Item {n+1}, Blocksize: {blocksize}, Name: {name}, ndim: {ndim}")
            print(f"\tAxes: {axes}, nelements: {nelements}, Shape: {myarr.shape}")
            print(f"\tfirst 2 ele: {myarr[0:2]}\n")

        if name in my_dmap:
            if ndim == 1:
                try:
                    my_dmap[name] = np.vstack((my_dmap[name], myarr))
                except:
                    print(f"ERROR - Unable to append data for {name}")
            else:
                ashape = list(myarr.shape)
                dshape = list(my_dmap[name].shape)
                dndim = len(dshape)
                newshape = [1] + ashape
                if ndim == dndim:
                    my_dmap[name] = np.vstack(
                        (my_dmap[name].reshape(newshape), myarr.reshape(newshape))
                    )
                else:
                    my_dmap[name] = np.vstack((my_dmap[name], myarr.reshape(newshape)))

        else:
            my_dmap[name] = myarr

    if flgret == 0:
        return
    else:
        return my_dmap


def check_block_validity(Blocks, byteinfo, datacode, verb=0):
    """
    This function is used when parsing DataMap data while using multi-processing.
    The entire file content is split into blocks using the 'magic' code. In some cases
    this code is used within the block, but not to indicate the beginning of the block
    itself. This function tries to mitigate issues that arises from the presence of the
    magic code within a block by checking that the block length is what it is supposed to be.
    In cases when this does not happen possibly caused by the presence of the magic code,
    and this function will try to merge the current block and the next while checking that the
    overall block size is the same as expected. If that is not the case, then the block is skipped.


    :param Blocks:      <list of binary blocks>
    :param byteinfo:    <dictionary containing the byte information>
    :param datacode:    <this is the 'magic' code>
    :param verb:        <verbosity level>
    :return:
    """
    endian = byteinfo["endian"]
    endiansymbol = byteinfo["endiansymbol"]
    compressed = byteinfo["compressed"]

    Nblocks = []
    skipblock = 0
    for i, block in enumerate(Blocks):
        if verb > 1:
            print(f"INFO - Checking block {i+1}")
        blocklen = len(block)
        if blocklen <= 0:
            continue
        if skipblock > 0:
            skipblock -= 1
            continue
        ptr = 0
        sizeinfo = int.from_bytes(block[ptr : ptr + 4], endian) - 8
        ptr += 4
        if sizeinfo != blocklen - 4:
            tblock = block
            print(
                f"WARNING - Block {i} is expected to have size {sizeinfo}, but has size {blocklen-4}"
            )
            j = 0
            while blocklen - 4 < sizeinfo:
                j += 1
                tblock += datacode + Blocks[i + j]
                blocklen = len(tblock)

            if sizeinfo == blocklen - 4:
                print(f"INFO - Block fixed using next block")
                skipblock = j
                block = tblock
                Nblocks.append(block)
            else:
                print(f"WARNING - Unable to fix block. It will be skipped\n")
                skipblock = 0

        else:
            Nblocks.append(block)

    return Nblocks


def read_datamap(fname, num_threads=0, verb=0):  # , debug=True):
    """
    This function reads an input DataMap file, and returns the parsed data as a
    dictionary and any possible error messages.

    :param fname:   <input DataMap file>
    :param verb:    <verbosity level of the parsing process; 0-quiet, 3-very verbose>
    :param debug:
    :return:
    """
    errormsg = ""
    my_dmap = {}
    filecontent = None

    if isinstance(fname, io.IOBase):
        try:
            filecontent = fname.read()
        except:
            errormsg = f"ERROR - Unable to read file using provided file handle"
            return None, errormsg

    else:
        try:
            fp = open(fname, "rb")
            filecontent = fp.read()
            fp.close()
        except:
            errormsg = f"ERROR - Unable to open file {fname} for reading"
            return None, errormsg

    # file_size = os.path.getsize(fname)
    file_size = len(filecontent)
    totptr = 0  # This is the total pointer, used to keep track what has been read/used in the file

    if num_threads > 0:
        datacode = filecontent[totptr : totptr + 4]
        if datacode == b"":
            totptr += 1
        if datacode == b"\x00\x01\x00\x01":
            endian, endiansymbol, compressed = "big", ">", False
        elif datacode == b"\x10\x01\x00\x01":
            endian, endiansymbol, compressed = "big", ">", True
        elif datacode == b"\x01\x00\x01\x00":
            endian, endiansymbol, compressed = "little", "<", False
        elif datacode == b"\x01\x00\x01\x10":
            endian, endiansymbol, compressed = "little", "<", True
        else:
            print("Cannot determine magic code, exiting")
            errormsg += "Cannot determine magic code, exiting"
            exit()

        byteinfo = {
            "endian": endian,
            "endiansymbol": endiansymbol,
            "compressed": compressed,
        }

        if verb > 3:
            print(
                f"raw datacode: {datacode}, Endianess: {endian}, compressed: {compressed}"
            )

        Sblocks = check_block_validity(
            filecontent.split(datacode), byteinfo, datacode, verb
        )

        # tmpdata = [decode(block, my_dmap, byteinfo, i, verb) for i, block in enumerate(Sblocks)]

        jobs = []

        pool = multiprocessing.Pool(processes=num_threads)
        for i, block in enumerate(Sblocks):
            jobs.append(pool.apply_async(decode, [block, None, byteinfo, i, 0]))

        pool.close()
        pool.join()

        for i, p in enumerate(jobs):
            dicto = p.get()
            if verb:
                print(f"Processing block {i}")
            for name in dicto:
                item = dicto[name]
                size = None
                if isinstance(item, list):
                    size = len(item)
                else:
                    size = item.size
                if verb:
                    if size == 1:
                        print(f"\t{name} = {item[0]}")
                    else:
                        outstr = f"\t{name} = "
                        shape = list(item.shape)
                        for j, d in enumerate(shape):
                            if j == 0:
                                outstr += f"[{d}] "
                            else:
                                outstr += f" x [{d}] "

                        print(outstr)

                if name not in my_dmap:
                    my_dmap[name] = item
                else:
                    if size == 1:
                        my_dmap[name].append(item[0])
                    else:
                        myarr = dicto[name]
                        ashape = list(myarr.shape)
                        dshape = list(my_dmap[name].shape)
                        ndim = len(ashape)
                        dndim = len(dshape)
                        newshape = [1] + ashape
                        if ndim == dndim:
                            my_dmap[name] = np.vstack(
                                (
                                    my_dmap[name].reshape(newshape),
                                    myarr.reshape(newshape),
                                )
                            )
                        else:
                            my_dmap[name] = np.vstack(
                                (my_dmap[name], myarr.reshape(newshape))
                            )

        for name in my_dmap:
            if isinstance(my_dmap[name], list):
                my_dmap[name] = np.asarray(my_dmap[name])

        return my_dmap, errormsg

    blocknumber = 0
    while totptr <= file_size:

        # first 4 bytes is magic ID (matches "DATACODE" or "DATACODEZ")
        # define DATACODE  0x00010001
        # define DATACODEZ  0x10010001
        datacode = filecontent[totptr : totptr + 4]
        totptr += 4
        if datacode == b"":
            totptr += 1
            break
        if datacode == b"\x00\x01\x00\x01":
            endian, endiansymbol, compressed = "big", ">", False
        elif datacode == b"\x10\x01\x00\x01":
            endian, endiansymbol, compressed = "big", ">", True
        elif datacode == b"\x01\x00\x01\x00":
            endian, endiansymbol, compressed = "little", "<", False
        elif datacode == b"\x01\x00\x01\x10":
            endian, endiansymbol, compressed = "little", "<", True
        else:
            print("Cannot determine magic code, exiting")
            errormsg += "Cannot determine magic code, exiting"
            exit()

        byteinfo = {
            "endian": endian,
            "endiansymbol": endiansymbol,
            "compressed": compressed,
        }

        if verb > 3:
            print(
                f"raw datacode: {datacode}, Endianess: {endian}, compressed: {compressed}"
            )

        sizeinfo = int.from_bytes(filecontent[totptr : totptr + 4], endian) - 8
        totptr += 4

        if verb > 2:
            print(f"sizeinfo: {sizeinfo}")

        # second 4 bytes is size in bytes of total storage of data block
        # l = long, default 4 bytes, but python says it needs 8? Trying i = int

        # tmpblock = filecontent[totptr:totptr+sizeinfo]
        tmpblock = filecontent[totptr - 4 : totptr + sizeinfo]

        decode(tmpblock, my_dmap, byteinfo, blocknumber, verb)
        blocknumber += 1

        totptr += sizeinfo

        # totptr += 1

    if totptr >= file_size:
        print("Success, file read complete.")
    else:
        print("Warning, still unread data")
        errormsg += "Warning, still unread data\n"

    # fp.close()

    for name in my_dmap:
        if isinstance(my_dmap[name], list):
            if verb:
                print(f"INFO - Converting {name} to a NUMPY array")
            my_dmap[name] = np.asarray(my_dmap[name])

    return my_dmap, errormsg


def analyze_dictionary(indict, verb):
    """
    This function will attempt to identify scalars, which are 1D arrays, and arrays intended
    as multidimensional arrays whose first dimension will be used for creating DataMap blocks.

    :param indict:       <Input dictionary with all data>
    :param verb:         <Verbosity level>
    :return:
        A dictionary with the keynames used to identify each variable type
    """

    endian = sys.byteorder
    endiansymb = ">"
    if endian == "little":
        endiansymb = "<"

    scalars = {}
    arrays = {}
    datatypes = {}

    varnames = indict.keys()
    maxdim = -1  # largets dimension

    # dtypes = {"char": 1, "int16": 2, "int32": 3, "int64": 4,
    #           "float": 4, "double": 8, "string": 9, "long": 10,
    #           "uchar": 16, "uint16": 17, "uint32": 18, "uint64": 19}

    # ndtypes = {'s1':'char', 'i2':'int16', 'i4':'int32', 'i8':'int64',
    #            'f4':'float', 'f8':'double', 'string':'string', 'i8':'long',
    #            'u1':'uchar', 'u2':'uint16', 'u4':'uint32', 'u8':'uint64',}

    for name in varnames:
        values = indict[name]
        if not isinstance(values, np.ndarray):
            values = np.asarray(indict[name])

        vdatatype = values.dtype.str[1:].lower()
        if verb > 1:
            print(f"Name: {name}, values: {values}, dtype: {vdatatype}")
        if vdatatype in ndtypes:
            if np.issubdtype(values.dtype, np.str_):
                datatypes[name] = "string"
            else:
                datatypes[name] = ndtypes[vdatatype]
        else:
            if re.match(r"s\d+", vdatatype) or re.match(r"u\d+", vdatatype):
                datatypes[name] = "string"
            elif vdatatype == "o":
                datatypes[name] = "object"
            else:
                pass

        shape = None
        try:
            shape = list(values.shape)
        except:
            print(f"ERROR - Unable to get dimensions for variable {name}")
            return None

        dim0 = 0
        ndims = len(shape)
        if ndims == 0:
            if dim0 in scalars:
                scalars[dim0].append(name)
            else:
                scalars[dim0] = [name]
        elif ndims == 1:
            dim0 = shape[0]
            if dim0 in scalars:
                scalars[dim0].append(name)
            else:
                scalars[dim0] = [name]
        else:
            dim0 = shape[0]
            if dim0 in arrays:
                arrays[dim0].append(name)
            else:
                arrays[dim0] = [name]

        if dim0 > maxdim:
            maxdim = dim0

    if verb:
        print(f"INFO - Max number of blocks is {maxdim}")

    scalars_fact = {}
    for dim in scalars:
        if dim == 0:
            val = maxdim
        else:
            val = math.floor(maxdim / dim)
        scalars_fact[dim] = val

    arrays_fact = {}
    for dim in arrays:
        if dim == 0:
            val = maxdim
        else:
            val = math.floor(maxdim / dim)
        arrays_fact[dim] = val

    return {
        "scalars": scalars,
        "arrays": arrays,
        "maxdim": maxdim,
        "datatypes": datatypes,
        "scalars_fact": scalars_fact,
        "arrays_fact": arrays_fact,
    }


def encodeData(name, value, endiansymb, dtype, dim, verb):
    """
    This function is used to convert to binary mode, encode, the value associated with the passed
    variable name. The function can handle either a single scalar, or an array of dimension 0. This
    is why the dim parameter is passed.

    :param name:            <Variable name>
    :param value:           <Variable value>
    :param endiansymb:      <endian symbol used for packing (encoding)>
    :param dtype:           <data type>
    :param dim:             <Parameter used to verify if dealing with a 0-size array>
    :param verb:            <verbosity level>
    :return:
        <Encoded to binary block>

    """

    if verb > 1:
        print(f"Encoding: name={name}, value:{value}")

    # Encoding variable name
    binblock = name.encode() + b"\0"
    dtn = dtypes[dtype]
    dformat = dformats[dtn]
    dsize = dsizes[dtn]
    val = value
    if dim == 0:
        val = value.item()

    # Encoding data type
    # binblock += dformat.encode()
    binblock += struct.pack(endiansymb + "B", dtn)

    # Encoding value

    if dformat == "B" and isinstance(val, str):
        binblock += val.encode()
    elif dformat == "s" and isinstance(val, str):
        binblock += val.encode() + b"\0"
    else:
        try:
            binblock += struct.pack(endiansymb + dformat, val)
        except:
            print(f"ERROR - Failed to encode name:{name}, val:{val}, format:{dformat}")

    return binblock


def encodeArrayData(name, values, endiansymb, dtype, verb):
    """
    This function is used to convert to binary mode, encode, the values associated with the passed
    variable name, and array values.

    :param name:            <Variable name>
    :param values:          <array of values associated with the given variable>
    :param endiansymb:      <endian symbol used for packing (encoding)>
    :param dtype:           <data type>
    :param verb:            <verbosity level>
    :return:
        <Encoded to binary block>
    """

    if verb > 1:
        print(f"Encoding: name={name}, value:{values}")

    # Encoding variable name
    binblock = name.encode() + b"\0"
    dtn = dtypes[dtype]
    dformat = dformats[dtn]

    binblock += struct.pack(endiansymb + "B", dtn)

    shape = list(values.shape)
    ndim = len(shape)
    binblock += struct.pack(endiansymb + "i", ndim)
    if ndim > 1:
        shape.reverse()
    for dim in shape:
        binblock += struct.pack(endiansymb + "i", dim)

    newvalues = np.copy(values)
    if ndim > 1:
        newvalues = values.flatten("C")

    n_elements = len(newvalues)
    if dformat == "s":
        for i in range(n_elements):
            binblock += newvalues[i].encode() + b"\0"
    else:
        binblock += struct.pack(endiansymb + str(n_elements) + dformat, *newvalues)

    return binblock

    pass


def write_datamap(outfile, indict, verb=0, compress=True):
    """
    This function takes a dictionary as input, analyzes it to understand which variables are
    scalars and which one are arrays, and then it will loop through the values to write out
    the content to a DataMap file.

    Notice: the first dimensions is assumed to be the one used for looping when creating blocks

    The function returns a string containing all errors and warnings, if any. If the string is empty
    then no error was found.

    :param outfile:      <Output file, where the data will be written>
    :param indict:       <Input dictionary with all data>
    :param verb:         <Verbosity level>
    :param compress:     <Boolean to indicate whether data rea to be compressed. Default is True>
    :return:
    """

    if os.path.exists(outfile):
        os.remove(outfile)

    erstr = ""

    outcode = b""

    datacode = b""
    endian = sys.byteorder
    endiansymb = ">"
    if endian == "little":
        endiansymb = "<"
        if compress:
            datacode = b"\x01\x00\x01\x10"
        else:
            datacode = b"\x01\x00\x01\x00"
    elif endian == "big":
        if compress:
            datacode = b"\x10\x01\x00\x01"
        else:
            datacode = b"\x00\x01\x00\x01"
    else:
        erstr = "ERROR - Unable to determine machine endianess"
        return erstr, -1

    dict_info = analyze_dictionary(indict, verb)
    if dict_info is None:
        erstr += "ERROR - Unable to parse data dictionary\n"
        return erstr, -1

    scalars = dict_info["scalars"]
    arrays = dict_info["arrays"]
    maxdim = dict_info["maxdim"]
    scal_fact = dict_info["scalars_fact"]
    arra_fact = dict_info["arrays_fact"]
    datatypes = dict_info["datatypes"]

    for i in range(maxdim):
        nscalars = 0
        binblock = b""
        for dim in scalars:
            fact = scal_fact[dim]
            if i < dim and dim <= maxdim:
                for var in scalars[dim]:
                    # if fact == maxdim:
                    #     value = indict[var]
                    if dim == 0:
                        value = indict[var]
                    else:
                        value = indict[var][i]

                    dtype = datatypes[var]

                    binblock += encodeData(var, value, endiansymb, dtype, dim, verb)

                    nscalars += 1

        narrays = 0
        for dim in arrays:
            fact = arra_fact[dim]
            if i < dim:
                for var in arrays[dim]:
                    dtype = datatypes[var]
                    if dtype == "object":
                        dtype = "string"
                    values = indict[var][i]
                    binblock += encodeArrayData(var, values, endiansymb, dtype, verb)

                    narrays += 1

        block = struct.pack(endiansymb + "i", nscalars)
        block += struct.pack(endiansymb + "i", narrays)
        block += binblock

        sizeblock = len(block)
        compsize = -1
        if compress:
            zblock = zlib.compress(block)
            compsize = len(zblock) + 8
            block = (
                datacode
                + struct.pack(endiansymb + "i", compsize + 4)
                + struct.pack(endiansymb + "i", sizeblock)
                + zblock
            )
        else:
            block = datacode + struct.pack(endiansymb + "i", sizeblock) + block

        outcode += block

    fp = open(outfile, "wb")
    fp.write(outcode)
    fp.close()

    return erstr, 1
