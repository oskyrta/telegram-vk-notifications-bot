import json
import sys
import time
from os import path
import traceback

import requests
import telegram
from daemons import daemonizer


class Bot:

    def __get_posts(self, count):
        params = {
            'owner_id': self.__bot_settings['vk_group_id'],
            'count': count,
            'extended': '1',
            'access_token': self.__bot_settings['vk_access_token'],
            'v': '5.130'
        }
        response = requests.get('https://api.vk.com/method/wall.get', params)
        
        if response.status_code != 200:
            return None

        content = json.loads(response.content)
        items =  content['response']['items']   
        items.reverse() 

        return items


    def __get_bot_settings(self, settings_path):
        if not path.exists(settings_path):
            raise RuntimeError('Settings file not found')
        
        with open(settings_path, 'r') as file:
            bot_settings = json.load(file)

            fields = ['telegram_bot_id', 'telegram_channel_id', 'telegram_log_user_id', 'vk_group_id', 'vk_access_token', 'refresh_interval_s']
            missing_fields = [x for x in fields if x not in bot_settings.keys()]

            if len(missing_fields) > 0:
                raise RuntimeError('Following fields are missing in the settings file: ' + ', '.join(missing_fields))

            if 'last_post_id' not in bot_settings.keys() or self.__bot_settings['last_post_id'] == None:
                posts = self.__get_posts(1)
                bot_settings['last_post_id'] = posts[0]['id']
                
                with open(settings_path, 'w+') as file:
                    json.dump(bot_settings, file)

            return bot_settings


    def __update_posts(self):
        items = self.__get_posts(5)

        if(items == None):
            return

        for item in items:
            id = item['id']
            message = item['text']

            if(id <= self.__bot_settings['last_post_id']):
                continue

            self.__bot.send_message(self.__bot_settings['telegram_channel_id'], message)

            self.__bot_settings['last_post_id'] = id
            with open(self.__settings_path, 'w+') as f:
                json.dump(self.__bot_settings, f)


    def __init__(self, settings_path):
        self.__settings_path = settings_path
        self.__bot_settings = self.__get_bot_settings(settings_path)

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
    

@daemonizer.run(pidfile="/tmp/telegram_bot.pid")
def process_bot():
    if len(sys.argv) < 2:
       raise RuntimeError('Path to settins is missing')

    bot = Bot(sys.argv[1])
    bot.start_bot()

process_bot()
