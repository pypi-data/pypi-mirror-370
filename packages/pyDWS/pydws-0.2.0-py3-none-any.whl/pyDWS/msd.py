import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from scipy.optimize import minimize
import os
from scipy.optimize import minimize_scalar

# plt.style.use('./pyDWS/plottingStyle.mplstyle')

from pyDWS.plots import plot_layout




# MSD calculation 
def msd(t, g2, lstar, lambda_laser, L, n, radi, range_icf, msdPath=None, savePlots=None):
    """
    Calculating MSD based on:
    D. J. Pine and D. A. Weitz, Diffusing-wave spectroscopy, in
    Dynamic Light Scattering: The Method and Some Applications,
    edited by W. Brown (Oxford University Press, Oxford, 1993)
    pp. 652–720.
    
    C. Zhang, M. Reufer, D. Gaudino, and F. Scheffold, Improved
    diffusing wave spectroscopy based on the automatized determi-
    nation of the optical transport and absorption mean free path,
    Korea-Australia Rheology Journal 29, 241 (2017).
    
    All parameters need to be in meters. 
    
    Parameters
    ----------
    t : numpy array
        time array.
    g2 : numpy array
        ICF -> Intensity correlation function.
    lstar : int
        transport mean free path.
    lambda_laser : float
        laser wavelength λ.
    L : int
        slab thickness.
    n : float
        refractive index.
    radi : float
        radius of the particles in the sample.
    range_icf : list
        time range of the ICF.
    msdPath : string, optional
        Path to save the msd. The default is None.
    savePlots : None or string
        Default None. Otherwise the path where the graphs should be saved. 

    Returns
    -------
    MSD : pandas dataframe
        First column time. Second column calculated mean squared displacement MSD. 
    gcal : numpy array
        Calculated g2 (ICF) function.
    resultL: list
        history of the fit

    """
    
    # setting range of icf
    valid = (g2 > 0) & ~np.isnan(g2)
    tfilt = t[valid]
    g2filt = g2[valid]

    if range_icf is not None:
        low, high = range_icf
        mask = (g2filt > low) & (g2filt < high)
        tfilt = tfilt[mask]
        g2filt = g2filt[mask]

    k0 = 2 * np.pi * n / lambda_laser

    # calculating mid value and start guess
    mi = (min(max(g2filt), 1) - max(min(g2filt), 0)) / 2 + max(min(g2filt), 0)
    r = np.where(g2filt < mi)[0][0]
    ratio = len(g2filt) / r
    idx = int(len(tfilt) / ratio)
    xf, yf = tfilt[idx], g2filt[idx]
    tau0start = -2 * xf * (L**2) / ((lstar**2) * np.log(yf))
    
    # print(idx)
    
    # Initialize empty arrays
    tau = np.zeros(len(tfilt))
    gcal = np.zeros(len(tfilt))
    
    resultL = []
    
    # calculate MSD
    for i in range(idx, -1, -1):
        ti, gi = tfilt[i], g2filt[i]
        
        if gi >= 1 or gi <= 0:
            # print('IN if 1')
            taui = tau[i+1] if i+1 < len(tau) else tau0start
        else:
            fun =  lambda t0: _g2_msd(t0, ti, gi, L, lstar, k0)[0]
            # result = minimize(fun, tau0start, method='Nelder-Mead', options={'xatol': 1e-15, 'maxiter': 10000, 'disp': False})
            result = minimize_scalar(fun, bounds=(1e-4, 1e5), method='bounded', options={'xatol': 1e-16})
            
            # taui = result.x[0]
            taui = result.x
            tau0start = taui
            
            resultL.append(result)
            
        tau[i] = taui
        _, gc = _g2_msd(taui, ti, gi, L, lstar, k0)
        gcal[i] = gc
    
    for i in range(idx + 1, len(tfilt)):
        ti, gi = tfilt[i], g2filt[i]
        if gi >= 1 or gi <= 0:
            # print('IN if 2')
            taui = tau[i - 1]
        else:
            fun =  lambda t0: _g2_msd(t0, ti, gi, L, lstar, k0)[0]
            # result = minimize(fun, tau0start, method='Nelder-Mead', options={'xatol': 1e-15, 'maxiter': 10000, 'disp': False})
            result = minimize_scalar(fun, bounds=(1e-4, 1e5), method='bounded', options={'xatol': 1e-16})
            
            # taui = result.x[0]
            taui = result.x
            tau0start = taui
            
            resultL.append(result)
            
        tau[i] = taui
        _, gc = _g2_msd(taui, ti, gi, L, lstar, k0)
        gcal[i] = gc
    
    
    # transforming t ot msd
    msdC = np.zeros((len(tfilt), 2))
    msdC[:, 0] = tfilt
    msdC[:, 1] = 6 / k0**2 * tfilt / tau
    
    
    
    # Plot g2 and calculated g2
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(tfilt, g2filt, 'ob', label='Measured')
    ax.plot(tfilt, gcal, '-r', label='calculated')
    plt.legend()
    plot_layout(fig, ax, True, False, 'Lag time t (s)', 'ICF')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'recalculated_icf.png'))


    # Plot calculated MSD 
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(msdC[:,0], msdC[:,1] , 'ob')
    plot_layout(fig, ax, True, True, 'Lag time t (s)', r'MSD')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'msd.png'))


    # Saving MSD
    
    pdMSD = pd.DataFrame({'t': msdC[:, 0], 'msd': msdC[:, 1]})
    
    
    if msdPath != None:
        pdMSD.to_csv(os.path.join(msdPath, 'msd.txt'), sep='\t', index=False)

    
    return pdMSD, gcal, resultL




def _g2_msd(tmsd, tr, g2real, L, lstar, k0):
    # defining components from equation
    Ll = L / lstar
    z0l = 2
    # ttau = k0**2 * tmsd
    
    ttau = 6 * tr / tmsd
    beta = 2/3
    
    sqrt_ttau = np.sqrt(ttau)
    
    g1 = (((Ll + 2*beta) / (z0l + beta) * (np.sinh(z0l * sqrt_ttau) + (beta * sqrt_ttau * np.cosh(z0l * sqrt_ttau)))) 
          / (((1 + (beta**2 * ttau)) * np.sinh(Ll * sqrt_ttau)) + (2*beta * sqrt_ttau * np.cosh(Ll * sqrt_ttau))))
    
    
    g2 = g1**2
    
    lerror = ((g2 - g2real) / g2real) ** 2
    
    
    return lerror, g2












