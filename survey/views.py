from django.shortcuts import render
from django.http.response import HttpResponse
from secrets_content.files.secret_key import *
import pymongo

client = pymongo.MongoClient(**SURVEY_DATABASES)

db = client.get_database('survey')
post_collection = db.get_collection('survey_post')

def test(request):
    return HttpResponse('test')
