#!/usr/bin/env python
# -*- coding: utf-8 -*-
#create a dictionary of tags

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import sqlite3
import pandas as pd
from clean_functions import clean_street_names, clean_sports, clean_oneway, add_postcode_to_suburb
from helper_functions import get_element, UnicodeDictWriter, clean, query_builder, fetch_Data
from mapping import postcode_dict, mapping, mapping_sports
from sql_queries import *

### DECLARATIONS ###
OSM_PATH = 'C:/Users/butte/Documents/Udacity/P3/Project/map'

NODES_PATH = "C:/Users/butte/Documents/Udacity/P3/Project/nodes.csv"
NODE_TAGS_PATH = "C:/Users/butte/Documents/Udacity/P3/Project/nodes_tags.csv"
WAYS_PATH = "C:/Users/butte/Documents/Udacity/P3/Project/ways.csv"
WAY_NODES_PATH = "C:/Users/butte/Documents/Udacity/P3/Project/ways_nodes.csv"
WAY_TAGS_PATH = "C:/Users/butte/Documents/Udacity/P3/Project/ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
# category definitions
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

node_types = ['int','float','float','str','int','str','int','str']
node_tag_types = ['int','str','str','str']
ways_types = ['int','str','int','str','str','str']
way_tags_types = ['int','str','str','str']
way_nodes_types = ['int','int','int']
#lists and mapping for cleaning and adding data
expected_names = ["Street", "Avenue", "Drive", "Court", "Place", "Lane", "Road", "Parkway", 'Parade', 'Way','Terrace',
'Crescent', 'Grove','Centre','Close', 'Hill','walworth','Salmon','Damba','Marlyn','Garrick','Shad','Mews']

expected_sports = ['baseball','basketball','bowls', 'canoeing','cricket', 'cycling', 'golf', 'Gym', 'hockey', 'horse_racing',
'long_jump', 'netball', 'rugby', 'running','skating', 'soccer', 'surfing', 'swimming', 'tennis','volleyball','weightlifting',
'fishing']

SQL_DB = "C:/Users/butte/Documents/Udacity/P3/Project/DB.db"

### MAIN FUNCTIONS ###
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    if element.tag == 'node':
        for field in NODE_FIELDS:
            node_attribs[field] = (element.attrib[field])
        for tag in element:
            tag_dict = {}
            #if PROBLEMCHARS.search(tag.attrib['k']):
            tag_dict['id'] = int(node_attribs['id'])
            tag_dict['value'] = tag.attrib['v']
            if LOWER_COLON.search(tag.attrib['k']):
                tag_dict['type'] = tag.attrib['k'].split(':')[0]
                tag_dict['key'] = tag.attrib['k'].split(':')[1]
            else:
                tag_dict['key'] = tag.attrib['k']
                tag_dict['type'] = 'regular'
        # cleans tags_dict before adding to tags
            tag_dict_clean2 = clean_oneway(tag_dict)
            tag_dict_clean1 = clean_street_names(tag_dict_clean2,expected_names,mapping)
            tag_dict_clean = clean_sports(tag_dict_clean1,expected_sports,mapping_sports)
            tags.append(tag_dict_clean)
        tags = add_postcode_to_suburb(tags,postcode_dict) #add postcode to postcode to tags that have a suburb
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for field in WAY_FIELDS:
            way_attribs[field] = element.attrib[field]
        for tag in element:
            count = 0
            if tag.tag == 'tag':
                tag_dict = {}
            #if PROBLEMCHARS.search(tag.attrib['k']):
                tag_dict['id'] = way_attribs['id']
                tag_dict['value'] = tag.attrib['v']
                if LOWER_COLON.search(tag.attrib['k']):
                    tag_dict['type'] = tag.attrib['k'].split(':')[0]
                    tag_dict['key'] = tag.attrib['k'].split(':')[1]
                else:
                    tag_dict['key'] = tag.attrib['k']
                    tag_dict['type'] = 'regular'
                #cleans tag_dict before adding to tags
                tag_dict_clean2 = clean_oneway(tag_dict)
                tag_dict_clean1 = clean_street_names(tag_dict_clean2,expected_names,mapping)
                tag_dict_clean = clean_sports(tag_dict_clean1,expected_sports,mapping_sports)
                tags.append(tag_dict_clean)
            if tag.tag == 'nd':
                way_dict = {}
                way_dict['id'] = way_attribs['id']
                way_dict['node_id'] = way_attribs['id']
                way_dict['position'] = count
        tags = add_postcode_to_suburb(tags,postcode_dict) #add postcode to tags that have suburb
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        for element in get_element(file_in, tags=('node', 'way')):
            try:
                el = shape_element(element)
                if el:
                    if element.tag == 'node':
                        try: #catches errors
                            nodes_writer.writerow(el['node'])
                            node_tags_writer.writerows(el['node_tags'])
                        except:
                            print(el)
                            raise
                    elif element.tag == 'way':
                        ways_writer.writerow(el['way'])
                        way_nodes_writer.writerows(el['way_nodes'])
                        way_tags_writer.writerows(el['way_tags'])
            except (Exception):
                print(str(element))
                raise Exception

def query(name_str,names_list, type_list):
    """runs a query that inserts data into a SQL database"""
    #gets category list in the specified type
    names_data = fetch_Data(('C:/Users/butte/Documents/Udacity/P3/Project/' + name_str + '.csv'), names_list, type_list)
    # runs the sql query
    c.executemany("""INSERT INTO """ + name_str +' ' + query_builder(names_list) + """ VALUES (""" + (len(names_list)-1)*('?,') + """?);""", names_data)
    return query

### running queries and adding data to SQL
process_map(OSM_PATH)
# connecting to SQL database
db = sqlite3.connect(SQL_DB)
c = db.cursor()
# c.execute("DROP TABLE nodes") # these clear the tables from previous additions for testing purposes
# c.execute("DROP TABLE nodes_tags")
# c.execute("DROP TABLE ways")
# c.execute("DROP TABLE ways_tags")
# c.execute("DROP TABLE ways_nodes")
c.execute(SQL_create_tables)
c.execute(SQL_create_table2)
c.execute(SQL_create_table3)
c.execute(SQL_create_table4)
c.execute(SQL_create_table5)

query('nodes', NODE_FIELDS ,node_types)
query('nodes_tags', NODE_TAGS_FIELDS ,node_tag_types)
query('ways', WAY_FIELDS ,ways_types)
query('ways_tags', WAY_TAGS_FIELDS ,way_tags_types)
query('ways_nodes', WAY_NODES_FIELDS ,way_nodes_types)

db.commit()
db.close()
