# Listen for tweets on User's timeline using straming API.
# import modules
# Import the API_Keys.py for the API keys for Twitter - Hidden for security reasons
# Serial to write serial to the Arduino
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from time import sleep
import serial
import json
import sys
import API_Keys

# establish a serial connection to arduino board
try:
    serial_port = "COM5"
    baud_rate = 9600
    arduino_ser = serial.Serial(serial_port, baud_rate)
    print("Connection established on %s" % serial_port)
    # Serial write to 'off'
    arduino_ser.write(2)
    arduino_ser.close()
except IndexError:
    # If there is no connection, print this to the console
    print("No arduino device port specified, Exit")
    sys.exit()
except BaseException as b:
    print (b)
    sys.exit()

# Username of the bot Twitter account we are watching
user_name = ['UniProjectBot']

# Class by tweepy to access the Twitter Streaming API
class StreamListener(tweepy.StreamListener):

    def play_notification(self):
        # Plays a beep on the Arduino
        # Flashes the LED
        arduino_ser.close()
        arduino_ser.open()
        arduino_ser.write(1)
        sleep(5)
        arduino_ser.write(2)
    
    def on_connect(self):
        # Called to connect to the API
        print("You are now connected to the streaming API")

    def on_error(self, status_code):
        # If error occurs, display the error / status code to the console
        print("An Error has occured: " + repr(status_code))
        return False

    def on_data(self, data):
        # Get the tweets information using the Twitter website to chose the elements 
        try: 
            datajson = json.loads(data)

            text = datajson['text']
            screen_name = datajson['user']['screen_name']
            tweet_id = datajson['id']
            
            # Print the tweet found to the console
            print("Tweet found: " + str(screen_name) + '' + str(text))

            # Play the notification
            self.play_notification()

        except Exception as e:
            print(e)

# Set up the Twitter API keys to access the tweets
auth = tweepy.OAuthHandler(API_Keys.consumer_key, API_Keys.consumer_secret)
auth.set_access_token(API_Keys.key, API_Keys.secret)

# Calls the Stream Listener
listener = StreamListener(api = tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)

# Print the username we are watching to the console
print("Watching: " + str(user_name))
streamer.filter(track=user_name)