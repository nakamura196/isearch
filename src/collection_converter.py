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
        'collection_uri',
        action='store',
        type=str,
        help='collection uri.')

    parser.add_argument(
        'output_file_path',
        action='store',
        type=str,
        help='output file path.')

    parser.add_argument(
        'tmp_dir_path',
        action='store',
        type=str,
        help='tmp dir path.')

    return parser.parse_args(args)

args = parse_args()

collection_uri = args.collection_uri

opath = args.output_file_path

tmp_dir = args.tmp_dir_path

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


def exec2collection(collection_uri):

    print(collection_uri)

    collection_uri = urllib.parse.quote(collection_uri, safe='/:?=')

    try:
        response = urllib.request.urlopen(collection_uri)
    except Exception as e: ###おかしい
        print(e)

    collection = json.loads(response.read().decode('utf8'))

    if "collections" in collection:
        for c in collection["collections"]:
            exec2collection(c["@id"])
    else:
        exec2manifest(collection["manifests"])


def exec2manifest(manifests):
    for i in range(len(manifests)):

        manifest_uri = manifests[i]["@id"]

        print(str(i+1)+"/"+str(len(manifests)))

        id = hashlib.md5(manifest_uri.encode('utf-8')).hexdigest()

        tmp_file = tmp_dir+"/"+id+".json"

        if not os.path.exists(tmp_file):

            response = urllib.request.urlopen(manifest_uri)
            manifest = json.loads(response.read().decode('utf8'))

            f2 = open(tmp_file, 'w')
            json.dump(manifest, f2, ensure_ascii=False, indent=4,
                    sort_keys=True, separators=(',', ': '))
        else:

            try:
                with open(tmp_file) as f:
                    manifest = json.load(f)
            except Exception as e:
                print(tmp_file+"\t"+e)
                continue


        thumbnail = None
        if "thumbnail" in manifest:
            if "@id" in manifest["thumbnail"]:
                thumbnail = manifest["thumbnail"]["@id"]
            else:
                thumbnail = manifest["thumbnail"]

        fulltext = ""

        obj = {
            "_label": manifest["label"],
            "_manifest": manifest["@id"]
        }

        obj["_thumbnail"] = thumbnail

        if "related" in manifest:
            obj["_related"] = manifest["related"]

        if "description" in manifest:
            obj["_description"] = manifest["description"]

        if "metadata" in manifest:
            for metadata in manifest["metadata"]:
                label = metadata["label"]
                value = metadata["value"]

                if label == "description":
                    label = "description_"

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


exec2collection(collection_uri)

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
