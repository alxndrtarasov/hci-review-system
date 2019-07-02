import datetime
import functools
import json

from wordcloud import WordCloud
from flask import Flask, request, jsonify
from textblob import TextBlob
from random import randint
from pymongo import MongoClient
from ibm_watson import AssistantV2
# Azure
import requests
# pprint is used to format the JSON response
from pprint import pprint

polarity_threshold = 0.5
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG, filename='logs.log')
subscription_key = "013cf56cff2242d389b36cdefca3ed52"
text_analytics_base_url = "https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/"
language = "ru"


class MongoController:
    def __init__(self, url):
        self.client = MongoClient(url)
        self.db = self.client.places
        # Issue the serverStatus command and print the results
        print(self.db.collection.count())

    def save_review(self, place_id, review_text, polarity):
        place = self.db.collection.find_one({'_id': place_id})
        positive_reviews = place['positive_reviews']
        negative_reviews = place['negative_reviews']
        if polarity >= polarity_threshold:
            positive_reviews[str(datetime.datetime.now()).replace('.', '-')] = review_text
            self.db.collection.find_one_and_update(
                {'_id': place_id}, {'$set': {'positive_reviews': positive_reviews}})
        else:
            negative_reviews[str(datetime.datetime.now()).replace('.', '-')] = review_text
            self.db.collection.find_one_and_update(
                {'_id': place_id}, {'$set': {'negative_reviews': negative_reviews}})
        all_reviews_text = ""
        # for review in positive_reviews.values():
        #     all_reviews_text += (" " + review)
        # word_cloud = WordCloud(max_words=100)
        # all_phrases = word_cloud.process_text(all_reviews_text)
        keyphrase_url = text_analytics_base_url + "keyPhrases"
        documents = {"documents": [
            {"id": "1", "language": language,
             "text": review_text}
        ]}
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        response = requests.post(keyphrase_url, headers=headers, json=documents)
        key_phrases_obj = response.json()
        key_phrases = key_phrases_obj["documents"][0]["keyPhrases"]
        place = mongo_controller.db.collection.find_one({'_id': "55.74833548.741747"})
        all_phrases = place["key_phrases"]
        for key_phrase in key_phrases:
            if key_phrase in all_phrases.keys():
                all_phrases[key_phrase] = all_phrases[key_phrase] + 1
            else:
                all_phrases[key_phrase] = 1
        array_for_sort = []
        for key in all_phrases.keys():
            array_for_sort.append((key, all_phrases[key]))

        def tuple_compare(x, y):
            return y[1] - x[1]

        array_for_sort = sorted(array_for_sort, key=functools.cmp_to_key(tuple_compare))
        result = {}
        for_range = 15 if len(array_for_sort) > 15 else len(array_for_sort)
        for i in range(for_range):
            result[array_for_sort[i][0]] = array_for_sort[i][1]
        logging.debug("tags: " + str(result))
        print("tags: " + str(result))
        logging.debug("all: " + str(all_phrases))
        print("all: " + str(all_phrases))
        self.db.collection.find_one_and_update(
            {'_id': place_id}, {'$set': {"key_phrases": all_phrases}})
        self.db.collection.find_one_and_update(
            {'_id': place_id}, {'$set': {"tags": result}})

    def get_places_by_tags(self, tags):
        result = []
        for place in self.get_all_places():
            if any(tag in tags for tag in place["tags"].keys()):
                result.append(place)
        return result

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
        logging.debug('Created {0}'.format(result.inserted_id))
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

    def get_all_places(self):
        result = []
        for place in self.db.collection.find():
            result.append(place)
        return result


app = Flask(__name__)

mongo_controller = MongoController("mongodb://35.234.77.26:27017")

assistant = AssistantV2(
    version='2019-02-28',
    iam_apikey='YD6wUn7f5hX1ZhPiCA_7Y-iVYYoWRWNBLpvuZymjlCOd',
    url='https://gateway-fra.watsonplatform.net/assistant/api'
)

open_sessions = {}


