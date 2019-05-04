#%%
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
from random import randint, random

#%%
url = 'https://xgis.maaamet.ee/xgis2/service/32g9/mit?service=WMS&request=GetMap&layers=nDSM&styles=&format=image%2Fpng&transparent=true&version=1.1.1&width=1024&height=1024&srs=EPSG%3A3301&bbox=657000,6472000,661000,6476000'
response = requests.get(url)
imgPIL = Image.open(BytesIO(response.content))

#%%
original = np.array(imgPIL)
plt.imshow(original)

#%%
def get_density_map(original, min_building_height=2, size=(128, 128)):
    img = np.zeros(original.shape)
    mask = original > min_building_height

    img[~mask] = 0
    img[mask] = 1  

    total = np.zeros(size)
    dx = original.shape[0] // size[0]
    dy = original.shape[1] // size[1]

    for x in range(dx):
        for y in range(dy):
            total += img[x::dx, y::dy]

    smoothed = total / dx / dy

    return smoothed

#%%
for i in range(10):
    plt.figure(i)
    plt.imshow(get_density_map(original, i))

#%%
plt.imshow(get_density_map(original, 2, (128, 128)))

#%%
def get_fitness(density_map, masts):
    coverage = 0

    for x in range(density_map.shape[0]):
        for y in range(density_map.shape[1]):
            for mast in masts:
                if mast.covers(x, y):
                    coverage += 1

    return coverage / density_map.shape[0] / density_map.shape[1]


def plot_coverage(density_map, masts):
    coverage = np.zeros(density_map.shape)

    for x in range(density_map.shape[0]):
        for y in range(density_map.shape[1]):
            for mast in masts:
                if mast.covers(x, y):
                    coverage[x, y] = 1

    plt.figure(1)
    plt.imshow(density_map)

    plt.figure(2)
    plt.imshow(coverage)

#%%
class Mast:
    def __init__(self, x, y, range):
        self.x = x
        self.y = y
        self.range = range
    
    def covers(self, x, y):
        return (x - self.x)**2 + (y - self.y)**2 < self.range**2


class SmallCellMast(Mast):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
    
    def copy(self):
        return SmallCellMast(self.x, self.y)


class MmWaveMast(Mast):
    def __init__(self, x, y):
        super().__init__(x, y, 25)
    
    def copy(self):
        return MmWaveMast(self.x, self.y)

#%%
def mutate(density_map, X):
    mutation = 4#randint(1, 4)

    # Add small cell mast
    if mutation == 1:
        return X + [SmallCellMast(
            random()*density_map.shape[0],
            random()*density_map.shape[1]
        )]
    
    # Add mm wave mast
    if mutation == 2:
        return X + [MmWaveMast(
            random()*density_map.shape[0],
            random()*density_map.shape[1]
        )]
    
    # Remove mast
    if mutation == 3:
        index = randint(0, len(X) - 1)
        return X[:index] + X[index + 1:]
    
    # Move mast
    if mutation == 4:
        index = randint(0, len(X) - 1)
        copy = X[index].copy()
        #copy.x += (random() - 0.5) * 5
        #copy.y += (random() - 0.5) * 5
        copy.x = random() * density_map.shape[0]
        copy.y = random() * density_map.shape[1]

        if copy.x < 0:
            copy.x = 0
        if copy.x > density_map.shape[0]:
            copy.x = density_map.shape[0]
        if copy.y < 0:
            copy.y = 0
        if copy.y > density_map.shape[1]:
            copy.y = density_map.shape[1]

        return X[:index] + [copy] + X[index + 1:]

#%%
def get_mutation_probability(density_map, X, Y, n):
    X_f = get_fitness(density_map, X)
    Y_f = get_fitness(density_map, Y)

    X_t = 1 / (np.log(n) + 1)
    Y_t = 1 / (np.log(n + 1) + 1)

    return np.exp(Y_f - X_f)

    #return min(1, np.exp(
    #    (Y_f - X_f) * (1/Y_t - 1/X_t)
    #))

#%%
X = [
    MmWaveMast(32, 32),
    SmallCellMast(0, 0),
    SmallCellMast(64, 64)
]

density_map = get_density_map(original, 2, (64, 64))

#%%
n = 0
f = [get_fitness(density_map, X)]
p_values = []
#get_fitness(density_map, X)
#get_fitness(density_map, X), get_fitness(density_map, mutate(density_map, X))
#exp[(coldFit - hotFit)*(1/coldTemp - 1/hotTemp)]

for i in range(100):
    Y = mutate(density_map, X)
    p = get_mutation_probability(density_map, X, Y, n)
    p_values.append(p)

    if random() < p:
        X = Y
        f.append(get_fitness(density_map, X))
        n += 1

plt.plot(f)
X, n

#%%
plt.plot(p_values)

#%%
plot_coverage(density_map, X)

get_fitness(density_map, X)


#%%
n = np.linspace(-0.1, 0.1, 100)

plt.plot(n, np.exp(n))

