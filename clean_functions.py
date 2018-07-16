import xml.etree.cElementTree as ET
from helper_functions import clean
#filename = 'C:/Users/butte/Documents/Udacity/P3/Project/map_sample'

def unique_k(filename, k):
    """takes an OSM file and given tag key and returns as unique
    set of values for that file and key
    filename - string
    k - string
    returns a set """
    k_set = set()
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == k:
                    k_set.add(clean(str((tag.attrib['v'].encode()))))
    return k_set

def clean_street_names(tag, expected_names, mapping):
    """function that takes a dictionary of tags and cleans street names according to the mapping supplied.
    Returns corrected tag_dict.
    tag - dict of tags - must be labelled with key and value
    expected_names - list of names that are accepted
    mapping - dict of erroneous names and corrections"""
    if tag['key'] == 'street':
        street_type = (str(tag['value']).split(' '))[-1]
        if street_type not in expected_names:
            try:
                new_name = tag['value'].replace(street_type,mapping[street_type])
                tag['value'] = new_name
            except(KeyError):
                print(street_type + ' NOT CLEANED')
    return tag


def clean_sports(tag, expected_names, mapping):
    """function that takes a dictionary of tags and cleans sports according to the mapping supplied.
    Returns corrected tag dictionery.
    tag - dict of tags - must be labelled with key and value
    expected_names - list of names that are accepted
        mapping - dict of erroneous names and corrections"""
    if tag['key'] == 'sport':
        sport_type = str(tag['value'])
        if sport_type not in expected_names:
            try:
                new_name = tag['value'].replace(sport_type,mapping[sport_type])
                tag['value'] = new_name
            except(KeyError):
                print(sport_type + ' NOT CLEANED (sport)')
    return tag

def clean_oneway(tag):
    """function that takes a dictionary of tags and cleans
    oneway definitions to be yes or no only. Returns 'unclassified'
     as value if yes or no not supplied
    tag - dict of tags - must be labelled with key and value"""
    expected_names = ['yes','no']
    if tag['key'] == 'oneway':
        oneway_type = str(tag['value'])
        if oneway_type not in expected_names:
            tag['value'] = 'unclassified'
    return tag

def add_postcode_to_suburb(tag_list,postcode_list):
    """Takes a dictionary of tag dictionaries for a given node and adds a postcode for a given suburb,
    according to the postcode list, if the tag has a suburb listed
    tag - dictionery of dictioneries of tags. Must be labeled key and value
    postcode_list - dictionary of suburbs as keys and postcodes as values"""
    change = False
    for tag in tag_list:
        if (tag['key'] == 'place') and (tag['value'] == 'suburb'):
            change = True
            tag_id = tag['id']
            tag_type = tag['type']
        if tag['key']  == 'name':
            suburb = tag['value']
    if change:
        try:
            postcode = postcode_list[suburb]
            tag_dict = {'id':tag_id,'value':postcode,'key':'postcode','type':tag_type}
            new_tag_list = tag_list.append(tag_dict)
            return tag_list
        except(KeyError):
            return tag_list
    else:
        return tag_list
