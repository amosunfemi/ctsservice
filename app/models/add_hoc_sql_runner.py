__author__ = 'sundayamosun'

import db_strings as db_strings
from flask.ext.restful import reqparse, abort, Resource
from app import db
from flask import Flask, jsonify, abort, request, make_response, url_for
from sqlalchemy.sql import text


def loadDbStrings():
    retdict = dict()
    for key in dir(db_strings):
        if key.isupper():
            retdict[key] = getattr(db_strings, key)

    return retdict

config_dict = loadDbStrings()

class ScalarQuery(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dbstring_code', type = str, required = True, help = 'No Maintained SQL Code', location = 'form')
        super(ScalarQuery, self).__init__()

    def get(self, dbstring_code):
        print request.args
        param_dict = self.getRequestArgValues(request.args)
        config_dict = loadDbStrings()
        if dbstring_code in config_dict:
            seq_query = config_dict[dbstring_code]
            seqval = db.engine.execute(text(seq_query), **config_dict).fetchall()[0][0]
            return jsonify(result=seqval)
        return jsonify(result='')

    def getRequestArgValues(self, request_args):
        retdict = dict();
        for k, v in request_args.iteritems():
            retdict[k] = str(v)
        return retdict

class Query(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dbstring_code', type = str, required = True, help = 'No Maintained SQL Code', location = 'form')
        super(Query, self).__init__()

    def get(self, dbstring_code):
        print config_dict
        param_dict = self.getRequestArgValues(request.args)


        if dbstring_code in config_dict:
            seq_query = config_dict[dbstring_code]
            print seq_query
            seqval = db.engine.execute(text(seq_query), **config_dict).fetchall()
            return seqval
        return jsonify(result='')

    def getRequestArgValues(self, request_args):
        retdict = dict();
        for k, v in request_args.iteritems():
            retdict[k] = str(v)
        return retdict