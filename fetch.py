import oauth2 as oauth
import time
import urllib

try:
    import json
except ImportError:
    import simplejson as json

from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

TWEET_FILE = 'my_tweets.json'
FAVES_FILE = 'my_faves.json'
REPLY_FILE = 'my_mentions.json'

# Configure httplib with the credentials
oauth_consumer = oauth.Consumer(
    key=CONSUMER_KEY,
    secret=CONSUMER_SECRET
)
oauth_token = oauth.Token(
    key=ACCESS_TOKEN,
    secret=ACCESS_TOKEN_SECRET
)
h = oauth.Client(oauth_consumer, oauth_token)

def sort_tweets(tweets):
    """Sorts the passed tweets into reverse-chronological order (inferred by
       the object ids), and also uniquifies them by id."""
    def _comparator(x, y):
        return cmp(y['id'], x['id'])
    tweets = sorted(tweets, _comparator)
    new_tweets = []
    processed_ids = set()
    for tweet in tweets:
        if tweet['id'] not in processed_ids:
            processed_ids.add(tweet['id'])
            new_tweets.append(tweet)
    return new_tweets

def load_saved(path):
    try:
        return json.load(open(path))
    except IOError:
        return []

def _fetch_url(url, *args, **kwargs):
    """Fetch a url from Twitter, returning the decoded JSON. Proxies arguments to the HTTP
       client."""
    headers = {}
    
    try:
        headers, response = h.request(url, *args, **kwargs)
        return json.loads(response)
    except Exception:
        # If Twitter's behaving badly, try again in 5 seconds
        if headers.get('status', None) in ('502', '503'):
            print '    !! Twitter returned a %s for %s. Backing off for 5s and retrying.' % (
                headers['status'],
                url
            )
            time.sleep(5)
            print '    ...going again'
            return _fetch_url(url, *args, **kwargs)
        else:
            raise

def fetch_new_tweets(tweets, base_url, params={}):
    # Figure out the max id already imported
    args = { 'count': 200 }
    if tweets:
        args['since_id'] = max(i['id'] for i in tweets)
    args.update(params)
    
    new_tweets = []
    seen_ids = set()
    page = 1
    while True:
        args['page'] = page
        url = base_url + '?' + urllib.urlencode(args)
        
        response = _fetch_url(url, method='GET')
        
        if not response:
            break
        else:
            for tweet in response:
                if tweet['id'] not in seen_ids:
                    new_tweets.append(tweet)
                    seen_ids.add(tweet['id'])
        page += 1
    
    tweets.extend(new_tweets)
    return tweets, new_tweets

def save(tweets, path):
    """Saves the tweets to the file path passed."""
    tweets = sort_tweets(tweets)
    json.dump(tweets, open(path, 'w'), indent=4)
    return tweets

if __name__ == '__main__':
    # First, update the user's own tweets
    print 'Fetching own tweets'
    tweets = load_saved(TWEET_FILE)
    old_count = len(tweets)
    tweets, added_tweets = fetch_new_tweets(
        tweets=tweets,
        base_url='http://api.twitter.com/1/statuses/user_timeline.json',
        params={
            'include_entities': '1',
            'include_rts': '1'
        }
    )
    tweets = save(tweets, TWEET_FILE)
    new_count = len(tweets)
    # Print some stats
    print '--- Storing %d tweets in total' % new_count
    print '--- Added %d tweets' % (new_count - old_count)
    
    # Now, the user's favourites
    print 'Fetching faved tweets'
    tweets = load_saved(FAVES_FILE)
    old_count = len(tweets)
    tweets, added_tweets = fetch_new_tweets(
        tweets=tweets,
        base_url='http://api.twitter.com/1/favorites.json',
        params={
            'include_entities': '1'
        }
    )
    tweets = save(tweets, FAVES_FILE)
    new_count = len(tweets)
    print '--- Storing %d faves in total' % new_count
    print '--- Added %d faves' % (new_count - old_count)
    
    # Finally, mentions
    print 'Fetching mentions'
    tweets = load_saved(REPLY_FILE)
    old_count = len(tweets)
    tweets, added_tweets = fetch_new_tweets(
        tweets=tweets,
        base_url='http://api.twitter.com/1/statuses/mentions.json',
        params={
            'include_entities': '1',
            'include_rts': '1'
        }
    )
    tweets = save(tweets, REPLY_FILE)
    new_count = len(tweets)
    print '--- Storing %d mentions in total' % new_count
    print '--- Added %d mentions' % (new_count - old_count)
