import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from scipy.signal import butter, lfilter
from scipy.interpolate import CubicSpline
from scipy.stats import pearsonr
import statsmodels.api as sm
from cmath import sqrt

# plt.style.use('./pyDWS/plottingStyle.mplstyle')

from pyDWS.plots import plot_layout




def microrheology(msdData, temperatur, freq_range, gau, radi, zPath=None, savePlots=None):
    """
    Calculation of the complex modulus based on:
    T. G. Mason, Estimating the viscoelastic moduli of complex fluids using the generalized stokes–einstein equation, Rheologica acta 39, 371 (2000).
    

    Curve Smoothing with lowess:
    Seabold, Skipper, and Josef Perktold. “statsmodels: Econometric and statistical modeling with python.” Proceedings of the 9th Python in Science Conference. 2010.
    

    Parameters
    ----------
    msdData : pandas Dataframe
        First column contains t and second column msd.
    temperatur : float
        temperatur at which measurement was performed.
    freq_range : list
        frequency range of the moduli.
    gau : tuple
        If len(gau) == 2, then a low-pass filter is applied to the derivative values. The first value corresponds to the order of the filter, and the second to the critical frequency.
        Else there is no filtering. 
    radi : float
        radius of the particles in the sample.
    zPath : string, optional
        Path to save the microrheology data. The default is None.

    Returns
    -------
    pdZ : pandas dataframe
    
    if filtering is performed:
        columns:
            ome: angular frequency
            zstar: Z*
            zpr: Z'
            zppr: Z''
            zstarFi: Z* with applied filter
            zprFi: Z' with applied filter
            zpprFi: Z'' with applied filter
            zprS: Z' with applied filter and with applied smoothing
            zpprS: Z'' with applied filter and with applied smoothing
            zC: complex Z* 
            
    else:
        columns:
            ome: angular frequency
            zstar: Z*
            zpr: Z'
            zppr: Z''
            zC: complex Z* 

    """
    
    
    if freq_range is not None:
        low = freq_range[0]
        high = freq_range[1]
        cmsd = msdData[(msdData.iloc[:, 0] >= 1 / high) & (msdData.iloc[:, 0] <= 1 / low)]


    cmsd = cmsd.to_numpy()
    # print(cmsd)
    
    ox = cmsd[:, 0]
    oy = cmsd[:, 1]
     
    
    x = np.log(ox)
    y = np.log(oy)
    
    dx = np.diff(x)
    dy = np.diff(y)
    
    slp = dy / dx
    xc = (x[:-1] + x[1:]) / 2
    
    # interpolation of the derivatives
    interp_func = CubicSpline(xc, slp, extrapolate=True)
    deriv = interp_func(x)
   
    
    
    ome = 1. / ox # angular frequency
    kB = 1.38064852e-23
    
    # smoothing 
    if isinstance(gau, (list, tuple)) and len(gau) == 2:
        print('Smoothing using Butterworth Lowpass Filter...')
        derivFi = butter_low_pass(deriv, gau[0], gau[1])
    
        
        # calculate  Z* Z' and Z'' with filtered derivatives
        gamaFi = 0.457 * (1 + derivFi)**2 - 1.36 * (1 + derivFi) + 1.90
        zstarFi = kB * temperatur / (np.pi * radi * oy * gamaFi)
        angFi = np.pi * derivFi / 2
        zprFi = zstarFi * np.cos(angFi)
        zpprFi = zstarFi * np.sin(angFi)
    
    
        # calculate  Z* Z' and Z'' without filtering
        gama = 0.457 * (1 + deriv)**2 - 1.36 * (1 + deriv) + 1.90
        zstar = kB * temperatur / (np.pi * radi * oy * gama)
        ang = np.pi * deriv / 2
        zpr = zstar * np.cos(ang)
        zppr = zstar * np.sin(ang)
    
        
        # Plot MSD
        fig, ax = plt.subplots(figsize=(6.4,4.8))
        ax.plot(ox, oy, 'ob')
        plot_layout(fig, ax, True, True, r'Lag time t (s)', r'MSD')
        
        
        
        # Plot Z* Z' and Z'' without filtering and filtering
        fig, ax = plt.subplots(figsize=(6.4,4.8))
        ax.plot(ome, zstar, '-k', linewidth=3, label=r"$ G* (\omega) $")
        ax.plot(ome, zpr, 'ob', label=r"$ G' (\omega) $")
        ax.plot(ome, zppr, 'or', label=r"$ G'' (\omega) $")
        
        ax.plot(ome, zstarFi, '-', linewidth=3, label=r"$ G* (\omega) $ filtered", color='gray')
        ax.plot(ome, zprFi, '--', linewidth=2, label=r"$ G' (\omega) $ filtered", color='gray')
        ax.plot(ome, zpprFi, '-.', linewidth=2, label=r"$ G'' (\omega) $ filtered", color='gray')
        
        ax.legend()
        plot_layout(fig, ax, True, True, r'Angular frequency $\omega$ (rad/s)', r'Modulus (Pa)')
        if savePlots != None:
            plt.savefig(os.path.join(savePlots, 'Z_filter.png'))
    
        
        # smoothing Z' & Z''
        zpr_smooth = sm.nonparametric.lowess(zprFi, ome, frac=0.1, it=0, delta=0.0, is_sorted=False)
        zppr_smooth = sm.nonparametric.lowess(zpprFi, ome, frac=0.1, it=0, delta=0.0, is_sorted=False)
        
        
        # Plot Z* Z' and Z'' but smoothed
        fig, ax = plt.subplots(figsize=(6.4,4.8))
        ax.plot(ome, zstarFi, '-k', linewidth=3, label=r"$ G* (\omega) $")
        ax.plot(ome, zprFi, 'ob', label=r"$ G' (\omega) $")
        ax.plot(ome, zpprFi, 'or', label=r"$ G'' (\omega) $")
        
        ax.plot(zpr_smooth[:,0], zpr_smooth[:,1], '-k', linewidth=2, label=r"$ G' (\omega) $ smooth")
        ax.plot(zppr_smooth[:,0], zppr_smooth[:,1], '-k', linewidth=2, label=r"$ G'' (\omega) $ smooth")
        
        ax.legend()
        plot_layout(fig, ax, True, True, r'Angular frequency $\omega$ (rad/s)', r'Modulus (Pa)')
        if savePlots != None:
            plt.savefig(os.path.join(savePlots, 'Z_filterSmooth.png'))
    
        # saving microrheology data
        pdZ = pd.DataFrame({'ome': ome, 'zstar': zstar, 'zpr': zpr, 'zppr': zppr, 'zstarFi': zstarFi, 'zprFi': zprFi, 'zpprFi': zpprFi, 'zprS': np.flip(zpr_smooth[:,1]), 'zpprS': np.flip(zppr_smooth[:,1])})
        pdZ['zC'] = pdZ.loc[:, 'zprS'] + (pdZ.loc[:, 'zpprS'] * 1j)
        
        
        if zPath != None:
            pdZ.to_csv(os.path.join(zPath, 'zmicrorheology-filtered.txt'), sep='\t', index=False)
            
        
        return pdZ

    
    else:
        # calculate  Z* Z' and Z''
        gama = 0.457 * (1 + deriv)**2 - 1.36 * (1 + deriv) + 1.90
        zstar = kB * temperatur / (np.pi * radi * oy * gama)
        ang = np.pi * deriv / 2
        zpr = zstar * np.cos(ang)
        zppr = zstar * np.sin(ang)
    
    
        # Plot MSD
        fig, ax = plt.subplots(figsize=(6.4,4.8))
        ax.plot(ox, oy, 'ob')
        plot_layout(fig, ax, True, True, r'Lag time t (s)', r'MSD')
        
        
        # Plot Z* Z' and Z'' with filtering 
        fig, ax = plt.subplots(figsize=(6.4,4.8))
        ax.plot(ome, zstar, '-k', linewidth=3, label=r"$ G* (\omega) $")
        ax.plot(ome, zpr, 'ob', label=r"$ G' (\omega) $")
        ax.plot(ome, zppr, 'or', label=r"$ G'' (\omega) $")
        
        ax.legend()
        plot_layout(fig, ax, True, True, r'Angular frequency $\omega$ (rad/s)', r'Modulus (Pa)')
        if savePlots != None:
            plt.savefig(os.path.join(savePlots, 'Z_nofilter.png'))
        
        
        # saving microrheology data
        pdZ = pd.DataFrame({'ome': ome, 'zstar': zstar, 'zpr': zpr, 'zppr': zppr})
        pdZ['zC'] = pdZ.loc[:, 'zpr'] + (pdZ.loc[:, 'zppr'] * 1j)
        
        
        if zPath != None:
            pdZ.to_csv(os.path.join(zPath, 'zmicrorheology.txt'), sep='\t', index=False)
    
             
        return pdZ
    


