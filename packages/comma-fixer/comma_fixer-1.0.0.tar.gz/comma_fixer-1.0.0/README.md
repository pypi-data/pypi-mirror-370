# comma-fixer
Python Library for fixing malformed csv files due to excessive commas

# Quickstart

The library can (currently) be imported like so:

```python
from comma_fixer.column import Column
from comma_fixer.schema import Schema
from comma_fixer.fixer import Fixer
```

# Problem Statement

We define a malformed CSV as a CSV where there may be rows with commas (the delimiter) have not been properly escaped, that is, there are no quotes surrounding entries that contain commas.

Given a malformed CSV file where the columns are known, we want to process the file such that the malformed rows can be pointed out, and given some form of validation, identify whether a given
token belongs to a specific column or not to parse the rows properly.

# Schema

First, we must define the Schema of the CSV file by determining the column's type and what can be inserted into the column.

## Column

Each column can be defined by the name of the column, the data type, whether it can be null, whether it can contain commas or spaces, as well as an optional RegEx formatting for string type columns.

Column Examples
```python
Column.string(name="name", is_nullable=False, has_commas=False, has_spaces=True) # Text columns
Column.numeric(name="age") # Integer columns
Column.float(name="height") # Float columns
Column.datetime(name="birthdate") # Datetime columns
```

For columns without a predefined type, i.e. String, Numeric, Float and Datetime, a custom column can be created, but will require importing the `pandas` library. This is because the library needs to create `panda.Series` for each column to be able to export the processed rows into a CSV file.

```python
import pandas as pd

Column.new(name="has_cats", data_type=bool, series_type=pd.Series(dtype=bool), is_nullable=False, has_commas=False, has_spaces=False, format=None) # For columns that don't have predefined types
```

A Schema can then be created from a list of columns **in the order of columns in the CSV file**.

```python
schema = Schema.new(columns=[
    Column.string(name="username", is_nullable=False, has_commas=False, has_spaces=False),
    Column.string(name="email", is_nullable=True, has_commas=False, has_spaces=False, format=r"[a-zA-Z0-9\.-]+@[a-z]+(\.[a-z]+)+")
    Column.numeric(name="age")
    Column.datetime(name="birthdate")
    Column.float(name="height")
])
schema.info()
```

Once a Schema is created, it can no longer be added to or editted. Any modifications will require creating a new Schema.
Schemas can be viewed with `.info()`, which will display each column's attributes as a table.

# Fixer

Schemas are required to create Fixer objects. Fixers will process the CSV file at the given filepath and return a Parsed object.

```python
fixer = Fixer.new(schema)
parsed = fixer.fix_file("/path/to/csv/file.csv")
```

The `fix_file` function will process each line at a time and determine whether there is a valid parsing such that the tokens
can be placed in a valid column.

Additional arguments can be supplied on whether to skip the first line, or to display the possible parsings of invalid rows (rows
which are unable to be parsed due to having multiple possible parses).

```python
fixer.fix_file("/path/to/csv/file.csv", skip_first_line=True, show_possible_parses=True)
```

Individual lines can also be processed, but will not be added to a Parsed object, as each Parsed object is dependent on the input file.
The possible parses can also be printed out.

```python
fixer.process_row("row,to,be,processed", show_possible_parses=True)
```


# Parsed

The Parsed object is returned as a result of running `fix_file`. Invalid entries and their line numbers can be viewed by calling
`print_invalid_entries()` on the Parsed object.

Only valid entries that have successfully been processed can be exported to a CSV file through `export_to_csv_best_effort("/path/to/write/to/file.csv")`,
that is, no entries that are shown in `print_invalid_entries()` will be in the CSV file.

```python
parsed.export_to_csv_best_effort("/path/to/processed/file.csv")
parsed.print_invalid_entries()
```

# Example Python Notebook file

An example of the library can be found [here](example.ipynb).

# How does it work?

Using the Schema, specifically, the functions which determine whether or not a token can be placed into a given column, we construct
an $n \times m$ matrix, $v$, where $n$ is the number of tokens (i.e. the number of strings after splitting the row by the delimiter ','), and
$m$ is the number of columns in the schema.

We construct it such that an entry $v_{t,c}$ is $0$ if and only if the token $t$ can be placed in column $c$, and $1$ otherwise.
Then we find the shortest path from the first token in the first column to the last token in the last column, i.e. $(0,0) \rightarrow (n,m)$.
There exists a valid parsing if and only if the cost of the path is 0.

To enforce the "no commas" constraint in a column, we don't allow movements from one token to another in the same column.

We then construct a graph out of the matrix, where edges represent the value of $v_{t,c}$ from node $(t, c)$ to either $(t+1, c+1)$ or $(t+1, c)$.

If there are multiple shortest paths found, then we fail to parse the row and the row must either be manually resolved or the schema must become more specific.
