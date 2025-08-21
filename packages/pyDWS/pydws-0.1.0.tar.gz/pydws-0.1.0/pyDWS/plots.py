import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator



# =============================================================================
# Standard Layout of the functions 
# ============================================================================= 
def plot_layout(fig, ax, logX, logY, xlabel, ylabel, title=None):
    """
    Function to set the layout of the plots

    Parameters
    ----------
    fig : figure variable
    ax : axis variable
    logX : True or False
        plot in log or not.
    logY : True or False
        plot in log or not.
    xlabel : string
        label of x axis.
    ylabel : string
        label of y axis .
    title : string
        Ttitle of the plot.

    Returns
    -------
    None.

    """
    
    # set title
    if title != None:
        ax.set_title(title, loc='right', fontsize=15)
    
    
    # log scale of the Plot
    if logY == True:
        ax.set_yscale('log')
        # plt.yscale('log')
    if logX == True:
        ax.set_xscale('log')
        # plt.xscale('log')
    
    

    # On both the X and Y axes, the start and end point of the axis is an integer or power      
    data_xlim = ax.dataLim.x0, ax.dataLim.x1
    data_ylim = ax.dataLim.y0, ax.dataLim.y1
    
    padding_x = 0.02 * (data_xlim[1] - data_xlim[0])
    padding_y = 0.02 * (data_ylim[1] - data_ylim[0])
    
            
    if data_xlim[0] - padding_x < 0:
        xmin = 10**np.floor(np.log10(data_xlim[0]))
        ax.set_xlim(xmin, data_xlim[1] + padding_x)
    else:    
        ax.set_xlim(data_xlim[0] - padding_x, data_xlim[1] + padding_x)
    
    if logY == True:
        if data_ylim[0] - padding_y < 0:
            ymin = 10**np.floor(np.log10(data_ylim[0]))
            ax.set_ylim(ymin, data_ylim[1] + padding_y)
        else:    
            ax.set_ylim(data_ylim[0] - padding_y, data_ylim[1] + padding_y)
    else:
        ax.set_ylim(data_ylim[0] - padding_y, data_ylim[1] + padding_y)
    
        
    # Set major ticks to be at edges
    if logX == False and logY == False:
        ax.xaxis.set_major_locator(MaxNLocator(nbins='auto', steps=[1, 2, 5, 10], prune=None))
        ax.yaxis.set_major_locator(MaxNLocator(nbins='auto', steps=[1, 2, 5, 10], prune=None))
    
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # tight layout = everthing of of the plot must be insede the Figure
    fig.tight_layout()

    
    # saving graph
    # if savePath[1] != None:
    #     plt.savefig(os.path.join(savePath[1], 'echo_peak_' + str(savePath[0])+'.png'), transparent=True)





