# Retrieves data from external data source applications and stores in a dataset file.
# Data source application parameters are temporarily stored in the dataset file.
import os
import socket
import sys
from json import dumps, loads

#from galaxy.jobs import TOOL_PROVIDED_JOB_METADATA_FILE
#from galaxy.util import get_charset_from_http_headers
print(sys.executable)

from omero.gateway import BlitzGateway
import numpy

GALAXY_PARAM_PREFIX = 'GALAXY'
GALAXY_ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
GALAXY_DATATYPES_CONF_FILE = os.path.join(GALAXY_ROOT_DIR, 'datatypes_conf.xml')


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def load_input_parameters(filename, erase_file=True):
    datasource_params = {}
    try:
        json_params = loads(open(filename, 'r').read())
        datasource_params = json_params.get('param_dict')
    except Exception:
        json_params = None
        for line in open(filename, 'r'):
            try:
                line = line.strip()
                fields = line.split('\t')
                datasource_params[fields[0]] = fields[1]
            except Exception:
                continue
    if erase_file:
        open(filename, 'w').close()  # open file for writing, then close, removes params from file
    return json_params, datasource_params


def __main__():
    filename = sys.argv[1]
    try:
        max_file_size = int(sys.argv[2])
    except Exception:
        max_file_size = 0

    job_params, params = load_input_parameters(filename)
    if job_params is None:  # using an older tabular file
        enhanced_handling = False
        job_params = dict(param_dict=params)
        job_params['output_data'] = [dict(out_data_name='output',
                                          ext='data',
                                          file_name=filename,
                                          extra_files_path=None)]
        # job_params['job_config'] = dict(GALAXY_ROOT_DIR=GALAXY_ROOT_DIR, GALAXY_DATATYPES_CONF_FILE=GALAXY_DATATYPES_CONF_FILE, TOOL_PROVIDED_JOB_METADATA_FILE=TOOL_PROVIDED_JOB_METADATA_FILE)
    else:
        enhanced_handling = True
        json_file = open(job_params['job_config']['TOOL_PROVIDED_JOB_METADATA_FILE'], 'w')  # specially named file for output junk to pass onto set metadata

    URL = params.get('URL', None)  # using exactly URL indicates that only one dataset is being downloaded
    URL_method = params.get('URL_method', None)

    # The Python support for fetching resources from the web is layered. urllib uses the httplib
    # library, which in turn uses the socket library.  As of Python 2.3 you can specify how long
    # a socket should wait for a response before timing out. By default the socket module has no
    # timeout and can hang. Currently, the socket timeout is not exposed at the httplib or urllib2
    # levels. However, you can set the default timeout ( in seconds ) globally for all sockets by
    # doing the following.
    socket.setdefaulttimeout(600)

    for data_dict in job_params['output_data']:
        # connect to idr
        conn = BlitzGateway('public', 'public',
                            host='ws://idr.openmicroscopy.org/omero-ws',
                            secure=True)
        conn.connect()

        # get the image
        image_id = 1884807
        image = conn.getObject("Image", image_id)
        print(image.getName())
        pixels = image.getPrimaryPixels()
        plane = pixels.getPlane(0, 0, 0)  # z, c, t
        tmp_file = "plane.npy" 
        numpy.save(tmp_file, plane)
        conn.close()
        data_dict['out_data_name'] = tmp_file
        info = dict(type='dataset',
                        dataset_id=data_dict['dataset_id'],
                        ext="data")

        json_file.write("%s\n" % dumps(info))



if __name__ == "__main__":
    __main__()
