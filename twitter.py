from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
import pymongo
import json
from flask import Flask, jsonify, request
import time
from datetime import datetime
from bson import json_util
import csv
import io
from flask import make_response





# Twitter developer keys and tokens which you can get from developers.twitter.com

consumer_key = 'gHbwzXgG2hNyf79kO5qJifSzj'
consumer_secret = 'BEpQ3mEwhBQ0zK98dApYmf4dN12jIhNirqMiUJu409WavfBIZg'
access_token = '1049599176743444480-YSGGr5IhkjWo8CtKJNnAufzx63D3g5'
access_token_secret = '5gvfailTgk4upmU7cJkPy9Bwudc9RBTc552t5JMQiDqGS' 


auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)


app = Flask(__name__)


clf = MongoClient()
#creating database
db = clf['data_base']
#creaing collections
tweets = db['tweets']


#First Endpoint

@app.route('/',methods=['GET'])
def hello():
	return jsonify({"API 1 => To trigger tweets ":"endpoint - /trigger?<arguments>",

		"API 2 => Get tweets from database":"endpoint - /getresults?<arguments>",

		"API 3 => Download Results as a CSV format":"endpoint - /download/getcsv?<arguments>"

		}
		)

# API 1 Trigger and store tweets in th database 

@app.route('/trigger',methods=['GET'])
def trigger():
	print("ih")
	key = request.args['keyword']
	if key==None:
		return ('Please enter keyword')
	limit_tweet = int(request.args.get('limit_tweet',15))

	#print(key)
	l = StdOutListener(key,limit_tweet)
	print(l)
	stream = Stream(auth, l)
	stream.filter(track=[key], async=True)
	return jsonify({"trigger":"it's begin"})



# API 2 Get tweets stored in database

@app.route('/download/getresults', methods=['GET'])
def downloadtweets():
	ans=get_data()
	si = io.StringIO()
	fieldnames = ['retweet_count', 'user_friends_count', 'created_at', 'user_followers_count', 'reply_count', 'name', 'location', 'keyword', 'favorite_count', 'user_time_zone', 'tweet_hashtags', 'lang', 'user_id', 'text', 'user_description', 'screen_name', 'retweeted', 'timestamp_ms', '_id', 'tweet_text_urls','url']
	writer = csv.DictWriter(si, fieldnames=fieldnames)
	writer.writeheader()
	writer.writerows(s)
	output = make_response(si.getvalue())
	output.headers["Content-Disposition"] = "attachment; filename=export.csv"
	output.headers["Content-type"] = "text/csv"
	return output
 


# API 3 download tweets as csv format

@app.route('/getresults', methods=['GET'])
def getresults():
	value=get_data()
	print value
	return value




class StdOutListener(StreamListener):
	
	count = 0
	keyword = ""
	limit_tweet = 0

	def __init__(self,key, limit_tweet):
		self.limit_tweet = limit_tweet
		self.count = 0
		self.keyword += key

	def on_data(self,data):

		obj = json.loads(data)
		
		tweet = {}
		tweet['keyword'] = self.keyword

		tweet['text'] = obj['text']
		tweet['lang'] = obj['user']['lang']
		tweet['timestamp_ms'] = obj['timestamp_ms']
		tweet['retweeted'] = obj['retweeted']
		tweet['retweet_count'] = obj['retweet_count']
		tweet['reply_count'] = obj['reply_count']
		tweet['favorite_count'] = obj['favorite_count']

		

		#print(tweet['created_at'])

		hashes = obj['entities']['hashtags']
		hashtags = []
		for hashtag in hashes:
			hashtags.append(hashtag['text'])
		tweet['tweet_hashtags'] = hashtags

		urls_list = obj['entities']['urls']
		urls = []
		for url in urls_list:
			urls.append(url['url'])
		tweet['tweet_text_urls'] = urls


		tweet['user_id'] = obj['user']['id']
		tweet['name'] = obj['user']['name']
		tweet['screen_name'] = obj['user']['screen_name']
		tweet['location'] = obj['user']['location']
		tweet['url'] = obj['user']['url']
		tweet['user_description'] = obj['user']['description']
		tweet['user_followers_count'] = obj['user']['followers_count']
		tweet['user_friends_count'] = obj['user']['friends_count']
		tweet['user_time_zone'] = obj['user']['time_zone']

		time_struct = time.strptime(obj['created_at'], "%a %b %d %H:%M:%S +0000 %Y")#Tue Apr 26 08:57:55 +0000 2011
		tweet['created_at'] = time.mktime(time_struct)

		#print(tweet)

		tweets.insert_one(tweet)
		print("Success")
		self.count += 1
		if self.count == self.limit_tweet:
			del self
			return False
		return True

	def on_error(self,status):
		print("Failed - Error: ",status)



