#%%
import matplotlib.pyplot as plt
import numpy as np

from simulation.optimizer import MastPositionOptimizer
from simulation.wms import get_height_map, get_density_map, get_absorption_between_points

#%%
mast_ranges = [0.5] * 4 + [0.05] * 22 #np.random.uniform(0.05, 0.25, 3)
density_map = get_density_map("658000,6473000,660000,6475000", 2, (32, 32))

plt.imshow(density_map)

#%%
660000 - 658000, 6475000 - 6473000

#%%
#1 km, 200 m

#%%
optimizer = MastPositionOptimizer(density_map, mast_ranges)
pop, stats, hof = optimizer.run(25, 5, True)

#%%
def plot_coverage(density_map, mast_ranges, p):
    coverage = np.zeros(density_map.shape)
    size = density_map.shape

    for x in range(size[0]):
        for y in range(size[1]):
            P_r = []

            for m, m_range in enumerate(mast_ranges):
                a = get_absorption_between_points((
                    min(0, max(size[0] - 1, int(p[m*2]*size[0]))),
                    min(0, max(size[1] - 1, int(p[m*2+1]*size[1])))
                ), (
                    x,
                    y
                ), density_map)

                d = np.sqrt((p[m*2] - x/size[0])**2 + (p[m*2+1] - y/size[1])**2)
                P_r.append(np.exp(-d/m_range) * a)
            
            coverage[x, y] = max(P_r)

    plt.title(str(coverage.sum()))
    #img = plt.imshow(density_map, zorder = 2, alpha=0.6)

    plt.figure(1)
    plt.imshow(coverage, zorder = 1)
    plt.colorbar()

    plt.figure(2)
    plt.imshow(coverage > 0.36)

    plt.plot()

plot_coverage(density_map, mast_ranges, list(hof[0]))

#%%
height_map = get_height_map("657000,6472000,661000,6476000")

plt.imshow(height_map, alpha=0.8)

coords = np.array(list(hof[0])) * 1024
coords_big = coords[:10]
coords_small = coords[10:]

plt.scatter(
    coords_big[1::2],
    coords_big[0::2],
    c="red",
    marker="o"
)

plt.scatter(
    coords_small[1::2],
    coords_small[0::2],
    c="red",
    marker="x"
)
