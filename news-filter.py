from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
import logging
import os
import xmltodict
import requests
from datetime import datetime, timedelta, timezone
from dateutil import parser

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)



telegram_token = os.environ['TELEGRAM_TOKEN']
updater = Updater(token=telegram_token, use_context=True)
dispatcher = updater.dispatcher

telegram_id = os.environ['TELEGRAM_ID']

keywords = os.environ['KEYWORDS'].split(',')

def rule(news_string):
    for keyword in keywords:
        if keyword.lower() in news_string.lower():
            return True
    return False
   


def check_news(rss_url, news_filter, check_interval=10):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(rss_url, headers=headers)
    logger.debug(response.content)
    dict_data = xmltodict.parse(response.content)
    news_items = dict_data['rss']['channel']['item']
    filtered_items =  []
    for item in news_items:        
        newsdate = parser.parse(item['pubDate'])
        hour_ago = (datetime.now(timezone.utc).astimezone() - timedelta(hours=1))
        word_filter = news_filter(item['title'])
        if word_filter and (newsdate > hour_ago):
            filtered_items.append(f"{item['title']} {item['link']}")
    return filtered_items
        
    


period = int(os.environ['PERIOD'])
def send_message(event, context):
    news_sources = [
        'https://ria.ru/export/rss2/archive/index.xml', 
        'http://feeds.bbci.co.uk/russian/rss.xml'
    ]

    news_items = []

    for news_source in news_sources:
        news_items.extend(check_news(news_source, rule, period))

    for news_item in news_items:
        dispatcher.bot.send_message(
            chat_id=telegram_id, text=news_item)
