import json
import os
import time

from flask import current_app, render_template, Blueprint, abort, url_for
from flask.ext.login import current_user
from errorhandler import ErrorHandler
from mad.lib.cache import Cache

# from htmlmin.minify import html_minify


class View(object):
	def __init__(self, bp_name, filename, url_prefix="", template_folder=""):
		# setting blue print for this module
		self.set_blueprint(bp_name, filename, url_prefix, template_folder)
		# ==
		self.error_handle = ErrorHandler()
		# common - varbiales available to all module templates
		self.common = {}
		# ==

		# Required roles, leaving this empty means anyone can access this module.
		# anon - is the defualt role a(not logged in).
		# viewer - is the default role of a logged in user.
		# buyer - Consumer looking for ad spaces, has access to the search module (has already made a payment).
		# subscriber - A subscribed user
		# provider - Ad space provider, who will have access to add their media to the system.
		# admin - Has access to everything
		self.admin_role = "admin"
		self.available_roles = ["anon", "viewer", "buyer", "subscriber", "provider", self.admin_role]
		self.required_roles = [] # set in each module
		# ==

	def enq_static_plugin(self, items):
		""" Enque static plugins/files to be loaded at the end, after default files"""
		item_type = type(items)
		if item_type is list:
			for item in items:
				self.enqued_plugins.append(item)
		elif item_type is str:
			self.enqued_plugins.append(items)

	def set_blueprint(self, name, filename, url_prefix, template_folder):
		"""Register a Flask Blueprint"""
		self.blueprint = Blueprint(name, filename, url_prefix, template_folder)

	def get_blueprint(self):
		""" Get blueprint """
		return self.blueprint

	def render(self, template, **kwargs):
		""" 
			This function is an encapsulation of Flask's default rendering function,
			it's being used to add any custom variables to be made available in the 
			template file. Also, restrict a view based on any required conditions.
		"""
		kwargs.update({
						"login_url": url_for("user.index", action="login"),
						"logout_url": url_for("user.index", action="logout", next=url_for("pages.index", name="home")),
						"current_year": time.strftime("%Y"),
						"plugin_urls": self.get_plugin_urls(location=current_app.config["STATIC_PATH"]+"/plugins", base_url=url_for("static", filename=""))
					})
		# data common to all modules
		kwargs.update(self.common)
		# ==

		if not self.check_role():
			abort(403)

		kwargs.update(page_name=template[template.rfind("/")+1:template.rfind(".html")])
		self.load_jinja_fns()
		return render_template(template, **kwargs)

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

	def get_wtf_errors(self, wtf_errors):
		""" Convert wt-forms errors into a single string """
		messages = []
		messages.append('<ol class="wtf-errors">')
		for field, errors in wtf_errors.iteritems():
			messages.append("<li>"+field+": <br />")
			for error in errors:
				messages.append("&mdash; "+error+ "<br />")
			messages.append("</li>")
		messages.append("</ol>")
		return "".join(messages)

	def json_out(self, data):
		""" This function returns a JSON-ified string of the given input """
		return json.dumps(data)

	def get_plugin_urls(self, location, base_url):
		""" 
		Load plugins from static/plugins/ . Only js & css files are loaded
		location: directory in which plugin files are located
		"""
		plugins = Cache.get_item("plugins")
		if plugins==None:
			plugins = []

			files = os.listdir(location)
			for root, dirs, files in os.walk(location):
				for f in files:
					fullpath = os.path.join(root, f)
					if os.path.splitext(fullpath)[1] == '.css':
						url = base_url + fullpath[fullpath.find("plugins"):]
						url = url.replace("\\", "/")
						plugins.append( url )

			Cache.set_item("plugins", plugins)
		return plugins

	def load_jinja_fns(self):
		"""
		Load a set of custom functions, to be used inside jinja templates
		"""

		# Function for jinja, to remove duplicates from flashed messages
		def remove_duplicates(msgs):
			uniq_msgs = []
			for msg in msgs:
				if msg not in uniq_msgs:
					uniq_msgs.append(msg)

			return uniq_msgs

		current_app.jinja_env.globals.update(remove_duplicates=remove_duplicates)