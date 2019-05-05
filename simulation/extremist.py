#%%
import random
import numpy as np

from simulation.parameters import *


class MastPositionOptimizer:
    def __init__(self, density_map, mast_ranges, fixed_p=[], weigh_density=False):
        self.density_map = density_map
        self.mast_ranges = mast_ranges
        self.fixed_p = fixed_p
        self.weigh_density = weigh_density

    def evaluate(self, p):
        coverage = 0
        size = self.density_map.density.shape
        p = np.concatenate((self.fixed_p, p))

        for x in np.linspace(0, 1, size[0], False) + 1/size[0]/2:
            for y in np.linspace(0, 1, size[1], False) + 1/size[1]/2:
                for m, m_range in enumerate(self.mast_ranges):
                    P_r = self.density_map.get_received_intensity(
                        (x, y),
                        (p[m*2], p[m*2+1]),
                        m_range
                    )

                    if P_r > MIN_RECEIVED_INTENSITY:
                        if self.weigh_density:
                            coverage += np.exp(self.density_map.get_density((x, y)))
                        else:
                            coverage += 1
                        break

        return coverage,

    def mate(self, ind1, ind2):
        size = len(ind1)
        cxpoint1 = random.randint(1, size)
        cxpoint2 = random.randint(1, size - 1)
        if cxpoint2 >= cxpoint1:
            cxpoint2 += 1
        else: # Swap the two cx points
            cxpoint1, cxpoint2 = cxpoint2, cxpoint1

        ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
            = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()

        return ind1, ind2

    def run(self, npop=300, ngen=20, verbose=False):
        pop = self.toolbox.population(n=npop)
        hof = tools.HallOfFame(1, similar=np.array_equal)
    
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)
        
        if verbose:
            algorithms.eaSimple(pop,
                self.toolbox,
                cxpb=0.5, mutpb=0.2, ngen=ngen,
                stats=stats,
                verbose=True,
                halloffame=hof)

        else:
            for i in range(ngen):
                algorithms.eaSimple(pop,
                    self.toolbox,
                    cxpb=0.5, mutpb=0.2, ngen=1,
                    verbose=False,
                    halloffame=hof)
                
                if not verbose:
                    p = self.fixed_p + list(hof[0])
                    
                    print("[" + ", ".join([
                        "{ \"x\": %f, \"y\": %f, \"type\": \"%s\" }" % (
                            p[m*2],
                            p[m*2+1],
                            self.get_mast_type(m)
                        ) for m, m_range in enumerate(self.mast_ranges)
                    ]) + "]", flush=True)

        return pop, stats, hof
    
    def get_mast_type(self, m):
        if self.mast_ranges[m] > SMALL_CELL_RANGE:
            return "mm-wave"
        
        return "small-cell"

#%%
if __name__ == "__main__":
    from simulation.density_map import get_test_density_map

    density_map = get_test_density_map()
    mast_ranges = [500, 500, 100, 100, 100, 100]

    optimizer = MastPositionOptimizer(density_map, mast_ranges)

    pop, stats, hof = optimizer.run(100, 10, True)

    density_map.plot_coverage(mast_ranges, list(hof[0]))
