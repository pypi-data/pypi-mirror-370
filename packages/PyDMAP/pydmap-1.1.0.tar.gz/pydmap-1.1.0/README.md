# DataMap Python Module

## DataMap Format Description

DataMap is a record based file format. A file is compromised of any number of independent records; each record can be of different length and contain different variables.

DataMap is a self describing format. Each record consists of a set of named vriables. The record header defines the data type for each variable together with information about it’s size - ie. Whether it is an array or scalar.

DataMap variables can be either scalar (a single variable), or an array. There are now limits on the number of dimensions of an array or the ranges of each dimension, however the format does not support sparse arrays as yet, so memory must be allocated for the entirety of the array.

Datatypes - the DataMap data types are defined in the header “dmap.h” and consist of:

DATACHAR Signed character (1 byte) DATASHORT Signed 16-bit integer (2 bytes DATAINT Signed 32-bit integer (4 bytes) DATAFLOAT IEEE Single precision floating point (4 bytes) DATADOUBLE IEEE Double precision floating point (8 bytes) DATASTRING Array of characters to store a string, terminated with a zero (N bytes) DATALONG 10 Signed 64-bit integer (8 bytes)

DATAUCHAR Unsigned character (1 byte) DATAUSHORT Unsigned 16-bit integer (2 bytes) DATAUINT Unsigned 32-bit integer (4 bytes) DATAULONG Unsigned 64-bit integer (65 bytes)

Compression. Data within a DataMap record can be compressed. The compression algorithm uses is zlib. Compression is done at the record level - so each record is uncompressed independently of the others to prevent file corruption.


## DataMap File format:
The DataMap file format does not have a header; the file consists of a stream of DataMap records or packets. This was done to allow the contents of multiple DataMap files to be combined together using the standard UNIX “cat” command and to allow the format to be used as a streaming protocol. Each file consists of N independent records, each record consists of a simple header followed by the record data:

Data Format

|Byte Offset          | Size                   | Contents |
|---------------------|------------------------|----------|
|0                    | 4                      |  Signature Word (defined in dmap.h as “DATACODE” or DATACODEZ”). Matching this signature identifies the data as being in DataMap format, if the signature matches “DATACODEZ” then the data is compressed. |
|4                    | 4                      |  Size in bytes of the data block (size). For uncompressed records, this represents the total storage required for the data; for compressed records this is the total storage for the compressed data. |
|8                    | 4                      |  Origianl size in bytes of the data if the record is compressed.  This field only appears if the data has been compressed. The reader  should allocate this amount of memory to store the record data when it is uncompressed.|
|8                    | size                  |  Data block |

Data can either be read directly from the file it is contained in using the standard UNIX I/O library (or in the case of compressed records, the zlib equivalents), or the data block can be loaded into a memory buffer and decoded directly. This is the reason that the compressed record header has an extra field that defines the total size of the uncompressed data block. This allows the reader to allocate memory to store the data before it is uncompressed.


## DataMap data
The DataMap data block contains the scalars and arrays that make up the record. The data is arranged with the scalar variables first followed by the array variables. The first two words of the data block define how many variables of each type there are:

Data Format

|Byte Offset      | Size                    |Contents|
|------------|-------------|-------|
|0                      |4                        |Number of scalar variables|
|4                      |4                        |Number of array variables|





## Scalars
Scalars consists of a variable name, the data type of the scalar, and then the scalar data. The variable name is a zero terminated string:

Data Format

|Byte Offset      | Size                    |Contents|
|------------|-------------|-------|
|0                      |N + 1                |Variable name of length N characters. A trailing zero byte marks the end of the name.|
|N + 1               |4                       |Scalar data type (As defined in “dmap.h”)|
|N + 5               |X                       |The variable data. A single character will occupy 1 byte, a double precision floating point number will occupy 8 bytes. The special type “DATA_STRING” is a zero terminated character array that represents a string.|

## Arrays
DataMap arrays can have an unlimited number of dimensions and
unlimited ranges, however the format does not support sparse arrays,
so the dimensions and range of each dimension must be fully allocated
in memory. 
As with scalars, array names are zero terminated:

Data Format

|Byte Offset      | Size                    |Contents|
|------------|-------------|-------|
|0                     | N                        |Array name of length N characters. A trailing zero byte marks the end of the name.|
|N + 1              | 5                        |Number of dimensions of the array (dim).|
|N + 5              | 4 * dim               |Range (Extent) of each dimension R[i] |
N + 5 + 4 * dim| X                       |Array data|

Depending on the data type, the array data will consist of X number of
bytes sufficient to store the array data. The total number of array
elements is the product of each range (R[0]*R[1]*R[2]….*R[dim]). 
So for a 3x3x3 array of integers, the array data consists of 108 byte - 3*3*3*4.

There is no convention as to whether array data is row or column ordered - this is at the discretion of the user.

When dealing with arrays of strings, each string is stored as a zero terminated array of characaters, and the exact amount of memory used is indeterminate until the arrays is decoded.

Nested DataMap records

An extension to the DataMap format is to support the nesting of
DataMap data. If a scalar or array has the special data type “DATAMAP”
then is assumed to be a DataMap record or an array of DataMap
records. 
This allows complex data structures to be represented in a file. The
problem is how to expose that data to the user through the API. For
the C interface this is actually simple, as the API returns a 
pointer to a data structure to the user that contains the contents of the DataMap record. Each scalar or array contains a pointer to the contents of the variable.



# DataMap Python Module PyDMAP
The DataMap Python module PyDMAP is derived from the C code written by
Barnes, Robin J. <Robin.Barnes@jhuapl.edu>. The module offers several 
methods for both reading and writing a binary DataMap input file, and
it is written entirely in Python, 
using only NUMPY as external module.

## Reading Example
There are different ways to read a DataMap binary file:

Reading the whole file using:

Using a file name

```python
import PyDMAP as dmap

my_dmap, errormsg = dmap.read_datamap(filename, num_threads, verbose)
```

Using a file handle

```python
import PyDMAP as dmap

fp = open(filename, 'rb')
my_dmap, errormsg = dmap.read_datamap(fb, num_threads, verbose)
```

Using a filename to read the whole file

```python
import PyDMAP as dmap

Reader = dmap.DataMapReader(filename, verbose)
# Reads the whole file at once
my_dmap = Reader.read_file()
```

Using a file handle

```python
import PyDMAP as dmap

fp = open(filename, 'rb')
Reader = dmap.DataMapReader(None, verbose)
Reader.set_filehandle4reading(fp)
my_dmap = Reader.read_file_fromhandle()
```

Using a file handle to read block by block

```python
import PyDMAP as dmap

fp = open(filename, 'rb')
Reader = dmap.DataMapReader(None, verbose)
Reader.set_filehandle4reading(fp)
my_dmap = []
data = 1
while data is not None:
    data = Reader.read_block_fromhandle()
    if isinstance(data, dict):
        my_dmap.append(data)
```



## Writing Example
In the same way, there are several ways for writing data in a binary DataMap format

```python
import PyDMAP as dmap
# outfile is the binary where all data will be written

# my_dmap is a dictionary that contains all scalars and arrays
# Notice that any 1D arrays will be considered scalars and written
# to each binary block
ermsg, status = dmap.write_datamap(outfile, my_dmap, verbose)
```

Using a filename to write the data to the specified output file
```python
import PyDMAP as dmap
# outfile is the binary where all data will be written

# my_dmap is a dictionary that contains all scalars and arrays
# Notice that any 1D arrays will be considered scalars and written
# to each binary block

# Creating teh writer object
writer = dmap.DataMapWriter(outfile, compress=True, verb=verbose)
# Writing the data
status = writer.write2file(my_dmap)
writer.close_file()
```

Alternatively, if there is a case where data are acquire during an iteration, or the data is contained in a list of dictionaries, the following example can be used

```python
import PyDMAP as dmap
# outfile is the binary where all data will be written
# my_dmap is a list of dictionaries, each dictionary will be
# written to the output file as a block

# Creating teh writer object
writer = dmap.DataMapWriter(outfile, compress=True, verb=verbose)
# Writing the data
if isinstance(my_dmap, list):
    for data in my_dmap:
        if isinstance(data, dict):
            status = writer.write2file(data)
            if status != 0:
                break

writer.close_file()
```




## Status

See *[TODO.md](TODO.md)* for current status and bugs.
