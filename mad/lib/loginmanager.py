import hashlib
from bson.objectid import ObjectId
from flask import current_app
from flask.ext.login import LoginManager, login_user, logout_user, current_user
from model import Model


login_manager = LoginManager()
logged_in_users_list = {}

def config_LM(app):
	global login_manager
	login_manager.init_app(app)
	login_manager.login_view = "/user/login"
	login_manager.login_message = '<span class="error">You should be logged in to view this page. Please login and try again.</span>'

class LoginHandler:
	def __init__(self):
		pass

	def login(self, user, remember=False):
		global logged_in_users_list
		logged_in_users_list.update({user.userid: user})
		login_user(user, remember=remember)

	def logout(self):
		global logged_in_users_list
		cuid = current_user.get_id()
		if cuid in logged_in_users_list:
			del(logged_in_users_list[cuid])
		logout_user()

	def get(self, userid):
		"""" returns a logged in user's User() object """
		if userid in logged_in_users_list:
			return logged_in_users_list[userid]
		return None

Login_Handler = LoginHandler()

@login_manager.user_loader
def load_user(userid):
	return Login_Handler.get(userid)

class User(Model):
	def __init__(self, email=None, password=None, userid=None, name=None, authenticated=False, role="anon", anonymous=True):
		super(self.__class__, self).__init__()
		self.collection_name = "users"
		self.name = name
		self.email = email
		self.role = role
		self.userid = userid
		self.password = self.enc_password(password=password)

		self.active_plugins = self.load_active_plugins()
		self.authenticated = authenticated
		self.anonymous = anonymous

	def load_active_plugins(self):
		""" Return a list of active plugin names """
		user_data = self.get(conditions={"email": self.email, "password": self.password}, findone=True)
		if user_data and "active_plugins" in user_data:
			return user_data["active_plugins"]
		return []

	def enc_password(self, password=None):
		""" Returns an encrypted password """
		return hashlib.sha224(self.email+password+current_app.config["SECRET_KEY"]).hexdigest()

	def set_content(self):
		self.content = {
			"name": self.name,
			"email": self.email,
			"password": self.password,
			"role": self.role,
			"_id": self.get_userid(),
			"active_plugins": self.active_plugins
		}

	def set_objprops(self, data):
		self.name = data["name"]
		self.email = data["email"]
		self.password = data["password"]
		self.userid = unicode(data["_id"])
		self.role = data["role"]
		self.active_plugins = data["active_plugins"]
		self.anonymous = data["anonymous"]
		self.authenticated = data["authenticated"]

	def get_name(self):
		return self.name

	def is_authenticated(self):
		""" Returns True if the user is authenticated, i.e. they have provided valid credentials. """
		return self.authenticated

	def is_active(self):
		""" Returns True if this is an active user. (registered but not validated users are "inactive", in which case
			this function returns False ) """
		if not self.anonymous:
			if self.get_role() in ["anon", "viewer", "buyer", "subscriber", "provider", "admin"]:
				return True
		return False

	def is_anonymous(self):
		""" Returns True if this is an anonymous user. (Actual users should return False instead.) """
		return self.anonymous

	def get_role(self):
		""" Returns the role of current user """
		return self.role

	def get_id(self):
		""" Returns the unique ID of a user """
		return unicode(self.userid)

	def get_userid(self):
		""" Returns actual DB id of the user """
		return ObjectId(self.userid)