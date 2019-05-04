#%%
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt

#%%
def get_density_map(bbox, min_building_height=2, size=(128, 128)):
    url = "https://xgis.maaamet.ee/xgis2/service/32g9/mit?service=WMS&request=GetMap&layers=nDSM&styles=&format=image%2Fpng&transparent=true&version=1.1.1&width=1024&height=1024&srs=EPSG%3A3301&bbox=" + bbox
    response = requests.get(url)
    original = np.array(Image.open(BytesIO(response.content)))

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

    density = total / dx / dy

    return density
