import urllib.request
from bs4 import BeautifulSoup
import csv
from time import sleep
import pandas as pd
import json
import urllib.request
import os
from PIL import Image
import glob
import sys
import argparse
import urllib.parse
import hashlib

def parse_args(args=sys.argv[1:]):
    """ Get the parsed arguments specified on this script.
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'curation_uri',
        action='store',
        type=str,
        help='curaion uri.')

    parser.add_argument(
        'output_file_path',
        action='store',
        type=str,
        help='output file path.')

    return parser.parse_args(args)

args = parse_args()

curation_uri = args.curation_uri

response = urllib.request.urlopen(curation_uri)
curation_data = json.loads(response.read().decode('utf8'))

opath = args.output_file_path

size = 10

result = {}
aggregations = {}
aggregations2 = {}

data = []
result["rows"] = data

config = {
    "searchableFields": [],
    "sortings": {
        "Title Asc": {
            "field": '_label',
            "order": 'asc'
        },
        "Title Desc": {
            "field": '_label',
            "order": 'desc'
        }
    },
    "aggregations": aggregations2
}

result["config"] = config

config["searchableFields"].append("_label")
config["searchableFields"].append("_description")
config["searchableFields"].append("_fulltext")


members_= []
selections = curation_data["selections"]

for selection in selections:
    members = selection["members"]

    for member in members:
        members_.append(member)

for i in range(len(members_)):
    member = members_[i]

    label = member["label"]

    fulltext = label

    obj = {
        "_label": label,
        "_related": "http://codh.rois.ac.jp/software/iiif-curation-viewer/demo/?curation="+curation_data["@id"]+"&pos="+str(i+1)
    }

    obj["_thumbnail"] = member["thumbnail"]

    if "metadata" in member:
        for metadata in member["metadata"]:
            label = metadata["label"]
            value = metadata["value"]

            if isinstance(value, list):
                values = value
            else:
                values = [value]

            for value in values:

                if value == None:
                    continue

                value = str(value)

                if "http" not in value:

                    if label not in aggregations:
                        aggregations[label] = {
                            "title": label,
                            "map": {}
                        }

                    if label not in obj:
                        obj[label] = []

                    map = aggregations[label]["map"]

                    if value not in map:
                        map[value] = 0

                    map[value] = map[value] + 1

                    obj[label].append(value)
                    fulltext += " "+value

    obj["_fulltext"] = fulltext
    data.append(obj)



for field in aggregations:
    obj = aggregations[field]
    map = obj["map"]
    map = sorted(map.items(), key=lambda kv: kv[1], reverse=True)

    if map[0][1] > 1 and len(map) != 1:
        aggregations2[field] = {
            "title": obj["title"],
            "size": size
        }

f2 = open(opath, 'w')
json.dump(result, f2, ensure_ascii=False, indent=4,
          sort_keys=True, separators=(',', ': '))