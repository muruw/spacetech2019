#%%
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from bresenham import bresenham

from simulation.wms import get_height_map
from simulation.parameters import *


class DensityMap:
    def __init__(self, bbox, density_size=(32, 32), min_building_height=2):
        self.original = get_height_map(bbox)
        self.min_building_height = min_building_height

        # Calculate map size (meters)
        self.corners = [float(coord) for coord in bbox.split(",")]
        self.size = np.array((
            self.corners[2] - self.corners[0],
            self.corners[3] - self.corners[1]
        ))
        self.area = self.size[0] * self.size[1]

        # Get obstacle mask
        img = np.zeros(self.original.shape)
        mask = self.original > min_building_height

        img[~mask] = 0
        img[mask] = 1

        # Estimate density
        self.density = np.zeros(density_size)
        dx = self.original.shape[0] // self.density.shape[0]
        dy = self.original.shape[1] // self.density.shape[1]

        for x in range(dx):
            for y in range(dy):
                self.density += img[x::dx, y::dy]

        self.density /= dx * dy
    
    # Convert normalized (0, 1) coords to map coords
    def get_map_coords(self, p):
        return (
            self.corners[0] + self.size[0] * p[0],
            self.corners[1] + self.size[1] * p[1]
        )
    
    # Convert normalized (0, 1) coords to grid coords
    def get_grid_coords(self, p):
        x = int(p[0] * self.density.shape[0])
        y = int(p[1] * self.density.shape[1])

        return (
            max(0, min(self.density.shape[0] - 1, x)),
            max(0, min(self.density.shape[1] - 1, y))
        )

    # Get absorption between normalized points (0, 1)
    def get_absorption(self, p1, p2):
        g1 = self.get_grid_coords(p1)
        g2 = self.get_grid_coords(p2)

        pixels = np.array(list(
            bresenham(g1[0], g1[1], g2[0], g2[1])
        ))

        a = self.density[pixels[:,0], pixels[:,1]].sum() * ABSORPTION_COEFFICIENT
        dx = (1 / self.density.shape[0] + 1 / self.density.shape[1]) / 2

        return np.exp(-a*dx)

    def plot_absorption(self, p1, p2):
        img = np.zeros(self.density.shape)
        pixels = bresenham(p1[0], p1[1], p2[0], p2[1])

        for p in pixels:
            img[p[0], p[1]] = self.density[p[0], p[1]]
        
        plt.imshow(img)
    
    # Get received intensity from mast at normalized position mast_p
    # and range mast_range
    def get_received_intensity(self, p, mast_p, mast_range):
        a = self.get_absorption(mast_p, p)
        c = self.get_map_coords(p)
        m_c = self.get_map_coords(mast_p)

        d = np.sqrt((c[0] - m_c[0])**2 + (c[1] - m_c[1])**2)
        P_r = np.exp(-d/mast_range) * a

        return P_r
    
    # Get density value at normalized point (0, 1)
    def get_density(self, p):
        g = self.get_grid_coords(p)
        return self.density[g[0], g[1]]
    
    # Get signal strength in grid points
    def get_coverage(self, mast_ranges, p):
        coverage = np.zeros(self.density.shape)
        size = self.density.shape

        for x in np.linspace(0, 1, size[0], False) + 1/size[0]/2:
            for y in np.linspace(0, 1, size[1], False) + 1/size[1]/2:
                P_r = []

                for m, m_range in enumerate(mast_ranges):
                    P_r.append(self.get_received_intensity(
                        (x, y),
                        (p[m*2], p[m*2+1]),
                        m_range
                    ))
                
                coverage[int(x*size[0]), int(y*size[1])] = max(P_r)
        
        return coverage
    
    # Get covered area
    def get_coverage_area(self, mast_ranges, p):
        coverage = self.get_coverage(mast_ranges, p)
        grid_coverage = (coverage > MIN_RECEIVED_INTENSITY).sum()

        return grid_coverage / self.density.shape[0] / self.density.shape[1] * self.area
    
    # Plot coverage results with given mast positions
    def plot_coverage(self, mast_ranges, p, figure=0):
        coverage = self.get_coverage(mast_ranges, p)

        plt.title(str(coverage.sum()))

        plt.figure(figure + 1)
        #plt.imshow(self.original, zorder=2, alpha=0.6)
        plt.imshow(coverage, zorder=1)
        plt.colorbar()

        plt.figure(figure + 2)
        #plt.imshow(self.original, zorder=2, alpha=0.6)
        plt.imshow(coverage > MIN_RECEIVED_INTENSITY, zorder=1)

        plt.plot()
    
    # Get mean density
    def get_mean_density(self):
        return np.mean(self.density)
    
    # Suggest number of masts for area size
    def get_suggested_mast_amount(self, mast_range, area):
        #area = self.size[0] * self.size[1]
        d_coeff = 1 + N_DENSITY_COEFFICIENT * self.get_mean_density()
        n = ceil(area / (np.pi * mast_range**2) * d_coeff)

        #n_mm_wave = ceil(area / (np.pi * MM_WAVE_RANGE**2) * d_coeff)
        #n_small_cell = ceil(
        #    (area - (n_mm_wave/d_coeff - 1) * np.pi * MM_WAVE_RANGE**2) /
        #    (np.pi * SMALL_CELL_RANGE**2)
        #)

        return min(n, MAX_MASTS)

    # Get suggested mast ranges
    def get_suggested_mast_ranges(self):
        n_mm_wave, n_small_cell = self.get_suggested_mast_amounts()

        return [MM_WAVE_RANGE] * n_mm_wave + [SMALL_CELL_RANGE] * n_small_cell

#%%
def get_test_density_map():
    return DensityMap("658000,6473000,660000,6475000")

if __name__ == "__main__":
    density_map = get_test_density_map()

    plt.figure(1)
    plt.imshow(density_map.original)

    plt.figure(2)
    plt.imshow(density_map.density)

    density_map.plot_coverage([500, 500], [0.2, 0.2, 0.5, 0.8], 3)
