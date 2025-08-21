#!/home/xevra/.local/bin/python3
'''\
Generate the likelihood function of each event
'''

######## Imports ########
import numpy as np
from gwalk.catalog.coordinates import coord_labels
from basil_core.astro.coordinates import m1_m2_of_mc_eta, mc_eta_of_m1_m2
from basil_core.astro.coordinates import detector_of_source, source_of_detector
from basil_core.astro.coordinates import chieff_of_m1_m2_chi1z_chi2z
from basil_core.astro.coordinates import lambda_tilde_of_eta_lambda1_lambda2
from basil_core.astro.coordinates import delta_lambda_of_eta_lambda1_lambda2
from xdata.database import Database
from os.path import join, isfile

######## Functions ########
#### Database handling ####
def get_samples(
                fname_event,
                names,
                group = "PublicationSamples",
               ):
    '''Get the posterior samples we need
    Parameters
    ----------
    fname_event: str
        Input file name  for catalog samples
    names: list
        Input list of names to draw from catalog samples
    group: str
        Input kind of samples to work with
    '''

    # Check if file exists
    assert isfile(fname_event)

    # Initialize database
    db = Database(fname_event)
    # Check if group exists
    assert db.exists(group, kind="group")

    # check if data exists
    data_addr = join(group, "posterior_samples")
    assert db.exists(data_addr, kind="dset")

    # Get the fields
    fields = db.dset_fields(data_addr)

    # Create a dictionary
    pdict = {}
    
    # Load each item
    for item in names:
        # Make sure the item is correct
        if item in fields:
            # append values
            pdict[item] = db.dset_value(data_addr, field=item)

    return pdict

######## Algorithm ########

def generate_samples(fname_event, group, **kwargs):
    ''' A wrapper for finding the sample values that we need
    Parameters
    ----------
    fname_event: str
        Input file name  for catalog samples
    group: str
        Input kind of samples to work with
    '''

    names = list(coord_labels.keys())

    pdict = \
            get_samples(
                        fname_event,
                        names,
                        group=group,
                       )

    # Generate some things not given
    pdict["inv_lum_dist"] = np.power(pdict["luminosity_distance"],-1.)

    # Check on spin coordinates
    if not "chi_eff" in pdict:
        pdict["chi_eff"] = chieff_of_m1_m2_chi1z_chi2z(
                                                pdict["mass_1_source"],
                                                pdict["mass_2_source"],
                                                pdict["a_1"],
                                                pdict["a_2"],
                                               )
    # Check aligned spin
    if not "spin_1z" in pdict:
        pdict["spin_1z"] = pdict["a_1"]*pdict["cos_tilt_1"]
    if not "spin_2z" in pdict:
        pdict["spin_2z"] = pdict["a_2"]*pdict["cos_tilt_2"]

    # check planar spin
    pdict["spin_1xy"] = pdict["a_1"]*np.power(1 - pdict["cos_tilt_1"]**2, 0.5)
    pdict["spin_2xy"] = pdict["a_2"]*np.power(1 - pdict["cos_tilt_2"]**2, 0.5)

    return pdict
