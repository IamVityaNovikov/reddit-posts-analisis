from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier
import pickle


with open('SentimentAnalysis\BayesClassifier.pkl', 'rb') as model:
    cl = pickle.load(model)

class Sentiment:

    def get_sentiment(list):
        poz = 0
        neg = 0
        neu = 0
        for i in list:
            sentiment = TextBlob(str(i), classifier=cl)
            if sentiment.polarity > 0:
                poz = poz + 1
            if sentiment.polarity == 0:
                neu = neu + 1
            if sentiment.polarity < 0:
                neg = neg + 1
            print(sentiment.polarity)
        res = [poz, neu, neg]
        return (res)