def butter_low_pass(data_in, order, smooth):
    """
    Low-pass Butterworth filter

    Parameters
    ----------
    data_in : numpy array
        Input data (1D NumPy array).
    order : int
        Filter order.
    smooth : float
        Normalized cutoff frequency (0 < smooth < 1).

    Returns
    -------
    result : numpy array
        Filtered data (same shape as input).

    """
    
    b, a = butter(order, smooth, btype='lowpass')

    # Extend the data at both ends to minimize edge effects
    data_in_ext = np.concatenate([np.full_like(data_in, data_in[0]), data_in, np.full_like(data_in, data_in[-1])])
    

    # Apply filter

    data_out = lfilter(b, a, data_in_ext)
    # print(data_out)

    # Try different shifts and compute correlation
    max_corr = -1
    best_shift = 0
    for i in range(1, 101):
        temp = np.roll(data_in_ext, i)
        corr, _ = pearsonr(temp, data_out)
        if corr > max_corr:
            max_corr = corr
            best_shift = i

    # Align the output
    data_out = data_out[best_shift:]

    # Extract central portion (original length)
    third = len(data_in_ext) // 3
    result = data_out[third:2*third]

    return result





def inertia_correction(omega, zcomplex, radi, rho_b, rho, ranges=[[1e-1, 5*1e6], [1, 1e5]], gPath=None, savePlots=None):    
    """
    Inertia correction based on:
    Domínguez-García, F. Cardinaux, E. Bertseva, L. Forró, F. Scheffold, and S. Jeney, Accounting for inertia effects to access the high-frequency microrheology of viscoelastic fluids, Physical Review E 90, 060301 (2014).

    Parameters
    ----------
    omega : numpy array
        angular frequency.
    zcomplex : numpy array
        complex modulus.
    radi : float
        radius of the particles in the sample.
    rho_b : float
        density of the particles (kg/m^3).
    rho : float
        medium density (kg/m^3).
    ranges : 2d list
        first row x axis range and second row y axis range
    gPath : string, optional
        Path to save the microrheology data. The default is None.
    savePlots : None or string
        Default None. Otherwise the path where the graphs should be saved. 

    Returns
    -------
    g_corrected : pandas dataframe
        columns:
            ome: angular frequency
            gStar: G*
            gStarABS: |G*|
            gpr: G'
            gppr: G''

    """
    
    
    # Compute m* (effective mass)
    mstar = ((4 * np.pi * radi**3 * rho_b) / 3) + ((2 * np.pi * rho * radi**3) / 3)

    # performing inertia Correction 
    term2 = (mstar * omega**2) / (6 * np.pi * radi)
    inner_term = rho**2 - (((2 * rho) / (3 * np.pi * radi**3)) * ((((6 * np.pi * radi) / omega**2) * zcomplex) + mstar))

    term3 = []
    for i in range(len(inner_term)):
        term3.append((radi**2 * omega[i]**2) / 2 * (sqrt(inner_term[i])-rho))


    gStar = (zcomplex + term2 + term3)
    gStarABS = np.abs(gStar)

    gpr = gStar.real
    gppr = gStar.imag
    
    
    # Preparing data for the plot in the correct range
    ranges = np.array(ranges, dtype=float)
    mask = np.logical_or.reduce([(omega >= lo) & (omega <= hi) for lo, hi in ranges])
    
    omegaP = omega[mask]
    gStarABSP = gStarABS[mask]
    gprP = gpr[mask]
    gpprP = gppr[mask]
    
        
    
    # Plot G* G' and G'' with filtering 
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(omegaP, gStarABSP, '-k', linewidth=3, label=r"$ G* (\omega) $")
    ax.plot(omegaP, gprP, 'ob', label=r"$ G' (\omega) $")
    ax.plot(omegaP, gpprP, 'or', label=r"$ G'' (\omega) $")
    
    ax.legend()
    plot_layout(fig, ax, True, True, r'Angular frequency $\omega$ (rad/s)', r'Modulus (Pa)')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'G_inertia_correction.png'))


    g_corrected = pd.DataFrame({'ome': omega, 'gStar': gStar, 'gStarABS': gStarABS, 'gpr': gpr, 'gppr': gppr})

    if gPath != None:
        g_corrected.to_csv(os.path.join(gPath, 'gmicrorheology-corrected.txt'), sep='\t', index=False)


    return g_corrected










