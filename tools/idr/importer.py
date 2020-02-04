import matplotlib.pyplot as plt
import os

from omero.gateway import BlitzGateway
from omero.constants.namespaces import NSBULKANNOTATIONS


def find_channel_index(image, channel_name):
    found = False
    index = 0
    count = 0
    for channel in image.getChannels():
        name = channel.getLabel()
        if channel_name in name:
            index = count
            found = True
            break
        count = count + 1
    # Check map annotation for information. (this is necessary for some images)
    if not found:
        for ann in image.listAnnotations(NSBULKANNOTATIONS):
            pairs = ann.getValue()
            for p in pairs:
                if p[0] == "Channels":
                    channels = p[1].replace(" ", "").split(";")
                    count = 0
                    for c in channels:
                        values = c.split(":")
                        if channel_name in values:
                            index = count
                            found = True
                            break
                        count = count + 1

    return found, index


def get_valid_region(image, x, y, w, h):
    size_x = image.getSizeX()
    size_y = image.getSizeY()
    if x < 0 or x >= size_x:
        return None
    if y < 0 or y >= size_y:
        return None
    if w < 0 or w > size_x:
        return None
    if h < 0 or h > size_y:
        return None
    if x + w > size_x:
        return None
    if y + h > size_y:
        return None
    # TODO improve if region is not set
    return [x, y, w, h]


def download_plane_as_tiff(image, tile, z, c, t):
    x = int(tile[0])
    y = int(tile[1])
    w = int(tile[2])
    h = int(tile[3])
    if z < 0 or z > image.getSizeZ():
        z = 0
    if t < 0 or t > image.getSizeT():
        t = 0
    region = get_valid_region(image, x, y, w, h)
    pixels = image.getPrimaryPixels()
    selection = pixels.getTile(theZ=z, theT=t, theC=c, tile=region)

    # save the crop image as TIFF
    filename, file_extension = os.path.splitext(image.getName())
    name = filename + "_" + str(image.getId()) + '_'.join(tile) + ".tiff"
    plt.imsave(name, selection)


def parse_ids(ids):
    # check if we have a list of comma separated id
    remote_url = False
    if remote_url:
        print("not supported yet")
    else:
        return ids.replace(" ", "").split(",")


def main():

    ids = parse_ids("1884807")
    channel_name = "PCNT"
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

    # Retrieve the images
    for image_id in ids:
        image = conn.getObject("Image", image_id)
        print(image.getName())
        found, channel_index = find_channel_index(image, channel_name)
        if found:
            download_plane_as_tiff(image, tile, z_section, channel_index, timepoint)

    conn.close()


if __name__ == "__main__":
    main()
