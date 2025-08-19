#! Reorganize nal data products


######## Globals ########

RELEASE = "GWTC-3"
NALDATA = "/home/xevra/Repos/nal-data/"
OUTDATA = "/home/xevra/Projects/basil-tools/pipeline/NAL/"
APPROXIMANTS = [
                "PublicationSamples",
                "NRSur7dq4",
                "SEOBNRv4PHM",
                "SEOBNRv4P",
                "SEOBNRv3",
                "IMRPhenomXPHM",
                "IMRPhenomPv3HM",
                "IMRPhenomPv2",
                "IMRPhenomPv2NRT_highSpin",
                "IMRPhenomPv2NRT_lowSpin",
                "IMRPhenomPv2_NRTidal-HS",
                "IMRPhenomPv2_NRTidal-LS",
                "IMRPhenomNSBH",
                "IMRPhenomNSBH_HighSpin",
                "IMRPhenomNSBH_LowSpin",
               ]
COMPRESSION = "gzip"

COORD_TAGS = [
              "aligned3d_source",
              "aligned3d_dist",
             ]

FIT_METHODS = [
               "select",
              ]


######## Imports ########

import numpy as np
from gwalk.data import Database
from os.path import join, isfile

######## Initialization ########

fname_release = join(NALDATA, "%s.nal.hdf5"%RELEASE)
db_release = Database(fname_release)
fname_final = join(OUTDATA, "%s.nal.hdf5"%RELEASE)
db_final = Database(fname_final)

######## Initialize events and copy attrs ########

# Identify top level attrs
release_attrs = db_release.attr_dict(".")
# Copy top level attrs
db_final.attr_set_dict('.',release_attrs)

# Identify events
events = db_release.list_items()
# Begin event loop
for item in events:
    # Create event group
    db_final.create_group(item)
    # Load event attrs
    event_attrs = db_release.attr_dict(item)
    # Set event attrs
    db_final.attr_set_dict(item,event_attrs)
    # get labels
    all_labels = db_release.list_items(item)
    # Begin label loop
    for jtem in all_labels:
        # split label
        coord_tag, approximant, fit_method = jtem.split(":")
        # check coord tag
        if not (coord_tag in COORD_TAGS):
            continue
        # Check approximant
        if not (approximant in APPROXIMANTS):
            continue
        # Check fit method
        if not (fit_method in FIT_METHODS):
            continue
        # We have decided to keep this label
        # Initialize the group
        db_final.create_group(join(item,jtem))
        # check group attrs
        group_attrs = db_release.attr_dict(join(item,jtem))
        # Save group attrs
        db_final.attr_set_dict(join(item,jtem),group_attrs)
        # Check datasets
        dsets = db_release.list_items(join(item,jtem),kind='dset')
        # Loop the dsets
        for ktem in dsets:
            # copy each dset
            db_final.dset_set(
                              join(item,jtem,ktem),
                              db_release.dset_value(join(item,jtem,ktem)),
                              compression=COMPRESSION,
                             )
# Done!
print("Success!")
