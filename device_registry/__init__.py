import markdown
import os
import functools
import json
from flask import Flask, g
from flask_restful import Resource, Api, reqparse
from flask.json import JSONEncoder
import shelve

import pandas as pd
import numpy as np

from datetime import datetime

# Flask serves invalid JSON by default. Because everything else in the world uses Python, especially web frontends.
class JSONEncoderthatencodesintoJSONnotintosomeFlaskdevsunilateralextensiontoJSON (JSONEncoder):
    def default(self, obj):
        return simplejson.JSONEncoder().encode(obj)

input_file = 'sample.csv'
debug  = False

app = Flask(__name__)
app.json_encoder = JSONEncoderthatencodesintoJSONnotintosomeFlaskdevsunilateralextensiontoJSON
api = Api(app)

def log (*args):
    if debug:
        print (*args)

## Flask seems to run ya functions through exec, so syntax errors wait til runtime to raise their heads
## Well, at least we can catch them...
# def catch_errors (func):
#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except as ex:
#             template = "An exception of type {0} occurred. Arguments:\n{1!r}"
#             message = template.format(type(ex).__name__, ex.args)
#             print message
#             print ('That shit was an errr..')
#             return {'message': message}, 500
#     return wrapper

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = shelve.open('our.db')
    return db

@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    with open(os.path.dirname(app.root_path) + '/README.md','r') as md_file:
        content = md_file.read()
        print (markdown.markdown(content))
        return markdown.markdown(content)

@app.route('/html')
def html_rand():
    with open(os.path.dirname(app.root_path) + '/README.md','r') as md_file:
        content = md_file.read()
        return "<h1>file!!!</h1><h3>I'm HTML, yo'</h3>", 200


class GetTitleByNumber(Resource):
    # @catch_errors
    def get(self, title_no):
        shelf = get_db()

        log (list(shelf.keys()))
        log ('______________________')
        keys = list(shelf.keys())

        if not (title_no in shelf):
            received_time = datetime.now()
            print ('______________________')
            print (received_time.time(),"Start query "+title_no)
            result = titles[titles['Title Number'] == title_no]
            print (datetime.now().time(),"End query "+title_no)
            if not result.empty:
                def denanify (x):
                    return None if (type(x) == float and np.isnan(x)) else x
                result_dict = dict( zip(result.columns.values, list(map( denanify, result.values[0]) )))
                # result = result.where(pd.notnull(result), "")
                log ("Response data: "+json.dumps(result_dict))
                return {
                    'message': 'Success - '+title_no+' Found',
                    'received': received_time.strftime('%H:%M:%S:%f'),
                    'completed': datetime.now().strftime('%H:%M:%S:%f'),
                    'data': result_dict
                    }, 200

            return {
                'message': 'Fail - '+title_no+' Not Found',
                'received': received_time.strftime('%H:%M:%S:%f'),
                'failed': datetime.now().strftime('%H:%M:%S:%f'),
                'data': {}
                }, 200
        return {
            'message': 'Success',
            'completed': datetime.now().strftime('%H:%M:%S:%f'),
            'data': shelf[title_no]}, 200


class RespondWithRandomness(Resource):
# See docs on inheritance & multiple inheritance (=L to R)
# - RWR is the derived class from the base class Resource
    def get(self):
        shelf = get_db()

        log (list(shelf.keys()))
        log ('______________________')
        keys = list(shelf.keys())

        things = []

        for key in keys:
            things.append(shelf[key])

        return {'message': 'Success', 'data': things}, 200

    def post(self):
        parser = reqparse.RequestParser()
        # will be replaced by marshmallow soon

        parser.add_argument('identifier', required=True)
        parser.add_argument('freesearch', required=False)

        args = parser.parse_args()
        shelf = get_db()
        shelf[args['identifier']] = args

        return {'message': 'Posted', 'data': args}, 201

        return markdown.markdown(content)

class Retrieve(Resource):
    def get(self, identifier, freesearch=None):
        shelf = get_db()

        if not (identifier in shelf) and not (freesearch in shelf):
            return {'message': 'Fail - Not Found', 'data': {}}, 404
        return {'message': 'Success', 'data': shelf[identifier]}, 200

    def delete(self, identifier):
        shelf = get_db()

        if not (identifier in shelf):
            return {'message': 'Fail - Not Found', 'data': {}}, 404
        del shelf[identifier]
        return 'Should not reach here', 204

print (datetime.now().time(),"Loading "+input_file)
titles = pd.read_csv (input_file, dtype='unicode')
# idx= titles.index[titles['Title Number'] == 'Row Count:']
titles.drop (titles.index[titles['Title Number'] == 'Row Count:'])
# titles = titles[titles['Title Number'] != 'Row Count:']
print (datetime.now().time(),"Done :)")

api.add_resource (GetTitleByNumber, '/title/<title_no>')
api.add_resource(RespondWithRandomness, '/random')
api.add_resource(Retrieve, '/retrieve/<string:identifier>')
