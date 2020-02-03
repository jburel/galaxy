import numpy
import os
import tempfile

from omero.gateway import BlitzGateway

# connect to idr
conn = BlitzGateway('public', 'public',
                    host='ws://idr.openmicroscopy.org/omero-ws',
                    secure=True)
conn.connect()

# get the image
image_id = 1884807
image = conn.getObject("Image", image_id)
print(image.getName())

# example loading one single plane and saving it 
pixels = image.getPrimaryPixels()
plane = pixels.getPlane(0, 0, 0)  # z, c, t

# create tmp directory and copy the plane as npy file
path = tempfile.mkdtemp()
if not os.path.exists(path):
    os.makedirs(path)
filename, file_extension = os.path.splitext(image.getName())
tmp_file = "plane.npy" # os.path.join(path, filename + ".npy")
numpy.save(tmp_file, plane)

print(tmp_file)
conn.close()