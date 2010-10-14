mytweets
========

A simple script to back up all of your tweets in to a local JSON file.

Dependencies:

- oauth2 from http://github.com/simplegeo/python-oauth2
- simplejson (unless Python 2.6) from http://pypi.python.org/pypi/simplejson/

Usage:

1. Register a new application at http://dev.twitter.com/, which is needed to make
authenticated requests.

2. Create a file called config.py in the same directory as the script:

CONSUMER_KEY = 'oauth-consumer-key'
CONSUMER_SECRET = 'oauth-consumer-secret'
ACCESS_TOKEN = 'oauth-access-token'
ACCESS_TOKEN_SECRET = 'oauth-access-token-secret'

(These are found in your application settings, the first two on the Application Details
page, and the second two on the "My Access Token" page)

3. Run the command like so:

python fetch.py

4. Your tweets will be saved to my_tweets.json, your faves will be saved to my_faves.json,
and your mentions will be saved to my_mentions.json.

You can run the command again any time to save new tweets created since you 
last ran the script. Note that if you delete any already backed-up Tweets, they won't be
deleted.
