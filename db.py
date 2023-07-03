import json
from bson import ObjectId
import pymongo
from pymongo import MongoClient
import pandas as pd
from functions import convert_float_values
from fastapi.responses import JSONResponse
import numpy as np


def get_courselist_collection():
    uri = 'mongodb+srv://fyp:fyp123@courselist.i0n97yv.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(uri)
    db = client.courselist
    collection = db.courselist
    return collection

def get_uni_location_collection():
    uri = 'mongodb+srv://fyp:fyp123@courselist.i0n97yv.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(uri)
    db = client.courselist
    collection = db.uni_location
    return collection

def get_personalities():
    uri = 'mongodb+srv://fyp:fyp123@courselist.i0n97yv.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(uri)
    db = client.courselist
    collection = db.personalities
    return collection

def get_all_courses_collection():
    courselist_collection = get_courselist_collection()
    universities_collection = get_uni_location_collection()

    courses = courselist_collection.find({}, {'code': 1, 'course': 1, 'uni': 1})
    courses = pd.DataFrame(courses)
    courses.drop('_id', inplace=True, axis=1)

    universities = universities_collection.find({}, {'code': 1, 'name': 1})
    universities = pd.DataFrame(universities)
    universities.drop('_id', inplace=True, axis=1)

    combined_dataframes = []

    for _, row in courses.iterrows():
        code = str(row['code'])
        uni = row['uni']
        code = code.zfill(3)
        df = pd.DataFrame({'code': [code + val for val in uni], 'course': row['course']})
        df['university'] = df['code'].str[-1].map(universities.set_index('code')['name'])
        combined_dataframes.append(df)

    all_courses = pd.concat(combined_dataframes, ignore_index=True)
    all_courses = all_courses.sort_values('code').drop_duplicates(subset=['code']).reset_index(drop=True)

    all_courses['code'] = all_courses['code'].astype(str)
    all_courses['course'] = all_courses['course'].astype(str)
    all_courses['university'] = all_courses['university'].astype(str)

    return all_courses.to_dict(orient='records')

def get_eligible_courses_collection(student):
    student_stream = student.get("stream")

    ol_results = student.get("ol")
    english_grade = ol_results.get("English")
    maths_grade = ol_results.get("Maths")
    science_grade = ol_results.get("Science")

    sub1 = student.get("al")[0]
    sub2 = student.get("al")[1]
    sub3 = student.get("al")[2]

    sub1_subject = sub1.get("sub")
    sub1_results = sub1.get("results")

    sub2_subject = sub2.get("sub")
    sub2_results = sub2.get("results")

    sub3_subject = sub3.get("sub")
    sub3_results = sub3.get("results")


    courselist_collection = get_courselist_collection()

    results_after_ol = courselist_collection.find({"$or": [{"stream": student_stream},{"stream": "Extra"}], \
                                         "$and":[
                                        {"$and":[{ "$or":[{"ol.English":{"$gte":english_grade}},{"ol.English":""}]}, \
                                         {"$or":[{"ol.Maths":{"$gte":maths_grade}},{"ol.Maths":""}]}, \
                                         {"$or":[{"ol.Science":{"$gte":science_grade}},{"ol.Science":""}]}]},\
                                         {"$or":[{"al":[]}, \
                                                 {"$or":[{"al":{"$elemMatch":{sub1_subject:{"$gte":sub1_results}}}},\
                                                             {"al":{"$elemMatch":{sub2_subject:{"$gte":sub2_results}}}},\
                                                  {"al":{"$elemMatch":{sub3_subject:{"$gte":sub3_results}}}},\
                                                  ]}]}, \
                                        {"$or":[{"30-21":{"$exists": False}}, \
                                                 {"$or":[{"30-21":{"$elemMatch":{sub1_subject:{"$gte":sub1_results}}}},\
                                                             {"30-21":{"$elemMatch":{sub2_subject:{"$gte":sub2_results}}}},\
                                                  {"30-21":{"$elemMatch":{sub3_subject:{"$gte":sub3_results}}}},\
                                                  ]}]}, \
                                        {"$or":[{"21-12":{"$exists": False}}, \
                                                 {"$or":[{"21-12":{"$elemMatch":{sub1_subject:{"$gte":sub1_results}}}},\
                                                             {"21-12":{"$elemMatch":{sub2_subject:{"$gte":sub2_results}}}},\
                                                  {"21-12":{"$elemMatch":{sub3_subject:{"$gte":sub3_results}}}},\
                                                  ]}]}, \
                                        {"$or":[{"30-21-12":{"$exists": False}}, \
                                                 {"$or":[{"30-21-12":{"$elemMatch":{sub1_subject:{"$gte":sub1_results}}}},\
                                                             {"30-21-12":{"$elemMatch":{sub2_subject:{"$gte":sub2_results}}}},\
                                                  {"30-21-12":{"$elemMatch":{sub3_subject:{"$gte":sub3_results}}}},\
                                                  ]}]}]}, \
                                        {"code":1,"course":1,"uni":1,"al":1,"30-21":1,"21-12":1,"30-21-12":1})
    
    results_after_ol = pd.DataFrame(results_after_ol)
    results_after_ol.drop('_id', inplace=True, axis=1)
    results_after_ol = results_after_ol.astype(object)
    results_after_ol = results_after_ol.applymap(lambda x: int(x) if isinstance(x, np.int64) else x)
    json_data = results_after_ol.to_json(orient='records')

    return json_data