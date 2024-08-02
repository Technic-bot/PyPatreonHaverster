import json
import sqlite3

from patreon_classes import PatreonPost
from dataclasses import asdict

class HarvestCache():
    def __init__(self, file):
        self.file = file
        self.cache = set()
        self.patreon_data = []

    def persist(self):
        pass

    def load_cache(self):
        for post in self.patreon_data:
            self.cache.add(post.post_id)

    def is_post_present(self, post_id):
        return post_id in self.cache

    def order(self):
        self.patreon_data.sort(reverse=True)

class JsonCache(HarvestCache):
    def __init__(self, file:str = ''):
        super().__init__(file)
        self.read_json()
        self.load_cache()
    
    def read_json(self):
        with open(self.file) as json_file:
            patreon = json.load(json_file)
        for p in patreon:
            post = PatreonPost(**p)
            self.patreon_data.append(post)
        return 

    def persist(self, post_list):
        """ Takes a list of posts and appends to cache before saving"""
        self.patreon_data.extend(post_list)
        self.order()
        with open(self.file, 'w') as json_file:
            json.dump(self.patreon_data, json_file, default=asdict)
        return 

class EmptyJsonCache(JsonCache):
    def __init__(self, file):
        self.file = file
        self.cache = set()
        self.patreon_data = []


class SqlCache(HarvestCache):
    ID_NAME = 'id'
    def __init__(self, file):
        super().__init__(file)
        rows = self.read_db()
        self.load_cache()

    def read_db(self):
        conn = sqlite3.connect(self.file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        sql_stmt = ("SELECT * FROM PATREON")
        rows = cursor.execute(sql_stmt).fetchall()
        conn.close()
        
        for r in rows:
            row_dic = {
                'post_id': int(r[self.ID_NAME]),
                'title' : r['title'],
                'description': r['description'],
                'filename': r['filename'],
                'post_type': r['type'],
                'patreon_url': r['src_url'],
                'publication_date': r['date']
                }
            post = PatreonPost(**row_dic)
            self.patreon_data.append(post)
        return rows

    def persist(self, post_list):
        posts, tags = self.make_sqllite_lists(post_list)
        self.patreon_data.extend(post_list)
        conn = sqlite3.connect(self.file)
        cursor = conn.cursor()
        sql_stmt = ("INSERT OR REPLACE INTO patreon " 
                    "(id, title, description, filename, type, "
                    "src_url, date) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?);")
        cursor.executemany(sql_stmt, posts)

        sql_stmt = ("INSERT OR REPLACE INTO tags (id, tag) "
                    "VALUES (?, ?);")
        cursor.executemany(sql_stmt, tags)
        conn.commit()
        conn.close()
        return

    def make_sqllite_lists(self, post_list):
        """ Turns a bunch of dataclasses into list of tuples for sqlite """
        # consider going sqlalchemy later
        patreon_list = []
        tag_list = []
        for p in post_list:
            tup = (p.post_id, p.title, p.description,
                   p.filename, p.post_type, p.patreon_url,
                   p.publication_date)
            patreon_list.append(tup)

            for tag in p.tags:
                tag_tup = (p.post_id, tag)
                tag_list.append(tag_tup)
        return patreon_list, tag_list
            

