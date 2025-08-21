#!/usr/bin/env python3
'''\
Test the Multivariate Normal object and methods
'''
######## Imports ########
from contextlib import contextmanager
from gwalk import MultivariateNormal
from gwalk.catalog import Catalog
import sys
from os.path import join, isfile, isdir
import os
import time
import numpy as np
from gwalk.catalog.coordinates import coord_tags as COORD_TAGS
from gwalk.tools.fit_catalog_samples import fit_real_event
from gwalk.tools.plot_mesh_norm_corner import plot_GW

######## Context Manager ########

@contextmanager
def custom_redirection(wkdir, logfile):
    # Check the run directory
    assert isdir(wkdir)
    # break up the logfile
    dirs = logfile.split('/')
    # Create directories
    for i in range(len(dirs)):
        if not isdir(join(wkdir,*dirs[:i])):
            os.mkdir(join(wkdir,*dirs[:i]))
    # Begin managing the context
    with open(join(wkdir,logfile),'w') as out:
        old_out = sys.stdout
        sys.stdout = out
        old_err = sys.stderr
        sys.stderr = out
        try:
            yield out
        finally:
            sys.stdout = old_out
            sys.stderr = old_err


######## Settings ########

#nal_methods = ["simple", "genetic", "select"]
nal_methods=["genetic"]
extensions = ["png", "pdf"]

# These ones are really important
convergence = "mesh_kl"
nwalk = 100
nstep = 100
evaluation_res = 100
kl_sensitivity = 1e-3
max_bins1d = 100
max_bins2d = 31
min_bins = 30

# These ones are less important
carryover = 0.05
sleep = 0

# Initialize hyperparameters
hyperparameters = {
                   "nwalk"          : nwalk,
                   "nstep"          : nstep,
                   "kl_sensitivity" : kl_sensitivity,
                   "carryover"      : carryover,
                   "convergence"    : convergence,
                  }

######## Arguments ########

wkdir = sys.argv[1]
fname_catalog = join(wkdir, "catalog_samples.hdf5")
assert isfile(fname_catalog)
fname_mesh = join(wkdir, "likelihood_mesh.hdf5")

event = sys.argv[2]
cata = Catalog(fname_catalog)
release = cata.release_of_event(event)
available_coord_tags = cata.tags_of_event(event)
fname_release = join(wkdir, "%s.nal.hdf5"%release)

######## Pipeline ########

# Delay start to reduce database lookup overlaps
sleeptime = sleep*np.random.uniform()
time.sleep(sleeptime)


# Loop the coord tags
for coord_tag in available_coord_tags:
    # Find available groups for this coord tag
    groups = cata.groups_of_event_tag(event, coord_tag)
    # Loop the groups
    for group in groups:
        # Check for singular values
        singular = False
        sample_dict = cata.load_data(event,group,COORD_TAGS[coord_tag])
        for key in sample_dict:
            if min(sample_dict[key]) == max(sample_dict[key]):
                singular = True
        if singular:
            continue
        # Update the user
        with open("nohup.out", 'a') as File:
            print(event, coord_tag, group, file=File)
        # Loop the fit methods
        for fit_method in nal_methods:
            # Identify fit log file
            fit_log = join("logs", event, "%s:%s:%s_fit.log"%(
                coord_tag, group, fit_method))
            # Open context manager
            with custom_redirection(wkdir, fit_log):
                fit_real_event(
                               fname_catalog,
                               fname_release,
                               event,
                               group,
                               coord_tag,
                               min_bins=min_bins,
                               max_bins1d=max_bins1d,
                               max_bins2d=max_bins2d,
                               evaluation_res=evaluation_res,
                               nwalk=nwalk,
                               nstep=nstep,
                               whitenoise=0.001,
                               sig_factor=0.5,
                               carryover=carryover,
                               fname_mesh=fname_mesh,
                               verbose=True,
                              )

            # Identify plot log file
            plot_log = join("logs", event, "%s:%s:%s_plot.log"%(
                coord_tag, group, fit_method))
            # Make sure there is a figures folder
            if not isdir(join(wkdir,"figures")):
                os.mkdir(join(wkdir,"figures"))
            # Make sure there is an event figures folder
            if not isdir(join(wkdir,"figures",event)):
                os.mkdir(join(wkdir,"figures",event))
            # Open context manager
            with custom_redirection(wkdir, plot_log):

                # loop extensions
                for extension in extensions:
                    # Identify plot name
                    fname_plot = join(wkdir, "figures", event, "%s:%s:%s:%s_likelihood.%s"%(
                        event, coord_tag, group, fit_method, extension))
                    # Identify labels
                    label_mesh = "%s/%s:%s"%(event,coord_tag,group)
                    label_nal = "%s/%s:%s:%s"%(event,coord_tag,group,fit_method)
                    # Generate plot
                    plot_GW(
                            fname_mesh,
                            fname_release,
                            fname_plot,
                            event,
                            coord_tag,
                            group,
                            fit_method,
                            evaluation_res=evaluation_res,
                           )

