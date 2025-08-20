![Logo](https://raw.githubusercontent.com/martinhillebrand/tdmlplus/refs/heads/main/media/tdmlplus-logo.png)

# teradataml-plus

Python Package that extends the functionality of the popular [teradataml](https://pypi.org/project/teradataml/) package through [monkey-patching](https://en.wikipedia.org/wiki/Monkey_patch).
This is to use field-developed assets more naturally with the existing interface.

## Installation

* `pip install teradataml-plus`

## Quickstart

```python
#always import teradata-plus (tdmlplus) first
import tdmlplus

#then import teradataml. It will have all the additional functionality
import teradataml as tdml

# one additional function is for instance to get a correlation matrix straight from the DataFrame, just like in pandas

DF = tdml.DataFrame("some_table")
DF_corr = DF.corr() # not possible withot tdmlplus
```

