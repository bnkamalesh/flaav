from flask import request, current_app
from flask.ext.login import current_user

from mad.lib.loginmanager import Login_Handler, User
from mad.lib.controller import Controller


class UserActions(Controller):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.user = current_user

		if not request.headers.get("X-Real-Ip"):
			self.remote_ip = request.remote_addr
		else:
			self.remote_ip = request.headers.get("X-Real-Ip")

	def login(self, email, password, remember=False):
		""" Login """
		try:
			user = User(email=email, password=password)
			result = user.get(conditions={"email": user.email, "password": user.password}, findone=True)
			if result:
				result.update({"anonymous": False, "authenticated": True})
				user.set_objprops(data=result)
				self.user = user
				Login_Handler.login(user=self.user, remember=remember)
				return {"status": "success", "message": "Succesfully logged in"}
			else:
				self.error_handle.get_error(error="Attempted login, Email:"+email+", password:"+password+", IP: "+self.remote_ip, log_file="logins")

			return {"status": "failed", "message": "Incorrect username/password"}
		except Exception as e:
			self.error_handle.get_error(error="Attempted login, Email:"+email+", password:"+password+", IP: "+self.remote_ip)
			return {"status": "failed", "message": "Incorrect username/password"}

	def encrypt_password(self, password=None):
		""" Returns an encrypted password """
		if password:
			return self.user.enc_password(password=password)
		return None


	def logout(self):
		""" Logout """
		try:
			Login_Handler.logout()
			return {"status": "success", "message": "Logged out Succesfully."}
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.user.controller.UserActions.logout()")
			return {"status": "failed", "message": "Unable to logout user."}

	def add_plugin(self, plugin_name):
		""" Add a plugin to the user's activated plugins list """
		try:
			if plugin_name:
				if not plugin_name in self.user.active_plugins:
					self.user.active_plugins.append(plugin_name)
					self.user.save()
					return {"status": "success", "message": "Added plugin Succesfully"}
			return {"status": "failed", "message": "Could not add plugin"}
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.user.controller.UserActions.add_plugin()")
			return {"status": "failed", "message": "Could not add plugin"}

	def remove_plugin(self, plugin_name):
		""" Remove a plugin from the user's activated plugins list """
		try:
			if plugin_name:
				if plugin_name in self.user.active_plugins:
					self.user.active_plugins.remove(plugin_name)
					self.user.update()
					return {"status": "success", "message": "Removed plugin Succesfully"}

			return {"status": "failed", "message": "Could not add plugin"}
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.user.controller.UserActions.add_plugin()")
			return {"status": "failed", "message": "Could not add plugin"}

	def get_active_plugins(self):
		return self.user.active_plugins


	def prepare_form_data(self, userdata, form_data):
		""" Prepares and returns form from user data """
		try:
			for fieldname, value in form_data.iteritems():
				if fieldname in userdata:
					form_data.update({fieldname: userdata[fieldname]})
			return form_data
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.user.controller.UserActions.prepare_form_data()")
			return {"status": "failed", "message": "Could not prepare user form"}