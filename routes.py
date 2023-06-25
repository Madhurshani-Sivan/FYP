import ast
import json
from fastapi import APIRouter
from db import get_courselist_collection, get_uni_location_collection, get_all_courses_collection, get_eligible_courses_collection
import pandas as pd
from functions import al, ThreeZero_TwoOne, TwoOne_OneTwo, ThreeZero_TwoOne_OneTwo


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

@router.get('/eligible_courses')
def get_eligible_courses():
    student = {
        "stream":"Commerce",
        "ol": {
            "English":"A",
            "Maths":"A",
            "Science":"A"
        },
        "al": [
            {
                "sub": "Economics",
                "results":"A"
            },
            {
                "sub": "Accounting",
                "results":"A"
            },
            {
                "sub": "ICT",
                "results":"A"
            }
        ]
    }
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

    universities_collection = get_uni_location_collection()
    universities = universities_collection.find({}, {'code': 1, 'name': 1})
    universities = pd.DataFrame(universities)
    universities.drop('_id', inplace=True, axis=1)

    combined_dataframes = []

    eligible_courses = pd.DataFrame(results_after_TZ_TO_OT)

    for _, row in eligible_courses.iterrows():
        code = str(row['code'])
        uni = row['uni']
        code = code.zfill(3)
        df = pd.DataFrame({'code': [code + val for val in uni], 'course': row['course']})
        df['university'] = df['code'].str[-1].map(universities.set_index('code')['name'])
        combined_dataframes.append(df)

    eligible_courses = pd.concat(combined_dataframes, ignore_index=True)
    eligible_courses = eligible_courses.sort_values('code').drop_duplicates(subset=['code']).reset_index(drop=True)

    eligible_courses['code'] = eligible_courses['code'].astype(str)
    eligible_courses['course'] = eligible_courses['course'].astype(str)
    eligible_courses['university'] = eligible_courses['university'].astype(str)

    return eligible_courses.to_dict(orient='records')

    #df_courses = pd.DataFrame(results_after_TZ_TO_OT)
    #df_courses.drop('_id', inplace=True, axis=1)
    #df_courses.drop('al', inplace=True, axis=1)
    #df_courses.drop('30-21', inplace=True, axis=1, errors='ignore')
    #df_courses.drop('21-12', inplace=True, axis=1, errors='ignore')
    

