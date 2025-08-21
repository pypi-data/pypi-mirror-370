# Licensed under a 3-clause BSD style license - see LICENSE.txt

"""
IO Interface for Writing CDF Data in Python.

cdfwriter is a Python package developed at Southwest Research Institute
that aims to provide a simple and efficient solution to generating CDF files.

It uses a high level Object-Oriented interface method that allows for
the definition of a common set of CDF files that are similar.

Exported Modules and Sub-packages
---------------------------------
Uses spacepy.pycdf to write a common set of CDFs.
"""

# For egg_info test builds to pass, put package imports here.

from .interface import (CDFWriter)

