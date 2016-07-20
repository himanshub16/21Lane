import os
import sys
import json

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir\
(path)]
    else:
        d['type'] = "file"
        d['size'] = os.path.getsize(path)/1024
    return d

open('sample.json', 'w').write( json.dumps(path_to_dict(sys.argv[1]), indent=2) )