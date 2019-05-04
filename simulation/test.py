#%%
import matplotlib.pyplot as plt
import numpy as np

from simulation.optimizer import MastPositionOptimizer
from simulation.wms import get_density_map, get_absorption_between_points

#%%
mast_ranges = [0.25] * 2 + [0.05] * 10 #np.random.uniform(0.05, 0.25, 3)
density_map = get_density_map("657000,6472000,661000,6476000", 2, (32, 32))

plt.imshow(density_map)

#%%
optimizer = MastPositionOptimizer(density_map, mast_ranges)
pop, stats, hof = optimizer.run(25, 25, True)

#%%
def plot_coverage(density_map, mast_ranges, p):
    coverage = np.zeros(density_map.shape)
    size = density_map.shape

    for x in range(size[0]):
        for y in range(size[1]):
            P_r = []

            for m, m_range in enumerate(mast_ranges):
                a = get_absorption_between_points((
                    min(0, max(size[0] - 1, int(p[m*2]*size[0]))),
                    min(0, max(size[1] - 1, int(p[m*2+1]*size[1])))
                ), (
                    x,
                    y
                ), density_map)

                d = np.sqrt((p[m*2] - x/size[0])**2 + (p[m*2+1] - y/size[1])**2)
                P_r.append(np.exp(-d/m_range) * 1/max(a, 1))
            
            coverage[x, y] = max(P_r)

    plt.title(str(coverage.sum()))
    #img = plt.imshow(density_map, zorder = 2, alpha=0.6)

    plt.figure(1)
    plt.imshow(coverage, zorder = 1)
    plt.colorbar()

    plt.figure(2)
    plt.imshow(coverage > 0.1)

    plt.plot()

plot_coverage(density_map, mast_ranges, list(hof[0]))
