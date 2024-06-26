'''
This script evaluates a possible random solution for the distribution of the mills in the environment 
of the example "WindFLO/Examples/Example1/example1.py". The score, the evaluation time and the graphical 
representation of the solution are obtained.
'''
#==================================================================================================
# LIBRARIES
#==================================================================================================
import os
import sys
import time

import numpy as np
import matplotlib.pyplot as plt
from numpy import linalg
from tqdm import tqdm as tqdm
import numpy.typing
import os

sys.path.append('other_src/WindFLO/API')
from WindFLO import WindFLO

#==================================================================================================
# FUNCTIONS
#==================================================================================================

N_TURBINES = 10
SOLUTION_DIM = N_TURBINES*2



def get_windFLO_object():
    '''Initialize the characteristics of the terrain and turbines on which the optimization will be applied.'''

    # Configuration and parameters.
    windFLO = WindFLO(
    inputFile = 'other_src/WindFLO/Examples/Example1/WindFLO.dat', # Input file to read.
    libDir = 'other_src/WindFLO/release/', # Path to the shared library libWindFLO.so.
    turbineFile = 'other_src/WindFLO/Examples/Example1/V90-3MW.dat',# Turbine parameters.
    terrainfile = 'other_src/WindFLO/Examples/Example1/terrain.dat', # File associated with the terrain.
    nTurbines = N_TURBINES, # Number of turbines.

    monteCarloPts = 1000# Parameter whose accuracy will be modified.
    )

    # Change the default terrain model from RBF to IDW.
    windFLO.terrainmodel = 'IDW'

    return windFLO
WINDFLO_OBJ=get_windFLO_object()


def from_0_1_to_windflo(x: numpy.typing.ArrayLike):
    assert x.shape == (SOLUTION_DIM,), f"x.shape={x.shape} SOLUTION_DIM={SOLUTION_DIM}"
    lbound = np.zeros(SOLUTION_DIM)    
    ubound = np.ones(SOLUTION_DIM)*2000
    return lbound + x*(ubound - lbound)



def f(x: numpy.typing.ArrayLike):
    '''Evaluating the performance of a single solution.'''
    solution=from_0_1_to_windflo(x)

    k = 0
    for i in range(0, N_TURBINES):
        for j in range(0, 2):
            WINDFLO_OBJ.turbines[i].position[j] = solution[k]
            k = k + 1

    WINDFLO_OBJ.run(clean = True) 

    return -WINDFLO_OBJ.farmPower / 10000000.0 # negative sign because we assume minimization in the paper Scale down to avoid numerical errors.






def plot_WindFLO(x: numpy.typing.ArrayLike):
    '''Graphically represent the solution.'''
    f(x) # Loads solution into WINDFLO_OBJ
    # Results in 2D.
    fig = plt.figure(figsize=(8,5), edgecolor = 'gray', linewidth = 2)
    ax = WINDFLO_OBJ.plotWindFLO2D(fig, plotVariable = 'P', scale = 1.0e-3, title = 'P [kW]')
    WINDFLO_OBJ.annotatePlot(ax)
    plt.show()

    # Results in 3D.
    fig = plt.figure(figsize=(8,5), edgecolor = 'gray', linewidth = 2)
    ax = WINDFLO_OBJ.plotWindFLO3D(fig)
    WINDFLO_OBJ.annotatePlot(ax)
    plt.show()



def constraint_check(x: numpy.typing.ArrayLike):
    
    # Assuming turbines are placed in a 2000x2000 grid.

    # get position of the turbines in the 2000x2000 grid.
    sol = from_0_1_to_windflo(x)
    k = 0
    x_pos = np.zeros((N_TURBINES, 2))
    for i in range(0, N_TURBINES):
        for j in range(0, 2):
            x_pos[i,j] = sol[k]
            k = k + 1

    # constraint 0: distance between every two turbines minimum 200 m
    min_distance = 300.0
    check_0 = np.inf
    for i_1 in range(N_TURBINES):
        for i_2 in range(N_TURBINES):
            if i_1==i_2:
                continue
            check_0 = min(check_0, np.linalg.norm(x_pos[i_1]- x_pos[i_2]) - min_distance)


    # constraint 1: solutions should be evenly distributed in the space: Each quandrant should not have more than 1/3 of the solutions.
    q_count = np.zeros(4)
    for i in range(N_TURBINES):
        if x_pos[i][0] > 1000 and x_pos[i][1] > 1000:
            q_count[0] += 1
        if x_pos[i][0] < 1000 and x_pos[i][1] > 1000:
            q_count[1] += 1
        if x_pos[i][0] < 1000 and x_pos[i][1] < 1000:
            q_count[2] += 1
        if x_pos[i][0] > 1000 and x_pos[i][1] < 1000:
            q_count[3] += 1
    check_1 = N_TURBINES * 0.333333333 - max(q_count)

    # constraint 2: Certain parts of the terrain are not valid. None of the solutions can be placed there.
    hole_centers = np.array([[708.8905828911846, 1260.4771639928265], [989.3119875121884, 660.7845491117623], [1987.104282428962, 305.0923824053107], [929.1961117086416, 1395.3453795609323], [307.03362602397857, 1563.8444852857797], [1417.7499940372359, 621.6371831490444], [564.8454935706593, 849.5591424031293], [1359.7356592197577, 606.894587154017], [249.21741910436057, 1852.908347601767], [997.8899037977513, 735.7795317462887], [1432.1922070653075, 730.3002772617315], [1406.8871687624742, 1525.401811750595], [1291.7086773075002, 519.8698443219552], [1056.7478073369641, 913.2615384103344], [1104.8969457872658, 337.9687180510689], [1794.4047180743548, 367.3240213120086]])
    diameter_holes = 400
    check_2 = 1e8
    for center_non_valid_terrain in hole_centers:
        center_non_valid_terrain = np.array([1350.0, 750.0])
        check_2 = min(np.min(np.linalg.norm(x_pos - center_non_valid_terrain, axis=1)) - diameter_holes, check_2)


    return (check_0, check_1, check_2)

if __name__ == "__main__":
    plot_WindFLO(np.random.random(SOLUTION_DIM))
    plot_WindFLO(np.random.random(SOLUTION_DIM)/10)
    plot_WindFLO(np.random.random(SOLUTION_DIM)/100)
    plot_WindFLO(np.random.random(SOLUTION_DIM)/1000)
    plot_WindFLO(np.random.random(SOLUTION_DIM)/10000)


# # Delete auxiliary files.
# os.remove(os.path.sep.join(sys.path[0].split(os.path.sep)[:-1])+'/terrain.dat')