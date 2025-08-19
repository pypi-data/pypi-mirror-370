#!/usr/bin/env python3
'''\
Build gwalk-friendly catalog database for samples from the GWTC catalogs

build_catalog.py

'''
######## Imports ########
from gwalk.catalog import Catalog
import sys

######## Arguments ########
print(sys.argv)
if len(sys.argv) == 4:
    # Name of the catalog file
    fname_db =      sys.argv[1]
    # Name of GW release
    release =       sys.argv[2]
    # Location of GWXXXXXX.h5 files from catalog release
    release_dir =   sys.argv[3]

    # Initialize catalog
    cata = Catalog(fname_db)
    # Build release
    cata.build_catalog(release, release_dir)

elif (len(sys.argv) == 3) and (sys.argv[2] == "clean"):
    # Name of the catalog file
    fname_db =      sys.argv[1]
    # Create a new database
    cata = Catalog(fname_db, clean=True)

else:
    raise RuntimeError("Usage: python3 build_catalog.py [fname_db] [release] [release directory]")

