#%%
import random
import numpy as np

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from simulation.wms import get_absorption_between_points

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)


class MastPositionOptimizer:
    def __init__(self, density_map, mast_ranges):
        self.density_map = density_map
        self.mast_ranges = mast_ranges

        self.toolbox = base.Toolbox()

        self.toolbox.register("attr_pos", random.random)
        self.toolbox.register("individual", tools.initRepeat, creator.Individual, self.toolbox.attr_pos, n=len(mast_ranges) * 2)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", self.mate)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=0.2, indpb=0.05)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def evaluate(self, p):
        coverage = 0
        size = self.density_map.shape

        for x in np.linspace(0, 1, size[0], False) + 1/size[0]/2:
            for y in np.linspace(0, 1, size[1], False) + 1/size[1]/2:
                for m, m_range in enumerate(self.mast_ranges):
                    a = get_absorption_between_points((
                        min(0, max(size[0] - 1, int(p[m*2]*size[0]))),
                        min(0, max(size[1] - 1, int(p[m*2+1]*size[1])))
                    ), (
                        int(x*size[0]),
                        int(y*size[1])
                    ), self.density_map)

                    d = np.sqrt((p[m*2] - x)**2 + (p[m*2+1] - y)**2)
                    P_r = np.exp(-d/m_range) * a

                    if P_r > 0.36:
                        coverage += 1 + self.density_map[
                            int(x*size[0]),
                            int(y*size[1])
                        ]
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

        for i in range(ngen):
            algorithms.eaSimple(pop,
                self.toolbox,
                cxpb=0.5, mutpb=0.2, ngen=1,
                stats=stats,
                verbose=verbose,
                halloffame=hof)
            
            if not verbose:
                p = list(hof[0])
                
                print("[" + ", ".join([
                    "{ \"x\": %f, \"y\": %f, \"type\": \"%s\" }" % (
                        p[m*2],
                        p[m*2+1],
                        self.get_mast_type(m)
                    ) for m, m_range in enumerate(self.mast_ranges)
                ]) + "]", flush=True)

        return pop, stats, hof
    
    def get_mast_type(self, m):
        if self.mast_ranges[m] > 0.2:
            return "mm-wave"
        
        return "small-cell"
