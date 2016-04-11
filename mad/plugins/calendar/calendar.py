import os
from mad.lib.plugin import Plugin

abspath = os.path.dirname(os.path.abspath(__file__))+"/"

class Calendar(object, Plugin):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.id = "calendar"
		self.required_roles = ["subscriber"]
		self.plugin_templates = abspath.split('/')[-2]+'/templates/'

	def add_event(self, date, data):
		"""Add event to the calendar"""
		try:
			pass
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.calendar.add_event()")

	def remove_event(self, event_id):
		try:
			pass
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.calendar.remove_event()")

	def update_event(self, event_id, date, data):
		try:
			pass
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.calendar.update_event()")


	def plugin_home(self):
		try:
			data = {"plugin_id": self.id}
			return self.render_plugin(template_src=self.plugin_templates+"home.html", data = data)
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.calendar.plugin_home()")

	def plugin_settings(self, params=None, form=None):
		""" This function should return HTML for the plugin's settings page. """
		try:
			data = {"plugin_id": self.id}
			return self.render_plugin(template_src=self.plugin_templates+"settings.html", data=data)

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.calendar.plugin_settings()")

	def main(self):
		try:
			pass
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.calendar.main()")