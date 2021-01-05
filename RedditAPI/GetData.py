import praw
import sqlite3
from TextRank import Summarizer


con = sqlite3.connect('reddit.db')
c = con.cursor()

r = praw.Reddit(client_id='-i-NmbnA3-VSSQ',
                client_secret='S3-AO-HZ-bTRpK5Gj2I4fyUGBV0',
                user_name='milden6',
                password='tiger14',
                user_agent='Daniel')

class GetData:
    c.execute('''DROP TABLE IF EXISTS topics''')
    c.execute('''DROP TABLE IF EXISTS comments''')
    c.execute('''CREATE TABLE topics
    (topicTitle text, topicText text, topicId text, topicCategory text, topicAuthor text)''')
    c.execute('''CREATE TABLE comments
    (commentText text, commentID text, topicTitle text, topicText text, topicID text, topicCategory text, topicAuthor text)''')

    #for use this method will create list of subreddit and run in it in loop
    def getdata(limit, subredditName, search_query):
            subreddit = r.subreddit(subredditName)
            # topics = subreddit.hot(limit=limit)
            topics = subreddit.search(search_query, limit=limit)
            commentInsert = []
            topicInsert = []
            topicNBR = 1
            for topic in topics:
                print('*********** TOPIC:' + str(topic.id) + '*********COMPLETE:')
                topicNBR += 1
                try:
                    topicInsert.append((topic.title, topic.selftext, topic.id, subredditName, topic.author.name))
                except:
                    pass
                try:
                    for comment in topic.comments:
                        comment_text = comment.body
                        if len(comment_text) > 1000:
                            comment_text = Summarizer.summarize(comment_text, language='english', ratio=0.4, words=500)
                            print("SUMMARIZED ", comment_text)
                        commentInsert.append((comment_text, comment.id, topic.title, topic.selftext, topic.id, subredditName, comment.author.name))
                except:
                    pass
                print('*****************************')
                print('INSERT DATA INTO SQLITE')
                c.executemany('INSERT INTO topics VALUES (?,?,?,?,?)', topicInsert)
                print('INSERTED TOPICS')
                c.executemany('INSERT INTO comments VALUES (?,?,?,?,?,?,?)',  commentInsert)
                print('INSERTED COMMENTS')
                con.commit()

# list = ['igor', 'tyler']
# for sub in list:
#     GetData.getdata(1, sub)