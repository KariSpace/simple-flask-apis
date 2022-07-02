import requests
from google.cloud import storage
import os
from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth
from bson import json_util

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

API_TOKEN = os.environ.get('API_TOKEN')

@auth.verify_token
def verify_token(token):
    if token == API_TOKEN:
        return token

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload():
    request_data = request.get_json()

    bucket_name = request_data['bucket_name']
    source_file_name = request_data['source_file_name']

    fsouse =  source_file_name.split("/")[-1]
    filename = requests.get(source_file_name) 

    open("/tmp/" + fsouse, "wb").write(filename.content)
    stats = os.stat("/tmp/" + fsouse)
    print(stats.st_size)

    if stats.st_size > 10000000:
        os.remove("/tmp/" + fsouse)
        return { "status" : 500, "desctiption" : "max file 10 MB"}

    storage_client = storage.Client.from_service_account_json(
        'creds.json')

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(fsouse)
    # blob.upload_from_filename(fsouse)
    os.remove("/tmp/" + fsouse)
    return { "status" : 200, "url" : blob.public_url}



from pymongo import MongoClient 
import json
from pprint import pprint

@app.route('/user_list', methods=['GET', 'POST'])
def user_list():
    # request_data = request.get_json()
    if 'list_id' in request.args:
            list_id = request.args['list_id']

    # list_id = request_data['list_id']

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING =  os.environ.get('CONNECTION_STRING')
    
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # list_id = "627801b121099dbe5a7c1017"
    results = client.diploma["lists"].find({"list_id": list_id}, {"title":1})

    parsed_res = []

    for obj in results:
        parsed_res.append({
            "_id" : str(obj['_id']),
            "title" : obj['title']
        })

    pprint(parsed_res)
    return json.loads(json_util.dumps({'result': parsed_res}))




if __name__ == '__main__':
   app.run()

