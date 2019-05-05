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
density_map = DensityMap(bbox_hybrid)
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

#%%
import scipy.ndimage.filters as filters
import scipy.ndimage.morphology as morphology

def detect_local_minima(arr):
    # https://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array/3689710#3689710
    """
    Takes an array and detects the troughs using the local maximum filter.
    Returns a boolean mask of the troughs (i.e. 1 when
    the pixel's value is the neighborhood maximum, 0 otherwise)
    """
    # define an connected neighborhood
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#generate_binary_structure
    neighborhood = morphology.generate_binary_structure(len(arr.shape),2)
    # apply the local minimum filter; all locations of minimum value 
    # in their neighborhood are set to 1
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.filters.html#minimum_filter
    local_min = (filters.minimum_filter(arr, footprint=neighborhood)==arr)
    # local_min is a mask that contains the peaks we are 
    # looking for, but also the background.
    # In order to isolate the peaks we must remove the background from the mask.
    # 
    # we create the mask of the background
    background = (arr==0)
    # 
    # a little technicality: we must erode the background in order to 
    # successfully subtract it from local_min, otherwise a line will 
    # appear along the background border (artifact of the local minimum filter)
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#binary_erosion
    eroded_background = morphology.binary_erosion(
        background, structure=neighborhood, border_value=1)
    # 
    # we obtain the final mask, containing only peaks, 
    # by removing the background from the local_min mask
    detected_minima = local_min.astype(int) - eroded_background.astype(int)
    return np.where(detected_minima)       

#%%
density_map = DensityMap(bbox_hybrid, (32, 32))

plt.imshow(density_map.density)

#%%
from scipy.ndimage import maximum_filter

dense = density_map.density > 0.3
maxima = maximum_filter(density_map.density, size=4) == density_map.density

plt.imshow(maxima * dense)

#%%
pos = maxima * dense
x, y = np.where(pos == True)


x, y

#%%
np.column_stack((x, y)).reshape(-1)
