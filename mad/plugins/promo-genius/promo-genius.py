import os
import imp
from mad.lib.plugin import Plugin

abspath = os.path.dirname(os.path.abspath(__file__))+'/'

class PromoGenius(object, Plugin):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.id = "promogenius"
		self.required_roles = ["subscriber", "provider"]
		self.plugin_templates = abspath.split('/')[-2]+"/templates/"
		self.forms = imp.load_source("forms", abspath+"forms.py")

	def plugin_home(self):
		try:
			data = {"plugin_id": self.id}
			return self.render_plugin(template_src=self.plugin_templates+"home.html", data = data)

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.promogenius.plugin_home()")

	def plugin_settings(self, params=None, form=None):
		""" This function should return HTML for the plugin's settings page. """
		try:
			NPF = self.forms.NewPromoForm(form)
			NPF.validate()
			data = { "plugin_id": self.id, "newpromoform": NPF }
			return self.render_plugin(template_src=self.plugin_templates+"settings.html", data=data)

		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.promogenius.plugin_settings()")

	def public_content(self, form=None, params=None):
		""" This function should return HTML for any public facing content the plugin wants to push"""
		self.required_roles = []
		if params:
			if params.get("offer"):
				data = {
						"plugin_id": self.id,
						"offer_title": params.get("offer")
					}
				return self.render_plugin(template_src=self.plugin_templates+"offer.html", data=data)

		return "Promo genius!!"

	def main(self):
		try:
			pass
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.plugins.promogenius.main()")