# hdfq

`hdfq` is a CLI tool for displaying and manipulating hdf5 files.
It uses syntax similar to [jq](https://jqlang.github.io/jq/) although it does not yet support everything `jq` does.
`hdfq` is written in Python.

## Installation

### with pipx

The recommended way of installing **hdfq** is trough the pipx installer :

```bash
pipx install hdfq
```

`hdfq` will be installed in an isolated environment but will be available globally as a shell application.

### from source

You can download the source code from gitlab with :

```bash
git clone git@github.com:MatteoBouvier/hdfq.git
```

## Usage

### Basics

`hdfq` requires both a **filter** (a command to be evaluated) and a **path** to a file saved in `hdf5` format.
A typical hdfq command would look like :

```bash
hdfq "." path/to/hdf5/file
```

👆 Tip : you can also invoke hdfq as :
```bash
echo path/to/hdf5/file | hdfq "."
```

The filter argument can be used to :
- read a specific object (stored under the `<name>` identifier) from the file with `.<name>`
- read a specific attribute from an object with `#<attr_name>`
- get the list of identifiers with `keys`, attributes with `attrs` and attribute identifiers with `kattrs`
- set an object's value with `<object>=<value>`
- delete an object with `del(<object>)`

Commands can be chained in the filter argument using a `|` symbol.

### Examples

View all contents in a file :
```bash
hdfq '.' file.h5
```

Read the contents of an object named `b` in `a`
```bash
hdfq '.a.b' file.h5
```

Read the `z` attribute of an object's (a.b) :
```bash
hdfq '.a.b#z' file.h5
```

Chain commands (select `a.b` and ...):
```bash
# list keys
hdfq '.a.b | keys' file.h5

# list attribute names
hdfq '.a.b | kattrs' file.h5

# list attribute key-value pairs
hdfq '.a.b | attrs' file.h5
```

Update an object's value :
```bash
hdfq '.a#version = 2' file.h5
```

Delete an object :
```bash
hdfq 'del(.obj)' file.h5
```

List object sizes (and compute total) in a group :
```bash
hdfq '.a | sizes' file.h5
```

Create a dataset :
```bash
# create a dataset from values
hdfq '.a = [1,2,3]' file.h5

# create a 10 x 10 matrix filled with ones
hdfq '.a = [1](10, 10)' file.h5

# specify the data type
hdfq '.a = [1,2,3]<float64>' file.h5

# create an empty dataset with shape (3, 4)
hdfq '.a = [](3, 4)' file.h5

# specify additional parameters of h5 datasets
hdfq '.a = [1,2,3, chunks=True, maxshape=(100, 100)]' file.h5
```
