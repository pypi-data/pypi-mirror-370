#!/usr/bin/env python3
'''\
Populate nal-figures with run figures and links
'''
import numpy
import os
from os.path import join, isfile, isdir

######## Globals ########
TOPDIR = "/home/xevra/Event_Likelihood_Approximation"
RUNDIR = join(TOPDIR, "nal-runs")
FIGDIR = join(TOPDIR, "nal-figures")

######## Copy plots ########
# Identify runs
runs = os.listdir(RUNDIR)
# Loop
for run in runs:
    # Make sure directory exists
    if not isdir(join(FIGDIR, run)):
        os.mkdir(join(FIGDIR, run))
    # Make sure images exists
    imagedir = join(FIGDIR, run, "images")
    if not isdir(imagedir):
        os.mkdir(imagedir)
    # rsync plots
    cmd = "rsync -ravz %s/* %s"%(
                                join(RUNDIR, run, "figures"),
                                imagedir
                               )
    os.system(cmd)

######## Gather information ########
# Move to the working directory 
os.chdir(FIGDIR)
# Initialize dictionaries for storing information about plots
allplots = {}
allevents = {}
allcoords = {}
allwaveforms = {}
allmethods = {}
# Loop through runs
for run in runs:
    # Initialize lists
    runplots = []
    runevents = []
    runcoords = []
    runwaveforms = []
    runmethods = []
    # Loop through plots
    for event in os.listdir(join(FIGDIR, run, "images")):
        for plot in os.listdir(join(FIGDIR, run, "images", event)):
            # Gather fname
            fname = join(RUNDIR, run, "figures", event, plot)
            runplots.append(fname)
            fields = plot.rstrip(".pdfng").rstrip("likelihood").rstrip("_").split(':')
            # Gather additional information
            runevents.append(fields[0])
            runcoords.append(fields[1])
            runwaveforms.append(fields[2])
            runmethods.append(fields[3])

    allplots[run] = runplots
    allevents[run] = runevents
    allcoords[run] = runcoords
    allwaveforms[run] = runwaveforms
    allmethods[run] = runmethods

######## Generate link structure using recursive symbolic links ########

for run in runs:
    #### Initialize directories ####
    ## sort1:
    ## coord
    ##  |_ waveform_method
    ## 
    ## sort2:
    ## coord
    ## |_ event

    # Name variables
    sort1 = "by_coord_and_waveform_method"
    sort2 = "by_coord_and_event"
    sortdir1 = join(FIGDIR, run, sort1)
    sortdir2 = join(FIGDIR, run, sort2)
    # Ensure directory exists
    if not isdir(sortdir1):
        os.mkdir(sortdir1)
    if not isdir(sortdir2):
        os.mkdir(sortdir2)
    # Loop each plot
    for i in range(len(allplots[run])):
        # Extract fields
        item = allplots[run][i].split("/")[-1]
        coord = allcoords[run][i]
        event = allevents[run][i]
        waveform = allwaveforms[run][i]
        method = allmethods[run][i]
        # check if coord directories exist
        if not isdir(join(sortdir1, coord)):
            os.mkdir(join(sortdir1, coord))
        if not isdir(join(sortdir2, coord)):
            os.mkdir(join(sortdir2, coord))
        # Ensure waveform_method directories exist
        plotdir1 = join(sortdir1, coord, "%s_%s"%(waveform, method))
        if not isdir(plotdir1):
            os.mkdir(plotdir1)
        plotdir2 = join(sortdir2, coord, event)
        if not isdir(plotdir2):
            os.mkdir(plotdir2)

        # Create a relative symbolic link to the appropriate plot
        # Sort1
        link_loc = join(run,sort1,coord,"%s_%s"%(waveform, method),item)
        if not isfile(link_loc):
            cmd = "ln -frs %s %s"%(
                                   join(run,"images",event,item),
                                   link_loc,
                                  )
            print(cmd)
            os.system(cmd)
        # Sort2
        link_loc = join(run,sort2,coord,event,item)
        if not isfile(link_loc):
            cmd = "ln -frs %s %s"%(
                                   join(run,"images",event,item),
                                   link_loc
                                  )
            print(cmd)
            os.system(cmd)




        
    

