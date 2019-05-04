#%%
import random
import numpy as np

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


class MastPositionOptimizer:
    def __init__(self, density_map, mast_ranges):
        self.density_map = density_map
        self.mast_ranges = mast_ranges

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", np.ndarray, fitness=creator.FitnessMax)

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

        for x in range(size[0]):
            for y in range(size[1]):
                for m, m_range in enumerate(self.mast_ranges):
                    if (p[m*2] - x/size[0])**2 + (p[m*2+1] - y/size[1])**2 < m_range**2:
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

    def run(self, npop=300, ngen=20):
        pop = self.toolbox.population(n=npop)
        hof = tools.HallOfFame(1, similar=np.array_equal)
        
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)

        algorithms.eaSimple(pop,
            self.toolbox, cxpb=0.5, mutpb=0.2, ngen=ngen, stats=stats,
            halloffame=hof)

        return pop, stats, hof
