# Import the relevant modules 
# Using BeautifulSoup in order to web scrape for the weather info
# Import the API_Keys.py for the API keys for Twitter - Hidden for security reasons
import API_Keys
import tweepy
import time
import sys
import urllib
import json
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from googlesearch import search  

# Using api objects to communicate with Twitter using the keys variables from API_Keys.py

auth = tweepy.OAuthHandler(API_Keys.consumer_key, API_Keys.consumer_secret)
auth.set_access_token(API_Keys.key, API_Keys.secret)
api = tweepy.API(auth)

# This text file stores the id of the last tweet response
# In order to make sure that we do not respond to the same tweet more than once

FILE_NAME = 'last_seen.txt'

# Check the last seen tweet id so we can compare it to a new tweet that comes in

def read_last_seen(FILE_NAME):
    file_read = open(FILE_NAME, 'r')
    last_seen_id = int(file_read.read().strip())
    file_read.close()
    return last_seen_id

# Store the tweet id of the new tweet we receive

def store_last_seen(FILE_NAME, last_seen_id):
    file_write = open(FILE_NAME, 'w')
    file_write.write(str(last_seen_id))
    file_write.close()
    return

# Location comes in the form of a hashtag from the tweet

def get_location(tweet):
    # Takes received tweet and returns only the substring attached to hashtag
    # We only want what is after the # for the location
    tweet_location = [i.strip("#") for i in tweet.split() if i.startswith("#")][0]
    tweet_location += " weather yourweather.co.uk"
    return tweet_location

# Search for the weather for the location in get_location using the website yourweather.co.uk

def get_weather(query):
    for url in search(query, stop=1):
        print("Results is " + url)

    # This sends a request and reads the webpage enclosed to the request
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    webpage = urlopen(request).read()
    soup = BeautifulSoup(webpage, "html.parser")

    # Try to get elements from the webpage opened
    # Used inspect to find out the class name etc. of the elements for the information we want

    try:
        title = soup.findAll('span', attrs={'class': 'dato-temperatura changeUnitT'})[0].text
        feelsLike = soup.findAll('span', attrs={'class': 'sensacion changeUnitT'})[0].text
        phrase = soup.findAll('span', attrs={'class': 'descripcion'})[0].text 
        hour = soup.findAll('span', attrs={'class': 'hour'})[0].text
        #next_time = soup.findAll('span', attrs={'class': 'titulo-aviso'})[0].text -> Not used anymore
        next_weather = soup.findAll('span', attrs={'class': 'textos'},)[0].text
        # wind = soup.findAll('span', attrs={'class': 'datos-uv'})[0].text -> Not used anymore
    except IndexError as e:
        # If no values from elements, tweet the following
        forecast = (" could not find the weather, check back later")
        print(e)
    else:
        # Set up the tweet as forecast then print the pending tweet
        forecast = (" The temperature is: " + title + ", "+ feelsLike +", and the weather is:" + phrase + " as of " + hour + "\n" + next_weather)
        print(forecast)

    return forecast

# Reply to the tweet tweeted at the bot 

def reply_to_tweet():
    # Update the console that it is looking for tweets to respond to 
    print("retrieving and replying to tweets...")
    last_seen_tweet = read_last_seen(FILE_NAME)
    # mentions_timeline() returns a list of 20 most recent mentions
    mentions = api.mentions_timeline(last_seen_tweet, tweet_mode="extended")

    # Reversing to read old tweets first
    for mention in reversed(mentions):
        print(str(mention.id) + " - " + mention.full_text)
        last_seen_tweet = mention.id
        store_last_seen(FILE_NAME, last_seen_tweet)
        # Updates the console if a hashtag has been found -> location
        if "#" in mention.full_text.lower():
            print("found #")

            # Call the functions to get the location and then weather from the hashtag 
            location = get_location(mention.full_text)
            weather = get_weather(location)

            # Responding to tweet mention using api.update_status, then like and retweet 
            api.update_status("@" + mention.user.screen_name + weather, mention.id)
            api.create_favorite(mention.id)
            api.retweet(mention.id)
            
# loop to reply every 15 seconds

while True:
    reply_to_tweet()
    time.sleep(15)