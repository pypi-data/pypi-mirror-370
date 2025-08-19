#! usr/env/bin python3
''' Plot a normal model against a mesh

long description
'''

######## script ########

def plot_mesh_norm_corner(
                          fname_mesh,
                          fname_nal,
                          fname_plot,
                          label_mesh,
                          label_nal,
                          title=None,
                          sample_labels=None,
                          scale=2,
                          linewidth_scale=4.,
                          coordinate_labels=None,
                          **kwargs
                         ):
    ''' Plot a normal model against a mesh

    Parameters
    ----------
    fname_mesh: str
        Input file locations for mesh
    fname_nal: str
        Input file locations for nal
    fname_plot: str
        Input file location for plot
    label_mesh: str
        Input label for mesh
    label_nal: str
        Input label for nal
    title: str, optional
        Input title of plot
    sample_labels: list, optional
        Input legend labels for mesh and nal
    scale: float, optional
        Input width compared to PRD standard
    '''
    from gwalk.density.mesh import Mesh
    from gwalk.bounded_multivariate_normal import MultivariateNormal
    from gwalk.plots.likelihood_corner import corner_cross_sample_normal
    # load mesh
    mesh = Mesh.load(fname_mesh,label_mesh)
    # Load normal
    MV = MultivariateNormal.load(fname_nal,label_nal)
    if not coordinate_labels is None:
        for i in range(len(coordinate_labels)):
            MV._parameters["mu_%d"%i].label = coordinate_labels[i]
    # Generate the plot
    corner_cross_sample_normal(
                               fname_plot,
                               MV,
                               mesh,
                               title=title,
                               sample_labels=sample_labels,
                               scale=scale,
                               linewidth_scale=linewidth_scale,
                               **kwargs
                              )

def plot_GW(
            fname_mesh,
            fname_nal,
            fname_plot,
            event,
            coord_tag,
            group,
            fit_method,
            **kwargs
           ):
    '''Standardize some of the plot arguments
    Parameters
    ----------
    fname_mesh: str
        Input file locations for mesh
    fname_nal: str
        Input file locations for nal
    fname_plot: str
        Input file location for plot
    event: str
        Input GW event name
    coord_tag: str
        Input coordinate tag for fit
    group: str
        Input approximate for fit
    fit_method: str
        Input method of fit
    '''
    from gwalk.catalog.coordinates import coord_tags, coord_labels
    coordinate_labels = []
    for coord in coord_tags[coord_tag][:-1]:
        coordinate_labels.append(coord_labels[coord])
    plot_mesh_norm_corner(
                          fname_mesh,
                          fname_nal,
                          fname_plot,
                          "%s/%s:%s"%(event,coord_tag,group),
                          "%s/%s:%s:%s"%(event,coord_tag,group,fit_method),
                          title=event,
                          sample_labels=["Catalog Samples","NAL"],
                          coordinate_labels=coordinate_labels,
                          **kwargs
                         )

######### Main ########

######## Execution ########
if __name__ == "__main__":
    import sys
    from os.path import join
    if len(sys.argv) > 1:
        fname_mesh, fname_nal, fname_plot, event, coord_tag, group, fit_method = sys.argv[1:8]
    else:
        event = "GW190425"
        release = "GWTC-2"
        coord_tag = "full_precessing_tides"
        group = "IMRPhenomPv2_NRTidal-LS"
        #group = "PublicationSamples"
        extension="png"
        fit_method = "select"
        run = "/home/xevra/Event_Likelihood_Approximation/nal-runs/run_0002"
        fname_mesh = join(run, "likelihood_mesh.hdf5")
        fname_nal = join(run, "%s.nal.hdf5"%release)
        fname_plot = join(run,"figures",event,"%s:%s:%s:%s_likelihood.%s"%(
            event,coord_tag,group,fit_method,extension))
        scale=16.
        rot_xlabel=True
        tight=True
        legend_loc=[0.58,0.7]
        #legend_loc=[0.45,0.68]

    plot_GW(
            fname_mesh,
            fname_nal,
            fname_plot,
            event,
            coord_tag,
            group,
            fit_method,
            scale=scale,
            rot_xlabel=rot_xlabel,
            tight=tight,
            legend_loc=legend_loc
           )
