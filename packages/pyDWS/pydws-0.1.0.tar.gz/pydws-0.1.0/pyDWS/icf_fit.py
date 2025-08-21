import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import os
import sys
import json
from pathlib import Path

# plt.style.use('./pyDWS/plottingStyle.mplstyle')

from pyDWS.plots import plot_layout
from pyDWS.utils import generate_time_array


def icf_fit(data, name, alphaRange=np.arange(0, 22.5, 1.5), plateauVal=False, max_iterations=400, iteration_step = 10000, PathPguess= None, icfFitPath=None, savePlots=None):
    """
    Fitting icf with a intercept-adjusted exponential spectrum fit

    Parameters
    ----------
    data : string or pandas Dataframe
        Path of the data to fit or the data as a pandas Dataframe
    name : string
        Name of the Pguess file.
    alphaRange : numpy array, optional
        Alpha range used for the fit. The default is np.arange(0, 22.5, 1.5).
    plateauVal : Bool, optional
        Can be used if data shows a plateau for a better fit. The default is False.
    max_iterations : int, optional
        The minimization must converge under max_iterations. The default is 400.
    iteration_step : int, optional
        How many interations the minimization does in one minimization loop. The default is 10000.
    PathPguess : string, optional
        Paht to save the optimized P values. The default is None.
    icfFitPath : string, optional
        Path to save the fitted icf. The default is None.
    savePlots : None or string
        Default None. Otherwise the path where the graphs should be saved. 

    Returns
    -------
    TYPE
        dictionary.
        icfFitData = {
            't': tN, (lag times)
            'icf': _ICFfit(tN, g2, alp, P_current), (fitted icf)
            'intercept': intercept, (to normalize to 1)
            'alpha': alp, (alpha values)
            'P': P_current, (optimized P values)
            'fun': functionVal, (function values of the minimization)
            'NIter': numberInter, (number of minimization loops)
            'MinIter': total_iterations (number of iterations in the last minimization loop)
        }

    """
    
    # Load data
    if isinstance(data, pd.DataFrame):
        t = data.iloc[:,0].values
        g2 = data.iloc[:,1].values
    elif isinstance(data, (str, Path)):
        ICF = pd.read_csv(data, sep='\t')
        t = ICF.iloc[:,0].values
        g2 = ICF.iloc[:,1].values
    else:
        raise TypeError(f"Expected a pandas DataFrame or path (str/Path), got {type(data).__name__}")
    
    
    # Alpha array
    alp = 1e-7 * np.exp(alphaRange)

    if plateauVal == True:
        alp[-1] = np.inf
        print('alpha:', alp)
    
    
    
    # Load previous guess or create new
    try:
        guess_path = os.path.join(PathPguess, f'ICFfitguess_{name}.npy')
    except TypeError:
        print("Error - Invalid path")
        sys.exit()
    
    if os.path.exists(guess_path):
        Pguess = np.load(guess_path)
    else:
        Pguess = np.random.rand(len(alp))
        Pguess = Pguess / np.sum(Pguess)



    # minimization parameters
    P_current = Pguess.copy()
    converged = False
    total_iterations = 10000
    history = [P_current.copy()]
    functionVal = []

    numberInter = 0

    # objectiv function used for minimization 
    def _objective(P):
       return _ICFfitMin(t, g2, alp, P)


    # minimize objectiv function 
    while not converged or (total_iterations > max_iterations):
    
        numberInter +=1
        
        result = minimize(_objective, P_current, method='Nelder-Mead', options={'maxiter': iteration_step, 'disp': False})
    
        P_current = result.x
        total_iterations = result.nit
        history.append(P_current.copy())
    
        # P_current = P_new
        converged = result.success
        functionVal.append(result.fun)
        
        
    
    # if not converged:
    #     print(f'Max iterations reached ({total_iterations}). Final ΔP={delta:.2e}')
    if PathPguess != None:
        np.save(guess_path, P_current)
        
    # Calculating Intercpt
    intercept = np.sum(P_current**2)


    # generate time array as for multitau measurement
    tN = generate_time_array()


    # Plot evolution of function values
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(np.arange(1, numberInter + 1, 1), functionVal , 'o')
    plot_layout(fig, ax, False, False, 'Iteration', 'Function value')
    
    
    
    # Plot fit
    fig, ax = plt.subplots(figsize=(6.4,4.8))
    ax.plot(t, g2 , 'o', label='merged')
    ax.plot(tN, _ICFfit(tN, g2, alp, P_current), '-', label='icf Fit')
    plt.legend()
    plot_layout(fig, ax, True, False, 'Lag time t (s)', r'ICF')
    if savePlots != None:
        plt.savefig(os.path.join(savePlots, 'icf_fit.png'))
    
    
    
    # Saving Fit
    icfFitData = {
        't': tN.tolist(), 
        'icf': _ICFfit(tN, g2, alp, P_current).tolist(),
        'intercept': intercept,
        'alpha': alp.tolist(), 
        'P': P_current.tolist(), 
        'fun': functionVal, 
        'NIter': numberInter,
        'MinIter': total_iterations
    }
    
    if icfFitPath != None:
        with open(os.path.join(icfFitPath, "icf_fit.txt"), "w") as f:
            json.dump(icfFitData, f, indent=4)
    
    

    
    
    return icfFitData
    



# Fit function to minimize 
def _ICFfitMin(t, g2, alp, P, ifweight=False):
    
    ICFfit = np.zeros_like(t)
    f2 = np.zeros_like(t)
    
    for i in range(len(t)):
        ICFfit[i] = np.sum(P**2 * np.exp(-t[i]/alp)**2)
        f2[i] = np.sum(ICFfit[i] / alp**2)
    
    residual = ICFfit - g2
    sigma = np.std(residual) + np.finfo(float).eps
    
    if ifweight:
        weights = 1 / (sigma**1)
        Er = np.mean(weights * (ICFfit - g2)**2)
    else:
        Er = np.mean((ICFfit - g2)**2)
    
    return Er

# ICF Fit
def _ICFfit(t, g2, alp, P):
    
    ICFfit = np.zeros_like(t)
    f2 = np.zeros_like(t)
    
    for i in range(len(t)):
        ICFfit[i] = np.sum(P**2 * np.exp(-t[i]/alp)**2)
        f2[i] = np.sum(ICFfit[i] / alp**2)
    
    
    return ICFfit













