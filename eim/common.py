import os 
import numpy as np


class DictClass(object):
    def __init__(self, dict):
        self.__dict__ = dict

    def update(self, dict):
        self.__dict__.update(dict)

	
def getDirAndFileName(filePath):
    fileDir = os.path.dirname(os.path.realpath(filePath))
    fileName = os.path.basename(filePath)
    return fileDir, fileName


def setVariable(var, lenght):
    """
    Creates set of values defined in 'var' of lenght 'lenght' by doing cylcing (modulo operation) 
    Example
        var = [1, 2, 3], lenght=5, return [1, 2, 3, 1, 2]
    """
    nvar = []
    l = len(var)
    for i in range(lenght):
        nvar.append(var[i % l])
    return nvar


class OUProcess:
    """
    Defines Ornstein-Uhlenbeck process
    """
    def __init__(self, mean, theta=0.03, sigma=0.05, dt = 0.001):
        """
        Inits class
            mean : desired mean membrane potential (ex. to convert to rate use log(mean) )
            theta : speed of convergance, it is 1/decay (ex. decay=0.03, 30ms)
            sigma : variance of noise (ex. 0.05)
            dt : simulation time step (ex. 0.001 = 1 ms)
        """
        self.mean = mean
        self.theta = theta
        self.sigma = sigma
        self.dt = dt
        self.f = lambda x:x

    def setFunction(self, func):
        """
        Defines function to be done over results of process.
        Default function is linear, f(x)=x
        
        Note:
            If OU proess is used to define membrane potential then f=exp
        """
        self.f = func

    def create(self,length, delay = 50):
        """
        Creates OU proess for time given by length.
            -> length : number of time steps
            -> delay : delay in time steps we discard results of process (burn in time)
        """
        dt =  self.dt
        sigma = self.sigma
        theta = self.theta
        ur = self.mean
        u0 = ur+np.random.randn(1)

        ut = np.zeros(length+delay)
        ut[0]=u0
        for t in range(1,length+delay):
            ut[t]=ut[t-1] + theta*(ur-ut[t-1])*dt + np.random.randn(1)*sigma
            ut[t] = min(np.log(50),ut[t])
        return self.f(ut[delay:])
