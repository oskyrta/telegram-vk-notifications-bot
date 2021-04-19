# import datetime
import json
import time
import sys
from os import path

import requests
# import streamlink
import telegram

def get_posts(count):
    params = {
        'owner_id': '-107349300',
        'count': count,
        'extended': '1',
        'access_token': 'cc402b9acc402b9acc17df3276cc0e69faccc40cc402b9a9497816f1875027e18e734be',
        'v': '5.130'
    }
    response = requests.get('https://api.vk.com/method/wall.get', params)
    
    if response.status_code != 200:
        return None

    content = json.loads(response.content)
    items =  content['response']['items']   
    items.reverse() 

    return items


def initialize_bot():
    global bot_data

    posts = get_posts(1)

    bot_data['last_post_id'] = posts[0]['id']
    # bot_data['last_post_utc_date'] = str(datetime.datetime.fromtimestamp(posts[0]['date']))

    with open('bot_data', 'w+') as file:
        json.dump(bot_data, file)


def load():
    global bot_data, bot

    bot = telegram.bot.Bot('1772976271:AAGri4aduWM-SwzQ4W4Sima5Bvaw_5op2Uo')

    if path.exists('bot_data'):
        with open('bot_data', 'r') as file:
            bot_data = json.load(file)
    else:
        initialize_bot()


def process_posts():
    global bot 
    global bot_data

    items = get_posts(5)

    if(items == None):
        return

    for item in items:
        id = item['id']
        # date = str(datetime.datetime.timestamp(item['date']))
        message = item['text']

        if(id <= bot_data['last_post_id']):
            continue

        bot.send_message('-1001340260232', message)

        bot_data['last_post_id'] = id
        with open('bot_data', 'w+') as f:
            json.dump(bot_data, f)
    

bot_data = {}
bot = None

load()

while(True):
    try:
        process_posts()
    except:
        bot.send_message( '373695639', json.dumps(sys.exc_info()) )
    
    time.sleep(300)


# while(True):
#     streams = streamlink.streams("https://www.youtube.com/watch?v=Np7YIiL-QAw")

#     if not streams:
#         print('Not live')
#     else:
#         print('Live')
#         break

#     time.sleep(10)

a = 0