def get_data():
	key = request.args['keyword']
	offset = int(request.args.get('offset',0))
	limit = int(request.args.get('limit',10))
	
	name = request.args.get('name',None)
	screenname = request.args.get('screen_name',None)
	retweet_count = int(request.args.get('retweet_count',-1))
	reply_count = int(request.args.get('reply_count',-1))
	favorite_count = int(request.args.get('favorite_count',-1))
	language = request.args.get('lang',None)



	filters = {'keyword':key}

	next_url = '/getresults?keyword=' + str(key)
	prev_url = '/getresults?keyword=' + str(key)


	if name!=None:
		filters['name'] = name
		next_url += '&name='+name
		prev_url += '&name='+name
	if screenname!=None:
		filters['screen_name'] = screenname
		next_url += '&screen_name='+screenname
		prev_url += '&screen_name='+screenname
	if retweet_count!=-1:
		filters['retweet_count'] = retweet_count
		next_url += '&retweet_count=' + str(retweet_count)
		prev_url += '&retweet_count=' + str(retweet_count)
	if reply_count!=-1:
		filters['reply_count'] = reply_count
		next_url += '&reply_count=' + str(reply_count)
		prev_url += '&reply_count=' + str(reply_count)
	if favorite_count!=-1:
		filters['favorite_count'] = favorite_count
		next_url += '&favorite_count=' + str(favorite_count)
		prev_url += '&favorite_count=' + str(favorite_count)
	if language!=None:
		filters['lang'] = language
		next_url += '&lang=' + language
		prev_url += '&lang=' + language
	
	sort_by = request.args.get('sort_by',None)
	order_by = request.args.get('order','ASC');
	if sort_by==None:
		sort_by = '_id'
		next_url += '&sort_by=' + sort_by
		prev_url += '&sort_by=' + sort_by
	else:
		next_url += '&sort_by=' + sort_by
		prev_url += '&sort_by=' + sort_by
	
	order = 0
	if(order_by=='ASC'):
		order = 0
		next_url += '&order=' + order_by
		prev_url += '&order=' + order_by
	else:
		order = 1
		next_url += '&order=' + order_by
		prev_url += '&order=' + order_by


	date_start = request.args.get('date_start',None)
	date_end = request.args.get('date_end',None)

	if date_start!=None and date_end!=None:
		start_time = time.mktime(time.strptime(date_start, "%d_%m_%Y"))
		end_time = time.mktime(time.strptime(date_end, "%d_%m_%Y"))
		next_url += '&date_start=' + date_start
		prev_url += '&date_end=' + date_end
		filters['created_at'] = {'$gte':start_time,'$lte':end_time}
	elif date_start !=None:
		start_time = time.mktime(time.strptime(date_start, "%d_%m_%Y"))
		next_url += '&date_start=' + date_start
		filters['created_at'] = {'$gte':start_time}
	elif date_end !=None:
		end_time = time.mktime(time.strptime(date_end, "%d_%m_%Y"))
		prev_url += '&date_end=' + date_end
		filters['created_at'] = {'$lte':end_time}

	search = request.args.get('search',None)
	if search!=None:
		search_type = request.args['search_type']
		search_value = request.args['search_value']
		next_url += '&search=' + search + '&search_type=' + search_type + '&search_value=' + search_value
		prev_url += '&search=' + search	+ '&search_type=' + search_type + '&search_value=' + search_value

	next_url += '&limit=' + str(limit) + '&offset=' + str(offset+limit)
	prev_url += '&limit=' + str(limit) + '&offset=' + str(offset-limit)


	if order==0:
		query = tweets.find(filters).sort(sort_by,pymongo.ASCENDING)
	else:
		query = tweets.find(filters).sort(sort_by,pymongo.DESCENDING)

	
	starting_id = query
	try:
		last_id = starting_id[offset]['_id']
	except:
		last_id= 0


	if order==0:
		filters['_id'] = {'$gte':last_id}
	else:
		filters['_id'] = {'$lte':last_id}
	
	s = []
	
	try:
		count = 0;
		full_find = query
		for tweet in full_find:
			#print(hello)
			if search==None:
				s.append(tweet)
				count += 1
				if count==limit:
					break
			else:
				if search_type=='starts':
					if tweet[search].startswith(search_value):
						s.append(tweet)
						count += 1
						if count==limit:
							break
				elif search_type=='ends':
					if tweet[search].endswith(search_value):
						s.append(tweet)
						count += 1
						if count==limit:
							break
				elif search_type=='contains':
					if tweet[search].find(search_value)!=-1:
						s.append(tweet)
						count += 1
						if count==limit:
							break

	except:
		s = []
	value = {}
	value['tweet_count'] = len(s)
	value['limit'] = limit
	value['offset'] = offset
	if offset+limit<=len(s):
		value['next_url'] = next_url
	if offset-limit>=0:
		value['prev_url'] = prev_url
	value['tweets'] = json_util._json_convert(s)
	return jsonify(value)



if __name__ == '__main__':
	app.run(port=5000,use_reloader=True)