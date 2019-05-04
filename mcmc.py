#%%
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt

#%%
url = 'https://xgis.maaamet.ee/xgis2/service/32g9/mit?service=WMS&request=GetMap&layers=nDSM&styles=&format=image%2Fpng&transparent=true&version=1.1.1&width=1024&height=1024&srs=EPSG%3A3301&bbox=657000,6472000,661000,6476000'
response = requests.get(url)
imgPIL = Image.open(BytesIO(response.content))

#%%
original = np.array(imgPIL)
np.unique(original.flatten())
#plt.hist(original.flatten())
plt.imshow(original)


#%%
mask = original > 3 
img = np.zeros((1024, 1024))
img[~mask] = 0
img[mask] = 1  
plt.imshow(img)

#%%

def get_density_map(original, min_building_height, size=(128, 128)):
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
plt.imshow(get_density_map(original, 3))