import matplotlib.pyplot as plt
import os
import sys

from omero.gateway import BlitzGateway


def main():
    image_id = 1884807
    channel_name = "DAPI"
    z_section = 0
    timepoint = 0
    region = "0, 0, 10, 20"

    # prepare the area to load
    tile = region.replace(" ", "").split(",")

    # connect to idr
    conn = BlitzGateway('public', 'public',
                        host='ws://idr.openmicroscopy.org/omero-ws',
                        secure=True)
    conn.connect()

    # get the image
    #image_id = 1884807
    image = conn.getObject("Image", image_id)
    print(image.getName())

    # example loading one single plane and saving it 
    pixels = image.getPrimaryPixels()
    # add control
    x = int(tile[0])
    y = int(tile[1])
    w = int(tile[2])
    h = int(tile[3])

    # Get the channel information
    # Check if it is the channel metadata if not in the map annotation
    
    # Determine channel by name
    selection = pixels.getTile(theZ=z_section, theT=timepoint, theC=0, tile=[x, y, h, w])

    # save the crop image as TIFF
    filename, file_extension = os.path.splitext(image.getName())
    name = filename + "_" + str(image.getId()) + '_'.join(tile) + ".tiff"
    plt.imsave(name, selection)
    conn.close()


if __name__ == "__main__":
    main()
