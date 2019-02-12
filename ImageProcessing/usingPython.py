import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from scipy import misc

from skimage.morphology import watershed
from skimage.feature import peak_local_max
from skimage.color import rgb2gray
from skimage.filters import (threshold_mean,
                             threshold_otsu, threshold_niblack, threshold_sauvola)


# Generate an initial image with two overlapping circles
x, y = np.indices((20, 20))
x1, y1, x2, y2 = 8, 8, 14, 12
r1, r2 = 6, 5
mask_circle1 = (x - x1)**2 + (y - y1)**2 < r1**2
mask_circle2 = (x - x2)**2 + (y - y2)**2 < r2**2
image = np.logical_or(mask_circle1, mask_circle2)
binary = image
# original = misc.imread('./assets/1_separated.png')
# image = rgb2gray(original)
# thresh_sauvola = threshold_sauvola(image, window_size=25)
# threshold_mean = threshold_mean(image)
# binary = image < threshold_mean

# Now we want to separate the two objects in image
# Generate the markers as local maxima of the distance to the background
distance = ndi.distance_transform_edt(binary)
print(distance)

local_maxi = peak_local_max(distance, indices=False, labels=binary)
print(local_maxi)

markers = ndi.label(local_maxi)[0]
labels = watershed(-distance, markers, mask=binary)
fig, axes = plt.subplots(ncols=3, figsize=(9, 3), sharex=True, sharey=True)
ax = axes.ravel()

ax[0].imshow(binary, cmap=plt.cm.gray, interpolation='nearest')
ax[0].set_title('Overlapping objects')
ax[1].imshow(-distance, cmap=plt.cm.gray, interpolation='nearest')
ax[1].set_title('Distances')
ax[2].imshow(labels, cmap=plt.cm.nipy_spectral, interpolation='nearest')
ax[2].set_title('Separated objects')

for a in ax:
    a.set_axis_off()

fig.tight_layout()
plt.show()
