#%%
import matplotlib.pyplot as plt
import numpy as np
from math import ceil

from simulation.optimizer import MastPositionOptimizer
from simulation.density_map import DensityMap
from simulation.parameters import *

#%%
bbox_field = "646827.3241459839,6470128.575091781,649289.8014071655,6472195.109801418"
bbox_town = "657116.4504978292,6472443.678982472,659362.2726506529,6474686.203315113"
bbox_hybrid = "655370.9544882914,6472575.328962082,657795.7594628605,6474688.885350946"

#%%
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
covered = density_map.get_coverage(mast_ranges, mm_wave_p) > MIN_RECEIVED_INTENSITY
sparse = density_map.density < DENSE_AREA_DENSITY

plt.imshow(sparse)

#%%
#covered_area = density_map.get_coverage_area(mast_ranges, mm_wave_p)
covered_area = np.logical_or(covered, sparse).sum()
covered_area /= density_map.density.shape[0] * density_map.density.shape[1]
covered_area *= density_map.area

n_small_cell = density_map.get_suggested_mast_amount(
    SMALL_CELL_RANGE,
    density_map.area - covered_area
)

density_map.area, covered_area, n_small_cell

#%%
mast_ranges = [MM_WAVE_RANGE] * n_mm_wave + [SMALL_CELL_RANGE] * n_small_cell
optimizer = MastPositionOptimizer(density_map, mast_ranges, mm_wave_p, True)
pop, stats, hof = optimizer.run(25, 5, True)
mast_p = mm_wave_p + list(hof[0])

density_map.plot_coverage(mast_ranges, mast_p)

#%%
'''
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
'''

pass
