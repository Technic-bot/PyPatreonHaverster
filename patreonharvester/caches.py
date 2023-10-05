import json

class HarvestCache():
    def __init__(self, file):
        self.file = file
        self.cache = set()

    def persist(self):
        pass

    def load_cache(self):
        pass

    def is_post_present(self, post_id):
        return post_id in self.cache

class JsonCache(HarvestCache):
    def __init__(self, file):
        super().__init__(file)
        self.read_json()
        self.load_cache()
    
    def read_json(self):
        with open(self.file) as json_file:
            self.patreon_data = json.load(json_file)
        return 

    def persist(self):
        with open(self.file, 'w') as json_file:
            json.dump(self.patreon_data, json_file)
        return 

    def load_cache(self):
        for post in self.patreon_data:
            self.cache.add(post['post_id'])

class SqlCache():
    def __init__(self, file):
        super().__init__(file)
        self.read_db()
        self.load_cache()
