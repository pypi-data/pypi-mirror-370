#!/usr/bin/env python3
'''\
generate plots on a living axis
'''
from .percentile_levels import percentile_levels

######## Axis Plot Methods ########
#### 1 Dimensional Plots ####

def histogram_1d(
                 ax,
                 x,
                 w = None,
                 xmin = None,
                 xmax = None,
                 log_scale = False,
                 log_offset = 1e-4,
                 bins = 100,
                 **kwargs
                ):
    '''\
    Quickly make a histogram of some samples
    '''
    import numpy as np
    
    # Update limits
    if xmin is None:
        xmin = np.min(x)
    if xmax is None:
        xmax = np.max(x)

    # Make histogram
    rho, xedge = \
            np.histogram(
                         x,
                         weights = w,
                         range = [xmin, xmax],
                         bins = bins,
                        )

    #rho = rho / np.sum(rho)
    dx = (xmax - xmin)/bins
    rho = rho / np.sum(rho*dx)

    # log scale
    if log_scale:
        # Check min val
        min_val = np.min(rho[rho > 0.])
        # Implement log scale
        rho = np.log(rho + log_offset*min_val)

    # Show data
    ax.plot(np.linspace(xmin, xmax, bins), rho, **kwargs)
    ax.set_xlim([xmin, xmax])
    return ax




#### 2 Dimensional Plots ####

def scatter_2d(
               ax,
               x,
               y,
               pt = 5,
               w = None,
               xmin = None,
               xmax = None,
               ymin = None,
               ymax = None,
               **kwargs
              ):
    '''\
    Quickly plot samples in a scatter plot
    '''
    import numpy as np
    
    # Update limits
    if xmin is None:
        xmin = np.min(x)
    if xmax is None:
        xmax = np.max(x)
    if ymin is None:
        ymin = np.min(y)
    if ymax is None:
        ymax = np.max(y)

    if w is None:
        colors = 'r'
    else:
        colors = w
    
    # plot samples
    ax.scatter(x, y, c = colors, s = pt, edgecolors = 'k', linewidths = 0.2)
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])

def histogram_2d(
                 ax,
                 x,
                 y,
                 w = None,
                 xmin = None,
                 xmax = None,
                 ymin = None,
                 ymax = None,
                 log_scale = False,
                 log_offset = 1e-4,
                 cmap = 'terrain_r',
                 bins = 100,
                ):
    '''\
    Quickly make a histogram of some samples
    '''
    import numpy as np
    
    # Update limits
    if xmin is None:
        xmin = np.min(x)
    if xmax is None:
        xmax = np.max(x)
    if ymin is None:
        ymin = np.min(y)
    if ymax is None:
        ymax = np.max(y)

    # Make histogram
    rho, xedge, yedge = \
            np.histogram2d(
                           x, y,
                           weights = w,
                           range = [[xmin, xmax], [ymin, ymax]],
                           bins = bins,
                          )

    # log scale
    if log_scale:
        # Check min val
        min_val = np.min(rho[rho > 0.])
        # Implement log scale
        rho = np.log(rho + log_offset*min_val)

    # Show data
    im = ax.imshow(
              np.rot90(rho),
              extent = [xmin, xmax, ymin, ymax],
              aspect = 'auto',
              cmap = cmap,
             )

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    return im
                     

def density_contour_2d(
                       ax,
                       x,
                       y,
                       w = None,
                       xmin = None,
                       xmax = None,
                       ymin = None,
                       ymax = None,
                        cmap = 'magma',
                       bins = 100,
                       levels = [0.25, 0.5, 0.75],
                       **kwargs
                      ):
    '''\
    Plot density contours
    '''
    import numpy as np
    from scipy.stats import gaussian_kde
    
    # Update limits
    if xmin is None:
        xmin = np.min(x)
    if xmax is None:
        xmax = np.max(x)
    if ymin is None:
        ymin = np.min(y)
    if ymax is None:
        ymax = np.max(y)

    # Generate inputs
    xspace = np.linspace(xmin, xmax, bins)
    yspace = np.linspace(ymin, ymax, bins)
    xgrid, ygrid = np.meshgrid(xspace, yspace)

    # Stack inputs
    rv_input = np.stack((xgrid.flatten(), ygrid.flatten()))

    # fit kde
    K = gaussian_kde(np.asarray([x,y]), weights = w)
    rho = K.pdf(rv_input).reshape((bins, bins)).T

    # Get values
    #rho, xedge, yedge = \
    #        np.histogram2d(
    #                       x, y,
    #                       weights = w,
    #                       range = [[xmin, xmax], [ymin, ymax]],
    #                       bins = bins,
    #                      )
    rho[~np.isfinite(rho)] = 0.0
    rho = rho /np.sum(rho)

    # Generate contour levels
    levels = percentile_levels(xgrid, ygrid, rho, levels)

    # Plot contours
    ax.contour(
               xspace,
               yspace,
               rho.T,
               levels = levels,
               cmap = cmap,
               vmin = 0.,
               vmax = np.max(rho),
               **kwargs
              )
    
    # Set limits
    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
                    
def gaussian_pdf_2d(
                    ax,
                    x,
                    y,
                    w = None,
                    xmin = None,
                    xmax = None,
                    ymin = None,
                    ymax = None,
                    log_scale = False,
                    log_offset = 1e-4,
                    cmap = 'terrain_r',
                    bins = 100,
                    approx = None,
                   ):
    '''\
    Quickly make a histogram of some samples
    '''
    import numpy as np
    # Complain about Gaussian
    if approx is None:
        raise Exception("Gaussian parameters unknown to plotting function")
    
    # Update limits
    if xmin is None:
        xmin = np.min(x)
    if xmax is None:
        xmax = np.max(x)
    if ymin is None:
        ymin = np.min(y)
    if ymax is None:
        ymax = np.max(y)

    # Reorganize samples
    samples = [x, y]
    limits = [[xmin, xmax], [ymin, ymax]]

    # Generate inputs
    xspace = np.linspace(xmin, xmax, bins)
    yspace = np.linspace(ymin, ymax, bins)
    xgrid, ygrid = np.meshgrid(xspace, yspace)

    # Stack inputs
    rv_input = np.stack((xgrid, ygrid)).T
    
    # Get values
    pdf = approx.pdf(rv_input)
    pdf[~np.isfinite(pdf)] = 0.0

    # log scale
    if log_scale:
        # Check min val
        min_val = np.min(pdf[pdf > 0.])
        #max_val = np.max(pdf[pdf > 0.])
        # Implement log scale
        pdf = np.log(pdf + log_offset*min_val)

    # Show data
    ax.imshow(
              np.rot90(pdf),
              extent = [xmin, xmax, ymin, ymax],
              aspect = 'auto',
              cmap = cmap,
             )
    

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
                     
