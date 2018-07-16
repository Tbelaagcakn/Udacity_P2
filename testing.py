#!/usr/bin/env python
# -*- coding: utf-8 -*-
#create a dictionary of tags

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

filename = 'C:/Users/butte/Documents/Udacity/P3/Project/map_sample'

def count_tags(filename):
    tag_dict = {}
    for event,elem in ET.iterparse(filename):
        if elem.tag in tag_dict:
            tag_dict[elem.tag] = tag_dict[elem.tag] + 1
        else:
            tag_dict[elem.tag] = 1
    return tag_dict

tag_dict = count_tags(filename)
#print(tag_dict)

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# looks at street names
def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']) != None:
            keys['lower'] = keys['lower'] +1
            print(element.attrib['k'] + 'lower')
        elif lower_colon.search(element.attrib['k']) != None:
            keys['lower_colon'] = keys['lower_colon'] + 1
            print(element.attrib['k'] + 'lower_c')
        elif problemchars.search(element.attrib['k']) != None:
            keys['problemchars'] = keys['problemchars'] +1
            print(element.attrib['k'] + 'problem')
        else:
            keys['other'] = keys['other'] + 1
            print(element.attrib['k'] + 'other')
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

#print(process_map(filename))

#unique Users

def get_user(element):
    return element.attrib['user'].encode()


def process_map2(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag == 'node' or element.tag == 'way' or element.tag == 'relation':
            user = get_user(element)
            users.add(user)

    return users

def unique_k(filename, k):
    k_set = set()
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == k:
                    k_set.add(tag.attrib['v'])
    return k_set


print(unique_k(filename, 'addr:postcode'))


#print(process_map2(filename))

#fixing street target_names

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons", 'Parade', 'Way','Terrace', 'Crescent']

# UPDATE THIS VARIABLE
mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd": "Road",
            'Cresent':'Crescent',
            }


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding = 'UTF-8')
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types
#pprint.pprint(audit(filename))

def update_name(name, mapping):
    #update the street name
    m = street_type_re.search(name)
    if m:
        street_name = m.group()
        print(street_name)
        map1 = mapping[street_name]
        better_name = name.replace(street_name, map1)

    return better_name

#print(update_name('Rd',mapping))
