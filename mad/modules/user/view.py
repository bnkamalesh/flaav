from flask import redirect, request, url_for, abort
from flask.ext.login import current_user

from mad.lib.view import View
from controller import UserActions
from forms import LoginForm, RegistrationForm, UpdateUserData


class UserView(View):
	""" Class to handle user views """

	def __init__(self):
		super(self.__class__, self).__init__("user", __name__)
		self.require_login = False

	def show(self, action):
		UA = UserActions()
		self.required_roles = []
		template = ""
		data = {}
		try:
			if current_user.is_authenticated():
				data.update({"message": "You're already logged in."})
			else:
				data.update({
					"login_form": LoginForm(),
					"reg_form": RegistrationForm()
				})

			if action=="logout":
				# Logout
				if current_user.is_authenticated():
					result = UA.logout()
					if result["status"]=="success":
						return redirect(request.args.get("next") or url_for("pages.index", name="home"))
					else:
						data.update({"message": "Unknown error occurred. Could not log user out."})
				else:
					return redirect(url_for("user.index", action="login"))

			elif action=="login":
				# Login
				template = "login"
				if request.form:
					lform = LoginForm(request.form)
					if lform.validate():
						result = UA.login(email=lform.email.data, password=lform.password.data, remember=False)
						if result["status"]=="success":
							nxt_url = request.args.get("next")
							if not nxt_url or nxt_url == "/":
								nxt_url = url_for("dashboard.index")

							return redirect(nxt_url)
						else:
							data.update({"status": "failed", "message": result["message"]})
					else:
						data.update({"login_form": lform})

			elif action=="register" and request.form:
				# User registration
				rform = RegistrationForm(request.form)

			elif action=="account" and current_user.is_authenticated():
				# User account page
				data.update({"message": "", "status": ""})

				self.required_roles = ["provider", "viewer", "subscriber", "buyer"]
				template = "account"
				UUD = UpdateUserData(request.form)

				if request.form:
					if UUD.validate():
						if UUD.password.data:
							UUD.password.data = UA.encrypt_password(UUD.password.data)
						else:
							UUD.password.data = current_user.password
						
						current_user.password = UUD.password.data
						current_user.update()

						data.update({"message": "Successfully updated your account details", "status": "success"})
				else:
					UUD.name.data = current_user.get_name()

				data.update({"update_form": UUD})

			return self.render("user/"+template+".html", data=data)
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.UserView.show()")
			abort(401)


UV = UserView()
user = UV.get_blueprint()

""" Set URI rules for the blueprint """
@user.route("/user/", defaults={"action": "account"}, methods=["GET", "POST"])
@user.route("/user/<action>", methods=["GET", "POST"])
def index(action):
	return UV.show(action)