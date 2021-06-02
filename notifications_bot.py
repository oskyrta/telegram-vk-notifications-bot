import json
import sys
import time
import os
from os import path
import traceback

import requests
import telegram
from daemons import daemonizer
from telegram import message


class Bot:

    def __get_posts(self, count, offset = 0):
        params = {
            'owner_id': self.__bot_settings['vk_group_id'],
            'count': count,
            'offset': offset,
            'extended': '1',
            'access_token': self.__bot_settings['vk_access_token'],
            'v': '5.130'
        }
        
        response = requests.get('https://api.vk.com/method/wall.get', params)
        
        if response.status_code != 200:
            raise RuntimeError('wall.get request returns status code ' + response.status_code)

        content = json.loads(response.content)
        items = content['response']['items']   
        items.reverse() 

        return items


    def __load_bot_settings(self, settings_path):
        if not path.exists(settings_path):
            raise RuntimeError('Settings file not found')
        
        with open(settings_path, 'r') as file:
            bot_settings = json.load(file)

            fields = ['telegram_bot_id', 'telegram_channel_id', 'telegram_log_user_id', 'vk_group_id', 'vk_access_token', 'refresh_interval_s']
            missing_fields = [x for x in fields if x not in bot_settings.keys()]

            if len(missing_fields) > 0:
                raise RuntimeError('Following fields are missing in the settings file: ' + ', '.join(missing_fields))

            self.__bot_settings = bot_settings

            if 'last_post_id' not in self.__bot_settings.keys() or self.__bot_settings['last_post_id'] == None:
                posts = self.__get_posts(1)
                self.__bot_settings['last_post_id'] = posts[0]['id']
                
                with open(settings_path, 'w+') as file:
                    json.dump(self.__bot_settings, file)


    def __send_post(self, post):
        photos = []

        if('attachments' in post.keys()):
            for attachment in post['attachments']:
                if attachment['type'] == 'photo':
                    photos.append(attachment['photo']['sizes'][-1]['url'])

        if('text' in post.keys()):
            self.__bot.send_message(self.__bot_settings['telegram_channel_id'], post['text'])
            
        if len(photos) == 1:
            self.__bot.send_photo(self.__bot_settings['telegram_channel_id'], photo = photos[0], disable_notification = True)
        elif len(photos) > 1:
            media = [telegram.InputMediaPhoto(photo) for photo in photos]

            self.__bot.send_media_group(self.__bot_settings['telegram_channel_id'], media, disable_notification = True)    


    def __update_posts(self):
        items = self.__get_posts(1)

        id = items[0]['id']
        
        posts = []
        offset = 0
        while id > self.__bot_settings['last_post_id']:
            posts.append(items[0])

            offset += 1
            items = self.__get_posts(1, offset)
            id = items[0]['id']
            
        if(len(posts) == 0):
            return

        posts.reverse()
        for post in posts:
            self.__send_post(post)

        self.__bot_settings['last_post_id'] = posts[-1]['id']
        with open(self.__settings_path, 'w+') as f:
            json.dump(self.__bot_settings, f)


    def __init__(self, settings_path):
        self.__settings_path = settings_path
        self.__load_bot_settings(settings_path)

        self.__bot = telegram.bot.Bot(self.__bot_settings['telegram_bot_id'])
        self.__bot.send_message(self.__bot_settings['telegram_log_user_id'], 'Bot is starting')


    def start_bot(self):
        while(True):
            try:
                self.__update_posts()
            except:
                exception = 'Type: {}\nValue: {}\nTraceback: {}'.format(sys.exc_info()[0], sys.exc_info()[1], traceback.format_exc())
                self.__bot.send_message( self.__bot_settings['telegram_log_user_id'], exception )

            time.sleep(self.__bot_settings['refresh_interval_s'])
    

if os.name == 'posix':
    @daemonizer.run(pidfile="/tmp/telegram_bot.pid")
    def run():
        if len(sys.argv) < 2:
            raise RuntimeError('Path to settins is missing')

        bot = Bot(sys.argv[1])
        bot.start_bot()

    run()
else:
    bot = Bot('bot_settings.json')
    bot.start_bot()
