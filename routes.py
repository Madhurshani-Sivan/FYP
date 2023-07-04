import ast
import json
from fastapi import APIRouter
from db import get_courselist_collection, get_uni_location_collection, get_all_courses_collection, get_eligible_courses_collection, get_personalities,get_zscore_from_db
import pandas as pd
from functions import al, ThreeZero_TwoOne, TwoOne_OneTwo, ThreeZero_TwoOne_OneTwo
from location import order_universities
import re
from final import add_field_col,extract_paths_for_personality

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

def get_all_courses_with_field():
    collection = get_courselist_collection()
    courses = collection.find({}, {'code': 1, 'course': 1, 'uni': 1, 'field':1})
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

def get_all_universities_with_image():
    collection = get_uni_location_collection()
    universities = collection.find({}, {'code': 1, 'name': 1, 'image':1})
    all_universities = []
    for university in universities:
        university['_id'] = str(university['_id'])  # Convert ObjectId to string
        all_universities.append(university)

    return all_universities

def get_all_universities_with_location():
    collection = get_uni_location_collection()
    universities = collection.find({}, {'code': 1, 'name': 1, 'city':1,'proximity':1,'cost':1})
    all_universities = []
    for university in universities:
        university['_id'] = str(university['_id'])  # Convert ObjectId to string
        all_universities.append(university)

    return all_universities

@router.get('/personalities')
def get_all_personalities():
    collection = get_personalities()
    personalities = collection.find()
    all_personalities = []
    for personality in personalities:
        personality['_id'] = str(personality['_id'])  # Convert ObjectId to string
        all_personalities.append(personality)

    return all_personalities

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

@router.post("/after_image")
def get_eligible_courses_after_image(location_preferences: dict, student: dict, image:dict):
    eligible_courses_after_image = get_eligible_courses_after_location(location_preferences,student)

    image = image.get("image")

    if image == True:
        collection = get_uni_location_collection()
        universities = collection.find({}, {'code': 1, 'image': 1})
        all_universities = []
        for university in universities:
            university['_id'] = str(university['_id'])  # Convert ObjectId to string
            all_universities.append(university)
        sorted_uni = sorted(all_universities, key=lambda x: x["image"], reverse=True)

        sorted_codes = [item["code"] for item in sorted_uni]
        df = pd.DataFrame(eligible_courses_after_image)

        df['numeric_code'] = df['code'].str.extract('(\d+)').astype(int)

        df['alpha_code'] = df['code'].str.extract('(\D+)')
        df['alpha_code'] = df['alpha_code'].map(lambda x: sorted_codes.index(x))

        df = df.sort_values(['numeric_code', 'alpha_code'])

        df = df.drop(['numeric_code', 'alpha_code'], axis=1)

        sorted_data = df.to_dict('records')
        return sorted_data
    
    return eligible_courses_after_image

@router.post("/final")
def get_preference_list(student:dict, personality:dict, reputation:dict, location:dict):
    eligible_courses = get_eligible_courses_as_list(student)

    all_courses = get_all_courses_with_field()

    eligible_courses_with_field = add_field_col(eligible_courses,all_courses)
    
    check_personality = personality.get("check")
    if check_personality:
        personalities = get_all_personalities()
        mbti = personality.get("mbti")
        paths = extract_paths_for_personality(personalities, mbti)
        sorted_courses = sorted(eligible_courses_with_field, key=lambda x: paths.index(x["field"]))
    else:
        sorted_courses = eligible_courses_with_field

    check_reputation = reputation.get("check")
    if check_reputation:
        universities = get_all_universities_with_image()
        importance = reputation.get("importance")
        for university in universities:
            weight = university["image"] * importance
            university["weight"] = weight
        sorted_universities = sorted(universities, key=lambda x: x["weight"], reverse=True)
        sorted_codes = [item["code"] for item in sorted_universities]
        for course in sorted_courses:
            course["uni"] = sorted(course["uni"], key=lambda x: sorted_codes.index(x))
    
    check_location = location.get("check")
    if check_location:
        universities = get_uni_location_collection()
        ordered_universities = order_universities(location, universities, weight)
        for course in sorted_courses:
            course["uni"] = sorted(course["uni"], key=lambda x: ordered_universities.index(x))

    sorted_courses = get_proper_list(sorted_courses)

    return sorted_courses.to_dict('records')

@router.post("/zscore")
def get_zscore(data: dict):
    course = data.get('course')
    district = data.get("district")
    zscore = get_zscore_from_db(course, district)
    if zscore is None:
        return {"error": "Invalid course or district"}
    return {"zscore": zscore}
    

