from bson.objectid import ObjectId
from datetime import datetime
from zlib import adler32

from config_reader import config


async def db_create_file(db, user_id, file_type, content, query):
    # file types = {0: 'PDF', 1: 'DOCX', 2: 'Analysis table', 3: 'Analysis'}
    # возможна оценка analysis с помощью rating
    user_id = adler32((user_id).to_bytes(32, 'little'))
    file = {
        "user_id": user_id,
        "type": file_type,
        "content": content,
        "query": query,
        'rating': None
    }

    result = await db.files.insert_one(file)
    return result.inserted_id


async def db_rate_file(db, user_id, analysis_id, rating):
    # file types = {0: 'PDF', 1: 'DOCX', 2: 'Analysis table', 3: 'Analysis'}
    # возможна оценка analysis с помощью rating
    user_id = adler32((user_id).to_bytes(32, 'little'))

    result = await db.files.update_one({'_id': ObjectId(analysis_id)}, {'$set': {'rating': rating}})
    return result.upserted_id


async def db_create_user(db, user_id):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    if not await db.users.find_one({"user_id": user_id}):
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

        result = await db.users.insert_one(user)
        return result.inserted_id
    return False


async def db_add_user_profile(db, user_id, name, sex, age, healthy, diseases=None):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    check = await db.users.find_one({'user_id': user_id, 'profiles.name': name})

    if check is None:
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
        return True

    return False


async def db_find_user_profile(db, user_id, profile_name):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    result = await db.users.find_one(
        {'user_id': user_id, 'profiles.name': profile_name},
        {'profiles.$': 1, '_id': 0}
    )
    if result:
        return result["profiles"][0]
    else:
        return result


async def db_find_user_profiles(db, user_id):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    return await db.users.find_one({'user_id': user_id}, {'_id': 0, 'profiles': 1})


async def db_check_confirmation(db, user_id):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    return not await db.users.find_one({'user_id': user_id}) is None

async def db_delete_user_profile(db, user_id, profile_name):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    result = await db.users.update_one(
        {'user_id': user_id},
        {'$pull': {'profiles': {'name': profile_name}}}
    )

    return result.modified_count > 0


async def db_analysis_inc(db, user_id):
    result = db.users.update_one(
        {'user_id': user_id},
        {'$inc': {'statistics.analyses_counter': 1}}
    )

    return result


async def db_get_jobs(db, user_id):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    return await db.users.find_one({'user_id': user_id}, {'_id': 0, 'statistics.jobs': 1})


async def db_add_jobs(db, user_id, jobs):
    user_id = adler32((user_id).to_bytes(32, 'little'))
    return await db.users.update_one(
        {'user_id': user_id},
        {'$inc': {'statistics.jobs': jobs}}
        )