import config
from modules.BotUtil import BotUtil

bot = BotUtil(config.token, config.creator)
from pymongo import MongoClient

db = MongoClient(config.database)
users = db.stickers.users

import hashlib
import redis

import urllib.parse as urlparse
import os
redis_url = os.getenv('REDISTOGO_URL')
urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
r = redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)

@bot.message_handler(commands=['login'])
def me_handler(m):
    user = users.find_one({'id': m.from_user.id})
    if not user:
        bot.reply_to(m, 'Вы не зарегестрированы. Нажмите /start')
        return
    user_id = str(m.from_user.id) + r.get('salt').decode("utf-8") 
    hash = hashlib.md5(user_id.encode()).hexdigest()
    link = f'lk-contest.herokuapp.com/?id={m.from_user.id}&session={hash}'
    tts = f'Вот ваша ссылка для входа. НИКОМУ ЕЕ НЕ ДАВАЙТЕ!\n{link}'
    bot.reply_to(m, tts)


@bot.message_handler()
def register_handler(m):
    if not users.find_one({'id': m.from_user.id}):
        user = {
            'id': m.from_user.id,
            'stickers': {
                'unsorted': []
            }
        }
        users.insert_one(user)


@bot.message_handler(content_types=['sticker'])
def stickers_handler(m):
    stickers = bot.get_sticker_set(m.sticker.set_name).stickers
    user = users.find_one({'id': m.from_user.id})
    if not user:
        bot.reply_to(m, 'Вы не зарегестрированы. Нажмите /start')
        return
    for sticker in stickers:
        file_id = str(sticker.file_id)
        user['stickers']['unsorted'].append(file_id)
    users.update_one({'id': m.from_user.id}, {'$set':user})
    bot.reply_to(m, 'Стикерпак добавлен.')
