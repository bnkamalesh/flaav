import datetime
from mad.lib.model import Model

class SearchHistory(Model):
	def __init__(self, searchparams=None, user_id=None, title=None):
		super(self.__class__, self).__init__()
		self.collection_name = "search_history"
		self.searchparams = searchparams
		self.user_id = user_id
		self.title = title
		self.created_on = None


	def set_content(self, content=None):
		""" Sets the content of the model"""
		self.content = {
			"searchparams": self.searchparams,
			"user_id": self.user_id,
			"title": self.title,
			"created_on": datetime.datetime.utcnow()
		}