import sys
import os
import numpy as np

sys.path.append(os.getcwd())

from simulation.optimizer import MastPositionOptimizer
from simulation.wms import get_density_map

bbox = sys.argv[1]
density_map = get_density_map(bbox)

bbox = [float(coord) for coord in bbox.split(",")]
width = bbox[2] - bbox[0]
height = bbox[3] - bbox[1]
size = (width + height) / 2000

mm_wave_masts = max(1, min(5, round(size**2 / np.pi)))
small_cell_masts = min(20, round(size**2 * (1 - 1 / np.pi / 2)))

optimizer = MastPositionOptimizer(
    density_map,
    [1/size] * mm_wave_masts + [0.1/size] * small_cell_masts
)

optimizer.run(1, 1)
optimizer.run(2, 9)
