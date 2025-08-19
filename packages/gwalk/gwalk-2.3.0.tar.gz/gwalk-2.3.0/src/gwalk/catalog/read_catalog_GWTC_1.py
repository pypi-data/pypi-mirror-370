'''\
Read samples from GWTC-1_sample_release and convert to source frame
'''

######## Imports ########
from gwalk.catalog.coordinates import z_of_lum_dist_interp
from gwalk.catalog.coordinates import coord_labels
from basil_core.astro.coordinates import m1_m2_of_mc_eta, mc_eta_of_m1_m2
from basil_core.astro.coordinates import detector_of_source, source_of_detector
from basil_core.astro.coordinates import chieff_of_m1_m2_chi1z_chi2z
from basil_core.astro.coordinates import lambda_tilde_of_eta_lambda1_lambda2
from basil_core.astro.coordinates import delta_lambda_of_eta_lambda1_lambda2
from os.path import join, isfile
from xdata.database import Database

######## Functions ########
#### Database handling ####

def get_samples(
                fname_event,
                names,
                group = "C01:IMRPhenomPv3HM",
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
    assert db.exists(group)

    # check if data exists
    data_addr = group
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

#### Calculations ####

def generate_samples(
                     fname_event,
                     group,
                     z_bins = 100,
                    ):
    '''Generate samples from GWTC-1 catalog release
    Parameters
    ----------
    fname_event: str
        Input file name  for catalog samples
    group: str
        Input kind of samples to work with
    z_bins: int
        Input number of bins for redshift interpolation
    '''
    import numpy as np

    names = [
             "costheta_jn",
             "luminosity_distance_Mpc",
             "right_ascension",
             "declination",
             "m1_detector_frame_Msun",
             "m2_detector_frame_Msun",
             "spin1",
             "spin2",
             "costilt1",
             "costilt2",
             "lambda1",
             "lambda2",
            ]

    #### Algorithm ####
    # Generate samples
    name_dict = \
            get_samples(
                        fname_event,
                        names,
                        group=group,
                       )

    pdict = {}
    pdict["cos_tilt_1"] = name_dict["costilt1"]
    pdict["cos_tilt_2"] = name_dict["costilt2"]

    ## Find redshift
    # Load luminosity distance in Mpc
    lum_dist = np.copy(name_dict["luminosity_distance_Mpc"])
    # Find redshift
    Z = z_of_lum_dist_interp(lum_dist, nbins = z_bins)
    # Append to dictionary
    pdict["redshift"] = np.copy(Z)



    pdict["cos_theta_jn"] = name_dict["costheta_jn"]
    pdict["luminosity_distance"] = name_dict["luminosity_distance_Mpc"]
    pdict["ra"] = name_dict["right_ascension"]
    pdict["dec"] = name_dict["declination"]
    pdict["mass_1"] = name_dict["m1_detector_frame_Msun"]
    pdict["mass_2"] = name_dict["m2_detector_frame_Msun"]
    pdict["a_1"] = name_dict["spin1"]
    pdict["a_2"] = name_dict["spin2"]

    # Find source frame masses
    mc, eta = mc_eta_of_m1_m2(name_dict["m1_detector_frame_Msun"],
                               name_dict["m2_detector_frame_Msun"])
    m1_source = source_of_detector(name_dict["m1_detector_frame_Msun"], Z)
    m2_source = source_of_detector(name_dict["m2_detector_frame_Msun"], Z)
    mc_source, eta_source = mc_eta_of_m1_m2(m1_source, m2_source)
    # Find Chieff
    spin_1z = pdict["a_1"]*pdict["cos_tilt_1"]
    spin_2z = pdict["a_2"]*pdict["cos_tilt_2"]
    spin_1xy = pdict["a_1"]*np.power(1 - pdict["cos_tilt_1"]**2, 0.5)
    spin_2xy = pdict["a_2"]*np.power(1 - pdict["cos_tilt_2"]**2, 0.5)
    chieff = chieff_of_m1_m2_chi1z_chi2z(m1_source, m2_source, spin_1z, spin_2z)
    # Append to dictionary
    pdict["mass_1_source"] = m1_source
    pdict["mass_2_source"] = m2_source
    pdict["chirp_mass_source"] = mc_source
    pdict["chirp_mass"] = mc
    pdict["symmetric_mass_ratio"] = eta
    pdict["chi_eff"] = chieff
    pdict["spin_1z"] = spin_1z
    pdict["spin_2z"] = spin_2z
    pdict["spin_1xy"] = spin_1xy
    pdict["spin_2xy"] = spin_2xy
    pdict["inv_lum_dist"] = np.power(pdict["luminosity_distance"],-1.)
    pdict["total_mass"] = pdict["mass_1"] + pdict["mass_2"]
    pdict["total_mass_source"] = pdict["mass_1_source"] + pdict["mass_2_source"]
    pdict["mass_ratio"] = pdict["mass_2"]/pdict["mass_1"]

    # Try to add lambda parameters
    try:
        pdict["lambda_1"] = name_dict["lambda1"]
        pdict["lambda_2"] = name_dict["lambda2"]
        pdict["lambda_tilde"] = lambdatilde_of_eta_lam1_lam2(
                                    pdict["symmetric_mass_ratio"],
                                    pdict["lambda_1"],
                                    pdict["lambda_2"],
                                   )
        pdict["delta_lambda"] = deltalambda_of_eta_lam1_lam2(
                                    pdict["symmetric_mass_ratio"],
                                    pdict["lambda_1"],
                                    pdict["lambda_2"],
                                   )
    except:
        pass

    # Return dictionary
    return pdict
