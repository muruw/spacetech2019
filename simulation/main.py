import sys
import os

sys.path.append(os.getcwd())

from simulation.optimizer import MastPositionOptimizer
from simulation.wms import get_density_map

bbox = sys.argv[1]
density_map = get_density_map(bbox)

mast_ranges = [0.25, 0.25, 0.25, 0.25]

optimizer = MastPositionOptimizer(density_map, mast_ranges)
pop, stats, hof = optimizer.run(100, 10)
