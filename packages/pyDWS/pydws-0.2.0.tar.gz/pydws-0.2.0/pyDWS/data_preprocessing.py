import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

from sklearn.metrics import r2_score

# plt.style.use('./pyDWS/plottingStyle.mplstyle')

import importlib.resources as resources

with resources.path("pyDWS", "plottingStyle.mplstyle") as style_path:
    plt.style.use(style_path)


from pyDWS.plots import plot_layout


def loading_data(dataPath, skipN = 6, save=None):
    """
    loading data

    Parameters
    ----------
    dataPath : string
        Path of the file to load
    skipN : int, optional
        Numver of rows to skip at the beginning of the csv file. The default is 6.

    Returns
    -------
    2 Pandas dataframe of data splitted into a top and bottom part

    """
    # Read the CSV, skipping the first 6 rows (by default)
    dfData_raw = pd.read_csv(dataPath, skiprows=skipN, header=None) 
    
    # Convert everything to float64, coercing errors (like strings) to NaN
    dfData = dfData_raw.apply(pd.to_numeric, errors='coerce')
    
    # Get indices where there's at least one NaN
    nan_rows = dfData[dfData.isna().any(axis=1)].index.tolist()
    
   
    # loading dataframe again, but only second part 
    # dfData_real = pd.read_csv(dataPath, skiprows=nan_rows[0], header=None, dtype=np.float64) 
    
    
    
    # splitting the dataframe into 2 parts
    if nan_rows:
        split_index = nan_rows[0]
        df_top = dfData.iloc[:split_index]
        df_bottom = dfData.iloc[split_index+1 :]
    else:
        df_top = dfData
        df_bottom = pd.DataFrame()  # no NaNs, nothing to split
    
    # saving raw data 
    if save != None:
        if df_bottom.empty:
            raise Exception('icf_raw.txt is empty')
        else:
            df_bottom.to_csv(os.path.join(save, 'icf_raw.txt'), sep='\t', header=['Lag Time [s]', 'Correlation Function'], index=False)
        
    return df_top.reset_index(drop=True), df_bottom.reset_index(drop=True)






def echo_peakFit(echoData, echoPeaks, f, fitModel='Lorentzian', plot_ind=False, savePlot=None, saveEcho=None):
    """
    Fitting the echo peaks using a Lorentzian Model and calculating the area below the peak. 

    Parameters
    ----------
    echoData : pandas dataframe
        Echo data to fit the peaks.
    echoPeaks : numpy array 
        Array which contain the echo peak indices.
    f : float
        frequency of the echo peaks.
    fitModel : String 
        Model to use for the fit. The default is 'Lorentzian'. 'Gaussian' is also predefined.
    plot_ind : boolean or int
        Show plot or not. By default the plot is not shown. 
        When plot is equal an integer the peak at this index is shwon
    save : string
        save the plot or not. The string corresponds to the path where the file is saved or is iqual to None.
        By default it is None. 
    saveEcho : string
        save the Echo data or not. The string corresponds to the path where the file is saved or is iqual to None.
        By default it is None. It saves t the fitting parameters and the area of the fit. 
    Returns
    -------
    df_icf_echo Dataframe which contains t, fit parameters and calculated area.

    """
    # fitting the echo peak and area calculation 

    icf_echo = []
    
    plot = False
    savePlotL = [0, savePlot]
    
    # Fit each peak
    for peak_index in echoPeaks:
        t = peak_index / f
        print('t: ', t)
        mask = np.abs(echoData.iloc[:, 0] - t) < 0.005
        tpeak = echoData[mask].iloc[:, 0]
        gpeak = echoData[mask].iloc[:, 1]
        
        # check wheater plotting or not
        if peak_index == plot_ind:
            plot = True
            savePlotL = [plot_ind, savePlot]
            
            # Plot all echo data
            fig, ax = plt.subplots(figsize=(6.4,4.8))
            ax.plot(echoData.iloc[:,0], echoData.iloc[:,1], 'o', label='Echo measurements')
            ax.plot(tpeak, gpeak, 'o', label='echo peak', color='None', markeredgecolor='red')
            
            plt.legend()
            plot_layout(fig, ax, False, False, 'x', 'y')
            savepath=[str(plot_ind)+'_1', savePlot]
            if savepath[1] != None:
                plt.savefig(os.path.join(savepath[1], 'echo_peak_' + str(savepath[0])+'.png'))
        else:
            plot = False
            

        # Fit using a Lorentzian model by default
        fit_result, gof, r2 = fit_echo_peak(tpeak, gpeak, fitModel, plot, savePlotL)
        
        a = fit_result[0]
        mu = fit_result[1]
        sigma = fit_result[2]

        # calculating area under the fit
        area = a * np.pi * abs(sigma) * 1e4
        
        icf_echo.append([t, a, mu, sigma, area, r2])
        
    df_icf_echo = pd.DataFrame(icf_echo, columns =['t', 'a', 'mu', 'sigma', 'area', 'r2'])
    
    # saving echo data 
    if saveEcho != None:
        df_icf_echo.to_csv(os.path.join(saveEcho, 'icf_echo.txt'), sep='\t', index=False)

    return df_icf_echo





