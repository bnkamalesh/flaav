from mad.lib.model import Model

class PluginModel(Model):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.collection_name = "plugins"