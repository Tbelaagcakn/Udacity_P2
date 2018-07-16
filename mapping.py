#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from durbanpc import html_doc
# import html document that contains postcodes for Durban, Westville, Chatworth and Pinetown
soup = BeautifulSoup(html_doc,'html.parser')
text = soup.get_text().strip()
text_list = text.split('\n')
#create a dictionery of postcodes to be used for mapping
count = 0
postcode_dict = {}
for i in text_list:
    # allows for satellite extensions of Durban to be included
    if ('DURBAN' in i) or 'WESTVILLE' in i or 'CHATSWORTH' in i or 'PINETOWN' in i:
        suburb = text_list[count+1].strip('\t').lower().title()
        postcode = text_list[count+3].strip('\t')
        postcode_dict[suburb]=postcode
    count = count + 1

#street name mapping
mapping= {'Rd':'Road','Cresent':'Crescent'}

#sports mapping
mapping_sports = {'field_hockey':'hockey','skateboard':'skating','rugby_league':'rugby','rugby_union':'rugby',
'long_jumpMoses Mabhida Stadium':'long_jump','canoe':'canoeing','multi':'multiple','Salmon':'fishing','Shad':'fishing',
'squash;indor_pool':'multi','rc_car':'driving'}
