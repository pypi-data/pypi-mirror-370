#!/home/xevra/.local/bin/python3
'''Reformulate package catalog samples'''

######## Imports ########
import numpy as np
import os
from os.path import join, isdir, isfile
from xdata.database import Database
from gwalk.catalog.coordinates import coord_tags as COORD_TAGS
from gwalk.catalog.coordinates import coord_labels as COORD_LABELS
from gwalk.catalog.coordinates import q_of_mc_eta
from gwalk.catalog.prior.prior_methods import prior_mc_eta as prior_mass
from gwalk.catalog.prior.prior_methods import prior_dist
from gwalk.catalog.prior.callister_prior import chi_effective_prior_of_aligned_spins as chi_eff_aligned_prior
from gwalk.catalog.prior.prior_methods import prior_full_spin


######## Globals ########


EVENTS = {
          "GWTC-1" : [
                      "GW150914",
                      "GW151012",
                      "GW151226",
                      "GW170104",
                      "GW170608",
                      "GW170729",
                      "GW170809",
                      "GW170814",
                      "GW170817",
                      "GW170818",
                      "GW170823",
                     ],
            "GWTC-2" : [
                        'GW190408_181802',
                        'GW190412',
                        'GW190413_052954',
                        'GW190413_134308',
                        'GW190421_213856',
                        'GW190424_180648',
                        'GW190425',
                        'GW190426_152155',
                        'GW190503_185404',
                        'GW190512_180714',
                        'GW190513_205428',
                        'GW190514_065416',
                        'GW190517_055101',
                        'GW190519_153544',
                        'GW190521_074359',
                        'GW190521',
                        'GW190527_092055',
                        'GW190602_175927',
                        'GW190620_030421',
                        'GW190630_185205',
                        'GW190701_203306',
                        'GW190706_222641',
                        'GW190707_093326',
                        'GW190708_232457',
                        'GW190719_215514',
                        'GW190720_000836',
                        'GW190727_060333',
                        'GW190728_064510',
                        'GW190731_140936',
                        'GW190803_022701',
                        'GW190814',
                        'GW190828_063405',
                        'GW190828_065509',
                        'GW190909_114149',
                        'GW190910_112807',
                        'GW190915_235702',
                        'GW190924_021846',
                        'GW190929_012149',
                        'GW190930_133541',
                       ],
            "GWTC-2p1" : [
                          "GW190403_051519",
                          "GW190426_190642",
                          "GW190725_174728",
                          "GW190805_211137",
                          "GW190916_200658",
                          "GW190917_114630",
                          "GW190925_232845",
                          "GW190926_050336",
                         ],
            "GWTC-3" : [
                        "GW191103_012549",
                        "GW191105_143521",
                        "GW191109_010717",
                        "GW191113_071753",
                        "GW191126_115259",
                        "GW191127_050227",
                        "GW191129_134029",
                        "GW191204_110529",
                        "GW191204_171526",
                        "GW191215_223052",
                        "GW191216_213338",
                        "GW191219_163120",
                        "GW191222_033537",
                        "GW191230_180458",
                        "GW200105_162426",
                        "GW200112_155838",
                        "GW200115_042309",
                        "GW200128_022011",
                        "GW200129_065458",
                        "GW200202_154313",
                        "GW200208_130117",
                        "GW200208_222617",
                        "GW200209_085452",
                        "GW200210_092255",
                        "GW200216_220804",
                        "GW200219_094415",
                        "GW200220_061928",
                        "GW200220_124850",
                        "GW200224_222234",
                        "GW200225_060421",
                        "GW200302_015811",
                        "GW200306_093714",
                        "GW200308_173609",
                        "GW200311_115853",
                        "GW200316_215756",
                        "GW200322_091133",
                       ],
        }

EXTENSION = {
             "GWTC-1"   : "_GWTC-1.hdf5",
             "GWTC-2"   : ".h5",
             "GWTC-2p1" : ".h5",
             "GWTC-3"   : ".h5",
            }

