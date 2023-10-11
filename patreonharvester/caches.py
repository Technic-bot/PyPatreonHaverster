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
                'patreon_url': r['patreon_url'],
                'publication_date': r['date']
                }
            post = PatreonPost(**row_dic)
            self.patreon_data.append(post)
        return rows

            



