from flask import request, current_app
from flask.ext.login import current_user
from flask_mail import Mail, Message

from mad.lib.loginmanager import Login_Handler, User
from mad.lib.controller import Controller


class PageActions(Controller):
	def __init__(self):
		super(self.__class__, self).__init__()

	def sendmail(self, name=None, email=None, message=None):
		try:
			if name and email and message:
				mail = Mail(current_app)
				msg = Message("Flaav- Contact Form", sender=("Flaav - Contact form", "contactform@flaav.com"), recipients=["jordan.flaav@gmail.com", "kbn.flaav@gmail.com"])
				message = "From: "+name+" ("+email+")<br />Message: <br/>" + message
				msg.html = message
				with current_app.app_context():
					mail.send(msg)

				return {"status": "success", "message": "Mail sent successfully"}

			return {"status": "failed", "message": "Could not send message"}
		except Exception as e:
			self.error_handle.get_error(error=str(e), occurred_at="mad.modules.pages.controller.sendmail()")
			return {"status": "failed", "message": "failed"}