from fastapi import APIRouter
from db import get_courselist_collection, get_uni_location_collection
import pandas as pd

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