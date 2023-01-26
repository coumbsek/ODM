import os
import json

from opendm import context
from opendm import io
from opendm import types
from opendm.photo import PhotoCorruptedException
from opendm import log
from opendm import system
from opendm.geo import GeoFile
from shutil import copyfile
from opendm import progress
from opendm import boundary
from cv2 import aruco

def read_coord_file(filepath):
    f = open(filepath, 'r')
    gcps = {}
    for line in f:
        split_line = line.strip().split(";")
        if len(split_line) < 4:
            print("Illegal input: {}".format(line))
            continue
        gcps[int(split_line[3])] = [float(x) for x in split_line[0:3]]
    f.close()
    return gcps

def process_image(image_path, aruco_dict, coords):
    img = cv2.imread(image_path)
    if img is None:
        log.ODM_ERROR('error reading image: {}'.format(image_path))
        return
    # convert image to gray
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # find markers
    params = cv2.aruco.DetectorParameters_create()
    params.minMarkerPerimeterRate = 0.01
    corners, ids, _ = aruco.detectMarkers(img,
                                            aruco_dict,
                                            parameters=params)
    if ids is None:
        log.ODM_ERROR('No markers found on image {}'.format(image_path))
        return

    gcp_lines = []

    for i in range(ids.size):
        j = ids[i][0]
        # calculate center of aruco code
        x = int(round(np.average(corners[i][0][:, 0])))
        y = int(round(np.average(corners[i][0][:, 1])))
        if j in coords:
            gcp_lines.append('{:.3f} {:.3f} {:.3f} {} {} {} {}\n'.format(
                coords[j][0], coords[j][1], coords[j][2],
                x, y, os.path.basename(image_path), j))
        else:
            log.ODM_INFO("No coordinates for {}".format(j))

    return gcp_lines
  
class ODMFindGCPStage(types.ODM_Stage):
    def process(self, args, outputs):
        tree = outputs['tree']

        # get images directory
        images_dir = tree.dataset_raw

        gcp_coord_file = args.find_gcp
        gcps = read_coord_file(gcp_coord_file)

        dict_param = 99
        if dict_param == 99:     # use special 3x3 dictionary
            aruco_dict = aruco.Dictionary_create(32, 3)
        else:
            aruco_dict = aruco.Dictionary_get(args.dict)

        output_file_path = tree.find_gcp_detected
        output_file = open(output_file_path, 'w')
        output_file.write("EPSG:{}".format("2154"))

        lines = []
        with open(tree.dataset_list, 'w') as dataset_list:
            log.ODM_INFO("Loading %s images" % len(path_files))
            path_files = [os.path.join(images_dir, f) for f in files]
            for image in path_files:
                lines.append(process_image(image,aruco_dict,coords))

        output_file.writelines(lines)
        output_file.close()

        exit()
