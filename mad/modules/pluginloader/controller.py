import os
import imp
from flask import current_app
from mad.lib.controller import Controller
from mad.modules.user.controller import UserActions

class PluginBase:
	pobj = None
	def __init__(self, name=None, pid=None, filename=None, classname=None, author=None, version=None, description=None, website=None, path=None):
		self.name = name
		self.id = pid
		self.description = description
		self.author = author
		self.website = website
		self.version = version
		self.abspath = path
		self.classname = classname
		#Filename of the plugin's source file
		self.filename = filename
		self.is_active = False
		self.pobj = None
		self.pclassobj = None

	def activate(self):
		try:
			if not self.pobj:
				self.pobj = self.get_plugin_object()

			self.is_active = True
			self.pobj.activate()
		except Exception as e:
			print "occurred_at: mad.modules.pluginloader.PluginBase.activate : "+str(e)

	def deactivate(self):
		try:
			if not self.pobj:
				self.pobj = self.get_plugin_object()
			self.is_active = False
			self.pobj.deactivate()
		except Exception as e:
			print "occurred_at: mad.modules.pluginloader.PluginBase.deactivate : "+str(e)

	def get_plugin_object(self):
		try:
			if not self.pobj:
				self.pobj = getattr(imp.load_source(self.id, self.abspath+self.filename+'.py'), self.classname)()
			return self.pobj
		except Exception as e:
			print "occurred_at: mad.modules.pluginloader.PluginBase.get_plugin_object : "+str(e)

class PluginActions(Controller):
	def __init__(self):
		super(self.__class__, self).__init__()
		# plugin manager
		self.plugin_root = current_app.config["PLUGINS_PATH"]
		self.UA = UserActions()

	def get_available_plugins(self, user_page=False):
		""" Returns a list of all available plugins """
		try:
			plugins = self.cache_handle.get_item("all_plugins")
			
			if not plugins:
				plugins = []
				for name in os.listdir(self.plugin_root):
					p_path = os.path.join(self.plugin_root, name)
					info_file = p_path+'/'+name+'.meta'
					if os.path.isfile(info_file):
						f = open(info_file)
						if f:
							pb = PluginBase()
							for line in f:
								label, value = line.split("=")
								label = label.strip().lower()
								if label and value and hasattr(pb, label):
									value = value.strip()
									setattr(pb, label, value)

							if pb.name and pb.id and pb.classname and pb.filename:
								pb.abspath = p_path+'/'
								plugins.append(pb)

				self.cache_handle.set_item("all_plugins", plugins)

			if user_page:
				active_plugins = self.get_active_plugins()
				for plugin in plugins:
					if plugin.name in active_plugins:
						plugin.activate()

			return plugins
		except Exception as e:
			return self.error_handle.get_error(error=str(e), occurred_at="mad.modules.pluginloader.PluginActions.get_available_plugins()")

	def get_pluginbyid(self, p_id=None, user_page=False):
		""" Return a plugin by its ID """
		try:
			for item in self.get_available_plugins(user_page=user_page):
				if item.id==p_id:
					return item
			return None
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.PluginActions.get_pluginbyid()")
			return None

	def get_pluginbyname(self, p_name=None, user_page=False):
		""" Return a plugin by its name """
		try:
			for item in self.get_available_plugins(user_page=user_page):
				if item.name==p_name:
					return item
			return None
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.PluginActions.get_pluginbyname()")
			return None

	def get_active_plugins(self):
		""" Returns all activated plugins for the user """
		return self.UA.get_active_plugins()

	def activate_plugin(self, name=None, category="Default"):
		""" Activate a plugin provided its name """
		try:
			if name:
				name = name.strip()
				plugin = self.get_pluginbyname(p_name=name)
				plugin.activate()
				self.UA.add_plugin(plugin_name=name)
				return {"status": "success", "message": "Plugin activated successfully"}
			return {"status": "failed", "message": "Could not activate plugin"}
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.PluginActions.activate_plugin()")
			return {"status": "failed", "message": "Could not activate plugin"}	

	def deactivate_plugin(self, name=None, category="Default"):
		""" Deactivate a plugin, provided its name """
		try:
			if name:
				name = name.strip()
				plugin = self.get_pluginbyname(p_name=name)
				plugin.deactivate()
				self.UA.remove_plugin(plugin_name=name)
				return {"status": "success", "message": "Plugin deactivated successfully"}

			return {"status": "failed", "message": "Could not deactivate plugin"}
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.PluginActions.deactivate_plugin()")
			return {"status": "failed", "message": "Could not deactivate plugin"}	

	def get_plugin_custom_content(self, plugin_id, form=None, params=None):
		""" Get custom content a plugin wants to push to public view  """
		try:
			if plugin_id:
				plugin = self.get_pluginbyid(plugin_id)
				if plugin:
					content = plugin.get_plugin_object().public_content(form, params)
					if content:
						return content

			return None

		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.PluginActions.get_plugin_custom_content()")
