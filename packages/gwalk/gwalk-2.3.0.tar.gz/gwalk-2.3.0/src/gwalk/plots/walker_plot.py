
def make_walker_plot(MLE_likelihood, plotdir, method, event):
    '''\
    Plot walker progress

    Inputs:
        MLE_likelihood: array of walker likelihood values
        nstep: number of steps walkers take

    '''
    ####  Imports ####
    ## Matplotlib
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    ## Public
    from os.path import join

    plt.style.use("bmh")
    fig, ax = plt.subplots()
    for i in range(MLE_likelihood.shape[0]):
        ax.plot(np.arange(MLE_likelihood.shape[1]), MLE_likelihood[i,:], 'o',markersize=2)

    savename = join(plotdir, "NAL_convergence_%s_%s.png"%(method, event))
    plt.savefig(savename)
