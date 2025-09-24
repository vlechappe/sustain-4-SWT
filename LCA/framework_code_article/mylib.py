import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
from brightway2 import *


def aep_rayleigh(v_mu,power_curve):
    p=power_curve.Pdc
    v=power_curve.Vw
    F=1-np.exp(-np.pi/(4*v_mu**2)*np.power(v,2)) # Rayleigh distribution
    sum=0
    for x in range(1,len(p)-1):
        bin_energy=(F[x]-F[x-1])*(p[x-1]+p[x])/2
        sum=sum+bin_energy
    aep=8760*sum # annual energy production  
    return aep

def wind_shear_log(v_ref,h_ref,h,z_0):
    return v_ref*np.log((h)/z_0)/np.log((h_ref)/z_0)

####COMPUTE RESULTS OF IMPACTS#####

def EF_single_score(scores,NF,WF):
    # returns EF single score from the (15x1) score, NF and WF vectors
    WS=scores/NF*WF
    return np.sum(WS)

def lca_single_score(activities,methods,NF,WF):
    array_score=np.zeros(len(methods)) #Results are in a np array
    for i in range(len(activities)): #Cycle through activities
        for j in range(len(methods)): # Cycle through methods
            lca = LCA(demand={activities[i]:1},
                 method=methods[j])
            lca.lci()
            lca.lcia()
            array_score[j]+=lca.score #sum impacts       
    return EF_single_score(array_score,NF,WF)



