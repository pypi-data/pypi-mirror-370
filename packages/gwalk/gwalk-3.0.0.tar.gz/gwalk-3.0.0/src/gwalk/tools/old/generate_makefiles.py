#!/usr/bin/env python3
'''\
Generate makefiles
'''

######## Globals ########

RUN_ID = int("0001")
RUN_DIR = '/home/xevra/Event_Likelihood_Approximation/nal-runs/run_%s'%(str(RUN_ID).zfill(4))
RUN_DIR_0 = '/home/xevra/Event_Likelihood_Approximation/nal-runs/run_0000'
MAKE_DIR = '/home/xevra/Event_Likelihood_Approximation/gwalk/tools/NAL_makefiles'
#MAKE_GWALK = '/home/xevra/Event_Likelihood_Approximation/gwalk/tools/make_gwalk.py'
MAKE_GWALK = 'make_gwalk.py'
#METHODS = ["simple", "genetic", "select"]

COORD_TAG_RUNS = []
COORD_TAG_RUNS.append("aligned3d")
COORD_TAG_RUNS.append("aligned3d_source")
COORD_TAG_RUNS.append("aligned3d_dist")
COORD_TAG_RUNS.append("mass_tides")
COORD_TAG_RUNS.append("mass_tides_source")
COORD_TAG_RUNS.append("aligned_tides")
COORD_TAG_RUNS.append("aligned_tides_source")
COORD_TAG_RUNS.append("aligned_tides_dist")
COORD_TAG_RUNS.append("spin6d")
COORD_TAG_RUNS.append("precessing8d")
COORD_TAG_RUNS.append("precessing8d_source")
COORD_TAG_RUNS.append("precessing8d_dist")
COORD_TAG_RUNS.append("precessing_tides_source")
COORD_TAG_RUNS.append("full_precessing_tides")


######## Imports ########
import numpy as np
import os
from os.path import join, isfile, isdir
import sys
from contextlib import contextmanager
from gwalk import NAL
from gwalk.grid import Grid
from gwalk.catalog import Catalog
from gwalk.catalog import EVENTS
from gwalk.coordinates import coord_tags as COORD_TAGS

######## Initialize ########

# Name the database
fname_cata = join(RUN_DIR_0, "catalog_samples.hdf5")
# Build a fresh catalog
cata = Catalog(fname_cata)

######## Gather Release Waveforms ########

# Initialize waveforms
Events = {}
Fields = {}

for release in EVENTS:
    # Identify release
    groups = cata.groups_of_release(release)
    for group in groups:
        Events[group] = cata.events_of_group(group)
        Fields[group] = cata.fields_of_group(group)

######## Generate Makefiles ########

for group in Events:

    #### Setup General Lines ####
    # Replace escape characters
    events = Events[group]
    fields = Fields[group]
    coord_tags = cata.tags_of_group(group)
    group = group.replace(":","\:")
    # Generate file name
    fname_group = join(MAKE_DIR, "make_%s.mk"%(group))
    # Initialize lines
    lines = []
    lines.append("all:\n")
    lines.append("RUN_ID = %s\n"%(str(RUN_ID).zfill(4)))
    lines.append("RUN_DIR = %s\n"%(RUN_DIR))
    # generate event line
    event_line = "%s = "%(group)
    #if len(Events[group]) == 1:
    #    event_line = event_line + "%s None "%(event)
    #else:
    for event in events:
        event_line = event_line + "%s "%(event)
    event_line = event_line + '\n'
    lines.append(event_line)
    # generate Initialize lines
    build = "build:\n" + \
        "\trm -rf  ${HOME}/.local/lib/python*/site-packages/gwalk* \n" +\
	    "\tpip3 install --user ${HOME}/Event_Likelihood_Approximation/gwalk\n"
    lines.append(build)
    run_dir_job = "$(RUN_DIR)/catalog_samples.hdf5: build\n" +\
        "\tpython3 %s $(RUN_ID) initialize\n"%MAKE_GWALK +\
        "\tmkdir -p $(RUN_DIR)/logs\n" +\
        "\tmkdir -p $(RUN_DIR)/figures\n"
    lines.append(run_dir_job)
    initialize = "initialize: $(RUN_DIR)/catalog_samples.hdf5 build\n" +\
        '\techo "Successfully build gwalk and found run_dir"\n'
    lines.append(initialize)

    #### Generate Coord Tags ####
    # Check aligned3d
    if not COORD_TAG_RUNS[0] in coord_tags:
        print(fields)
        raise RuntimeError("Cannot produce aligned3d for %s"%group)

    # Identify prerequisites
    prereq = []
    for tag in coord_tags:
        # Skip bad tags
        if not tag in COORD_TAG_RUNS:
            continue
        # Initialize tag line
        tag_lines = []

        # Fit simple job
        line = r"%." + "%s_%s_fit_simple: "%(tag,group)
        if tag == COORD_TAG_RUNS[0]:
            line = line + "initialize\n"

        else:
            for item in prereq:
                line = line + "\\\n\t\t%." + "%s_%s_plot_select "%(item,group)
            line = line + '\n'
        tag_lines.append(line)
        tag_lines.append("\tpython3 %s %d fit-simple $(basename $@) %s %s\n"%(
                                            MAKE_GWALK, RUN_ID, group, tag))
        # Plot simple job
        tag_lines.append(
            "%." + "%s_%s_plot_simple: "%   (tag,group) +\
            "%." + "%s_%s_fit_simple\n"%    (tag,group)
                        )
        tag_lines.append("\tpython3 %s %d plot-simple $(basename $@) %s %s\n"%(
                                            MAKE_GWALK, RUN_ID, group, tag))
        # Fit genetic job
        tag_lines.append(
            "%." + "%s_%s_fit_genetic: "%   (tag,group) +\
            "%." + "%s_%s_plot_simple \n"%  (tag,group)
                        )
        tag_lines.append("\tpython3 %s %d fit-genetic $(basename $@) %s %s\n"%(
                                            MAKE_GWALK, RUN_ID, group, tag))
        # Plot genetic job
        tag_lines.append(
            "%." + "%s_%s_plot_genetic: "%  (tag,group) +\
            "%." + "%s_%s_fit_genetic \n"%  (tag,group)
                        )
        tag_lines.append("\tpython3 %s %d plot-genetic $(basename $@) %s %s\n"%(
                                            MAKE_GWALK, RUN_ID, group, tag))
        # Fit select job
        tag_lines.append(
            "%." + "%s_%s_fit_select: "%   (tag,group) +\
            "%." + "%s_%s_plot_genetic \n"%  (tag,group)
                        )
        tag_lines.append("\tpython3 %s %d fit-select $(basename $@) %s %s\n"%(
                                            MAKE_GWALK, RUN_ID, group, tag))
        # Plot genetic job
        tag_lines.append(
            "%." + "%s_%s_plot_select: "%  (tag,group) +\
            "%." + "%s_%s_fit_select \n"%  (tag,group)
                        )
        tag_lines.append("\tpython3 %s %d plot-select $(basename $@) %s %s\n"%(
                                            MAKE_GWALK, RUN_ID, group, tag))
        
        # Append tag lines
        for item in tag_lines:
            lines.append(item)
        tag_lines = []
        prereq.append(tag)
    
    # Define All
    lines.append("all: $(%s)\n"%group)
    # Define group
    lines.append("$(%s)"%group + ": %: %." + "%s_%s_plot_select\n"%(prereq[-1],group))

    with open(fname_group, 'w') as F:
        F.writelines(lines)

