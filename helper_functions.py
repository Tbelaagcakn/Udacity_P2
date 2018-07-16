#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import xml.etree.cElementTree as ET
import sqlite3
import pandas as pd


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


class UnicodeDictWriter(csv.DictWriter):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, str) else v) for k, v in row.items()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def clean(arg):
    """cleans an argument of the unicode tag"""
    return arg[1:].strip('\'')


def fetch_Data(filename, category_list, type_list):
    """ returns a tuple of data for entering into a SQL database for a list of categories in the correct format
    as specified in the type list
    filename - OSM path in str
    category_list - list of categories in list
    type_list - type (in str) in same order as category_list in list"""
    with open(filename, 'r') as fin:
        dr = csv.DictReader(fin)
        category_list_b = [str("b'" + i +"'") for i in category_list]
        to_db = []
        for d in dr:
            lst = []
            for c in range(len(category_list_b)):
                if d[category_list_b[c]]:
                    category_type = type_list[c]
                    if category_type == 'int':
                        lst.append(int(clean(d[category_list_b[c]])))
                    elif category_type == 'float':
                        lst.append(float(clean(d[category_list_b[c]])))
                    else:
                        lst.append(str(clean(d[category_list_b[c]])))
            tup = tuple(lst)
            to_db.append(tup)
    return(to_db)

def query_builder(lst):
    """returns a string from a list for the query builder"""
    string = '('
    for i in lst:
        string = string + str(i) +','
    string = string[:-1]
    string = string + ')'
    return string
