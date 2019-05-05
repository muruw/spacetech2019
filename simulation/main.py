import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy.ndimage import maximum_filter

sys.path.append(os.getcwd())
warnings.filterwarnings("ignore")

from simulation.optimizer import MastPositionOptimizer
from simulation.density_map import DensityMap
from simulation.parameters import *

# Check if figures folder exists
directory = 'web/figures'
if not os.path.exists(directory):
    os.makedirs(directory)


# Plot high resolution density
density_map = DensityMap(sys.argv[1], (128, 128))

plt.imshow(density_map.density)
plt.tick_params(axis="both", which="both", bottom=False, top=False,
    labelbottom=False, left=False, right=False, labelleft=False)
plt.savefig(
    "web/figures/density.png",
    bbox_inches="tight",
    transparent=True,
    aspect=density_map.size[1]/density_map.size[0]
)

# Calculate lower resolution density and optimize mast positions
density_map = DensityMap(sys.argv[1])

# Save coverage plots
def save_coverage_plots(mast_ranges, p):
    coverage = density_map.get_coverage(mast_ranges, p)

    plt.clf()
    plt.imshow(coverage)
    plt.tick_params(axis="both", which="both", bottom=False, top=False,
        labelbottom=False, left=False, right=False, labelleft=False)
    plt.savefig(
        "web/figures/signal.png",
        bbox_inches="tight",
        transparent=True,
        aspect=density_map.size[1]/density_map.size[0]
    )

    plt.clf()
    covered = coverage > MIN_RECEIVED_INTENSITY

    if np.min(covered.flatten().astype(int)) == 1:
        plt.imshow(covered, cmap="viridis_r")
    else:
        plt.imshow(covered, cmap="viridis")
    
    plt.tick_params(axis="both", which="both", bottom=False, top=False,
        labelbottom=False, left=False, right=False, labelleft=False)
    plt.savefig(
        "web/figures/coverage.png",
        bbox_inches="tight",
        transparent=True,
        aspect=density_map.size[1]/density_map.size[0]
    )

# Place big masts
n_mm_wave = density_map.get_suggested_mast_amount(
    MM_WAVE_RANGE, density_map.area
)

mast_ranges = [MM_WAVE_RANGE] * n_mm_wave

optimizer = MastPositionOptimizer(density_map, mast_ranges)

for i in range(2):
    pop, stats, hof = optimizer.run(20, 1)
    mm_wave_p = list(hof[0])
    save_coverage_plots(mast_ranges, mm_wave_p)

# Place small masts
dense = density_map.density > 0.3
maxima = maximum_filter(density_map.density, size=4) == density_map.density

n_small_cell = (maxima * dense).sum()
mast_ranges = [MM_WAVE_RANGE] * n_mm_wave + [SMALL_CELL_RANGE] * n_small_cell

x, y = np.where((dense * maxima) == True)
x =  x /density_map.density.shape[0]
y =  y / density_map.density.shape[1]

mast_p = mm_wave_p + list(np.column_stack((x, y)).reshape(-1))

def get_mast_type(m):
    if m < n_mm_wave:
        return "mm-wave"
    else:
        return "small-cell"

print("[" + ", ".join([
    "{ \"x\": %f, \"y\": %f, \"type\": \"%s\" }" % (
        mast_p[m*2],
        mast_p[m*2+1],
        get_mast_type(m)
    ) for m, m_range in enumerate(mast_ranges)
]) + "]", flush=True)

save_coverage_plots(mast_ranges, mast_p)

if False:
    # Place small masts
    covered = density_map.get_coverage(mast_ranges, mm_wave_p) > MIN_RECEIVED_INTENSITY
    sparse = density_map.density < DENSE_AREA_DENSITY

    #covered_area = density_map.get_coverage_area(mast_ranges, mm_wave_p)
    covered_area = np.logical_or(covered, sparse).sum()
    covered_area /= density_map.density.shape[0] * density_map.density.shape[1]
    covered_area *= density_map.area

    n_small_cell = density_map.get_suggested_mast_amount(
        SMALL_CELL_RANGE,
        density_map.area - covered_area
    )

    if n_small_cell > 0:
        mast_ranges = [MM_WAVE_RANGE] * n_mm_wave + [SMALL_CELL_RANGE] * n_small_cell
        optimizer = MastPositionOptimizer(density_map, mast_ranges, mm_wave_p)

        for i in range(5):
            pop, stats, hof = optimizer.run(25, 1)
            mast_p = mm_wave_p + list(hof[0])
            save_coverage_plots(mast_ranges, mast_p)
