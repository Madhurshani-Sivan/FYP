import ast
import json
from fastapi import APIRouter
from db import get_courselist_collection, get_uni_location_collection, get_all_courses_collection, get_eligible_courses_collection
import pandas as pd
from functions import al, ThreeZero_TwoOne, TwoOne_OneTwo, ThreeZero_TwoOne_OneTwo
from location import order_universities
import re

router = APIRouter()

@router.get('/courses')
def get_all_courses():
    collection = get_courselist_collection()
    courses = collection.find({}, {'code': 1, 'course': 1, 'uni': 1})
    all_courses = []
    for course in courses:
        course['_id'] = str(course['_id'])  # Convert ObjectId to string
        all_courses.append(course)

    return all_courses


@router.get('/universities')
def get_all_universities():
    collection = get_uni_location_collection()
    universities = collection.find({}, {'code': 1, 'name': 1})
    all_universities = []
    for university in universities:
        university['_id'] = str(university['_id'])  # Convert ObjectId to string
        all_universities.append(university)

    return all_universities

@router.get('/all_courses')
def get_all_courses():
    return get_all_courses_collection()

@router.post('/eligible_courses')
def get_eligible_courses(student: dict):
    courses = get_eligible_courses_as_list(student)

    eligible_courses = get_proper_list(courses).sort_values("code")

    return eligible_courses.to_dict(orient='records')


def get_eligible_courses_as_list(student):
    
    courses = get_eligible_courses_collection(student)

    sub1 = student.get("al")[0].get("sub")
    sub2 = student.get("al")[1].get("sub")
    sub3 = student.get("al")[2].get("sub")
    subs=[sub1,sub2,sub3]

    courses = json.loads(courses)

    results_after_al = json.loads(al(courses, subs))
    results_after_TZ_TO = json.loads(ThreeZero_TwoOne(results_after_al, subs))
    results_after_TO_OT = json.loads(TwoOne_OneTwo(results_after_TZ_TO, subs))
    results_after_TZ_TO_OT = json.loads(ThreeZero_TwoOne_OneTwo(results_after_TO_OT, subs))

    return results_after_TZ_TO_OT

def get_proper_list(courses):
    universities_collection = get_uni_location_collection()
    universities = universities_collection.find({}, {'code': 1, 'name': 1})
    universities = pd.DataFrame(universities)
    universities.drop('_id', inplace=True, axis=1)

    combined_dataframes = []

    eligible_courses = pd.DataFrame(courses)

    for _, row in eligible_courses.iterrows():
        code = str(row['code'])
        uni = row['uni']
        code = code.zfill(3)
        df = pd.DataFrame({'code': [code + val for val in uni], 'course': row['course']})
        df['university'] = df['code'].str[-1].map(universities.set_index('code')['name'])
        combined_dataframes.append(df)

    eligible_courses = pd.concat(combined_dataframes, ignore_index=True)
    eligible_courses = eligible_courses.drop_duplicates(subset=['code']).reset_index(drop=True)

    eligible_courses['code'] = eligible_courses['code'].astype(str)
    eligible_courses['course'] = eligible_courses['course'].astype(str)
    eligible_courses['university'] = eligible_courses['university'].astype(str)

    return eligible_courses

@router.post("/after_location")
def get_eligible_courses_after_location(location_preferences: dict, student: dict):
    universities_collection = get_uni_location_collection()
    ordered_universities = order_universities(location_preferences, universities_collection)

    university_codes = [code for code in ordered_universities]

    eligible_courses = get_eligible_courses_as_list(student)
    
    eligible_courses_after_location = get_proper_list(eligible_courses)

    df = pd.DataFrame(eligible_courses_after_location)

    df['numeric_code'] = df['code'].str.extract('(\d+)').astype(int)

    df['alpha_code'] = df['code'].str.extract('(\D+)')
    df['alpha_code'] = df['alpha_code'].map(lambda x: university_codes.index(x))

    df = df.sort_values(['numeric_code', 'alpha_code'])

    df = df.drop(['numeric_code', 'alpha_code'], axis=1)

    sorted_data = df.to_dict('records')
    return sorted_data

    