GROUP_ALIAS = {
               "IMRPhenomPv2_posterior"                     : "IMRPhenomPv2",
               "SEOBNRv3_posterior"                         : "SEOBNRv3",
               "Overall_posterior"                          : "Overall",
               "IMRPhenomPv2NRT_highSpin_posterior"         : "IMRPhenomPv2NRT_highSpin",
               "IMRPhenomPv2NRT_lowSpin_posterior"          : "IMRPhenomPv2NRT_lowSpin",
               "C01:IMRPhenomD"                             : "IMRPhenomD",
               "C01:IMRPhenomPv2"                           : "IMRPhenomPv2",
               "C01:SEOBNRv4P"                              : "SEOBNRv4P",
               "C01:SEOBNRv4PHM"                            : "SEOBNRv4PHM",
               "C01:IMRPhenomHM"                            : "IMRPhenomHM",
               "C01:IMRPhenomPv3HM"                         : "IMRPhenomPv3HM",
               "C01:SEOBNRv4HM_ROM"                         : "SEOBNRv4HM_ROM",
               "C01:SEOBNRv4_ROM"                           : "SEOBNRv4_ROM",
               "C01:NRSur7dq4"                              : "NRSur7dq4",
               "C01:SEOBNRv4P_nonevol"                      : "SEOBNRv4P_nonevol",
               "C01:IMRPhenomD_NRTidal-HS"                  : "IMRPhenomD_NRTidal-HS",
               "C01:IMRPhenomD_NRTidal-LS"                  : "IMRPhenomD_NRTidal-LS",
               "C01:IMRPhenomPv2_NRTidal-HS"                : "IMRPhenomPv2_NRTidal-HS",
               "C01:IMRPhenomPv2_NRTidal-LS"                : "IMRPhenomPv2_NRTidal-LS",
               "C01:SEOBNRv4T_surrogate_HS"                 : "SEOBNRv4T_surrogate_HS",
               "C01:SEOBNRv4T_surrogate_LS"                 : "SEOBNRv4T_surrogate_LS",
               "C01:SEOBNRv4T_surrogate_highspin_RIFT"      : "SEOBNRv4T_surrogate_highspin_RIFT",
               "C01:SEOBNRv4T_surrogate_lowspin_RIFT"       : "SEOBNRv4T_surrogate_lowspin_RIFT",
               "C01:TEOBResumS-HS"                          : "TEOBResumS-HS",
               "C01:TEOBResumS-LS"                          : "TEOBResumS-LS",
               "C01:TaylorF2-HS"                            : "TaylorF2-HS",
               "C01:TaylorF2-LS"                            : "TaylorF2-LS",
               "C01:IMRPhenomNSBH"                          : "IMRPhenomNSBH",
               "C01:TaylorF2"                               : "TaylorF2",
               "C01:SEOBNRv4P_RIFT"                         : "SEOBNRv4P_RIFT",
               "C01:IMRPhenomXPHM"                          : "IMRPhenomXPHM",
               "C01:Mixed"                                  : "Mixed",
               "C01:IMRPhenomNSBH:HighSpin"                 : "IMRPhenomNSBH_HighSpin",
               "C01:IMRPhenomNSBH:LowSpin"                  : "IMRPhenomNSBH_LowSpin",
               "C01:IMRPhenomXPHM:HighSpin"                 : "IMRPhenomXPHM_HighSpin",
               "C01:IMRPhenomXPHM:LowSpin"                  : "IMRPhenomXPHM_LowSpin",
               "C01:Mixed:NSBH:HighSpin"                    : "Mixed_NSBH_HighSpin",
               "C01:Mixed:NSBH:LowSpin"                     : "Mixed_NSBH_LowSpin",
               "C01:SEOBNRv4_ROM_NRTidalv2_NSBH"            : "SEOBNRv4_ROM_NRTidalv2_NSBH",
               "C01:SEOBNRv4_ROM_NRTidalv2_NSBH:HighSpin"   : "SEOBNRv4_ROM_NRTidalv2_NSBH_HighSpin",
               "C01:SEOBNRv4_ROM_NRTidalv2_NSBH:LowSpin"    : "SEOBNRv4_ROM_NRTidalv2_NSBH_LowSpin",
              }