def make_answer(polarity):
    logging.debug('Polarity of review is: ' + str(polarity))
    print('Polarity of review is: ' + str(polarity))
    if polarity >= polarity_threshold:
        answer = {
            # '1': ("Thank you for your feedback! Have a nice day!", ("Thank you", "Спасибо", "Grazie", "ありがとう", "Gracias", "Merci", "Danke")),
            # '2': ("We are glad that you liked everything! Thank you!",("Thank you", "Спасибо", "Grazie", "ありがとう", "Gracias", "Merci", "Danke")),
            # '3': ("Thank you so much for your review! We will be waiting to see you again!",("Thank you", "Спасибо", "Grazie", "ありがとう", "Gracias", "Merci", "Danke"))
            '1': ("Спасибо за ваш отзыв! Желаем вам хорошего дня!",
                  ("Thank you", "Спасибо", "Grazie", "ありがとう", "Gracias", "Merci", "Danke")),
            '2': ("Мы рады, что вам понравилось! Спасибо!",
                  ("Thank you", "Спасибо", "Grazie", "ありがとう", "Gracias", "Merci", "Danke")),
            '3': ("Спасибо большое за ваш отзыв! Ждем вас снова!",
                  ("Thank you", "Спасибо", "Grazie", "ありがとう", "Gracias", "Merci", "Danke"))

        }[str(randint(1, 3))]
        return answer
    else:
        answer = {
            # Не ошибается тот, кто ничего не делает. Спасибо за ваш отзыв!
            '1': ("Дерьмо случается. Приходите еще", (
                "We are sorry", "Нам жаль", "Siamo spiacenti", "申し訳ありません", "Lo sentimos", "Pardon", "Es tut mir Leid")),
            '2': ("Нам жаль, что так вышло! Мы свяжемся с администратором и примем меры. Благодарим за отзыв!", (
                "We are sorry", "Нам жаль", "Siamo spiacenti", "申し訳ありません", "Lo sentimos", "Pardon", "Es tut mir Leid")),
            '3': ("Мы стараемся постоянно становиться лучше, и ваш отзыв нам очень поможет. Спасибо вам огромное!", (
                "We are sorry", "Нам жаль", "Siamo spiacenti", "申し訳ありません", "Lo sentimos", "Pardon", "Es tut mir Leid"))
        }[str(randint(2, 3))]
        return answer


def make_watson_answer(review, polarity, place_id):
    logging.debug('Polarity of review is: ' + str(polarity))
    print('Polarity of review is: ' + str(polarity))
    plus_minus = "+" if polarity >= polarity_threshold else "-"
    if place_id in open_sessions.keys() and open_sessions[place_id] != "":
        session_id = open_sessions[place_id]
    else:
        session_id = assistant.create_session(assistant_id='eeeca3f4-ff14-4412-b588-2da8933c0519').get_result()[
            "session_id"]
        open_sessions[place_id] = session_id
    print(session_id)
    answer = assistant.message(
        assistant_id='eeeca3f4-ff14-4412-b588-2da8933c0519',
        session_id=session_id,
        input={'message_type': 'text', 'text': review + plus_minus}
    ).get_result()["output"]["generic"][0]["text"]
    if "$" in answer:
        assistant.delete_session(
            assistant_id='{assistant_id}',
            session_id='{session_id}'
        ).get_result()
    print(answer)
    return answer.replace("$", "") + plus_minus


def analyze_review(review, place_id):
    # testimonial = TextBlob(review)
    sentiment_url = text_analytics_base_url + "sentiment"
    documents = {"documents": [
        {"id": "1", "language": language,
         "text": review}
    ]}
    headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    response = requests.post(sentiment_url, headers=headers, json=documents)
    sentiments = response.json()
    polarity = sentiments["documents"][0]["score"]
    mongo_controller.save_review(place_id, review, polarity)
    answer = make_watson_answer(review, float(polarity), place_id)

    return answer


@app.route('/')
def hello_world():
    return 'Voice Review Aggregator!'


@app.route("/reviewSystem/places/all", methods=['GET'])
def get_all_places():
    return json.dumps({"places": mongo_controller.get_all_places()}), 200


@app.route("/reviewSystem/places/", methods=['GET'])
def get_places_by_tags():
    tags = request.json["tags"]
    return str(json.dumps({"places": mongo_controller.get_places_by_tags(tags)})), 200


@app.route("/reviewSystem/processReview", methods=['POST'])
def process_review():
    assert request.method == 'POST'
    place_id = request.json["place_id"]
    review_text = request.json["review"]["speech"]
    testimonial = TextBlob(review_text)

    # ast.literal_eval
    return analyze_review(review_text, place_id), 201


if __name__ == '__main__':
    # print(datetime.datetime.now())
    # sentiment_url = text_analytics_base_url + "sentiment"
    # documents = {"documents": [
    #     {"id": "1", "language": language,
    #      "text": "the pizza was cold"}
    # ]}
    # headers = {"Ocp-Apim-Subscription-Key": subscription_key}
    # response = requests.post(sentiment_url, headers=headers, json=documents)
    # sentiments = response.json()
    # polarity = sentiments["documents"][0]["score"]
    # print(datetime.datetime.now())
    app.run()
