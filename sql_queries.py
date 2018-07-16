#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
SQL_DB = "C:/Users/butte/Documents/Udacity/P3/Project/DB.db"

# defining SQL queries
SQL_create_tables = """
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY NOT NULL, lat REAL, lon REAL, user TEXT, uid INTEGER, version TEXT, changeset INTEGER, timestamp TEXT
);"""
SQL_create_table2 = """
    CREATE TABLE nodes_tags (
    id INTEGER, key TEXT, value TEXT, type TEXT,
    FOREIGN KEY (id) REFERENCES nodes(id)
);"""
SQL_create_table3 = """
CREATE TABLE ways (
    id INTEGER PRIMARY KEY NOT NULL, user TEXT, uid INTEGER, version TEXT, changeset INTEGER, timestamp TEXT
);"""
SQL_create_table4 = """
CREATE TABLE ways_tags (
    id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, type TEXT,
    FOREIGN KEY (id) REFERENCES ways(id)
);"""
SQL_create_table5 = """
CREATE TABLE ways_nodes (
    id INTEGER NOT NULL, node_id INTEGER NOT NULL, position INTEGER NOT NULL,
    FOREIGN KEY (id) REFERENCES ways(id),
    FOREIGN KEY (node_id) REFERENCES nodes(id)
);"""

SQL_unique_users = """
SELECT a.user, count(a.uid) from
(SELECT uid, user from nodes UNION ALL SELECT uid, user from ways) a
GROUP BY a.uid;
"""

SQL_number_nodes = """
SELECT count(*) from nodes_tags;
"""
SQL_number_ways = """
SELECT count(id) from ways;
"""

SQL_unique_node_types = """
SELECT key, count(key) from nodes_tags
GROUP BY key
ORDER BY count(key) DESC;
"""

SQL_repeat_contributers = """
SELECT a.uid, a.user, count(*) as num from
(SELECT user, uid FROM nodes UNION ALL SELECT user, uid FROM ways) a
GROUP BY a.uid
HAVING num > 10
"""

SQL_top3_sport = """
SELECT a.value, count(a.value) from
(SELECT value, key FROM nodes_tags UNION ALL SELECT value, key FROM ways_tags) a
WHERE a.key = 'sport'
GROUP BY a.value
ORDER BY count(a.value) DESC
LIMIT 3;
"""

SQL_popular_shop = """
SELECT a.value, count(a.value) from
(SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) a
WHERE a.key = 'shop'
GROUP BY a.value
ORDER by count(a.value) DESC
LIMIT 10
"""

SQL_popular_cuisines = """
SELECT a.value, count(a.value) as num from
(SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) a
WHERE a.key = 'cuisine'
GROUP BY a.value
HAVING num > 1
ORDER by count(a.value) DESC;
"""

SQL_rail_types = """
SELECT value, count(value) FROM ways_tags
WHERE key = 'railway'
GROUP BY value
ORDER BY count(value) DESC;
"""
SQL_postcode_tag="""
SELECT count(*) FROM nodes_tags
WHERE key = 'postcode';
"""

# run queries
db = sqlite3.connect(SQL_DB)
c = db.cursor()
queries = [SQL_unique_users, SQL_number_nodes, SQL_number_ways, SQL_unique_node_types,SQL_top3_sport, SQL_popular_shop,
SQL_popular_cuisines, SQL_rail_types, SQL_repeat_contributers,SQL_postcode_tag]

for query in queries:
    c.execute(query)
    rows = c.fetchall()
    df = pd.DataFrame(rows)
    print(df)
db.close()
