def add_field_col(collection, all_collection):
    for course in collection:
        code = course['code']
        for doc in all_collection:
            if code == doc['code']:
                course['field'] = doc['field']
                break
    return collection

def extract_paths_for_personality(collection, personality):
    paths = []
    for item in collection:
        if item['personality'] == personality:
            paths.extend(item['paths'])
    return paths