######## Functions ########

#### Read Samples ####

def event_groups(fname_event):
    '''find all the groups for an event in a catalog file
    Parameters
    ----------
    fname_event: str
        Input the file location for posterior samples
    '''
    # Check that the database exists
    assert isfile(fname_event)
    # Open it up
    db = Database(fname_event)
    # Initialize the list of groups
    groups = []
    # Loop through each group
    for item in db.list_items('.'):
        if db.kind(item) == 'group':
            # Check if there are posterior samples for that group
            if "posterior_samples" in db.list_items(item,kind='dset'):
                # if there are, it's safe to say it's a waveform
                groups.append(item)
        elif item.endswith("posterior"):
            groups.append(item)
    return groups

def load_GWTC_1_event_samples(fname_event, group):
    ''' Load GWTC_1 Event samples 
    Parameters
    ----------
    fname_event: str
        Input the file location for posterior samples
    group: str
        Input the label for the waveform model posterior samples
    '''
    from .read_catalog_GWTC_1 import generate_samples
    # Generate samples
    pdict = generate_samples(fname_event, group)
    return pdict

def load_GWTC_2_event_samples(fname_event, group):
    ''' Load GWTC_2 Event samples 
    Parameters
    ----------
    fname_event: str
        Input the file location for posterior samples
    group: str
        Input the label for the waveform model posterior samples
    '''
    from .read_catalog_GWTC_2 import generate_samples
    # Generate samples
    pdict = generate_samples(fname_event, group)
    return pdict

def load_GWTC_2p1_event_samples(fname_event, group):
    ''' Load GWTC_3 Event samples 
    Parameters
    ----------
    fname_event: str
        Input the file location for posterior samples
    group: str
        Input the label for the waveform model posterior samples
    '''
    from .read_catalog_GWTC_2p1 import generate_samples
    # Generate samples
    pdict = generate_samples(fname_event, group)
    return pdict

def load_GWTC_3_event_samples(fname_event, group):
    ''' Load GWTC_3 Event samples 
    Parameters
    ----------
    fname_event: str
        Input the file location for posterior samples
    group: str
        Input the label for the waveform model posterior samples
    '''
    from .read_catalog_GWTC_3 import generate_samples
    # Generate samples
    pdict = generate_samples(fname_event, group)
    return pdict

def load_event_samples(release, fname_event, group):
    '''Load Release Samples 
    Parameters
    ----------
    release: str
        Input the release associated with the event
    fname_event: str
        Input the file location for posterior samples
    group: str
        Input the label for the waveform model posterior samples
    '''
    # Generate samples
    if release == "o3a":
        pdict = load_o3a_event_samples(fname_event, group)
    elif release == "GWTC-1":
        pdict = load_GWTC_1_event_samples(fname_event, group)
    elif release == "GWTC-2":
        pdict = load_GWTC_2_event_samples(fname_event, group)
    elif release == "GWTC-2p1":
        pdict = load_GWTC_2p1_event_samples(fname_event, group)
    elif release == "GWTC-3":
        pdict = load_GWTC_3_event_samples(fname_event, group)
    else:
        raise ValueError("Unknown sample release")
    return pdict



######## CATALOG Object ########

