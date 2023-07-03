from functools import reduce
import json
import numpy as np

import pandas as pd

def common_data(list1, list2):
  result = False
  for x in list1:
    for y in list2:
      if x == y:
        result = True
        return result
  return result

def count_match(list1,list2):
  return reduce(lambda x, y: x+list1.count(y), set(list2), 0)

def al(courses, subs):
  res=[]
  
  for val in courses:
    if(val['al']==[]):
      res.append(val)
    else:
      results = True
      for x in val['al']:
        keys=list(x.keys())
        if(not common_data(subs,keys)):
          results=False
      if(results):
        res.append(val)
  res = pd.DataFrame(res)
  res.drop('al', inplace=True, axis=1)
  res = res.astype(object)
  res = res.applymap(lambda x: int(x) if isinstance(x, np.int64) else x)
  json_data = res.to_json(orient='records')
  
  return json_data

def ThreeZero_TwoOne(courses, subs):
    res = []

    for val in courses:
        if '30-21' in val:
            if val['30-21'] is None:
                res.append(val)  # Skip the processing if '30-21' is None
                continue
            match1 = count_match(list(val['30-21'][0].keys()), subs)
            match2 = count_match(list(val['30-21'][1].keys()), subs)
            if match1 == 3 and match2 == 0:
                res.append(val)
            elif match1 == 2 and match2 == 1:
                res.append(val)
        else:
            res.append(val)

    res = pd.DataFrame(res)
    if '30-21' in res.columns:
        res.drop('30-21', inplace=True, axis=1)    
    res = res.astype(object)
    res = res.applymap(lambda x: int(x) if isinstance(x, np.int64) else x)
    json_data = res.to_json(orient='records')
    return json_data


def TwoOne_OneTwo(courses, subs):
  res=[]

  for val in courses:
    if('21-12' in val):
      if val['21-12'] is None:
          res.append(val)  # Skip the processing if '30-21' is None
          continue
      match1=count_match(list(val['21-12'][0].keys()),subs)
      match2=count_match(list(val['21-12'][1].keys()),subs)
      if(match1==2 and match2==1):
         res.append(val)
      elif(match1==1 and match2==2):
        res.append(val)
    else:
      res.append(val)
  
  res = pd.DataFrame(res)
  if '21-12' in res.columns:
        res.drop('21-12', inplace=True, axis=1)  
  res = res.astype(object)
  res = res.applymap(lambda x: int(x) if isinstance(x, np.int64) else x)
  json_data = res.to_json(orient='records')
  return json_data

def ThreeZero_TwoOne_OneTwo(courses, subs):
  res=[]

  for val in courses:
    if('30-21-12' in val):
      if val['30-21-12'] is None:
          res.append(val)  # Skip the processing if '30-21' is None
          continue
      match1=count_match(list(val['30-21-12'][0].keys()),subs)
      match2=count_match(list(val['30-21-12'][1].keys()),subs)
      if(match1==3 and match2==0):
         res.append(val)
      elif(match1==2 and match2==1):
        res.append(val)
      elif(match1==1 and match2==2):
        res.append(val)
    else:
      res.append(val)
  
  res = pd.DataFrame(res)
  if '30-21-12' in res.columns:
        res.drop('30-21-12', inplace=True, axis=1)  
  res = res.astype(object)
  res = res.applymap(lambda x: int(x) if isinstance(x, np.int64) else x)
  json_data = res.to_json(orient='records')
  return json_data

def convert_float_values(data):
    # Convert float values to valid JSON-compliant values
    def float_handler(x):
        if isinstance(x, float) and (x == float('inf') or x == float('-inf') or x != x):
            return str(x)
        return x

    # Convert the data to JSON string and parse it back
    json_str = json.dumps(data, default=float_handler)
    converted_data = json.loads(json_str)

    return converted_data