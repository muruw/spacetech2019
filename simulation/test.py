#%%
import matplotlib.pyplot as plt
import numpy as np
from math import ceil

from simulation.optimizer import MastPositionOptimizer
from simulation.density_map import DensityMap
from simulation.parameters import *

#%%
bbox_forest = "653840.2028413543,6475325.432370271,655077.7935806693,6476604.332011141"
bbox_field = "652063.0487542147,6475264.017033348,652984.7924631344,6475956.906271896"
bbox_town = "658000,6473000,660000,6475000"

density_map = DensityMap(bbox_town)
plt.imshow(density_map.original, aspect=density_map.size[1]/density_map.size[0])

n_mm_wave = density_map.get_suggested_mast_amount(MM_WAVE_RANGE, density_map.area)

mast_ranges = [MM_WAVE_RANGE] * n_mm_wave
n_mm_wave

#%%
optimizer = MastPositionOptimizer(density_map, mast_ranges)
pop, stats, hof = optimizer.run(25, 5, True)
mm_wave_p = list(hof[0])

density_map.plot_coverage(mast_ranges, mm_wave_p)

#%%
covered_area = density_map.get_coverage_area(mast_ranges, mm_wave_p)

n_small_cell = density_map.get_suggested_mast_amount(
    SMALL_CELL_RANGE,
    density_map.area - covered_area
)

n_small_cell

#%%
mast_ranges = [MM_WAVE_RANGE] * n_mm_wave + [SMALL_CELL_RANGE] * n_small_cell
optimizer = MastPositionOptimizer(density_map, mast_ranges, mm_wave_p)
pop, stats, hof = optimizer.run(25, 5, True)
mast_p = mm_wave_p + list(hof[0])

density_map.plot_coverage(mast_ranges, mast_p)

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

#%%
1 + np.mean(density_map.density) * 5

