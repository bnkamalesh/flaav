from flask import request, abort
from mad.lib.view import View

from forms import ContactForm
from controller import PageActions
from mad.modules.pluginloader.controller import PluginActions

class PageView(View):
	""" Class to handle all static pages """

	def __init__(self):
		super(self.__class__, self).__init__("pages", __name__, url_prefix="", template_folder="")

	def show(self, name, plugin_id):
		""" Render respective templates for the static page"""
		# default page content and template
		try:
			data = {
				"page_title": "",
				"content": ""
			}
			template = name
			# ===
			if name=="home":
				data = {}
				data.update({"page_title": "Home"})

			elif name=="about":
				template = "about"

			elif name=="contact":
				CF = ContactForm(request.form)
				data.update({"contact_form": CF})
				if request.form:
					if CF.validate():
						PA = PageActions()
						result = PA.sendmail(name=CF.name.data, email=CF.email.data, message=CF.message.data)
						if result["status"]=="success":
							data.update({"status": "success", "message": "Thank you for contacting us."})
						else:
							data.update({"status": "failed", "message": "Sorry, could not send your message."})

			elif name=="services" and not plugin_id == None:
				template = "page"
				content = PluginActions().get_plugin_custom_content(plugin_id, request.form, request.args)
				if content:
					data["content"] = content
				else:
					abort(404)

			return self.render("pages/"+template+".html", data=data)

		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.PageView.show()")
			abort(404)

PV = PageView()
pages = PV.get_blueprint()

""" Set URI rules for the blueprint """
@pages.route("/", defaults={"name": "home"})
@pages.route("/<name>", methods=["GET", "POST"])
@pages.route("/<name>/<plugin_id>", methods=["GET", "POST"], defaults={"name": "services"})
def index(name, plugin_id=None):
	return PV.show(name, plugin_id)