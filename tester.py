from utils.helpers import *
from config.path_config import *
from pipeline.prediction_pipeline import *
'''
similar_users = find_similar_users(1,
                   USER_WEIGHTS_PATH,
                   USER2USER_ENCODED,
                   USER2USER_DECODED)

print(similar_users)
user_pref = get_user_preferences(1309,RATING_DF,DF)
print(user_pref)'''

print(hybrid_recommendation(10))
