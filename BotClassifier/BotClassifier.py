import pickle
from sklearn.tree import DecisionTreeClassifier

class BotClassifier:
	"""docstring for ClassName"""
	def __init__(self):
		
		self.classifier = DecisionTreeClassifier()
		
		with open("BotClassifier\DecisionTreeClassifier.pkl", 'rb') as model:
			self.classifier = pickle.load(model)


	def predict(self, data):
		y_pred = self.classifier.predict(data)
		return(y_pred)