class Catalog(object):
    '''Handle pointers to the catalog database file'''
    def __init__(
                 self,
                 fname,
                 clean=False,
                ):
        '''Initialize catalog object
        Parameters
        ----------
        fname: str
            Input name of catalog file
        clean: bool
            Delete the database and make a new one?
        '''
        self.fname = fname
        if clean and isfile(fname):
            os.system("rm %s"%fname)
        self.db = Database(fname,sleep=0)

    def events_of_release(self, release):
        '''Return events associated with a given release
        Parameters
        ----------
        release: str
            Input A label for a Gravitational-Wave Tranient Catalog
        '''
        return EVENTS[release]

    def events_of_group(self, group):
        '''Return a list of all the events which have a particular group
        Parameters
        ----------
        group: str
            Input waveform identifier
        '''
        events = []
        for release in EVENTS:
            for event in EVENTS[release]:
                if group in self.groups_of_event(event):
                    events.append(event)
        return events

    def release_of_event(self, event):
        '''Return the release associated with an event
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        '''
        for release in EVENTS:
            if event in EVENTS[release]:
                return release

    def release_of_group(self, group):
        '''Return the release associated with a group
        Parameters
        ----------
        group: str
            Input waveform identifier
        '''
        releases = []
        for release in EVENTS:
            for event in EVENTS[release]:
                if group in self.groups_of_event(event):
                    releases.append(release)
        return releases

    def groups_of_event(self, event):
        '''Return the groups associated with an event
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        '''
        release = self.release_of_event(event)
        event_addr = join(release, event)
        return self.db.list_items(event_addr, kind='group')

    def groups_of_release(self, release):
        '''Return the groups associated with release events
        Parameters
        ----------
        release: str
            Input A label for a Gravitational-Wave Tranient Catalog
        '''
        groups = []
        events = self.events_of_release(release)
        for event in events:
            for item in self.groups_of_event(event):
                if not item in groups:
                    groups.append(item)
        return groups

    def fields_of_group(self, group, mode='any'):
        '''Return a list of the fields available for a group
        Parameters
        ----------
        group: str
            Input waveform identifier
        mode: str
            Input 'any' or 'all'
        '''
        fields = []
        events = self.events_of_group(group)
        for event in events:
            for field in self.fields_of_event_group(event,group):
                if not field in fields:
                    fields.append(field)
        if mode == "any":
            return fields
        elif mode == "all":
            common = []
            for field in fields:
                has_field = True
                for event in events:
                    if not field in self.fields_of_event_group(event,group):
                        has_field = False
                if has_field:
                    common.append(field)
            return common
        else:
            raise RuntimeError("Unknown mode: %s"%mode)

    def fields_of_event_group(self, event, group):
        '''Return a list of the fields available for a group
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        group: str
            Input waveform identifier
        '''
        release = self.release_of_event(event)
        group_addr = join(release, event, group)
        return self.db.list_items(group_addr)

    def tags_of_event_group(self, event, group):
        '''
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        group: str
            Input waveform identifier
        '''
        fields = self.fields_of_event_group(event, group)
        tags = []
        for tag in COORD_TAGS:
            has_tag = True
            for item in COORD_TAGS[tag]:
                if not (item in fields):
                    has_tag = False
            if has_tag:
                tags.append(tag)

        return tags

    def tags_of_event(self, event):
        '''
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        '''
        groups = self.groups_of_event(event)
        tags = []
        for item in groups:
            group_tags = self.tags_of_event_group(event, item)
            for jtem in group_tags:
                if not jtem in tags:
                    tags.append(jtem)
        return tags

    def groups_of_event_tag(self, event, coord_tag):
        '''
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        coord_tag: str
            Input label for set of coordinates
        '''
        groups = []
        for item in self.groups_of_event(event):
            if coord_tag in self.tags_of_event_group(event, item):
                groups.append(item)
        return groups

                
    def tags_of_group(self, group):
        '''
        Parameters
        ----------
        group: str
            Input waveform identifier
        '''
        fields = self.fields_of_group(group,mode='all')
        tags = []
        for tag in COORD_TAGS:
            has_tag = True
            for item in COORD_TAGS[tag]:
                if not (item in fields):
                    has_tag = False
            if has_tag:
                tags.append(tag)

        return tags

                
    def group_has_tides(self, event, group):
        '''check if a group has tidal parameters
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        group: str
            Input waveform identifier
        '''
        # Identify the release
        release = self.release_of_event(event)
        # Find the address for the group
        group_addr = join(release, event, group)
        # Check for lambda1
        datasets = self.db.list_items(group_addr)
        if "lambda_1" in datasets:
            return True
        else:
            return False

    def event_has_tides(self, event):
        '''check if an event has tidal parameters
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        '''
        # Get groups for event
        groups = self.groups_of_event(event)
        # Initialize truth value
        tides = False
        # Loop through each group
        for group in groups:
            if self.group_has_tides(event, group):
                tides = True
        return tides

    def all_tidal_events(self):
        '''Find all the tidal events
        Parameters
        ----------
        '''
        # Initialize list of tidal events
        tidal_events = []
        # Loop through each release
        for release in EVENTS:
            # Loop through each event
            for event in EVENTS[release]:
                if self.event_has_tides(event):
                    tidal_events.append(event)
        # Print update to user
        print("All tides events: ", tidal_events)

    def group_has_full_spin(self, event, group):
        '''Check if a group has full spin parameters for its posterior
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        group: str
            Input waveform identifier
        '''
        # Identify the release
        release = self.release_of_event(event)
        # Find the address for the group
        group_addr = join(release, event, group)
        # Check for spin
        datasets = self.db.list_items(group_addr)
        if "spin_x" in datasets:
            return True
        else:
            return False

    def event_has_full_spin(self, event):
        '''check if an event has tidal parameters
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        '''
        # Get groups for event
        groups = self.groups_of_event(event)
        # Initialize truth value
        full_spin = False
        # Loop through each group
        for group in groups:
            if self.group_has_full_spin(event, group):
                full_spin = True
        return full_spin

    def full_spin_groups(self, event):
        '''Return a list of groups for an event which have full spin
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        '''
        # Initialize list
        group_list = []
        # Loop through groups
        groups = self.groups_of_event(event)
        for group in groups:
            if self.group_has_full_spin(event, group):
                group_list.append(group)
        # Return groups
        return group_list

    def load_data(
                  self,
                  event,
                  group,
                  names
                 ):
        '''Read data from a group for a waveform
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        group: str
            Input waveform identifier
        names: list
            Input names of coordinates
        '''
        # Identify the release
        release = self.release_of_event(event)
        # Find the address for the group
        group_addr = join(release, event, group)
        # Initialize the dictionary
        pdict = {}
        # Loop through each name
        for item in names:
            # Load data
            pdict[item] = self.db.dset_value(join(group_addr, item))
        return pdict

    def group_status(
                     self,
                     event,
                     group,
                     names
                    ):
        '''Check if the group is ready for analysis
        Parameters
        ----------
        event: str
            Input the GW tag for an event in the GWTC
        group: str
            Input waveform identifier
        names: list
            Input names of coordinates
        '''
        # Identify the release
        release = self.release_of_event(event)
        # Find the address for the group
        group_addr = join(release, event, group)
        # Initialize the dictionary
        pdict = {}
        # Loop through each name
        ready = True
        for item in names:
            ready = ready and self.db.exists(join(group_addr, item))
        return ready
    
    def build_prior(
                    self,
                    release,
                    event,
                    group,
                    compression='gzip',
                    spin_max = 1.,
                    mc_min_hard=0.0,
                    mc_max_hard=100.,
                    eta_min_hard=1e-6,
                    eta_max_hard=0.25,
                   ):
        '''Build the prior functions
        Parameters
        ----------
        release: str
            Input the release associated with the event
        event: str
            Input the GW tag for an event in the GWTC
        group: str
            Input waveform identifier
        compression: str, optional
            Input compression level for database
        spin_max: float, optional
            Input maximum allowed spin
        mc_min_hard: float
            Input minimum value for mc
        mc_max_hard: float
            Input maximum value for mc
        eta_min_hard: float
            Input minimum value for eta
        eta_max_hard: float
            Input maximum value for eta
        '''
        # Find the group we are interested in
        group_addr = join(release,event,group)
        # Load coordinates
        mc =        self.db.dset_value(join(group_addr, "chirp_mass"))
        eta =       self.db.dset_value(join(group_addr, "symmetric_mass_ratio"))
        lum_dist =  self.db.dset_value(join(group_addr, "luminosity_distance"))
        chieff =    self.db.dset_value(join(group_addr, "chi_eff"))
        z =         self.db.dset_value(join(group_addr, "redshift"))
        q =         self.db.dset_value(join(group_addr, "mass_ratio"))
        # Compute priors
        mass_prior = prior_mass(
                                mc, eta,
                                mc_min=mc_min_hard, mc_max=mc_max_hard,
                                eta_min=eta_min_hard,eta_max=eta_max_hard, 
                               )
        chieff_aligned_prior = chi_eff_aligned_prior(q, spin_max, chieff)
        aligned_3d_prior = mass_prior*chieff_aligned_prior
        dist_prior = prior_dist(lum_dist)
        aligned_3d_dist_prior = dist_prior*aligned_3d_prior
        # Save priors
        self.db.dset_set(join(group_addr, "prior_mass"), mass_prior, compression=compression)
        self.db.dset_set(join(group_addr, "prior_chi_eff_aligned"), chieff_aligned_prior, compression=compression)
        self.db.dset_set(join(group_addr, "prior_aligned3d"), aligned_3d_prior, compression=compression)
        self.db.dset_set(join(group_addr, "prior_aligned3d_dist"), aligned_3d_dist_prior, compression=compression)
        # Precessing components
        try:
            chi1x = self.db.dset_value(join(group_addr, "spin_1x"))
            chi1y = self.db.dset_value(join(group_addr, "spin_1y"))
            chi1z = self.db.dset_value(join(group_addr, "spin_1z"))
            chi2x = self.db.dset_value(join(group_addr, "spin_2x"))
            chi2y = self.db.dset_value(join(group_addr, "spin_2y"))
            chi2z = self.db.dset_value(join(group_addr, "spin_2z"))
            spin_prior = prior_full_spin(chi1x, chi2x, chi1y, chi2y, chi1z, chi2z)
            precessing8d_prior = mass_prior*spin_prior
            precessing8d_dist_prior = precessing8d_prior*dist_prior
            self.db.dset_set(join(group_addr, "prior_precessing8d"), 
                    precessing8d_prior,compression=compression)
            self.db.dset_set(join(group_addr, "prior_precessing8d_dist"),
                    precessing8d_dist_prior,compression=compression)
        except:
            pass

    def build_catalog(
                      self,
                      release,
                      catalog_directory,
                      compression='gzip',
                      **kwargs
                     ):
        '''build a catalog database
        Parameters
        ----------
        release: str
            Input the release associated with the event
        catalog_directory: str
            Input path to GWXXXXXX.h5 zenodo files
        compression: str, optional
            Input compression level for database
        '''
        print("Building new catalog!")
        # Initialize the release in the database
        if not self.db.exists(release, kind='group'):
            self.db.create_group(release)
        ## Event loop ##
        for event in EVENTS[release]:
            # Identify the event address
            event_addr = join(release, event)
            # Initialize the event in the datanase
            if not self.db.exists(event_addr, kind='group'):
                self.db.create_group(event_addr)
            # Find the event in the catalog directory
            fname_event = join(catalog_directory, event) + EXTENSION[release]
            assert isfile(fname_event)
            # Find the groups in a catalog for a particular event
            groups = event_groups(fname_event)
            # Loop through each group
            for group in groups:
                if group in GROUP_ALIAS:
                    print("alias %s %s"%(group, GROUP_ALIAS[group]))
                    alias = GROUP_ALIAS[group]
                else:
                    print("No alias %s"%(group))
                    alias = group
                # Group address
                group_addr = join(release,event,alias)
                # Initialize the group in the datanase
                if not self.db.exists(group_addr, kind='group'):
                    self.db.create_group(group_addr)
                print("Reading posterior for %s %s"%(event, group))
                # Find the posterior samples in the catalog
                pdict = load_event_samples(release, fname_event, group)
                # Save catalog samples
                for item in pdict:
                    # save the dataset
                    if not self.db.exists(join(group_addr,item), kind='dset'):
                        self.db.dset_set(join(group_addr,item),pdict[item],compression=compression)
                    
                ## Compute the prior ##
                self.build_prior(release,event,alias,compression=compression,**kwargs)
    
