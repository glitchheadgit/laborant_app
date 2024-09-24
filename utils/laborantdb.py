from pymongo import MongoClient
from datetime import datetime


def db_create_file(db, user_id, file_type, content, rating=None):
    # file types = {0: 'PDF', 1: 'DOCX', 2: 'Analysis table', 3: 'Analysis'}
    # возможна оценка analysis с помощью rating
    file = {
        "user_id": user_id,
        "type": file_type,
        "content": content,
        'rating': rating
    }

    result = db.files.insert_one(file)
    return result.inserted_id


def db_create_user(db, user_id):
    if not db.users.find_one({"user_id": user_id}):
        user = {
            'user_id': user_id,
            'profiles': [],
            "statistics": {
                'registration_date': datetime.now(),
                'analyses_counter': 0,
                'users_invited': 0,
                'free_jobs': 0
            }
        }

        result = db.users.insert_one(user)
        return result.inserted_id
    return None


def db_add_user_profile(db, user_id, name, sex, age, healthy, diseases=None):
    existing_profiles = db.users.find_one({'user_id': user_id}, {'profiles': 1})
    if existing_profiles and len(existing_profiles) < 5:
        profile = {
            'name': name,
            'sex': sex,
            'age': age,
            'healthy': healthy,
            'diseases': diseases
        }

        result = db.users.update_one(
            {'user_id': user_id}, {'$addToSet': {'profiles': profile}}
        )
        return result.inserted_id
    
    return None


def db_delete_user_profile(db, user_id, profile_name):
    result = db.users.update_one(
        {'user_id': user_id},
        {'$pull': {'profiles': {'name': profile_name}}}
    )
    
    return result.modified_count > 0