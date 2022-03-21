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

def save_images_database(photos, database_file):
    with open(database_file, 'w') as f:
        f.write(json.dumps([p.__dict__ for p in photos]))
    
    log.ODM_INFO("Wrote images database: %s" % database_file)

def load_images_database(database_file):
    # Empty is used to create types.ODM_Photo class
    # instances without calling __init__
    class Empty:
        pass

    result = []

    log.ODM_INFO("Loading images database: %s" % database_file)

    with open(database_file, 'r') as f:
        photos_json = json.load(f)
        for photo_json in photos_json:
            p = Empty()
            for k in photo_json:
                setattr(p, k, photo_json[k])
            p.__class__ = types.ODM_Photo
            result.append(p)

    return result

class ODMFindGCPStage(types.ODM_Stage):
    def process(self, args, outputs):
        outputs['start_time'] = system.now_raw()
        tree = types.ODM_Tree(args.project_path, args.gcp, args.geo)
        outputs['tree'] = tree

        # get images directory
        images_dir = tree.dataset_raw
        photos = reconstruction.photos

