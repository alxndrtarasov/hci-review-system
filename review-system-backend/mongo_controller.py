import datetime

from pymongo import MongoClient
from pprint import pprint


# pprint library is used to make the output look more pretty


class MongoController:
    def __init__(self, url):
        self.client = MongoClient(url)
        self.db = self.client.places
        # Issue the serverStatus command and print the results
        server_status_result = self.db.command("serverStatus")
        pprint(server_status_result)

    def insert_place(self, name, latitude, longitude, description, img_link):
        place = {
            '_id': latitude + longitude,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
            'img_link': img_link,
            'positive_reviews': {},
            'negative_reviews': {},
            'tags': {},
            'key_phrases': {}
        }
        # Step 3: Insert business object directly into MongoDB via isnert_one
        result = self.db.collection.insert_one(place)
        # Step 4: Print to the console the ObjectID of the new document
        print('Created {0}'.format(result.inserted_id))

        # insert_place(name='Burger & Beer 108', latitude='55.748335', longitude='48.741747',
        #              description='Cozy bar with great cocktails',
        #              img_link='https://avatars.mds.yandex.net/get-altay/998237/2a0000016134c3c9e792c566a6f888b5be75/XXL')
        # insert_place(name='Cacio e vino', latitude='55.747730', longitude='48.741435',
        #              description='Italian restaurant with vegetarian options',
        #              img_link='https://avatars.mds.yandex.net/get-altay/248099/2a0000015c8c36dacb522cb5012232804edc/XXL')
        # insert_place(name='Nashe Mesto', latitude='55.748976', longitude='48.742572',
        #              description='Hookah place with board games',
        #              img_link='https://where2smoke.ru/img/Kazan/nashemestokzn_innipolis/nashemestokzn_innipolis1526841980.jpg')

    def save_review(self, place_id, review_text):
        place = self.db.collection.find_one({'_id': place_id})
        reviews = place['reviews']
        reviews[str(datetime.now())] = review_text
        self.db.collection.find_one_and_update(
            {'_id': place_id}, {'$set': {'reviews': reviews}})

    def get_all_places(self):
        result = []
        for place in self.db.collection.find():
            result.append(place)
        return result


mongo_controller = MongoController("mongodb://35.234.77.26:27017")
mongo_controller.db.collection.remove({})
mongo_controller.insert_place(name='Burger & Beer 108', latitude='55.748335', longitude='48.741747',
                              description='Cozy bar with great cocktails',
                              img_link='https://avatars.mds.yandex.net/get-altay/998237/2a0000016134c3c9e792c566a6f888b5be75/XXL')
mongo_controller.insert_place(name='Cacio e vino', latitude='55.747730', longitude='48.741435',
                              description='Italian restaurant with vegetarian options',
                              img_link='https://avatars.mds.yandex.net/get-altay/248099/2a0000015c8c36dacb522cb5012232804edc/XXL')
mongo_controller.insert_place(name='Nashe Mesto', latitude='55.748976', longitude='48.742572',
                              description='Hookah place with board games',
                              img_link='https://where2smoke.ru/img/Kazan/nashemestokzn_innipolis/nashemestokzn_innipolis1526841980.jpg')
mongo_controller.insert_place(name='Cava', latitude='55.753459', longitude='48.743420',
                              description='Coffee shop',
                              img_link='https://img.localway.ru/scaled/poi/329802/682940/544x286.jpg')