def fit_echo_peak(xData, yData, model, plot, save):
    """
    Fit function to fit the echo peaks. By default it fits the peaks with a Lorentzian. 
    Lorentzian and Gaussian are predefined. It is also possible to fit the data with a custom function.

    Parameters
    ----------
    xData : Dataframe
        One column of a dataframe.
    yData : Dataframe
        One column of a dataframe.
    model : String or custom function
        Model to use for the fit. The default is 'Lorentzian'. 'Gaussian' is also predefined. 
    plot : boolean  
        Default False. 
    save : list or None
        save the plot or not. The first element contains the index of the echo to save and the second element the path where the file is saved.
        By default it is None.
    Returns
    -------
    Fit parameters.

    """
    
    # Initial guess for [amplitude, mean, width]
    initial_guess = [np.max(yData), np.mean(xData), np.std(xData)]
    
    # generate x Data for plotting the fit
    xDataFit = np.linspace(min(xData), max(xData), 100)
    # plot lables
    xlabel = 'x'
    ylabel = 'y'
    
    # Lorentzian Model 
    if model=='Lorentzian':
        # Perform the fit
        print('Lorentzian')
        try:
            popt, pcov = curve_fit(_lorentzian, xData, yData, p0=initial_guess)
            y_pred = _lorentzian(xData, *popt)
            # print('r2: ', r2_score(yData, y_pred))
            r2Score = r2_score(yData, y_pred)
            
        except RuntimeError:
            popt = np.array([0, 0, 0])
            pcov = 0
            r2Score = 0
            print("Error - curve_fit failed")
        
        # plotting data with the fit
        if plot == True:
            fig, ax = plt.subplots(figsize=(6.4,4.8))
            ax.plot(xData, yData, 'o', label='Measurement')
            ax.plot(xDataFit, _lorentzian(xDataFit, popt[0], popt[1], popt[2]), '-', label=model+' Fit')
            
            plt.legend()
            plot_layout(fig, ax, False, False, xlabel, ylabel)
            if save[1] != None:
                plt.savefig(os.path.join(save[1], 'echo_peak_' + str(save[0])+'.png'))
            
            
    # Gaussian Model 
    elif model=='Gaussian':
        # Perform the fit
        print('Gaussian')
        try:
            popt, pcov = curve_fit(_gaussian, xData, yData, p0=initial_guess)
            y_pred = _gaussian(xData, *popt)
            # print('r2: ', r2_score(yData, y_pred))
            r2Score = r2_score(yData, y_pred)
        except RuntimeError:
            popt = np.array([0, 0, 0])
            pcov = 0
            r2Score = 0
            print("Error - curve_fit failed")
        
        # plotting data with the fit
        if plot == True:
            fig, ax = plt.subplots(figsize=(6.4,4.8))
            ax.plot(xData, yData, 'o', label='Measurement')
            ax.plot(xDataFit, _gaussian(xDataFit, popt[0], popt[1], popt[2]), '-', label=model+' Fit')
            
            plt.legend()
            plot_layout(fig, ax, False, False, xlabel, ylabel)
            if save[1] != None:
                plt.savefig(os.path.join(save[1], 'echo_peak_' + str(save[0])+'.png'))

    else:
        raise Exception('Fit could not be performed. Wrong model parameter')
        

    return popt, pcov, r2Score



def generate_echoPeaks():
    """
    Generating echo peaks layout for the echo peak fitting. 
    So the rule is:
    Start with 1–8
    Then generate blocks of 7 numbers with increasing step sizes (2, 3, 4, ..., 11)


    Returns
    -------
    numpy array.

    """
    
    # generating peak distribution 
    all_peak = []
    
    # Subsequent blocks
    current = 1
    for step in range(1, 10):  # Steps from 2 to 11
        for _ in range(7): # Repeat this loop 7 times, but I don’t care about the loop variable
            all_peak.append(current)
            current += step
    all_peak.append(current) # adding one last aditionally 
    
    # converting list to numpy array 
    all_peak_arr = np.array(all_peak, dtype='int32')
    print('Peak distribution: ', all_peak_arr)
    
    

    return all_peak_arr






# =============================================================================
# Private functions
# =============================================================================

# Lorentzian function
def _lorentzian(x, a, mu, sigma):
    """
    Parameters
    ----------
    x : dataframe
        data to fit.
    a : float
        Amplitude.
    mu : float
        center.
    sigma : float
        full width at half maximum.

    Returns
    -------
    TYPE
        Lorentzian function.

    """
    # return a *sigma / (sigma**2 + (x - mu)** 2) # Fully correct Lorentzian 
    return a / (1 + ((x - mu) / sigma)** 2)


# Gaussian function
def _gaussian(x, a, mu, sigma):
    """
    Parameters
    ----------
    x : dataframe
        data to fit.
    a : float
        Amplitude.
    mu : float
        center.
    sigma : float
        full width at half maximum.

    Returns
    -------
    TYPE
        Lorentzian function.

    """
    return a * np.exp(-((x - mu)**2) / (2 * sigma**2))










