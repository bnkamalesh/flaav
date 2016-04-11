import feedparser
from flask import abort, request, url_for
from flask.ext.login import login_required, current_user
from mad.lib.view import View
from controller import DashboardActions
from mad.modules.pluginloader.controller import PluginActions

class DashboardView(View):
	""" Class to handle all dashboard views """
	def __init__(self):
		super(self.__class__, self).__init__("dashboard", __name__, url_prefix="", template_folder="")

	def show(self, name):
		""" Render respective templates for the dashboard view """
		# default page content and template
		try:
			data ={}
			template = "home"
			get_item = request.args.get("get")

			if get_item=="blog-feed":
				feeds = []
				d = feedparser.parse("http://blog.flaav.com/feed")
				feeds.append({"blog_title": d["feed"]["title"]})
				for entry in d["entries"]:
					feeds.append({"title": entry["title"], "link": entry["link"], "author": entry["author_detail"]["name"], "published": entry["published"]})
				return self.json_out(feeds)
			elif get_item=="active-plugins":
				active_plugins = []
				PA = PluginActions()
				for p_name in PA.get_active_plugins():
					plugin = PA.get_pluginbyname(p_name=p_name)
					if plugin:
						active_plugins.append({"url": url_for("pluginloader.index", plugin_id=plugin.id, action="view"), "name": plugin.name, "plugin_id": plugin.id})
				return self.json_out(active_plugins)

			# statistics 
			if name=="home":
				DA = DashboardActions()
				data.update({"media_stat": DA.get_statistics()})
			# ===
			data.update({"dashboard_page": template})
			return self.render("dashboard/"+template+".html", data=data)
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.DashboardView.show()")
			abort(500)

DV = DashboardView()
dashboard = DV.get_blueprint()

""" Set URI rules for the blueprint """
@dashboard.route("/dashboard", defaults={"name": "home"})
@dashboard.route("/dashboard/<name>")
@login_required
def index(name):
	return DV.show(name)