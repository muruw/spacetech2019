import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.append(os.getcwd())

from simulation.optimizer import MastPositionOptimizer
from simulation.density_map import DensityMap

# Plot high resolution density
density_map = DensityMap(sys.argv[1], (128, 128))

plt.imshow(density_map.density)
plt.savefig("web/figures/density.png", bbox_inches="tight", transparent=True)

# Calculate lower resolution density and optimize mast positions
density_map = DensityMap(sys.argv[1])
mast_ranges = density_map.get_suggested_mast_ranges()

optimizer = MastPositionOptimizer(density_map, mast_ranges)

optimizer.run(2, 10)
