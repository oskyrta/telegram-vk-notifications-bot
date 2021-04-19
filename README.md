# telegram-vk-notifications-bot
Python script for the telegram bot, which copies posts from the VK group to the Telegram channel.

# Usage
To create a daemon process run notifications_bot.by with the bot_settings.json file path as argument.<p>
Example bot_settings.json file:  
```
{
    "telegram_bot_id": "bot_id",
    "telegram_channel_id": "channel_id", // the bot should be added to the channel as admin
    "telegram_log_user_id": "user_id",   // id of the user to send debug info
    "vk_group_id": "group_id",
    "vk_access_token": "access_token",
    "refresh_interval_s": 300,           // refresh interval in seconds
    "last_post_id": null                 // if null or missing will be set to last post in group
}
```
