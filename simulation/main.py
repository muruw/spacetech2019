import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())

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
    plt.imshow(covered)
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

for i in range(5):
    pop, stats, hof = optimizer.run(10, 1)
    mm_wave_p = list(hof[0])
    save_coverage_plots(mast_ranges, mm_wave_p)

# Place small masts
covered_area = density_map.get_coverage_area(mast_ranges, mm_wave_p)

n_small_cell = density_map.get_suggested_mast_amount(
    SMALL_CELL_RANGE,
    density_map.area - covered_area
)

mast_ranges = [MM_WAVE_RANGE] * n_mm_wave + [SMALL_CELL_RANGE] * n_small_cell
optimizer = MastPositionOptimizer(density_map, mast_ranges, mm_wave_p)

for i in range(5):
    pop, stats, hof = optimizer.run(10, 1)
    mast_p = mm_wave_p + list(hof[0])
    save_coverage_plots(mast_ranges, mast_p)

