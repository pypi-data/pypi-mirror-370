import numpy as np


def generate_EchoLayout(tstep, f, save=False):
    """
    Generating Echo layout to perform linear correlation measurement with the LS Instruments Correlator
    
    So the rule is:
    Start with 1–8
    Then generate blocks of 7 numbers with increasing step sizes (2, 3, 4, ..., 11)

    Parameters
    ----------
    tstep : float
        Linear Tau Sampling time.
    f : float
        frequency.
    save : bol or string
        If you want to save it to a text file (default False).
        If you want to save it, you have to define the path. 

    Returns
    -------
    None.

    """
    # Initial time vector
    t = list(range(1, 7))  
    t0 = 1/f
    
    # generating peak distribution 
    all_peak = []
    
    # Subsequent blocks
    current = 1
    for step in range(1, 11):  # Steps from 2 to 11
        for _ in range(7): # Repeat this loop 7 times, but I don’t care about the loop variable
            all_peak.append(current)
            current += step
    all_peak.append(current) # adding one last aditionally 
    print('Peak distribution: ', all_peak)
    
          
    

    # Expand time points around each peak
    for peak in all_peak:
        sumit = int(np.floor(peak * t0 / tstep))
        t1 = list(range(sumit - 6, sumit + 7))
        t.extend(t1)

    # Convert to numpy array and reshape as a column vector
    t = np.array(t).reshape(-1, 1)
    
    if save != False:
        with open(save, 'w') as file:
            for val in t:
                file.write(f"{val[0]}\n")

    return t






# generate time scaling as for multitau measurement
def generate_time_array(start=1.25e-8, stop=12.6, initial_step=1.25e-8, steps_per_block=8, step_growth=2):
    """
    Generates a time array that starts with small uniform steps and increases the step size every block.
    
    Parameters:
    - start: Initial time value
    - stop: Maximum time value to reach
    - initial_step: Starting step size
    - steps_per_block: Number of steps before step size increases
    - step_growth: Multiplicative factor to grow step size
    
    Returns:
    - np.ndarray of time values
    """
    time_values = []
    current = start
    step = initial_step
    
    for i in range(16):
        time_values.append(current)
        current += step
    
    step *= step_growth
    # print(current)
    
    while current < stop:
        for _ in range(steps_per_block):
            if current >= stop:
                break
            time_values.append(current)
            current += step
        step *= step_growth

    time_values.insert(0, 1e-8)
    return np.array(time_values)













