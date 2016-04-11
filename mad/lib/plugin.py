import os
from collections import namedtuple

from flask import url_for, current_app, abort
from flask.ext.login import current_user
from jinja2 import Environment, FileSystemLoader

from model import Model
from errorhandler import ErrorHandler
from cache import Cache

class PluginDataModel(Model):
	def __init__(self, plugin_id=None):
		super(self.__class__, self).__init__()
		self.collection_name = "plugin_data"
		self.plugin_id = plugin_id
		self.data = {}

	def set_content(self):
		self.data.update({ "plugin_id": self.plugin_id })
		self.content = self.data

class PluginSettingsModel(Model):
	def __init__(self, plugin_id=None):
		super(self.__class__, self).__init__()
		self.collection_name = "plugin_settings"
		self.plugin_id = plugin_id
		self.settings = None

	def set_content(self):
		self.content = {
			"plugin_id": self.plugin_id,
			"settings": self.settings
			}

class Struct:
	""" This class is used to convert the dict received in render_plugin into an object """
	def __init__(self, **entries):
		self.__dict__.update(entries)

class Plugin:
	is_active = False
	url_for = url_for
	error_handle = ErrorHandler()
	template = Environment(loader=FileSystemLoader(current_app.config["PLUGINS_PATH"]))
	admin_role = "admin"
	available_roles = ["anon", "viewer", "buyer", "subscriber", "provider", admin_role]
	required_roles = [] # set in each module

	def __init__(self):
		self.required_roles = [] # set in each module

	def activate(self):
		"""Activate this plugin"""
		if self.is_active==False:
			self.is_active = True
			self.main()

	def deactivate(self):
		"""Deactivate this plugin"""
		if self.is_active==True:
			self.is_active = False

	def main(self):
		""" 
			This is the entry point of plugin functions. All plugin 
			activities should be within main function. It'll be called
			right after "activating" the plugin. Also, after "save_settings"
			and "save data".
		"""
		pass

	def reload(self):
		""" 
			This function will by default call the main function.
			It'll be called after saving settings, or inserting new data.
			This is to prevent
		"""
		self.main()


	def save_settings(self, settings, user_specific=True, overwrite=False):
		""" This function saves any settings specific to a plugin """
		try:
			PSM = PluginSettingsModel(plugin_id=self.id)
			if overwrite==False:
				PSM.settings = self.get_settings()
			
			if PSM.settings:
				PSM.settings.update(settings)
			else:
				PSM.settings = settings

			conditions = {"plugin_id": PSM.plugin_id}
			if user_specific:
				conditions.update({"user_id": current_user.get_userid()})

			PSM.update(conditions=conditions, upsert=True, overwrite=overwrite)
			self.reload()
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.plugin.save_settings()")

	def get_settings(self, user_specific=True):
		""" This function returns the settings stored by the plugin """
		try:
			PSM = PluginSettingsModel(plugin_id=self.id)
			settings = None
			conditions = {"plugin_id": PSM.plugin_id}
			if user_specific:
				conditions.update({"user_id": current_user.get_userid()})

			result = PSM.get(conditions=conditions, findone=True)

			if result:
				settings = result["settings"]

			return settings
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.lib.plugin.get_settings()")
			return None

	def save_data(self, data=None, conditions={}, upsert=False, user_specific=True, update=False, allow_duplicate=False, dup_fields=None):
		""" 
			This function is used to save/insert/update data, specific to a plugin 
			data      : data to be saved 
			conditions: conditions, in case data is being updated
			upsert    : if data is to be upserted
		"""
		try:
			if user_specific:
				data.update({"user_id": current_user.get_userid()})

			PDM = PluginDataModel(plugin_id=self.id)
			PDM.data = data
			status = None
			if update:
				status = PDM.update(conditions=conditions, upsert=upsert)
			else:
				dup_fields.update({"plugin_id": PDM.plugin_id})
				status =  PDM.save(allow_duplicate=allow_duplicate, duplicate_fields_check=dup_fields)

			self.reload()
			return status
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.plugin.save_data()")


	def get_data(self, conditions=None, sort_by=[("_id", 1)], distinct=False, distinct_fieldname=None, user_specific=True):
		""" This function is used to retrieve data stored by the pliugin based on the condition provided """
		try:
			PDM = PluginDataModel(plugin_id=self.id)
			if not conditions:
				conditions = {}
			conditions.update({"plugin_id": PDM.plugin_id})

			if user_specific:
				conditions.update({"user_id": current_user.get_userid()})

			if distinct==True:
				return PDM.get(conditions=conditions, sort_by=sort_by, distinct=True, distinct_fieldname=distinct_fieldname)
			else:
				return PDM.get(conditions=conditions, sort_by=sort_by)
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.plugin.get_data()")


	def plugin_home(self):
		"""This function should return HTML for the plugin's home page"""
		html = (
				'<h2 class="title">Plugin Home</h2>'
			   	'<p>Hello, this is your plugin homepage</p>'
			   )
		return html

	def plugin_settings(self):
		""" This function should return HTML for the plugin's settings page. """
		html = (
				'<h2 class="title">Plugin Settings</h2>'
			   	'<p>Display all your plugin settings here.</p>'
			   )
		return html

	def public_content(self, form=None, params=None):
		""" This function should return HTML for any public facing content the plugin wants to push"""
		return None

	def check_role(self):
		""" 
			Check if the current user has the required role to access this view.
			If the function returns:
			True : User has the required role/permission to access this page.
			False: User does not have required role/permission to access this page.
			Available  roles:
				anon - not logged in user
				viewer - is the default role of a logged in user.
				provider - Ad space provider, who will have access to add their media to the system.
				buyer - Consumer looking for ad spaces, has access to the search module.
				subscriber - A subscribed user
		"""
		if not self.required_roles or not self.available_roles:
			return True
		elif current_user.is_authenticated():
			current_user_role = current_user.get_role()
			if current_user_role in self.available_roles:
				if current_user_role==self.admin_role or current_user_role in self.required_roles:
					return True

		return False

	def render_plugin(self, template_src=None, data=None):
		""" Render html"""
		try:
			if not self.check_role():
				abort(403)

			if not data or not type(data)==dict:
				data = {}
			
			data.update({"current_user": current_user})
			data.update({"url_for": url_for})
			data.update({"plugin_id": self.id})
			args = Struct(**data)

			return self.template.get_template(template_src).render(data=args)
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.lib.plugin.render_plugin()")