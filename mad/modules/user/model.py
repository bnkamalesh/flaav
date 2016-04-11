from mad.lib.model import Model

class Users(Model):
	""" User model """
	def __init__(self, content=None):
		super(self.__class__, self).__init__()
		self.collection_name = "users"
		self.content = content