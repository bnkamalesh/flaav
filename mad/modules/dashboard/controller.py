from mad.lib.controller import Controller
from mad.modules.media.controller import MediaController

class DashboardActions(Controller):
	def __init__(self):
		super(self.__class__, self).__init__()

	def get_statistics(self):
		""" Prepare and return statistics of the data available """
		MC = MediaController()
		return MC.get_media_statistics()