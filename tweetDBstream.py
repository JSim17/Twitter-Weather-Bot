# Import required modules 
# Import the API_Keys.py for the API keys for Twitter - Hidden for security reasons
# tweepy to access Twitter API
# JSON to transfer data as text
# MySQLdb is an interface for connecting to database server from Python
import tweepy
import json
import MySQLdb
from dateutil import parser
import API_Keys

# Login variables for database hosted on localhost using MySQL workbench
host = 'localhost'
user = 'username'
passwd = 'password'
database = 'database'

# What we are tracking to stream into the database -> the username for the bot account
word = ['UniProjectbot']

# This function takes the 'created_at', 'text', 'screen_name', and 'tweet_id' of the tweet 
# and stores the tweet into a MySQL database 
# These are the columns in the database table 
def store_data(created_at, text, screen_name, tweet_id):
    # Connect to the database

    db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database, charset="UTF8")
    cursor = db.cursor()
    # Set up query to insert into the database

    insert_query = "INSERT INTO twitter (tweet_id, screen_name, created_at, text) VALUES (%s, %s, %s, %s)"
    cursor.execute(insert_query, (tweet_id, screen_name, created_at, text))
    db.commit()
    cursor.close()
    db.close()
    return

# This is a class provided by tweepy to access the Twitter Streaming API
# Set up a 'listener' to watch Twitter feed from Twitter API

class StreamListener(tweepy.StreamListener):

    # Called initially to connect to the Streaming API

    def on_connect(self):
        # Print to the console as a guide to know it is working and connected

        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code

        print("An Error has occured: " + repr(status_code))
        return False

    def on_data(self, data):
        # This connects to your DB and stores the tweet

        try:
            # Decode trhe JSON file from Twitter

            datajson = json.loads(data)

            # Grab the wanted data from the Tweet using the variable names available from
            # Twitter API website, we can access any element of the tweet

            text = datajson['text']
            screen_name = datajson['user']['screen_name']
            tweet_id = datajson['id']
            created_at = parser.parse(datajson['created_at'])

            # Print out a message to the console that we have collected a tweet -> update

            print("Tweet collected at " + str(created_at))

            # Insert the data into the MySQL database using the function we declared

            store_data(created_at, text, screen_name, tweet_id)

        except Exception as e:
            print(e)

# Connect to the Twitter API using the keys in API_Keys.py

auth = tweepy.OAuthHandler(API_Keys.consumer_key, API_Keys.consumer_secret)
auth.set_access_token(API_Keys.key, API_Keys.secret)

# Set up the listener
# 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.

listener = StreamListener(api = tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)

#Update the console that we are 'tracking' the word declared earlier

print("Tracking: " + str(word))
streamer.filter(track=word)