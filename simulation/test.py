#%%
import matplotlib.pyplot as plt
import numpy as np
from math import ceil

from simulation.optimizer import MastPositionOptimizer
from simulation.density_map import DensityMap
from simulation.parameters import *

#%%
density_map = DensityMap("658000,6473000,660000,6475000")
plt.imshow(density_map.density)

#%%
mast_ranges = density_map.get_suggested_mast_ranges()

#%%
optimizer = MastPositionOptimizer(density_map, mast_ranges)
pop, stats, hof = optimizer.run(25, 5, True)

#%%
density_map.plot_coverage(mast_ranges, list(hof[0]))

#%%
plt.imshow(density_map.original, alpha=0.8)

coords = np.array(list(hof[0])) * 1024
coords_big = coords[:10]
coords_small = coords[10:]

plt.scatter(
    coords_big[0::2],
    coords_big[1::2],
    c="red",
    marker="o"
)

plt.scatter(
    coords_small[0::2],
    coords_small[1::2],
    c="red",
    marker="x"
)
