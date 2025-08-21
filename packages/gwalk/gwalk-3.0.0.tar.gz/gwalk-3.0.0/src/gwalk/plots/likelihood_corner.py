#!/home/xevra/.local/bin/python3
'''\
Generate the likelihood function of each event
'''

######## Imports ########
from os.path import join, isfile, isdir
import os
import numpy as np
from .percentile_levels import percentile_levels
from ..utils.multivariate_normal import multivariate_normal_marginal1d
from ..utils.multivariate_normal import multivariate_normal_marginal2d

######## Plot Tools ########

def likelihood_1d(
                  ax,
                  Norm,
                  mesh,
                  index,
                  labels,
                  **kwargs
                 ):
    '''\
    make a 1d pdf for an ND gaussian
    
    Inputs:
        ax:     A plot axis
        Norm:   A MultivariateNormal object from basil.fit.models
        ind:    The index of the dimension we are plotting
        limits: The soft limits (that describe our distribution)
        bins:   The number of bins used on the associated histogram
    '''

    # Initialize limits
    xlims = mesh.limits[index]
    # Initialize dimensionality
    ndim = mesh.ndim

    # Generate x_test and y_test
    y_mesh, L_mesh = mesh.fetch_1d_evaluations(index)

    # Generate y_norm
    L_norm = multivariate_normal_marginal1d(
            Norm.check_sample(Norm.read_guess()),
            y_mesh,
            index,
            scale=Norm.scale,
           )

    # Normalize L_norm
    L_norm /= np.sum(L_norm)

    y_mesh = y_mesh.flatten()
    L_norm = L_norm.flatten()

    # Plot marginalized pdf of Normal object
    ax.plot(y_mesh, L_mesh, label = labels[0], **kwargs)
    ax.plot(y_mesh, L_norm, label = labels[1], **kwargs)
    ax.set_xlim(xlims)

def likelihood_2d(
                  ax,
                  Norm,
                  mesh,
                  index, jndex,
                  cmap = 'magma',
                  levels = [0.25, 0.5, 0.75],
                  **kwargs
                 ):
    '''\
    Plot some Gaussian contours!
    '''
    #from scipy.signal import convolve
    
    # Update limits
    xlims, ylims = mesh.limits[jndex], mesh.limits[index]
    # Initialize dimensionality
    ndim = mesh.ndim
    # Find 2d Evaluations 
    y_mesh, L_mesh = mesh.fetch_2d_evaluations(index, jndex)
    # Find L_norm
    L_norm = multivariate_normal_marginal2d(
            Norm.check_sample(Norm.read_guess()),
            y_mesh,
            index, jndex,
            scale=Norm.scale,
           )
    # Normalize L_norm
    L_norm /= np.sum(L_norm)
    # Recall resolution
    res = mesh.evaluation_res

    # Identify xgrid and ygrid
    x_grid = y_mesh[:,1].reshape((res,res))
    y_grid = y_mesh[:,0].reshape((res,res))
    # Identify xspace and yspace
    x_space = x_grid[0,:]
    y_space = y_grid[:,0]
    # Reshape outputs
    L_mesh = L_mesh.reshape((res,res))
    L_norm = L_norm.reshape((res,res))

    # Generate contour levels for catalog
    levels_mesh = percentile_levels(x_grid, y_grid, L_mesh, levels)

    # Generate contour levels for normal
    levels_norm = percentile_levels(x_grid, y_grid, L_norm, levels)

    # Plot contours for catalog
    ax.contour(
               x_space,
               y_space,
               L_mesh,
               levels = levels_mesh,
               cmap = cmap,
               vmin = 0.,
               vmax = np.max(L_mesh),
               linestyles = 'solid',
               **kwargs
              )
       
    # Plot contours for normal
    ax.contour(
               x_space,
               y_space,
               L_norm,
               levels = levels_norm,
               cmap = cmap,
               vmin = 0.,
               vmax = np.max(L_norm),
               linestyles = 'dotted',
               **kwargs
              )
       
    # Set limits
    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    
                     

######## Plots ########

#### Corner Plots ####

def corner_cross_sample_normal(
                               savename,
                               Norm,
                               mesh,
                               levels = [0.25, 0.5, 0.75],
                               title=None,
                               evaluation_res=100,
                               sample_labels=[None,None],
                               scale=1.,
                               rot_xlabel=False,
                               tight=False,
                               legend_loc=[0.45,0.68],
                               linewidth_scale=1.,
                              ):
    '''\
    Generate a corner plot for posterior/likelihood samples with model

    Inputs:
        title: title for plot
        bins: histogram/pdf bins
    '''
    #### Imports ####
    # Matplotlib 
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    # Public

    #### Initialize Environment ####

    # Find the dimensionality
    ndim = mesh.ndim

    # Load data
    mesh.generate_evaluation_set(evaluation_res)

    # Initialize style
    plt.style.use('bmh')
    ## Initialize axes
    fig, axes = plt.subplots(
                             nrows = ndim,
                             ncols = ndim,
                             figsize = (3.375*scale,3.375*scale),
                             sharex = 'col',
                            )

    # Initialize ticks
    all_ticks = []

    #### 1-d plots ####
    for i in range(ndim):
        ## axes[i,i] ##
        # Here, we want to plot a 1-d histogram of the posterior samples
        # alongside a histogram of the reweighted likelihood samples resampled
        # from our gaussian
        axes[i,i].tick_params(axis='both',which='both',labelsize=6*scale)
        if rot_xlabel:
            axes[i,i].tick_params(axis='x',which='both',labelrotation=90,pad=0)
        if i == 0:
            labels = sample_labels
        else:
            labels = np.empty_like(sample_labels,dtype=object)
            for j in range(len(labels)):
                labels[j] = None
        
        # Make the appropriate plots
        likelihood_1d(
                      axes[i,i],
                      Norm,
                      mesh,
                      i,
                      labels,
                      linewidth=1.0*linewidth_scale,
                     )

        # Remove yticklabels
        axes[i,i].set_yticklabels([])
        # Append ticks
        all_ticks.append(axes[i,i].get_xticks())
        # Handle axis labels
        axes[-1,i].set_xlabel(Norm._parameters["mu_%d"%i].label,size=10*scale)

    #### 2-d plots ####
    for i in range(ndim):
        for j in range(i):
            # Remove unwanted plot
            axes[j,i].remove()

            ## axes[i,j] ##
            # Here we want a 2D histogram of the posterior samples alongside 
            # The reweighted likelihood samples resampled from our gaussian
            ax = axes[i,j]
            ax.tick_params(axis='both',which='both',labelsize=6*scale)
            if rot_xlabel:
                ax.tick_params(axis='x',which='both',labelrotation=90,pad=0)
    
            # Make the appropriate plots
            likelihood_2d(
                          ax,
                          Norm,
                          mesh,
                          i,
                          j,
                          linewidths = 1.5*linewidth_scale,
                         )

            if j != 0:
                # Remove yticklabels
                ax.set_yticklabels([])

    # Fill the legend for the contours
    axes[0,0].plot(
                   [], [], 
                   color = 'gray', 
                   linestyle = 'solid',
                   label = sample_labels[0],
                  )
    axes[0,0].plot(
                   [], [], 
                   color = 'gray', 
                   linestyle = 'dotted',
                   label = sample_labels[1],
                  )

    # Make 2D legend
    fig.legend(loc=legend_loc, prop={"size":8*scale})
    ## Wrapping up
    if not (title is None):
        fig.suptitle(title, fontsize = float(12*scale))
    if tight:
        plt.tight_layout()

    # Make sure there's a place to store the figures #
    plt.savefig(savename)
    plt.close()
