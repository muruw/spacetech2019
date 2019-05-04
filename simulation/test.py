#%%
import matplotlib.pyplot as plt
import numpy as np

from simulation.optimizer import MastPositionOptimizer
from simulation.wms import get_density_map

#%%
mast_ranges = np.random.uniform(0.05, 0.25, 10)
density_map = get_density_map("657000,6472000,661000,6476000", 2, (64, 64))

plt.imshow(density_map)

#%%
optimizer = MastPositionOptimizer(density_map, mast_ranges)
pop, stats, hof = optimizer.run(100, 10)

#%%
def plot_coverage(density_map, mast_ranges, p):
    coverage = np.zeros(density_map.shape)
    size = density_map.shape

    for x in range(size[0]):
        for y in range(size[1]):
            for m, m_range in enumerate(mast_ranges):
                if (p[m*2] - x/size[0])**2 + (p[m*2+1] - y/size[1])**2 < m_range**2:
                    coverage[x, y] = 1
                    break

    plt.title(str(coverage.sum()))
    plt.imshow(coverage)

plot_coverage(density_map, mast_ranges, list(hof[0]))
