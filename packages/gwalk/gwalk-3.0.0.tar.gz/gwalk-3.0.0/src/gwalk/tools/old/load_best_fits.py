#!/usr/bin/env python3
'''\
load_best_fits.py

Vera Del Favero

Load the best fits for each event, for specified coordinate tags
'''
######## Imports ########

#### Public Imports ####
import numpy as np
from scipy.stats import multivariate_normal
import h5py
from os.path import join, isfile, isdir

#### Local Imports ####
from gwalk.data import Database
from gwalk.coordinates import coord_tags
from gwalk import NAL
from gwalk.multivariate_normal_pdf import multivariate_normal_pdf as parallel_likelihood

######## GLOBALS ########

data_location = "/home/xevra/Repos/nal-methods-paper/data/raw/"
releases = ["GWTC-1", "GWTC-2", "GWTC-2p1", "GWTC-3"]
TEXT_OUTPUT = "/home/xevra/Repos/nal-methods-paper/data/raw"

######## Algorithms ########

def get_bestfits():
    #### Initialize Dictionaries ####
    bestgroups = {}
    bestfits = {}
    bestkl = {}
    for coords in coord_tags:
        bestfits[coords] = {}
        bestgroups[coords] = {}
        bestkl[coords] = {}

    #### Check Data ####

    for release in releases:
        # Check that the file exists
        fname_release = join(data_location, release + ".nal.hdf5")
        if not isfile(fname_release):
            raise RuntimeError("No such file as %s"%fname_release)
        # Load the database
        db_release = Database(fname_release)
        # Get a list of events
        events = db_release.list_items()
        # Loop through each event
        for event in events:
            # Identify fit labels
            labels = db_release.list_items(event)
            if len(labels) == 0:
                raise RuntimeError("No fits at all for %s"%event)
        
            #### Initialize aligned3d_source flag ####
            for coords in coord_tags:
                found = False
                best_fit = None
                best_fit_kl = None
                # Check each label
                for label in labels:
                    # Fit location in file
                    fit_addr = join(event,label)
                    # Fields
                    coord_tag, group, fit_method = label.split(':')
                    # Check coord_tag
                    if coord_tag == coords:
                        # Check kl divergence
                        try:
                            fit_kl = float(db_release.attr_value(fit_addr, "kl"))
                            found = True
                            # Check best fits while at it
                            if best_fit is None:
                                best_fit = label
                                best_fit_kl = float(fit_kl)
                            elif fit_kl < best_fit_kl:
                                best_fit = label
                                best_fit_kl = fit_kl
                        except:
                            pass
                if found:
                    # Identify best fit information from label
                    [coord_tag, group, fit_method] = best_fit.split(":")
                    Norm = NAL.load_fit(
                                        fname_release,
                                        group,
                                        event,
                                        coord_tag,
                                        fit_method,
                                       )
                    bestfits[coords][event] = Norm
                    bestgroups[coords][event] = group
                    bestkl[coords][event] = best_fit_kl
                
    return bestfits, bestgroups, bestkl

def write_tag_summary(bestfits, bestgroups, bestkl, coord_tag, outfile):
    '''\
    Write data output to file
    '''
    fit_dict = bestfits[coord_tag]
    fit_groups = bestgroups[coord_tag]
    fit_kl = bestkl[coord_tag]
    coords = coord_tags[coord_tag][:-1]
    ndim = len(coords)
    events = fit_dict.keys()
    with open(outfile, 'w') as F:
        for event in events:
            # Load physical quantities
            mean, cov = fit_dict[event].read_physical()
            # Load these other quantities
            std = np.sqrt(np.diag(cov))
            cor = fit_dict[event].guess_cor()
            # Initialize fields for line
            fields = []
            # Append event name
            fields.append(event)
            # Append group
            fields.append(fit_groups[event])
            # Append kl divergence 
            fields.append(fit_kl[event])
            # Append coordinate names
            for item in coords:
                fields.append(item)
            # Append mean
            for i in range(ndim):
                fields.append("%2.6f"%mean[i])
            # Append standard deviations
            for i in range(ndim):
                fields.append("%2.6f"%std[i])
            # Append correlation factors
            for i in range(ndim):
                for j in range(i):
                    fields.append("%2.6f"%cor[i,j])
            # Generate the line
            line = ""
            for item in fields:
                line = line + "%s, "%item
            line.rstrip(", ")
            line = line + "\n"
            F.writelines(line)

def write_all_bestfits(outdir):
    '''\
    Write all the best fits in text format
    '''
    bestfits, bestgroups, bestkl = get_bestfits()
    for coord_tag in bestfits.keys():
        outfile = join(outdir, "best_nal_fits_%s.txt"%(coord_tag))
        write_tag_summary(bestfits, bestgroups, bestkl, coord_tag, outfile)





######## Main ########

def main():
    write_all_bestfits(TEXT_OUTPUT)

######## Execution ########

if __name__ == "__main__":
    main()
