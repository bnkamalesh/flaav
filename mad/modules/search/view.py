import ast
import datetime
from flask import abort, request, redirect, url_for
from flask.ext.login import login_required
from mad.lib.view import View

from forms import SearchForm, SaveSearchForm
from controller import SearchController

class SearchView(View):
	""" Class to handle all static pages """

	def __init__(self):
		super(self.__class__, self).__init__("search", __name__, url_prefix="", template_folder="")

	def show(self, action):
		""" Render respective templates for search [search page, search results page etc]"""
		try:
			data = {}
			if action=="" or action=="results": #this is the search page
				SC = SearchController()
				if request.args.get("get")=="search-history":
					search_history = []
					for item in SC.get_search_history():
						search_history.append({"title": item["title"], "search_id": str(item["_id"]), "created_on": str(item["created_on"]), "details": item["searchparams"]})
					return self.json_out(search_history)

				search_template = "search"
				searchform = SC.prepare_form_data(SearchForm(request.form))
				if action=="results":
					searchparams = None
					savesearchform = SaveSearchForm(request.form)
					search_template = "results"
					if request.form:
						if "searchparams" in request.form:
							if savesearchform.validate():
								try:
									searchparams = ast.literal_eval(savesearchform.data["searchparams"])
									if type(searchparams)==dict:
										return self.json_out(SC.save_search(searchparams, title=savesearchform.title.data))
								except Exception as e:
									return self.json_out({"status": "failed", "message": "Incorrect search parameters received."})
							else:
								return self.json_out({"status": "failed", "message": self.get_wtf_errors(savesearchform.errors) })
						else:
							if searchform.validate():
								searchparams = searchform.data
							else:
								search_template = "search"

					elif request.args.get("search_id"):
						searchparams = SC.get_search_params(search_id=request.args.get("search_id"))
					else:
						return redirect(url_for("search.index", action=""))

					savesearchform.searchparams.data = searchparams
					data.update({"media_items": SC.get_search_results(searchparams)})
					data.update({"savesearchform": savesearchform})

				elif request.args.get("delete"):
					return self.json_out(SC.delete_search_history(search_id=request.args.get("delete")))


				data.update({"searchform": searchform})
			return self.render("search/"+search_template+".html", data=data)
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.SearchView.show()")
			abort(500)

SV = SearchView()
search = SV.get_blueprint()

""" Set URI rules for the blueprint """
@search.route("/search", defaults={"action": ""}, methods=["GET", "POST"])
@search.route("/search/<action>", methods=["GET", "POST"])
def index(action):
	return SV.show(action)