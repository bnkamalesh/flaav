from flask import abort, request
from flask.ext.login import login_required
from mad.lib.view import View
from controller import PluginActions

class PluginsView(View):
	""" Class to handle all dashboard views """
	def __init__(self):
		super(self.__class__, self).__init__("pluginloader", __name__, url_prefix="", template_folder="")
		self.required_roles = ["subscriber"]

	def show(self, plugin_id=None, action=None):
		""" Render respective templates for the pluginloader view """
		try:
			data ={}
			PA = PluginActions()
			template = "plugins"

			if plugin_id:
				if "name" in request.form:

					if "activate" in request.form:
						return self.json_out(PA.activate_plugin(name=request.form.get("name")))

					elif "deactivate" in request.form:
						return self.json_out(PA.deactivate_plugin(name=request.form.get("name")))
				else:
					plugin = PA.get_pluginbyid(p_id=plugin_id, user_page=True)

					if plugin and plugin.is_active:
						content = ""
						data.update({"plugin_id": plugin.id, "plugin_name": plugin.name })
						template = "plugin-home"
						po = plugin.get_plugin_object()

						if action=="view":
							content = po.plugin_home()

						elif action=="settings":
							content = po.plugin_settings(params=request.args, form=request.form)

							# This section is used if any plugin requires to return data via AJAX
							if request.args.get("get"):
								return self.json_out(content)

						data.update({"content": content})

			else:
				data.update({"plugins": PA.get_available_plugins(user_page=True)})

			return self.render("pluginloader/"+template+".html", data=data)

		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.PluginView.show()")
			if "403" in str(e):
				abort(403)
			else:
				abort(500)

PV = PluginsView()
pluginloader = PV.get_blueprint()

""" Set URI rules for the blueprint """
@pluginloader.route("/dashboard/services", methods=["GET", "POST"])
@pluginloader.route("/dashboard/services/<plugin_id>/<action>", methods=["GET", "POST"])
@login_required
def index(plugin_id=None, action=None):
	return PV.show(plugin_id, action)
