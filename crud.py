#!/home/tea/venv2.7/bin/python2.7

__author__ = 'vic'

from pymongo import MongoClient, errors



class MongoDriver:

    mongo_server = {"host": "localhost", "port": 27017}

    def __init__(self):
        pass

    def MongoConnection(self):
        """
        mongo_server: host , port

        @return:
        """
        return MongoClient(host=self.mongo_server['host'], port=self.mongo_server['port'])


class MongoCRUD:
    """
    @author V
    """

    def __init__(self):
        md = MongoDriver()
        self.con = md.MongoConnection()

    def save_map_data_update(self, results):
        db = self.con.map_data
        try:
            db.google_places.insert(results, save=True)
        except errors.DuplicateKeyError:
            for r in results:
                db.google_places.update({'id': r['id']}, {'$set': {'reference': r['reference']}}, upsert=True, safe=True)
        # close connection
        self.con.close()

    def save_map_data_insert(self, results):
        db = self.con.map_data
        for r in results:
            try:
                db.google_places.insert(r, save=True)
                db.google_places.ensureIndex({'id':1},{"unique":true, "dropDups":true});
            except errors.DuplicateKeyError, e:
                print 'save_map_data_insert errors.DuplicateKeyError', e
        # close connection
        self.con.close()
    def save_html_insert(self,item):
        db = self.con.map_data
        try:
            db.google_places.insert(r, save=True)
            db.google_places.ensureIndex({'id':1},{"unique":true, "dropDups":true});
        except errors.DuplicateKeyError, e:
            print 'save_map_data_insert errors.DuplicateKeyError', e
        self.con.close()


    def save_circle_center(self, result):
        db = self.con.map_data
        try:
            db.google_circle_center.insert(result, save=True)
        except errors.DuplicateKeyError, e:
            print 'pymongo errors.DuplicateKeyError',

    def save_circle_centers(self, results):
        db = self.con.map_data
        for result in results:
            try:
                db.google_circle_center.insert(result, save=True)
            except errors.DuplicateKeyError, e:
                print 'pymongo errors.DuplicateKeyError', e

    def read_all_locations(self):
        db = self.con.map_data
        return db.google_circle_center.find({'status': '0'}, timeout=False)

    def update_location_status(self, _id):
        db = self.con.map_data
        db.google_circle_center.update({'_id': _id}, {'$set': {'status': '1'}}, upsert=False)


