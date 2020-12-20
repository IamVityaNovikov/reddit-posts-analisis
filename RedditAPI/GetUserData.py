import praw
from prawcore.exceptions import NotFound
import datetime
from statistics import mean
import difflib
from textblob import TextBlob


def diff_ratio(_a, _b):
	return difflib.SequenceMatcher(a=_a,b=_b).ratio()

reddit = praw.Reddit(client_id='-i-NmbnA3-VSSQ',
				client_secret='S3-AO-HZ-bTRpK5Gj2I4fyUGBV0',
				user_name='milden6',
				password='tiger14',
				user_agent='Daniel')


class UserData:
	redditor = None

	def __init__(self, user_name):
		try:
			self.redditor = reddit.redditor(user_name)
		except NotFound:
			print("USER DO NOT EXIST")
			return None
		try:
			self.author_verified = bool(self.redditor.has_verified_email)
		except:
			self.author_verified = False
		try:
			self.author_comment_karma = self.redditor.comment_karma
		except:
			self.author_verified = 0
		try:
			self.author_link_karma = self. redditor.link_karma
		except:
			self.author_link_karma = 0
		try:
			self.over_18 = self.redditor.subreddit["over_18"]
		except:
			self.over_18 = False
		self.is_submitter = False

		self.comments = []

		for comment in self.redditor.comments.new():
			self.comments.append(comment)

	def get_features(self):

		if self.redditor == None:
			return None

		curr = datetime.date.today()
		delta = datetime.timedelta(days = 30)
		no_follow = True
		is_submitter = False
		recent_num_comments = 0
		recent_num_last_30_days = 0
		recent_avg_no_follow = 0
		recent_avg_gilded = 0
		recent_avg_responses = 0
		recent_percent_neg_score = 0
		recent_avg_score = 0
		recent_min_score = 0
		recent_avg_controversiality = 0
		recent_avg_ups = 0
		recent_avg_diff_ratio = 0
		recent_max_diff_ratio = 0
		recent_avg_sentiment_polarity = 0
		recent_min_sentiment_polarity = 0

		if len(self.comments) > 0:
			body = str(self.comments[0].body)
			recent_num_comments = len(self.comments)
			comments_last_30_days = list(filter(lambda x: datetime.datetime.fromtimestamp(x.created).date() >= (curr - delta), self.comments))
			recent_num_last_30_days = len(comments_last_30_days)
			recent_avg_no_follow = mean([comment.no_follow for comment in self.comments])
			recent_avg_gilded = mean([comment.gilded for comment in self.comments])
			num_comments_cnts = []
			for comment in self.comments:
				try:
					num_comments_cnts.append(comment.num_comments)
				except AttributeError:
					num_comments_cnts.append(len(comment.replies))

			recent_avg_responses = mean(num_comments_cnts)
			recent_percent_neg_score = mean([comment.score < 0 for comment in self.comments]) * 100  #check later
			recent_avg_score = mean([comment.score for comment in self.comments])
			recent_min_score = min([comment.score for comment in self.comments])
			recent_avg_controversiality = mean([comment.controversiality for comment in self.comments])
			recent_avg_ups = mean([comment.ups for comment in self.comments])

			diff = [diff_ratio(body, comment.body) for comment in self.comments]

			recent_avg_diff_ratio = mean(diff)
			recent_max_diff_ratio = min(diff)
			polarities = [TextBlob(comment.body).sentiment.polarity for comment in self.comments]
			recent_avg_sentiment_polarity = mean(polarities) 
			recent_min_sentiment_polarity = min(polarities)

		return([[no_follow, self.author_verified, self.author_comment_karma, self.author_link_karma, self.over_18, self.is_submitter, 
				 recent_num_comments, recent_num_last_30_days, recent_avg_no_follow, recent_avg_gilded, 
				 recent_avg_responses, recent_percent_neg_score, recent_avg_score, recent_min_score, 
				 recent_avg_controversiality, recent_avg_ups, recent_avg_diff_ratio, recent_max_diff_ratio, 
				 recent_avg_sentiment_polarity, recent_min_sentiment_polarity]])	








'''
try:
	redditor = reddit.redditor("dsbhgdfdhfh").id
except NotFound:
	print('not found')
'''
