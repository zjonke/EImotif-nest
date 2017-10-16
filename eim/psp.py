"""
Module defining (E,I) PSP shapes
"""
import numpy as np

def createPSPShape(PSP, dt=1e-3):
    """
    Create EPSP shape
        -> EPSP: dictionary describing EPSP
                -> 'shape' : string("rectangular", "plataue", "alpha", "doubleexp")
                -> 'duration' : float (total duration of EPSP we consider)
                -> 'type' : string ("renewal","additive")
                -> 'maxvalue' : float ( max value of EPSP)
                -> additionally for "doubleexp":
                    -> 'trise' : float (rising constant)
                    -> 'tfall' : float (falling constant)
        -> dt : simulation time step
    """
    PSPshape = PSP['shape']
    PSPduration = PSP['duration']
    maxvalue = PSP['maxvalue']

    if PSPshape == "rectangular":
        psp = rectangular(PSPduration, maxvalue, dt)
    elif PSPshape == "doubleexp":
        tr = PSP['trise']  # s
        tf = PSP['tfall']  # s
        psp = doubleExp(tr, tf, PSPduration, maxvalue, dt)
    elif PSPshape == "alpha":
        # just upper part of double exponential, its shorter, smoother and more closer to rectangular
        psp = alpha(PSPduration, maxvalue, dt)
    elif PSPshape == "plataue":
        psp = plataue(PSPduration, maxvalue, dt)
    else: # default is rectangular
        psp = rectangular(PSPduration, maxvalue, dt)

    return psp


def rectangular(duration, maxvalue, dt):
    """
    Rectangular shape
    Returns array
        -> duration : duration of PSP shape we are interested in sec
        -> maxvalue : max value of PSP shape
        -> dt : timestep
    Note:
         Duration of PSP shape is what we consider, it can be shorter or longer then actual duration.
    """
    nsteps = int(np.ceil(duration / dt))  # round up, at least 1 simulation time step length
    return np.ones([nsteps]) * maxvalue

	
def doubleExp(trise, tfall, duration, maxvalue, dt=1):
    """
    Double exponential shape
    Returns array
        -> trise : (float) define rising constant
        -> tfall : (float) define falling constant
        -> duration : duration of PSP shape we are interested in (timesteps!)
        -> maxvalue : max value of PSP shape
        -> dt : (int) ms
    Note:
         Duration of PSP shape is what we consider, it can be shorter or longer then actual duration.
    """

    tr = np.ceil(trise / dt)
    tf = np.ceil(tfall / dt)
    nsteps = int(np.ceil(duration / dt))
    yv = np.zeros([nsteps + 1])
    vr = 1
    vf = 1
    for i in range(nsteps + 1):
        yv[i] = vf - vr
        vr *= np.exp(-1./tr) 
        vf *= np.exp(-1./tf) 
    tmax = tr * tf * np.log(tr/tf) / (tr-tf)
    m = np.exp(-tmax/tf)-np.exp(-tmax/tr)
    yv/=m
    #remove 1 values as it is 0, not to introduce any delay
    yv = yv[1:]
    return yv * maxvalue


def alpha(duration, maxvalue, dt):
    """
    Alpha shape (top of double exp)
    Returns array
        -> duration : duration of PSP shape we are interested in sec
        -> maxvalue : max value of PSP shape
        -> dt : (float) sec (0.001 = 1ms)
    Note:
         Duration of PSP shape is what we consider, it can be shorter or longer then actual duration.
    """
    epsp_T = 60e-3
    epsp_tau = epsp_sqr_tau = 30e-3
    epsp_sqr_kernel = np.hstack((np.ones(epsp_sqr_tau / dt), np.zeros((epsp_T - epsp_sqr_tau) / dt)))
    
    epsp_alpha_tau = 17e-3
    x_root_1 = 0.2231961
    x_root_2 = 2.67835
    epsp_alpha_kernel = 2.3*(np.exp(1)* (np.arange(0, (x_root_2 - x_root_1)*epsp_alpha_tau, dt) / epsp_alpha_tau + x_root_1)* \
                            np.exp(-(np.arange(0, (x_root_2 - x_root_1)*epsp_alpha_tau, dt) / epsp_alpha_tau + x_root_1)) - 0.5)
    epsp_alpha_kernel = np.hstack((epsp_alpha_kernel, np.zeros(len(epsp_sqr_kernel) - len(epsp_alpha_kernel))))
    
    m = epsp_alpha_kernel.max()
    epsp_alpha_kernel /= m
    yv = epsp_alpha_kernel * maxvalue
    nsteps = np.ceil(duration / dt)
    r = yv[1: nsteps + 1]  # skiping first value which is 0
    fr = np.zeros(nsteps)
    fr[:r.shape[0]] = r  # copying
    return np.maximum(fr, np.zeros(nsteps))

def plataue(duration, maxvalue, dt):
    """
    Plataue shape
    Returns array
        -> duration : duration of PSP shape we are interested in sec
        -> maxvalue : max value of PSP shape
        -> dt : (float) sec (0.001 = 1ms)
    Note:
         Duration of PSP shape is what we consider, it can be shorter or longer then actual duration.
    """
    pi = np.pi
    conv_sin_tau_start = 7e-3
    conv_sin_tau_end = 18e-3
    epsp_T = 60e-3
    epsp_tau = epsp_sqr_tau = 30e-3
    epsp_sqr_kernel = np.hstack((np.ones(epsp_sqr_tau / dt), np.zeros((epsp_T - epsp_sqr_tau) / dt)))
    
    t_range_start = np.arange(0, conv_sin_tau_start, dt)
    t_range_end = np.arange(0, conv_sin_tau_end, dt)
    
    epsp_sin_kernel_part_start = np.sin(pi / 2 * t_range_start / conv_sin_tau_start)
    epsp_sin_kernel_part_end = t_range_end / conv_sin_tau_end - np.sin(2 * pi * t_range_end / conv_sin_tau_end) / (2 * pi)
    epsp_sin_kernel_part_end = epsp_sin_kernel_part_end[::-1] 
    
    epsp_sin_based_kernel = 1.03 * np.hstack((epsp_sin_kernel_part_start, np.ones((epsp_tau - (conv_sin_tau_start + 0.5 * conv_sin_tau_end)) / dt), epsp_sin_kernel_part_end))
    epsp_sin_based_kernel = np.hstack((epsp_sin_based_kernel, np.zeros(len(epsp_sqr_kernel) - len(epsp_sin_based_kernel))))
    
    m = epsp_sin_based_kernel.max()
    epsp_sin_based_kernel /= m
    yv = epsp_sin_based_kernel * maxvalue
    nsteps = np.ceil(duration / dt)
    r = yv[:nsteps]
    fr = np.zeros(nsteps)
    fr[:r.shape[0]] = r  #copying
    return fr
