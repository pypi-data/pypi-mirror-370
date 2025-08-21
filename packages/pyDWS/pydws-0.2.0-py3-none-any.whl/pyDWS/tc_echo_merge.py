import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline

# plt.style.use('./pyDWS/plottingStyle.mplstyle')

from pyDWS.plots import plot_layout

from pyDWS.utils import generate_time_array


def tc_echo_merge(tc_icf, echo_icf, overlapN, overlap_threshold, fitP=False, savePlots=None, saveData=None):   
    """
    Function to merge and blend the two-cell and echo measurements.

    Parameters
    ----------
    tc_icf : dataframe
        two Cell data.
    echo_icf : dataframe
        echo data.
    overlapN : int
        Number of points to use from the echo to fit the second decay to get A and tau_TC. 
    overlap_threshold : float
        Permitted difference between the echo and the two-cell data set in order to merge the two. 
    fitP : bool, optional
        If fitP = True, then A, tauTC, and p are fitted in the second decay. Otherwise, only A, tauTC, and p = 2 is fixed. 
        The default is False.
    savePlots : None or string
        Default None. Otherwise the path where the graphs should be saved. 
    saveData : None or string
        Default None. Otherwise the path where the text files should be saved. 

    Returns
    -------
    All are panda dataframes
    If saveData is set, then these dataframes are saved in txt files. 
    ratioTC_E: columns t & ratio (ratio of two-cell and echo) -> ratioTC_echo.txt
    a_tauTC_p: columns A & tauTC (and p if fitted) second decay fitting parameters -> a_tauTC_p.txt
    tc_icf_overlap: columns t & icf (corrected two-cell data) -> tc_corrected.txt
    echo_icf_corrected: columns t & icf (corrected echo data) -> echo_corrected.txt
    sortedCombined: columns t & icf (merged two-cell and echo without adjusted time spacing) -> tc_echo_merged.txt
    tc_echo_mergeInt: columns t & icf (merged two-cell and echo with adjusted time spacing) -> tc_echo_merged_Interpolation.txt
    
    
    """
    
    # =============================================================================
    # two cell data 
    # =============================================================================
    # interpolate two cell data 
    tc_icf_int = CubicSpline(tc_icf.iloc[:, 0], tc_icf.iloc[:, 1])
    
    # genarate log spaced x data
    startE = np.log10(min(tc_icf.iloc[:, 0]))
    endE = np.log10(round(max(tc_icf.iloc[:, 0])))
    # endE = -1
    xval = np.logspace(startE, endE, 1000)
    # print(xval)

    
    # normalize the interpolation 
    norm_factor = tc_icf.iloc[0, 1]
    def interPolationNorm(x):
        return tc_icf_int(x) / norm_factor
    
    
    tc_icfNorm = tc_icf.iloc[:, 1] / norm_factor
    tc_icf_Int_Norm = interPolationNorm(xval)
    
    
    # plto interpolation 
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    # normalized
    # ax.plot(tc_icf.iloc[:, 0], tc_icf.iloc[:, 1] / norm_factor, 'o', label='two cell measurement')
    # ax.plot(xval, interPolationNorm(xval), '-', label='interpolation', color='red')
    
    ax.plot(tc_icf.iloc[:, 0], tc_icf.iloc[:, 1], 'o', label='two cell measurement')
    ax.plot(xval, tc_icf_int(xval), '-', label='interpolation', color='red')
    
    plt.legend()
    plot_layout(fig, ax, True, False, 'Lag time t (s)', 'ICF')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'twoCell_Interpolation.png'))


    # =============================================================================
    # Echo with overlap
    # =============================================================================
    # plot echo with overlap 
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(echo_icf.iloc[:, 0], echo_icf.loc[:, 'area'] , 'o', label='echo measurement')
    # ax.plot(echo_icf.iloc[:, 0], echo_icf.loc[:, 'ICF'] , 'o', label='echo measurement')
    ax.plot(echo_icf.iloc[:overlapN, 0], echo_icf.iloc[:overlapN, 4], 'o', color='None', markeredgecolor='red')
    

    plt.legend()
    plot_layout(fig, ax, True, False, 'Lag time t (s)', 'ICF')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'echo_Overlap.png'))


    # =============================================================================
    # Mercing two cell echo
    # =============================================================================

    # ratio calculation normalized
    # ratioTC_E = pd.DataFrame({'t': echo_icf.iloc[:overlapN, 0], 'ratio': interPolationNorm(echo_icf.iloc[:overlapN, 0]) / echo_icf.iloc[:overlapN, 4]})
    
    # ratio calculation 
    ratioTC_E = pd.DataFrame({'t': echo_icf.iloc[:overlapN, 0], 'ratio': tc_icf_int(echo_icf.iloc[:overlapN, 0]) / echo_icf.iloc[:overlapN, 4]})
   
       
    
    # fitting of the parameters A and tau_TC or also p
    if fitP == True:
        popt, pcov = curve_fit(_secondDecay_p, ratioTC_E['t'], ratioTC_E['ratio'], p0=(200000, 0.1, 2))
    else:
        # popt, pcov = curve_fit(_secondDecay, ratioTC_E['t'], ratioTC_E['ratio'], p0=(0.1, 0.1))
        popt, pcov = curve_fit(_secondDecay, ratioTC_E['t'], ratioTC_E['ratio'], p0=(200000, 0.1))

    

    # plot of fitting A and tau_TC 
    xratio = np.linspace(echo_icf.iloc[0, 0], echo_icf.iloc[overlapN-1, 0], 100)

    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(ratioTC_E['t'], ratioTC_E['ratio'] , 'o')
    if fitP == True:
        ax.plot(xratio, _secondDecay_p(xratio, popt[0], popt[1], popt[2]), '-', color='red')
        
    else:
        ax.plot(xratio, _secondDecay(xratio, popt[0], popt[1]), '-', color='red')
    
    plot_layout(fig, ax, False, False, 'Lag time t (s)', r'$\frac{g_2^{TC}(t)-1}{g_2^{Echo}(t)-1}$')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'second_Decay_fit.png'))


    # Correcting two cell data 
    if fitP == True:
        correctFactor_TC = np.exp((tc_icf.iloc[:, 0] / popt[1])**popt[2])
    else:
        correctFactor_TC = np.exp((tc_icf.iloc[:, 0] / popt[1])**2)
    
    
    # normalized
    # tc_icf_corrected = pd.DataFrame({'t': tc_icf.iloc[:, 0], 'icf': (tc_icf.iloc[:, 1] * correctFactor_TC) / tc_icf.iloc[0, 1]})
    # unnormalized
    tc_icf_corrected = pd.DataFrame({'t': tc_icf.iloc[:, 0], 'icf': ((tc_icf.iloc[:, 1]) * correctFactor_TC)})
    
    
    # removing all inf values
    tc_icf_corrected = tc_icf_corrected[np.isfinite(tc_icf_corrected).all(1)]
    
    
    # calculate interpolation of corrected two cell data
    # tc_icf_corrected_int = CubicSpline(tc_icf_corrected.iloc[:, 0], tc_icf_corrected.iloc[:, 1])

    # Correction echo data
    echo_icf_corrected = pd.DataFrame({'t': echo_icf.iloc[:, 0], 'icf': echo_icf.iloc[:, 4] * popt[0]})
    
    
    echo_icf_corrected = echo_icf_corrected[1:]
    
    echo_icf_corrected_int = CubicSpline(echo_icf_corrected.iloc[:, 0], echo_icf_corrected.iloc[:, 1])
    
    # connecting two cell data and echo data into single dataset
    # echo_overlap = echo_icf_corrected[abs(echo_icf_corrected.loc[:, 'icf'] - tc_icf_corrected_int(echo_icf_corrected.loc[:, 't'])) < overlap_threshold]
    
    echo_icf = echo_icf[1:]
    
    condition = (
    ((tc_icf_corrected['t'] > echo_icf.iloc[0, 0]) & 
     (abs(tc_icf_corrected['icf'] - echo_icf_corrected_int(tc_icf_corrected['t'])) < overlap_threshold))
    | (tc_icf_corrected['t'] <= echo_icf.iloc[0, 0])
    )

    echo_overlap = tc_icf_corrected[condition]

    plotEchoOverlap = echo_overlap[echo_overlap['t'] >= echo_icf.iloc[0, 0]]

    # Plot corrected two-cell & Echo and the overlap region 
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(tc_icf_corrected['t'], tc_icf_corrected['icf'] , 'o', label='two cell')
    ax.plot(echo_icf_corrected['t'], echo_icf_corrected['icf'] , 'o', label='echo')
    ax.plot(plotEchoOverlap['t'], plotEchoOverlap['icf'] , '--', label='overlap')
    plt.legend()
    plot_layout(fig, ax, True, False, 'Lag time t (s)', r'ICF')
    ax.set_ylim(0, 1)
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'tc_echo_corrected.png'))


   
    tc_icf_overlap = echo_overlap


    combined = pd.concat([tc_icf_overlap, echo_icf_corrected])

    sortedCombined = combined.sort_values(by=['t'])

    # Plot merged two-cell & echo
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(tc_icf_overlap['t'], tc_icf_overlap['icf'] , 'o', label='two cell')
    ax.plot(echo_icf_corrected['t'], echo_icf_corrected['icf'] , 'o', label='echo')
    ax.plot(sortedCombined['t'], sortedCombined['icf'] , '--', label='merged')
    plt.legend()
    plot_layout(fig, ax, True, False, 'Lag time t (s)', r'ICF')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'tc_echo_merged.png'))
        
        
    # Interpolating tc - echo merge to have same time spacing as for the two-cell measurement
    sortedCombined_InterP = CubicSpline(sortedCombined.iloc[:, 0], sortedCombined.iloc[:, 1])
    tN = generate_time_array()    
    tc_echo_mergeInt = pd.DataFrame({'t':tN, 'icf':sortedCombined_InterP(tN)})
    
    
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(sortedCombined['t'], sortedCombined['icf'] , 'o', label='merged')
    ax.plot(tc_echo_mergeInt['t'], tc_echo_mergeInt['icf'] , '-', label='Interpolation')
    plt.legend()
    plot_layout(fig, ax, True, False, 'Lag time t (s)', r'ICF')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'tc_echo_merged.png'))
    
    # fitting parameters save as a pandas Dataframe
    if fitP == True:
        a_tauTC_p = pd.DataFrame({'A':[popt[0]], 'tauTC':[popt[1]], 'p':[popt[2]]})
    else:
        a_tauTC_p = pd.DataFrame({'A':[popt[0]], 'tauTC':[popt[1]]})
    
    # =============================================================================
    # saving data
    # =============================================================================
    if saveData != None:
        sortedCombined.to_csv(os.path.join(saveData, 'tc_echo_merged.txt'), sep='\t', index=False)
        tc_icf_overlap.to_csv(os.path.join(saveData, 'tc_corrected.txt'), sep='\t', index=False)
        echo_icf_corrected.to_csv(os.path.join(saveData, 'echo_corrected.txt'), sep='\t', index=False)
        tc_echo_mergeInt.to_csv(os.path.join(saveData, 'tc_echo_merged_Interpolation.txt'), sep='\t', index=False)
        ratioTC_E.to_csv(os.path.join(saveData, 'ratioTC_echo.txt'), sep='\t', index=False)
        a_tauTC_p.to_csv(os.path.join(saveData, 'a_tauTC_p.txt'), sep='\t', index=False)
        
    # return sortedCombined.reset_index(drop=True)
    return ratioTC_E, a_tauTC_p, tc_icf_overlap, echo_icf_corrected, sortedCombined.reset_index(drop=True), tc_echo_mergeInt.reset_index(drop=True)
    





# =============================================================================
# Private functions
# =============================================================================
# second decay fit function 
def _secondDecay(t, A, tauTC):
    """
    Second deay function from which A and tauTC can be extracted
    Parameters
    ----------
    t : Dataframe
        lag time t .
    A : float
        Prefactor.
    tauTC : float
        decay time.

    Returns
    -------
    Second deay function.

    """
    return A * np.exp(-(t / tauTC)**2)


def _secondDecay_p(t, A, tauTC, p):
    """
    Second deay function from which A and tauTC can be extracted.
    Parameters
    ----------
    t : TYPE
        DESCRIPTION.
    A : TYPE
        DESCRIPTION.
    tauTC : TYPE
        DESCRIPTION.
    p : float, optional
        If the fluctuation become noticable, p can be fitted (adjustable parameter). The default is 2.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return A * np.exp(-(t / tauTC)**p)







