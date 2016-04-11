from flask import abort, request, session
from flask.ext.login import login_required, current_user
from mad.lib.view import View

from controller import MediaController
from forms import AddMediaForm

class MediaView(View):
	""" Media views """

	def __init__(self):
		super(self.__class__, self).__init__("media", __name__, url_prefix="", template_folder="")
		self.required_roles = ["provider"]

	def show(self, action, media_id=None):
		""" Render respective templates for the static page"""
		# default page content and template
		try:
			data = {}
			media_template = "view"

			# Changing collection for listing media items added through the ad-publisher page
			if request.args.get("unverified-media-items") or request.args.get("unverified-media-item"):
				data.update({"unverified_items": True})
			else:
				data.update({"unverified_items": False})
			# ===

			if action=="view":
				MC = MediaController()

				if data["unverified_items"] == True:
					MC.change_collection(name="media_items", new_col_name="public_media_items")

				if request.args.get("get")=="industries":
					# return the list of industries as an array
					return self.json_out(MC.get_industries(as_list=True))

				elif request.args.get("get")=="geographies":
					return self.json_out(MC.get_geographies(as_list=True))

				elif media_id and current_user.is_authenticated():
					# Show a single media item with all its info
					media_template = "single-view"
					media_item = {}
					conditions = {"_id": media_id}
					# prevent non-admin, non-owner users from viewing a media item
					if not current_user.get_role()==self.admin_role:
						conditions.update({"owner": current_user.get_id()})
					# ===

					for item in MC.get_media_items(conditions=conditions):
						for key, value in item.iteritems():
							if type(value) is list:
								value = ", ".join(value)

							elif key=="customer_type" and value=="both":
								value = "Both B2B and B2C"

							media_item.update({key: value})

					data.update({"media_item": media_item})

				elif current_user.is_authenticated():
					# List all media items, accessible ONLY to admins or display all provider media items.
					# Each media item should/will have an "owner" attribute, which is the user ID of the
					# user adding the media item.
					conditions = {}
					# if not an admin, only items owned by the user are displayed
					if not current_user.get_role()==self.admin_role:
						conditions.update({"owner": current_user.get_id()})
					# ===

					# Apply filters if any
					if request.args.get("filter") and request.args.get("name"):
						data.update({"filter": {"business": request.args.get("name").strip()}})
						conditions.update({"name": request.args.get("name").strip()});
					# ===

					data.update({"media_items": []})
					media_items = MC.get_media_items(conditions=conditions)

					if len(media_items)>0:
						data["media_items"] = media_items

			elif action=="add" and current_user.is_authenticated():
				MC = MediaController()
				media_template = "add"
				AMF = AddMediaForm(request.form)
				AMF.demography.choices = [(x.strip(), x.strip()) for x in MC.get_demographies(as_list=True)]

				if request.form:
					if data["unverified_items"] == True:
						MC.change_collection(name="media_items", new_col_name="public_media_items")

					if AMF.validate():
						data.update({"message": MC.add_media_item(MC.prepare_media_item(form_data=AMF.data))["message"], "status": "success"})
					else:
						data.update({"message": "There were some errors", "status": "failed"})

				data.update({"add_form": AMF})

			elif action=="public-add":
				ajx_resp = False
				MC = MediaController()
				# return the list of industries as an array
				if request.args.get("get")=="industries":
					return self.json_out(MC.get_industries(as_list=True))

				# return the list of geographies as an array
				elif request.args.get("get")=="geographies":
					return self.json_out(MC.get_geographies(as_list=True))

				if request.args.get("next")=="show-form":
					data.update({"show_add_form": True})

				if request.args.get("ajax-response")=="true":
					ajx_resp = True


				self.required_roles = []
				media_template = "public-add"

				AMF = AddMediaForm(request.form)
				AMF.demography.choices = [(x.strip(), x.strip()) for x in MC.get_demographies(as_list=True)]

				if request.form:
					# Remove required validator from fields
					AMF.price = AMF.removeValidators(AMF.price, ["DataRequired"])
					AMF.market_goal = AMF.removeValidators(AMF.market_goal, ["DataRequired"])
					AMF.customer_type = AMF.removeValidators(AMF.customer_type, ["DataRequired"])
					AMF.campaign_length = AMF.removeValidators(AMF.campaign_length, ["DataRequired"])
					AMF.provider_industry = AMF.removeValidators(AMF.provider_industry, ["DataRequired"])
					AMF.viewership_industry = AMF.removeValidators(AMF.viewership_industry, ["DataRequired"])
					AMF.demography = AMF.removeValidators(AMF.demography, ["DataRequired"])
					AMF.geography = AMF.removeValidators(AMF.geography, ["DataRequired"])
					AMF.ad_name = AMF.removeValidators(AMF.ad_name, ["DataRequired"])
					AMF.description = AMF.removeValidators(AMF.description, ["DataRequired"])
					# ==

					status = {"message": "", "status": "success"}

					if AMF.validate():
						MC = MediaController()
						MC.change_collection(name="media_items", new_col_name="public_media_items")

						try:
							if session["media-id"]:
								result = MC.update_media_item(media_item=MC.prepare_media_item(form_data=AMF.data, no_owner=True), media_id=session["media-id"], conditions=None)
							else:
								result = MC.add_media_item(MC.prepare_media_item(form_data=AMF.data, no_owner=True))
								session["media-id"] = result["_id"]

						except KeyError:
							result = MC.add_media_item(MC.prepare_media_item(form_data=AMF.data, no_owner=True))
							session["media-id"] = result["_id"]

						if request.args.get("complete") and request.args.get("complete")=="true":
							session.clear()

						status = {"message": result["message"], "status": result["status"]}
					else:
						status = {"message": "There were some errors", "status": "failed", "errors": AMF.errors}

					if ajx_resp:
						return self.json_out(status)

					data.update(status)

				data.update({"add_form": AMF})

			elif action=="edit" and media_id and current_user.is_authenticated():
				MC = MediaController()
				media_template = "edit"
				AMF = AddMediaForm(request.form)
				AMF.demography.choices = [(x.strip(), x.strip()) for x in MC.get_demographies(as_list=True)]

				if data["unverified_items"] == True:
					MC.change_collection(name="media_items", new_col_name="public_media_items")

				if request.args.get("save"):
					if AMF.validate():
						conditions = None
						# prevent any non-admin, non-owner from updating a media item
						if not current_user.get_role()==self.admin_role:
							conditions = {"owner": current_user.get_id() }
						# ===
						data.update({"message": MC.update_media_item(media_item=MC.prepare_media_item(form_data=AMF.data), media_id=media_id, conditions=conditions)["message"], "status": "success"})

					else:
						data.update({"message": "Error", "status": "failed"})

				else:
					media_item = {}
					# the fields mentioned here will be converted to a comma seperated string from list
					fields_to_join = ["viewership_industry", "provider_industry", "select_markets"]
					# ==

					conditions = {"_id": media_id}

					if not current_user.get_role()==self.admin_role:
						conditions.update({ "owner": current_user.get_id() })

					for item in MC.get_media_items(conditions=conditions):
						for key, value in item.iteritems():
							if key in fields_to_join:
								value = ", ".join(value) 

							media_item.update({key: value})

					for field, value in AMF.data.items():
						if field in media_item:
							AMF[field].data = media_item[field]

					media_item["geography"]
					media_item["demography"]

				data.update({"add_form": AMF})
				data.update({"media_id": media_id})
			return self.render("media/"+media_template+".html", data=data)

		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.MediaView.show()")
			abort(401)

MV = MediaView()
media = MV.get_blueprint()

""" Set URI rules for the blueprint """
@media.route("/dashboard/media", defaults={"action": "view"}, methods=["GET", "POST"])
@media.route("/dashboard/media/<action>", methods=["GET", "POST"])
@media.route("/dashboard/media/<action>/<media_id>", methods=["GET", "POST"])
# @login_required
def index(action, media_id=None):
	return MV.show(action, media_id)

@media.route("/ad-publisher", methods=["GET", "POST"])
def public_add():
	return MV.show(action="public-add", media_id=None)
